import logging

import requests
from requests import RequestException

logger = logging.getLogger(__name__)


def http_post(url, data=None, json=None, params=None, headers=None, timeout=10):
    """Send a POST request and return the parsed JSON response."""
    try:
        response = requests.post(
            url, data=data, json=json, params=params, headers=headers, timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except RequestException:
        logger.exception("HTTP POST error for %s", url)
        raise
    except ValueError as exc:
        logger.error("Invalid JSON from %s: %s", url, response.text[:200])
        raise ValueError(f"Invalid JSON response from {url}") from exc