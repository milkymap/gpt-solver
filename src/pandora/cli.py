from typing import Optional
import click
import asyncio
from dotenv import load_dotenv
from .core.engine import Engine
from .mcp.handler import MCPHandler

@click.command()
@click.option("--model", "-m", default="gpt-4.1", 
              type=click.Choice(["gpt-4.1", "gpt-4.1-mini"]))
@click.option("--openai_api_key", "-k", required=True, envvar="OPENAI_API_KEY")
@click.option("--path2mcp_servers_file", "-mcp", type=click.Path(exists=False))
@click.option("--startup_timeout", "-t", default=10.0, type=float)
@click.option("--parallel_tool_calls", "-p", is_flag=True)
@click.option("--print_mode", default="rich", 
              type=click.Choice(["json", "rich"]))
def main(model: str, openai_api_key: str, path2mcp_servers_file: Optional[str], 
         startup_timeout: float, parallel_tool_calls: bool, print_mode: str):
    async def run():
        mcp_handler = MCPHandler(
            path2mcp_servers_file=path2mcp_servers_file, 
            startup_timeout=startup_timeout
        )
        async with mcp_handler:
            await mcp_handler.launch_mcp_servers()
            engine = Engine(
                mcp_handler=mcp_handler,
                openai_api_key=openai_api_key, 
                model=model,
                parallel_tool_calls=parallel_tool_calls,
                default_print_mode=print_mode
            )
            async with engine:
                await engine.loop()
    asyncio.run(run())

if __name__ == "__main__":
    main()