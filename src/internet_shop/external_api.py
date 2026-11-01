import asyncio
import httpx


async def fetch_product(
    client: httpx.AsyncClient,
    product_id: int,
    semaphore: asyncio.Semaphore,
    base_url: str,
    attempts: int = 3,
) -> dict:
    """Fetch one product with concurrency limiting and retry."""
    async with semaphore:
        for attempt in range(1, attempts + 1):
            try:
                response = await client.get(f"{base_url}/products/{product_id}")
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError):
                if attempt == attempts:
                    raise
                await asyncio.sleep(attempt)
    raise RuntimeError("Retry loop ended unexpectedly")


async def fetch_many_products(base_url: str, product_ids: list[int]) -> list[dict]:
    """Fetch multiple products concurrently using Task, gather and timeout."""
    semaphore = asyncio.Semaphore(5)
    timeout = httpx.Timeout(5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [
            asyncio.create_task(fetch_product(client, product_id, semaphore, base_url))
            for product_id in product_ids
        ]
        return list(await asyncio.wait_for(asyncio.gather(*tasks), timeout=10.0))
