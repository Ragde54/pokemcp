from pokemcp.app import mcp

# Import all tool/resource modules so their @mcp.tool() / @mcp.resource()
# decorators run and register against the shared mcp instance.
import pokemcp.tools.pokemon      # noqa: F401
import pokemcp.tools.moves        # noqa: F401
import pokemcp.tools.items        # noqa: F401
import pokemcp.tools.types        # noqa: F401
import pokemcp.resources.pokedex  # noqa: F401


def main():
    mcp.run()


if __name__ == "__main__":
    main()