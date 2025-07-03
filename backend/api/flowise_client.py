import os
import aiohttp
import asyncio
from django.conf import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FlowiseClient:
    """
    Client for interacting with Flowise API for LLM orchestration.
    """
    def __init__(self):
        self.base_url = os.getenv('FLOWISE_URL', 'http://flowise:3000')
        self.flow_id = os.getenv('FLOWISE_FLOW_ID')
        self.timeout = int(os.getenv('FLOWISE_TIMEOUT', 60))
        self.max_retries = int(os.getenv('FLOWISE_MAX_RETRIES', 10))

    async def send_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to Flowise and get the response.
        
        Args:
            message: The message to send
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Dict containing the response from Flowise
        """
        url = f"{self.base_url}/api/v1/prediction/{self.flow_id}"
        
        payload = {
            "question": message,
            "sessionId": session_id
        }

        logger.info(f"FlowiseClient: Sending payload to Flowise: {payload}")

        # Tries up to max_retries times in case of errors.
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        json=payload,
                        timeout=self.timeout
                    ) as response:
                        if response.status == 200:
                            # If the response is successful, return the JSON response.
                            logger.info(f"Flowise API response: {await response.json()}")
                            return await response.json()
                        
                        else:
                            error_text = await response.text()
                            raise Exception(f"Flowise API error: {error_text}")
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    raise Exception("Flowise API timeout after all retries")
                await asyncio.sleep(1)  # Wait before retrying
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Flowise API error: {str(e)}")
                await asyncio.sleep(1)  # Wait before retrying

    async def check_health(self) -> bool:
        """
        Check if Flowise is healthy and accessible.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/health",
                    timeout=5
                ) as response:
                    return response.status == 200
        except:
            return False 