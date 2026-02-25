from mcp.server.fastmcp import FastMCP
from pokemcp.tools import pokemon, moves, items, types

mcp = FastMCP("pokemcp")

mcp.include_router(pokemon.router)
mcp.include_router(moves.router)
mcp.include_router(items.router)
mcp.include_router(types.router)