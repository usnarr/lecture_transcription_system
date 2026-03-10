import aiohttp

async def http_get(url, params=None, headers=None, timeout=30):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
            response.raise_for_status()
            return await response.json()

async def http_post(url, data=None, json=None, headers=None, timeout=30):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, json=json, headers=headers, timeout=timeout) as response:
            response.raise_for_status()
            return await response.json()