import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class PokeAPIClient:
    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=10.0
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    async def get(self, endpoint: str) -> dict:
        response = await self.client.get(endpoint)
        response.raise_for_status()
        return response.json()