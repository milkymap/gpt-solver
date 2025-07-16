import json 
import asyncio 
import zmq
import zmq.asyncio
from contextlib import asynccontextmanager, AsyncExitStack

from enum import Enum
from pydantic import BaseModel

from typing import List, Dict, Tuple, Optional, Any, Self 

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from pandora.log import logger

class MCPConfig(BaseModel):
    command:str 
    args:Optional[List[str]] = None
    env:Optional[Dict[str, str]] = None

class MCPServersConfig(BaseModel):
    mcpServers:Dict[str, MCPConfig]

class MCPHandler:
    def __init__(self, path2mcp_servers_file:Optional[str]=None, startup_timeout:float=10.0):
        self.path2mcp_servers_file = path2mcp_servers_file
        self.startup_timeout = startup_timeout

        if path2mcp_servers_file is not None:
            with open(path2mcp_servers_file, "r") as file_pointer:
                configs = json.load(file_pointer)
            self.mcp_servers_config = MCPServersConfig(**configs)
        else:
            self.mcp_servers_config = MCPServersConfig(mcpServers={})
        
    async def __aenter__(self) -> Self:
        self.mutex = asyncio.Lock()
        self.barrier : asyncio.Barrier = asyncio.Barrier(len(self.mcp_servers_config.mcpServers) + 1)
        self.ctx = zmq.asyncio.Context()
        self.mcp_workers:List[asyncio.Task] = []
        self.tools:List[Dict[str, Any]] = []
        
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
            print(f"launching mcp server {server_name}")
            task = asyncio.create_task(self.mcp_worker(server_name, mcp_config))
            print(f"task {task} created")
            self.mcp_workers.append(task)
        
        await self.barrier.wait()
        
    async def _call_tool(self, client_session:ClientSession, name:str, arguments:Dict[str, Any]) -> Any:
        try:
            tool_call_result = await client_session.call_tool(
                name=name,
                arguments=arguments
            )
            response = {
                "status": "success",
                "content_blocks": [ block.model_dump() for block in tool_call_result.content]
            }
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            response = {
                "status": "error",
                "error": str(e)
            }
        return response

    async def mcp_worker(self, server_name:str, mcp_config:MCPConfig) -> None:
        logger.info(f"mcp worker {server_name} started")
        server_params = StdioServerParameters(
            command=mcp_config.command,
            args=mcp_config.args,
            env=mcp_config.env
        )

        initialized = False
        async with stdio_client(server_params) as stdio_transport:
            reader, writer = stdio_transport
            async with ClientSession(read_stream=reader, write_stream=writer) as client_session:
                logger.info(f"initializing mcp server {server_name}")

                try:
                    async with asyncio.timeout(delay=self.startup_timeout):
                        await client_session.initialize()
                except TimeoutError:
                    logger.warning(f"MCP server {server_name} failed to initialize")
                    await self.barrier.wait()  # do not block the main thread
                    return
                
                logger.info(f"mcp server {server_name} initialized")
                initialized = True
                await self.barrier.wait()
                results = await client_session.list_tools()
                logger.info(f"{len(results.tools)} tools found for {server_name}")
                tools = []
                for tool in results.tools:
                    item = {
                        "name": f'mcp__{server_name}__{tool.name}',  # inspired with claude code standard
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    tools.append(item)
                    print(json.dumps(item, indent=3))
                
                async with self.mutex:
                    self.tools.extend(tools)
                
                router_socket = self.ctx.socket(zmq.ROUTER)
                router_socket.bind(f"inproc://mcp_server_{server_name}")

                while True:
                    try:
                        event = await router_socket.poll(timeout=1000)
                        if event != zmq.POLLIN:
                            continue 
                        logger.info(f"MCP server {server_name} received a message")
                        incoming_message = await router_socket.recv_multipart()
                        client_socket_id, _, encoded_name, encoded_args = incoming_message
                        name = encoded_name.decode()
                        arguments = json.loads(encoded_args.decode())
                        response = await self._call_tool(client_session, name, arguments)
                        stringified_content = json.dumps(response)
                        await router_socket.send_multipart([client_socket_id, b"", stringified_content.encode()])
                        logger.info(f"MCP server {server_name} sent a response")
                    except asyncio.CancelledError:
                        logger.warning(f"MCP server {server_name} cancelled")
                        break
                    except Exception as e:
                        logger.error(f"Error calling tool {encoded_name.decode()}: {e}")

                
                router_socket.close(linger=0)
        
        if not initialized:
            logger.warning(f"MCP server {server_name} failed to initialize")
            await self.barrier.wait()  # do not block the main thread
            
    async def execute_tool(self, name:str, arguments:Dict[str, Any]) -> str:
        _, server_name, tool_name = name.split("__")  # ignore the mcp__ prefix
        dealer_socket = self.ctx.socket(zmq.DEALER)
        dealer_socket.connect(f"inproc://mcp_server_{server_name}")
        await dealer_socket.send_multipart([b"", tool_name.encode(), json.dumps(arguments).encode()])
        _, encoded_response = await dealer_socket.recv_multipart()
        dealer_socket.close(linger=0)
        return encoded_response.decode()



        
        


