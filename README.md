# pokemcp

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes the [PokéAPI](https://pokeapi.co) as tools and resources, letting any MCP-compatible AI assistant look up Pokémon data in real time.

## Features

- **22 tools** across Pokémon, moves, items, and types
- **8 MCP resources** for direct URI-based data access
- Optional **Redis caching** with a local in-memory fallback
- Automatic **retry with exponential back-off** on API errors
- Zero configuration required — works out of the box against the public PokéAPI

---

## Requirements

- Python ≥ 3.11
- [uv](https://github.com/astral-sh/uv) package manager

---

## Installation

```bash
git clone https://github.com/Ragde54/pokemcp.git
cd pokemcp
uv sync
```

---

## Running the server

```bash
PYTHONPATH=src uv run pokemcp
```

> **Note:** The `PYTHONPATH=src` prefix is required due to a known incompatibility between Homebrew Python's venv and editable-install `.pth` file processing.

---

## Claude Desktop integration

Add the following to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pokemcp": {
      "command": "uv",
      "args": ["run", "pokemcp"],
      "cwd": "/path/to/pokemcp",
      "env": {
        "PYTHONPATH": "/path/to/pokemcp/src"
      }
    }
  }
}
```

Replace `/path/to/pokemcp` with the absolute path to this repository, then restart Claude Desktop.

---

## Configuration

Settings are read from environment variables or a `.env` file in the project root.

| Variable | Default | Description |
|---|---|---|
| `POKEAPI_BASE_URL` | `https://pokeapi.co/api/v2` | PokéAPI base URL |
| `REDIS_URL` | _(none)_ | Redis URL for persistent caching (e.g. `redis://localhost:6379`). If unset, an in-memory cache is used. |
| `CACHE_TTL` | `3600` | Cache time-to-live in seconds |
| `LOG_LEVEL` | `INFO` | Python logging level |

---

## Tools

### 🐾 Pokémon

| Tool | Description |
|---|---|
| `get_pokemon(name_or_id)` | Full Pokémon details: types, stats, abilities, sprites, forms, held items, and more |
| `get_pokemon_species(name_or_id)` | Species data: Pokédex flavor text, habitat, generation, legendary/mythical status, gender rate |
| `get_pokemon_stats(name_or_id)` | Base stats (HP, Attack, Defense, Sp. Atk, Sp. Def, Speed) plus total BST |
| `get_pokemon_abilities(name_or_id)` | All abilities and whether each is a hidden ability |
| `get_evolution_chain(name_or_id)` | Full evolution chain with trigger conditions |
| `list_pokemon(limit, offset)` | Paginated list of all Pokémon (max 100 per page) |
| `search_pokemon_by_type(type_name)` | All Pokémon belonging to a given type |

### ⚔️ Moves

| Tool | Description |
|---|---|
| `get_move(name_or_id)` | Full move details: type, power, accuracy, PP, damage class, effect, and more |
| `get_move_summary(name_or_id)` | Concise move summary with effect description |
| `get_moves_learned_by_pokemon(name_or_id)` | All moves a Pokémon can learn, grouped by learn method (level-up, TM/HM, egg, tutor) |
| `list_moves(limit, offset)` | Paginated list of all moves (max 100 per page) |
| `get_moves_by_type(type_name)` | All moves that belong to a specific type |

### 🎒 Items

| Tool | Description |
|---|---|
| `get_item(name_or_id)` | Full item details: category, cost, effect, attributes, and held-by Pokémon |
| `get_item_summary(name_or_id)` | Concise item summary with short effect and Pokédex flavor text |
| `list_items(limit, offset)` | Paginated list of all items (max 100 per page) |
| `get_items_by_category(category)` | All items in a category (e.g. `pokeballs`, `healing`, `held-items`, `berries`, `evolution`) |
| `get_item_held_by_pokemon(item_name)` | All Pokémon that hold an item in the wild, with per-version rarity |

### 🔥 Types

| Tool | Description |
|---|---|
| `get_type(name_or_id)` | Full type details including damage relations, resident Pokémon, and moves |
| `get_type_matchups(attacking_type)` | Offensive chart: super effective / not very effective / no effect / normal |
| `get_type_defenses(defending_type)` | Defensive chart: weak to / resists / immune to |
| `get_dual_type_matchups(type_one, type_two)` | Combined defensive multipliers for a dual-type Pokémon (4×, 2×, 1×, 0.5×, 0.25×, 0×) |
| `list_types()` | List all 18 Pokémon types |

---

## Resources

Resources are accessible via URI and return raw JSON.

| URI pattern | Description |
|---|---|
| `pokedex://pokemon/{name_or_id}` | Full Pokémon data |
| `pokedex://species/{name_or_id}` | Species data including Pokédex entries |
| `pokedex://move/{name_or_id}` | Full move data |
| `pokedex://item/{name_or_id}` | Full item data |
| `pokedex://type/{name_or_id}` | Full type data with damage relations |
| `pokedex://ability/{name_or_id}` | Ability data with effect descriptions |
| `pokedex://generation/{name_or_id}` | Generation data with Pokémon species and version groups |
| `pokedex://pokedex/{name_or_id}` | Regional Pokédex entries (e.g. `national`, `kanto`) |

---

## Project structure

```
src/pokemcp/
├── app.py          # Shared FastMCP instance
├── server.py       # Entry point — imports all tools/resources
├── config.py       # Settings via pydantic-settings
├── api/
│   ├── client.py   # Async HTTP client with retry logic
│   └── cache.py    # Redis / in-memory cache layer
├── models/
│   └── pokemon.py  # Pydantic models (Pokemon, PokemonSummary, EvolutionChain)
├── tools/
│   ├── pokemon.py  # Pokémon tools
│   ├── moves.py    # Move tools
│   ├── items.py    # Item tools
│   └── types.py    # Type tools
└── resources/
    └── pokedex.py  # MCP resources
```

---

## Data source

All data is fetched from the [PokéAPI](https://pokeapi.co) — a free, open REST API for Pokémon data. No API key required.
