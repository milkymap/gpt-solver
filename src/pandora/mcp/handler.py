import json 
import asyncio 
import zmq
import zmq.asyncio
from contextlib import asynccontextmanager, AsyncExitStack
from typing import List, Dict, Tuple, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .config import MCPConfig, MCPServersConfig
from pandora.log import logger

class MCPHandler:
    def __init__(self, path2mcp_servers_file: Optional[str] = None, startup_timeout: float = 10.0):
        self.path2mcp_servers_file = path2mcp_servers_file
        self.startup_timeout = startup_timeout
        self.mcp_workers: List[asyncio.Task] = []
        self.tools: List[Dict[str, Any]] = []
        self.tool_registry: Dict[str, Dict] = {}  # Registry for tool metadata
        
        if path2mcp_servers_file is not None:
            with open(path2mcp_servers_file, "r") as file_pointer:
                configs = json.load(file_pointer)
            self.mcp_servers_config = MCPServersConfig(**configs)
        else:
            self.mcp_servers_config = MCPServersConfig(mcpServers={})
    
    async def __aenter__(self) -> 'MCPHandler':
        self.mutex = asyncio.Lock()
        self.barrier = asyncio.Barrier(len(self.mcp_servers_config.mcpServers) + 1)
        self.ctx = zmq.asyncio.Context()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            logger.error(exc_value)
            logger.exception(traceback)
        for worker in self.mcp_workers:
            worker.cancel()
        await asyncio.gather(*self.mcp_workers, return_exceptions=True)
        self.ctx.term()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return self.tools
    
    async def launch_mcp_servers(self) -> None:
        for server_name, mcp_config in self.mcp_servers_config.mcpServers.items():
            task = asyncio.create_task(self.mcp_worker(server_name, mcp_config))
            self.mcp_workers.append(task)
        await self.barrier.wait()
        
    async def mcp_worker(self, server_name: str, mcp_config: MCPConfig) -> None:
        logger.info(f"Starting MCP worker for {server_name}")
        
        server_params = StdioServerParameters(
            command=mcp_config.command,
            args=mcp_config.args,
            env=mcp_config.env
        )

        initialized = False
        try:
            async with stdio_client(server_params) as stdio_transport:
                reader, writer = stdio_transport
                async with ClientSession(read_stream=reader, write_stream=writer) as client_session:
                    logger.info(f"Initializing MCP server {server_name}")

                    try:
                        async with asyncio.timeout(delay=self.startup_timeout):
                            await client_session.initialize()
                    except TimeoutError:
                        logger.error(f"MCP server {server_name} failed to initialize within timeout")
                        await self.barrier.wait()
                        return
                    except Exception as e:
                        logger.error(f"Error initializing MCP server {server_name}: {e}")
                        await self.barrier.wait()
                        return
                    
                    logger.info(f"MCP server {server_name} initialized")
                    initialized = True
                    await self.barrier.wait()
                    
                    # Get available tools from server
                    try:
                        results = await client_session.list_tools()
                        logger.info(f"{len(results.tools)} tools found for {server_name}")
                        tools = []
                        for tool in results.tools:
                            full_tool_name = f'mcp__{server_name}__{tool.name}'
                            item = {
                                "name": full_tool_name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema
                            }
                            tools.append(item)
                            
                            # Store in registry
                            self.tool_registry[full_tool_name] = {
                                "server_name": server_name,
                                "tool_name": tool.name
                            }
                        
                        async with self.mutex:
                            self.tools.extend(tools)
                    except Exception as e:
                        logger.error(f"Error listing tools for {server_name}: {e}")
                    
                    # Set up ZMQ router for handling tool calls
                    router_socket = self.ctx.socket(zmq.ROUTER)
                    router_socket.bind(f"inproc://mcp_server_{server_name}")

                    while True:
                        try:
                            if await router_socket.poll(timeout=1000) != zmq.POLLIN:
                                continue
                            
                            incoming = await router_socket.recv_multipart()
                            if len(incoming) < 4:
                                logger.error(f"Invalid message format: {incoming}")
                                continue
                                
                            client_id, _, name_bytes, args_bytes = incoming
                            name = name_bytes.decode()
                            arguments = json.loads(args_bytes.decode())
                            
                            response = await self._call_tool(client_session, name, arguments)
                            await router_socket.send_multipart([
                                client_id, 
                                b"", 
                                json.dumps(response).encode()
                            ])
                            
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            logger.error(f"Tool call error: {e}")
                            error_response = json.dumps({
                                "status": "error",
                                "error": str(e)
                            })
                            await router_socket.send_multipart([client_id, b"", error_response.encode()])
                    
                    router_socket.close(linger=0)
        except Exception as e:
            logger.error(f"Error in MCP server {server_name} communication: {e}")
        if not initialized:
            logger.warning(f"MCP server {server_name} failed to initialize")
            await self.barrier.wait()
            
    async def _call_tool(self, client_session: ClientSession, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call on the MCP server."""
        try:
            # Extract the actual tool name from the prefixed name
            if name.startswith("mcp__"):
                # Format is mcp__server__tool, so split to get the actual tool name
                parts = name.split("__")
                if len(parts) >= 3:
                    actual_tool_name = "__".join(parts[2:])  # Handle names with multiple underscores
                else:
                    actual_tool_name = name
            else:
                actual_tool_name = name
                
            tool_call_result = await client_session.call_tool(
                name=actual_tool_name,
                arguments=arguments
            )
            return {
                "status": "success",
                "content_blocks": [block.model_dump() for block in tool_call_result.content]
            }
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP tool by name."""
        if name not in self.tool_registry:
            return json.dumps({
                "status": "error",
                "error": f"Tool {name} not found in registry"
            })
        
        server_name = self.tool_registry[name]["server_name"]
        dealer_socket = self.ctx.socket(zmq.DEALER)
        dealer_socket.connect(f"inproc://mcp_server_{server_name}")
        
        try:
            # Send just the tool name without the mcp__ prefix
            tool_name = self.tool_registry[name]["tool_name"]
            await dealer_socket.send_multipart([
                b"", 
                tool_name.encode(), 
                json.dumps(arguments).encode()
            ])
            
            # Receive response with timeout
            try:
                async with asyncio.timeout(60.0):  # 60-second timeout for tool execution
                    response = await dealer_socket.recv_multipart()
            except asyncio.TimeoutError:
                return json.dumps({
                    "status": "error",
                    "error": "Timeout waiting for tool response"
                })
                
            if len(response) < 3:
                return json.dumps({
                    "status": "error",
                    "error": f"Invalid response format: {response}"
                })
                
            _, _, encoded_response = response
            return encoded_response.decode()
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
        finally:
            dealer_socket.close(linger=0)
