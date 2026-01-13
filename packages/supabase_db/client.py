import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self, url: str, key: str, schema: str = "assistant") -> None:
        self.client: Client = create_client(url, key)
        self.schema = schema

    def _table(self, name: str):
        return self.client.table(name).schema(self.schema)

    def upsert_user(self, user: Dict[str, Any]) -> None:
        logger.info("Upsert user %s", user.get("telegram_id"))
        self._table("users").upsert(user).execute()

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        resp = self._table("users").select("*").eq("telegram_id", telegram_id).limit(1).execute()
        if resp.data:
            return resp.data[0]
        return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        resp = self._table("users").select("*").execute()
        return resp.data or []

    def insert_auth_code(self, record: Dict[str, Any]) -> None:
        self._table("auth_codes").insert(record).execute()

    def get_auth_code(self, telegram_id: int, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query = self._table("auth_codes").select("*").eq("telegram_id", telegram_id)
        if email:
            query = query.eq("email", email)
        resp = query.order("created_at", desc=True).limit(1).execute()
        if resp.data:
            return resp.data[0]
        return None

    def upsert_tasks_cache(self, tasks: List[Dict[str, Any]]) -> None:
        if not tasks:
            return
        logger.info("Upsert %s tasks into cache", len(tasks))
        self._table("tasks_cache").upsert(tasks, on_conflict="bitrix_task_id").execute()

    def upsert_events_cache(self, events: List[Dict[str, Any]]) -> None:
        if not events:
            return
        logger.info("Upsert %s events into cache", len(events))
        self._table("events_cache").upsert(events, on_conflict="bitrix_event_id").execute()

    def upsert_sync_state(self, bitrix_user_id: int, entity_type: str, last_synced_at: datetime) -> None:
        self._table("sync_state").upsert(
            {
                "bitrix_user_id": bitrix_user_id,
                "entity_type": entity_type,
                "last_synced_at": last_synced_at.isoformat(),
            },
            on_conflict="bitrix_user_id,entity_type",
        ).execute()

    def get_sync_state(self, bitrix_user_id: int, entity_type: str) -> Optional[Dict[str, Any]]:
        resp = (
            self._table("sync_state")
            .select("*")
            .eq("bitrix_user_id", bitrix_user_id)
            .eq("entity_type", entity_type)
            .limit(1)
            .execute()
        )
        if resp.data:
            return resp.data[0]
        return None
