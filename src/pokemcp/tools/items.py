import logging
from pokemcp.app import mcp
from pokemcp.api import PokeAPIClient, CacheLayer
from pokemcp.config import settings

logger = logging.getLogger(__name__)

client = PokeAPIClient()
cache = CacheLayer(settings.redis_url)


@mcp.tool()
async def get_item(name_or_id: str) -> dict:
    """
    Get full details for an item by name or ID.
    Includes category, cost, effect, attributes, and Pokémon it's held by.
    """
    key = f"item:{name_or_id.lower()}"

    async def fetch():
        return await client.get(f"/item/{name_or_id.lower()}")

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"item": result}


@mcp.tool()
async def get_item_summary(name_or_id: str) -> dict:
    """
    Get a concise summary of an item: name, category, cost, and
    its short effect description.
    """
    key = f"item_summary:{name_or_id.lower()}"

    async def fetch():
        data = await client.get(f"/item/{name_or_id.lower()}")
        effect = (
            data.get("effect_entries", [{}])[0]
            .get("short_effect", "No description available.")
        )
        flavor_text = next(
            (
                ft["text"]
                for ft in data.get("flavor_text_entries", [])
                if ft["language"]["name"] == "en"
            ),
            None,
        )
        return {
            "name": data["name"],
            "category": data["category"]["name"],
            "cost": data.get("cost"),
            "effect": effect,
            "flavor_text": flavor_text,
            "attributes": [a["name"] for a in data.get("attributes", [])],
        }

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result


@mcp.tool()
async def list_items(limit: int = 20, offset: int = 0) -> dict:
    """
    List all items with pagination. Returns names and URLs.
    Max limit is 100 per request.
    """
    limit = min(limit, 100)
    key = f"items_list:{limit}:{offset}"

    async def fetch():
        data = await client.get(f"/item?limit={limit}&offset={offset}")
        return [{"name": i["name"], "url": i["url"]} for i in data["results"]]

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"items": result, "limit": limit, "offset": offset}


@mcp.tool()
async def get_items_by_category(category: str) -> dict:
    """
    Get all items in a specific category (e.g. 'pokeballs', 'healing',
    'held-items', 'berries', 'evolution').
    """
    key = f"items_by_category:{category.lower()}"

    async def fetch():
        data = await client.get(f"/item-category/{category.lower()}")
        return {
            "name": data["name"],
            "items": [{"name": i["name"], "url": i["url"]} for i in data.get("items", [])],
        }

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return result


@mcp.tool()
async def get_item_held_by_pokemon(item_name: str) -> dict:
    """
    Get all Pokémon that can hold a specific item in the wild,
    along with the rarity of them holding it per game version.
    """
    key = f"item_held_by:{item_name.lower()}"

    async def fetch():
        data = await client.get(f"/item/{item_name.lower()}")
        return [
            {
                "pokemon": holder["pokemon"]["name"],
                "rarity_by_version": [
                    {
                        "version": v["version"]["name"],
                        "rarity": v["rarity"],
                    }
                    for v in holder["version_details"]
                ],
            }
            for holder in data.get("held_by_pokemon", [])
        ]

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"item": item_name, "held_by": result}
