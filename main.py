import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("pokemcp")

#Constants
POKEMON_API_URL = "https://pokeapi.co/api/v2"

async def get_pokemon(url: str):
    """Get a pokemon from the API
    
    Args:
        url (str): The url to get the pokemon data from
    
    Returns:
        dict: The pokemon data
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_pokemon_by_name(name: str):
    """Get a pokemon from the API by name
    
    Args:
        name (str): The name of the pokemon to get
    
    Returns:
        dict: The pokemon data
    """
    url = f"{POKEMON_API_URL}/pokemon/{name}"
    return await get_pokemon(url)

def main():
    print("Hello from pokemcp!")


if __name__ == "__main__":
    main()
