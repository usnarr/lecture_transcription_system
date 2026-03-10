import aiohttp
from aiohttp import ClientError, ClientTimeout
from src.logger import logger

async def http_get(url, params=None, headers=None, timeout=5):
    timeout_config = ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            async with session.get(url, params=params, headers=headers) as response:
               
                response.raise_for_status()
                
                try:
                    return await response.json()
                except Exception as json_error:
                    logger.error("Failed to parse JSON from %s: %s", url, json_error)

                    text_content = await response.text()
                    logger.error("Response content: %s", text_content[:200])
                    raise ValueError(f"Invalid JSON response from {url}: {json_error}")
                    
    except ClientError as e:
        logger.error("HTTP client error for %s: %s", url, e)
        raise
    except Exception as e:
        logger.error("Unexpected error for %s: %s", url, e)
        raise