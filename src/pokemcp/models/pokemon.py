from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Shared / primitive models
# ---------------------------------------------------------------------------

class NamedResource(BaseModel):
    """A named API resource reference (name + url pair)."""
    name: str
    url: str


class VersionGameIndex(BaseModel):
    game_index: int
    version: NamedResource


class VersionGroupDetail(BaseModel):
    level_learned_at: int
    move_learn_method: NamedResource
    version_group: NamedResource


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

class StatDetail(BaseModel):
    base_stat: int
    effort: int
    stat: NamedResource


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class TypeSlot(BaseModel):
    slot: int
    type: NamedResource


# ---------------------------------------------------------------------------
# Abilities
# ---------------------------------------------------------------------------

class AbilitySlot(BaseModel):
    ability: NamedResource
    is_hidden: bool
    slot: int


# ---------------------------------------------------------------------------
# Moves
# ---------------------------------------------------------------------------

class MoveEntry(BaseModel):
    move: NamedResource
    version_group_details: list[VersionGroupDetail]


# ---------------------------------------------------------------------------
# Sprites
# ---------------------------------------------------------------------------

class Sprites(BaseModel):
    front_default: str | None = None
    front_shiny: str | None = None
    front_female: str | None = None
    front_shiny_female: str | None = None
    back_default: str | None = None
    back_shiny: str | None = None
    back_female: str | None = None
    back_shiny_female: str | None = None

    # Other versions and official artwork are nested under `other`
    other: dict[str, Any] | None = None

    @property
    def official_artwork(self) -> str | None:
        """Convenience accessor for the official artwork URL."""
        try:
            return self.other["official-artwork"]["front_default"]
        except (TypeError, KeyError):
            return None

    @property
    def shiny_official_artwork(self) -> str | None:
        try:
            return self.other["official-artwork"]["front_shiny"]
        except (TypeError, KeyError):
            return None


# ---------------------------------------------------------------------------
# Held items
# ---------------------------------------------------------------------------

class HeldItemVersionDetail(BaseModel):
    rarity: int
    version: NamedResource


class HeldItem(BaseModel):
    item: NamedResource
    version_details: list[HeldItemVersionDetail]


# ---------------------------------------------------------------------------
# Cries
# ---------------------------------------------------------------------------

class Cries(BaseModel):
    latest: str | None = None
    legacy: str | None = None


# ---------------------------------------------------------------------------
# Core Pokémon model
# ---------------------------------------------------------------------------

class Pokemon(BaseModel):
    """
    Full Pokémon model matching the /pokemon/{id} PokeAPI response.
    Unknown or extra fields are ignored rather than raising validation errors.
    """

    model_config = {"extra": "ignore"}

    id: int
    name: str
    base_experience: int | None = None
    height: int  # in decimetres
    weight: int  # in hectograms
    is_default: bool
    order: int

    abilities: list[AbilitySlot]
    forms: list[NamedResource]
    game_indices: list[VersionGameIndex] = Field(default_factory=list)
    held_items: list[HeldItem] = Field(default_factory=list)
    moves: list[MoveEntry] = Field(default_factory=list)
    species: NamedResource
    sprites: Sprites
    stats: list[StatDetail]
    types: list[TypeSlot]
    cries: Cries | None = None

    @field_validator("name")
    @classmethod
    def normalise_name(cls, v: str) -> str:
        return v.lower().strip()

    @property
    def height_m(self) -> float:
        """Height in metres."""
        return self.height / 10

    @property
    def weight_kg(self) -> float:
        """Weight in kilograms."""
        return self.weight / 10

    @property
    def primary_type(self) -> str:
        slot1 = next((t for t in self.types if t.slot == 1), None)
        return slot1.type.name if slot1 else "unknown"

    @property
    def secondary_type(self) -> str | None:
        slot2 = next((t for t in self.types if t.slot == 2), None)
        return slot2.type.name if slot2 else None

    @property
    def stat_map(self) -> dict[str, int]:
        """Returns stats as a plain dict: {'hp': 45, 'attack': 49, ...}"""
        return {s.stat.name: s.base_stat for s in self.stats}

    @property
    def base_stat_total(self) -> int:
        return sum(s.base_stat for s in self.stats)


# ---------------------------------------------------------------------------
# Lightweight summary (used in list responses)
# ---------------------------------------------------------------------------

class PokemonSummary(BaseModel):
    """Minimal model used when listing Pokémon (name + URL only)."""
    name: str
    url: str

    @property
    def id(self) -> int:
        """Extract Pokédex ID from the resource URL."""
        return int(self.url.rstrip("/").split("/")[-1])


# ---------------------------------------------------------------------------
# Evolution chain
# ---------------------------------------------------------------------------

class EvolutionDetail(BaseModel):
    """Conditions required for an evolution to occur."""
    model_config = {"extra": "ignore"}

    gender: int | None = None
    held_item: NamedResource | None = None
    item: NamedResource | None = None
    known_move: NamedResource | None = None
    known_move_type: NamedResource | None = None
    location: NamedResource | None = None
    min_affection: int | None = None
    min_beauty: int | None = None
    min_happiness: int | None = None
    min_level: int | None = None
    needs_overworld_rain: bool = False
    party_species: NamedResource | None = None
    party_type: NamedResource | None = None
    relative_physical_stats: int | None = None
    time_of_day: str = ""
    trade_species: NamedResource | None = None
    trigger: NamedResource | None = None
    turn_upside_down: bool = False


class ChainLink(BaseModel):
    """A single node in an evolution chain tree."""
    model_config = {"extra": "ignore"}

    is_baby: bool
    species: NamedResource
    evolution_details: list[EvolutionDetail] = Field(default_factory=list)
    evolves_to: list[ChainLink] = Field(default_factory=list)


# Required for self-referential model
ChainLink.model_rebuild()


class EvolutionChain(BaseModel):
    model_config = {"extra": "ignore"}

    id: int
    baby_trigger_item: NamedResource | None = None
    chain: ChainLink

    def flat_chain(self) -> list[str]:
        """
        Returns a flat list of species names in evolution order.
        For branching evolutions (e.g. Eevee), all branches are included.
        """
        names: list[str] = []

        def walk(link: ChainLink) -> None:
            names.append(link.species.name)
            for next_link in link.evolves_to:
                walk(next_link)

        walk(self.chain)
        return names