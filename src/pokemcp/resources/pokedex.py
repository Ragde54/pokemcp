import json
import logging
from pokemcp.app import mcp
from pokemcp.api import PokeAPIClient, CacheLayer
from pokemcp.config import settings

logger = logging.getLogger(__name__)

client = PokeAPIClient()
cache = CacheLayer(settings.redis_url)


@mcp.resource("pokedex://pokemon/{name_or_id}")
async def pokemon_resource(name_or_id: str) -> str:
    """
    MCP resource representing a single Pokémon.
    URI: pokedex://pokemon/pikachu  or  pokedex://pokemon/25
    Returns full Pokémon data as JSON.
    """
    key = f"resource:pokemon:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://species/{name_or_id}")
async def species_resource(name_or_id: str) -> str:
    """
    MCP resource representing a Pokémon species.
    URI: pokedex://species/pikachu  or  pokedex://species/25
    Returns species data including Pokédex entries and evolution chain URL.
    """
    key = f"resource:species:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon-species/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://move/{name_or_id}")
async def move_resource(name_or_id: str) -> str:
    """
    MCP resource representing a move.
    URI: pokedex://move/tackle  or  pokedex://move/33
    Returns full move data as JSON.
    """
    key = f"resource:move:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/move/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://item/{name_or_id}")
async def item_resource(name_or_id: str) -> str:
    """
    MCP resource representing an item.
    URI: pokedex://item/master-ball  or  pokedex://item/1
    Returns full item data as JSON.
    """
    key = f"resource:item:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/item/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://type/{name_or_id}")
async def type_resource(name_or_id: str) -> str:
    """
    MCP resource representing a type.
    URI: pokedex://type/fire  or  pokedex://type/10
    Returns full type data including damage relations as JSON.
    """
    key = f"resource:type:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/type/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://ability/{name_or_id}")
async def ability_resource(name_or_id: str) -> str:
    """
    MCP resource representing an ability.
    URI: pokedex://ability/intimidate  or  pokedex://ability/22
    Returns ability data including effect descriptions and Pokémon with the ability.
    """
    key = f"resource:ability:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/ability/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://generation/{name_or_id}")
async def generation_resource(name_or_id: str) -> str:
    """
    MCP resource representing a generation.
    URI: pokedex://generation/generation-i  or  pokedex://generation/1
    Returns all Pokémon species and version groups introduced in that generation.
    """
    key = f"resource:generation:{str(name_or_id).lower()}"

    async def fetch():
        data = await client.get(f"/generation/{str(name_or_id).lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)


@mcp.resource("pokedex://pokedex/{name_or_id}")
async def pokedex_resource(name_or_id: str) -> str:
    """
    MCP resource representing a regional Pokédex.
    URI: pokedex://pokedex/national  or  pokedex://pokedex/kanto
    Returns all Pokémon entries in that Pokédex with their regional numbers.
    """
    key = f"resource:pokedex:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokedex/{name_or_id.lower()}")
        return json.dumps(data)

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result if isinstance(result, str) else json.dumps(result)
