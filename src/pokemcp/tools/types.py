import asyncio
import logging
from pokemcp.app import mcp
from pokemcp.api import PokeAPIClient, CacheLayer
from pokemcp.config import settings

logger = logging.getLogger(__name__)

client = PokeAPIClient()
cache = CacheLayer(settings.redis_url)

ALL_TYPES = [
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel", "fairy",
]


@mcp.tool()
async def get_type(name_or_id: str) -> dict:
    """
    Get full details for a type by name or ID.
    Includes damage relations, Pokémon of that type, and moves of that type.
    """
    key = f"type:{name_or_id.lower()}"

    async def fetch():
        return await client.get(f"/type/{name_or_id.lower()}")

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"type": result}


@mcp.tool()
async def get_type_matchups(attacking_type: str) -> dict:
    """
    Get the offensive matchup chart for a type — which types it hits for
    super effective (2x), not very effective (0.5x), no effect (0x), or normal damage.
    """
    key = f"type_matchups:{attacking_type.lower()}"

    async def fetch():
        data = await client.get(f"/type/{attacking_type.lower()}")
        relations = data["damage_relations"]
        return {
            "super_effective": [t["name"] for t in relations["double_damage_to"]],
            "not_very_effective": [t["name"] for t in relations["half_damage_to"]],
            "no_effect": [t["name"] for t in relations["no_damage_to"]],
            "normal": [
                t for t in ALL_TYPES
                if t not in [x["name"] for x in relations["double_damage_to"]]
                and t not in [x["name"] for x in relations["half_damage_to"]]
                and t not in [x["name"] for x in relations["no_damage_to"]]
            ],
        }

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"attacking_type": attacking_type, "matchups": result}


@mcp.tool()
async def get_type_defenses(defending_type: str) -> dict:
    """
    Get the defensive matchup chart for a type — what it takes
    super effective, not very effective, or no damage from.
    """
    key = f"type_defenses:{defending_type.lower()}"

    async def fetch():
        data = await client.get(f"/type/{defending_type.lower()}")
        relations = data["damage_relations"]
        return {
            "weak_to": [t["name"] for t in relations["double_damage_from"]],
            "resists": [t["name"] for t in relations["half_damage_from"]],
            "immune_to": [t["name"] for t in relations["no_damage_from"]],
        }

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"defending_type": defending_type, "defenses": result}


@mcp.tool()
async def get_dual_type_matchups(type_one: str, type_two: str) -> dict:
    """
    Calculate the combined defensive matchup for a dual-type Pokémon.
    Multiplies the damage modifiers from both types together to give the
    final effective multiplier (e.g. 4x, 2x, 1x, 0.5x, 0.25x, 0x).
    """
    key = f"dual_type:{type_one.lower()}_{type_two.lower()}"

    async def fetch():
        data1, data2 = await asyncio.gather(
            client.get(f"/type/{type_one.lower()}"),
            client.get(f"/type/{type_two.lower()}"),
        )

        def build_multiplier_map(type_data: dict) -> dict[str, float]:
            relations = type_data["damage_relations"]
            multipliers = {t: 1.0 for t in ALL_TYPES}
            for t in relations["double_damage_from"]:
                multipliers[t["name"]] = 2.0
            for t in relations["half_damage_from"]:
                multipliers[t["name"]] = 0.5
            for t in relations["no_damage_from"]:
                multipliers[t["name"]] = 0.0
            return multipliers

        map1 = build_multiplier_map(data1)
        map2 = build_multiplier_map(data2)

        combined = {t: map1[t] * map2[t] for t in ALL_TYPES}

        grouped: dict[str, list] = {"4x": [], "2x": [], "1x": [], "0.5x": [], "0.25x": [], "0x": []}
        label_map = {4.0: "4x", 2.0: "2x", 1.0: "1x", 0.5: "0.5x", 0.25: "0.25x", 0.0: "0x"}

        for t, mult in combined.items():
            label = label_map.get(mult, "1x")
            grouped[label].append(t)

        return {k: v for k, v in grouped.items() if v}

    result = await cache.get_or_fetch(key, fetch, ttl=settings.cache_ttl)
    return {"types": [type_one, type_two], "matchups": result}


@mcp.tool()
async def list_types() -> dict:
    """
    List all available Pokémon types.
    """
    return {"types": ALL_TYPES}
