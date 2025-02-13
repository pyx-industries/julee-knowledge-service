import asyncio
import logging
from typing import List

import httpx

import domain
from repositories import WebClient

logger = logging.getLogger(__name__)


class HttpxWebClient(WebClient):
    """Implementation of WebClient using httpx library."""

    async def send_resource_callbacks(
        self,
        resource: domain.Resource,
    ) -> List[bool]:
        """Send callbacks for a resource to all its callback URLs.

        Args:
            resource: The Resource object containing callback URLs and data
            headers: Optional dictionary of HTTP headers to include
            timeout: Request timeout in seconds

        Returns:
            List[bool]: List of success/failure status for each callback URL
        """
        if not resource.callback_urls:
            return []

        # Set default headers if none provided
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        timeout = 30

        # Prepare the payload from resource data
        payload = {
            "resource_id": resource.id,
            "name": resource.name,
            "message": "resource processed, ready to query",
        }

        async def send_single_callback(
            client: httpx.AsyncClient, url: str
        ) -> bool:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                )
                response.raise_for_status()
                return True

            except httpx.TimeoutException:
                logger.error(f"Timeout sending webhook to {url}")
                return False

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error sending webhook to {url}: {e}")
                return False

            except Exception as e:
                logger.error(f"Error sending webhook to {url}: {e}")
                return False

        # Make concurrent requests to all callback URLs
        async with httpx.AsyncClient() as client:
            tasks = [
                send_single_callback(client, url)
                for url in resource.callback_urls
            ]
            results = await asyncio.gather(*tasks)

        return list(results)
