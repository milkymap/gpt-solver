import click 
from pandora.engine import Engine
from pandora.mcp_servers_handler import MCPHandler
from os import getenv
import asyncio
from typing import Optional

@click.command()
@click.option("--model", "-m", type=click.Choice(["gpt-4.1", "gpt-4.1-mini"]), default="gpt-4.1")
@click.option("--openai_api_key", "-k", type=str, envvar="OPENAI_API_KEY", required=True)
@click.option("--path2mcp_servers_file", "-mcp", type=click.Path(exists=False, dir_okay=False))
@click.option("--startup_timeout", "-t", type=float, default=10.0)
@click.option("--parallel_tool_calls", "-p", is_flag=True, default=False)
def main(model:str, openai_api_key:str, path2mcp_servers_file:Optional[str]=None, startup_timeout:float=10.0, parallel_tool_calls:bool=False) -> None:
    async def main_loop():
        print(parallel_tool_calls)
        mcp_handler = MCPHandler(path2mcp_servers_file=path2mcp_servers_file, startup_timeout=startup_timeout)
        async with mcp_handler as mcp_handler:
            await mcp_handler.launch_mcp_servers()
            engine = Engine(
                mcp_handler=mcp_handler,
                openai_api_key=openai_api_key, 
                model=model,
                parallel_tool_calls=parallel_tool_calls
            )
            async with engine as engine:
                await engine.loop()
    asyncio.run(main_loop())
