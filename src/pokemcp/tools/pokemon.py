import logging
from pokemcp.app import mcp
from pokemcp.api import PokeAPIClient, CacheLayer
from pokemcp.config import settings
from pokemcp.models.pokemon import Pokemon, PokemonSummary, EvolutionChain

logger = logging.getLogger(__name__)

client = PokeAPIClient()
cache = CacheLayer(settings.redis_url)


@mcp.tool()
async def get_pokemon(name_or_id: str) -> dict:
    """
    Get full details for a Pokémon by name or Pokédex ID.
    Returns species info, types, stats, abilities, sprites, and more.
    """
    key = f"pokemon:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon/{name_or_id.lower()}")
        return Pokemon(**data).model_dump_json()

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"pokemon": result}


@mcp.tool()
async def get_pokemon_species(name_or_id: str) -> dict:
    """
    Get species-level data for a Pokémon including flavor text (Pokédex entries),
    habitat, generation, legendary/mythical status, and gender rate.
    """
    key = f"pokemon_species:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon-species/{name_or_id.lower()}")
        return data

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"species": result}


@mcp.tool()
async def get_pokemon_stats(name_or_id: str) -> dict:
    """
    Get base stats for a Pokémon (HP, Attack, Defense, Sp. Atk, Sp. Def, Speed)
    along with the total base stat sum.
    """
    key = f"pokemon_stats:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon/{name_or_id.lower()}")
        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        stats["total"] = sum(stats.values())
        return stats

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"name": name_or_id, "stats": result}


@mcp.tool()
async def get_pokemon_abilities(name_or_id: str) -> dict:
    """
    Get all abilities for a Pokémon, including whether they are hidden abilities.
    """
    key = f"pokemon_abilities:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon/{name_or_id.lower()}")
        abilities = [
            {
                "name": a["ability"]["name"],
                "is_hidden": a["is_hidden"],
                "slot": a["slot"],
            }
            for a in data["abilities"]
        ]
        return abilities

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"name": name_or_id, "abilities": result}


@mcp.tool()
async def get_evolution_chain(name_or_id: str) -> dict:
    """
    Get the full evolution chain for a Pokémon species.
    Returns the chain of evolutions with trigger conditions.
    """
    key = f"evolution_chain:{name_or_id.lower()}"

    async def fetch():
        species = await client.get(f"/pokemon-species/{name_or_id.lower()}")
        chain_url = species["evolution_chain"]["url"]
        chain_id = chain_url.rstrip("/").split("/")[-1]
        chain_data = await client.get(f"/evolution-chain/{chain_id}")
        return chain_data

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"evolution_chain": result}


@mcp.tool()
async def list_pokemon(limit: int = 20, offset: int = 0) -> dict:
    """
    List Pokémon with pagination. Returns names and URLs.
    Max limit is 100 per request.
    """
    limit = min(limit, 100)
    key = f"pokemon_list:{limit}:{offset}"

    async def fetch():
        data = await client.get(f"/pokemon?limit={limit}&offset={offset}")
        return [PokemonSummary(name=p["name"], url=p["url"]).model_dump() for p in data["results"]]

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"pokemon": result, "limit": limit, "offset": offset}


@mcp.tool()
async def search_pokemon_by_type(type_name: str) -> dict:
    """
    Get all Pokémon that belong to a given type (e.g. 'fire', 'water', 'dragon').
    """
    key = f"pokemon_by_type:{type_name.lower()}"

    async def fetch():
        data = await client.get(f"/type/{type_name.lower()}")
        return [
            {"name": p["pokemon"]["name"], "slot": p["slot"]}
            for p in data["pokemon"]
        ]

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"type": type_name, "pokemon": result}
