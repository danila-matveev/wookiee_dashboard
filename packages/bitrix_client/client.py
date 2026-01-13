import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class BitrixAPIError(Exception):
    pass


class BitrixClient:
    def __init__(
        self,
        webhook_url: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> None:
        self.webhook_url = webhook_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def _post(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.webhook_url}/{method}"
        attempt = 0
        while True:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=params)
                data = response.json()
                if "error" in data:
                    raise BitrixAPIError(f"{data.get('error')}: {data.get('error_description')}")
                return data
            except (httpx.HTTPError, BitrixAPIError) as err:
                attempt += 1
                if attempt > self.max_retries:
                    logger.error("Bitrix request failed permanently: %s", err)
                    raise
                sleep_for = self.backoff_factor**attempt
                logger.warning("Bitrix request failed (attempt %s), retry in %.2fs", attempt, sleep_for)
                await asyncio.sleep(sleep_for)

    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        params = {"filter": {"EMAIL": email}, "select": ["ID", "EMAIL", "NAME", "LAST_NAME"]}  # user.get supports filter
        result = await self._post("user.get", params)
        users = result.get("result", [])
        return users[0] if users else None

    async def send_im_notify(self, to_user_id: int, message: str) -> None:
        params = {"to": to_user_id, "message": message}
        await self._post("im.notify", params)

    async def list_tasks(
        self,
        responsible_id: int,
        deadline_from: Optional[datetime] = None,
        deadline_to: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        filters: Dict[str, Any] = {"RESPONSIBLE_ID": responsible_id}
        if deadline_from:
            filters[">=DEADLINE"] = deadline_from.isoformat()
        if deadline_to:
            filters["<=DEADLINE"] = deadline_to.isoformat()
        params = {
            "filter": filters,
            "select": [
                "ID",
                "TITLE",
                "STATUS",
                "DEADLINE",
                "RESPONSIBLE_ID",
                "CREATED_DATE",
                "CHANGED_DATE",
            ],
        }
        result = await self._post("tasks.task.list", params)
        tasks = result.get("result", {}).get("tasks", [])
        return tasks

    async def list_events(
        self,
        user_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> List[Dict[str, Any]]:
        params = {
            "type": "user",
            "ownerId": user_id,
            "from": date_from.isoformat(),
            "to": date_to.isoformat(),
            "skipDeclined": "Y",
        }
        result = await self._post("calendar.event.get", params)
        return result.get("result", [])
