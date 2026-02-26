import logging
from pokemcp.app import mcp
from pokemcp.api import PokeAPIClient, CacheLayer
from pokemcp.config import settings

logger = logging.getLogger(__name__)

client = PokeAPIClient()
cache = CacheLayer(settings.redis_url)


@mcp.tool()
async def get_move(name_or_id: str) -> dict:
    """
    Get full details for a move by name or ID.
    Includes type, power, accuracy, PP, damage class, effect, and more.
    """
    key = f"move:{name_or_id.lower()}"

    async def fetch():
        return await client.get(f"/move/{name_or_id.lower()}")

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"move": result}


@mcp.tool()
async def get_move_summary(name_or_id: str) -> dict:
    """
    Get a concise summary of a move: name, type, power, accuracy, PP,
    damage class (physical/special/status), and short effect description.
    """
    key = f"move_summary:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/move/{name_or_id.lower()}")
        effect = (
            data.get("effect_entries", [{}])[0]
            .get("short_effect", "No description available.")
            .replace("$effect_chance", str(data.get("effect_chance") or ""))
        )
        return {
            "name": data["name"],
            "type": data["type"]["name"],
            "power": data.get("power"),
            "accuracy": data.get("accuracy"),
            "pp": data.get("pp"),
            "damage_class": data["damage_class"]["name"],
            "effect": effect,
            "priority": data.get("priority", 0),
        }

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result


@mcp.tool()
async def get_moves_learned_by_pokemon(name_or_id: str) -> dict:
    """
    Get all moves a Pokémon can learn, grouped by learn method
    (level-up, TM/HM, egg, tutor).
    """
    key = f"moves_learned:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/pokemon/{name_or_id.lower()}")
        grouped: dict[str, list] = {}

        for entry in data["moves"]:
            move_name = entry["move"]["name"]
            for version_detail in entry["version_group_details"]:
                method = version_detail["move_learn_method"]["name"]
                level = version_detail.get("level_learned_at", 0)
                if method not in grouped:
                    grouped[method] = []
                grouped[method].append({"move": move_name, "level": level})

        # Sort level-up moves by level
        if "level-up" in grouped:
            grouped["level-up"].sort(key=lambda x: x["level"])

        return grouped

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"name": name_or_id, "moves": result}


@mcp.tool()
async def list_moves(limit: int = 20, offset: int = 0) -> dict:
    """
    List all moves with pagination. Returns names and URLs.
    Max limit is 100 per request.
    """
    limit = min(limit, 100)
    key = f"moves_list:{limit}:{offset}"

    async def fetch():
        data = await client.get(f"/move?limit={limit}&offset={offset}")
        return [{"name": m["name"], "url": m["url"]} for m in data["results"]]

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"moves": result, "limit": limit, "offset": offset}


@mcp.tool()
async def get_moves_by_type(type_name: str) -> dict:
    """
    Get all moves that belong to a specific type (e.g. 'fire', 'psychic').
    Returns move names and their URLs for further lookup.
    """
    key = f"moves_by_type:{type_name.lower()}"

    async def fetch():
        data = await client.get(f"/type/{type_name.lower()}")
        return [{"name": m["name"], "url": m["url"]} for m in data.get("moves", [])]

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"type": type_name, "moves": result}
