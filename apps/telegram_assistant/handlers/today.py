from datetime import timedelta

from aiogram import Router
from aiogram.types import Message
from dateutil import parser

from apps.telegram_assistant.utils.dates import day_bounds, now_utc


async def build_summary(supabase, bitrix, user, default_timezone: str) -> str:
    tz = user.get("timezone") or default_timezone
    now = now_utc()
    start_day, end_day = day_bounds(now, tz)

    tasks_today = await bitrix.list_tasks(
        responsible_id=int(user["bitrix_user_id"]),
        deadline_from=start_day,
        deadline_to=end_day,
    )
    tasks_overdue = await bitrix.list_tasks(
        responsible_id=int(user["bitrix_user_id"]),
        deadline_to=start_day,
    )

    # события на сегодня
    events_today = await bitrix.list_events(
        user_id=int(user["bitrix_user_id"]),
        date_from=start_day,
        date_to=end_day + timedelta(seconds=1),
    )

    cached_rows = []
    for item in tasks_today + tasks_overdue:
        deadline_str = item.get("DEADLINE")
        deadline_dt = parser.isoparse(deadline_str) if deadline_str else None
        updated_str = item.get("CHANGED_DATE") or item.get("CREATED_DATE")
        updated_dt = parser.isoparse(updated_str) if updated_str else None
        cached_rows.append(
            {
                "bitrix_task_id": int(item["ID"]),
                "bitrix_user_id": int(user["bitrix_user_id"]),
                "title": item["TITLE"],
                "status": item["STATUS"],
                "deadline": deadline_dt.isoformat() if deadline_dt else None,
                "updated_at": updated_dt.isoformat() if updated_dt else None,
                "raw_payload": item,
            }
        )
    supabase.upsert_tasks_cache(cached_rows)

    event_rows = []
    for ev in events_today:
        start = ev.get("DATE_FROM")
        end = ev.get("DATE_TO")
        start_dt = parser.isoparse(start) if start else None
        end_dt = parser.isoparse(end) if end else None
        event_rows.append(
            {
                "bitrix_event_id": int(ev["ID"]),
                "bitrix_user_id": int(user["bitrix_user_id"]),
                "title": ev.get("NAME") or ev.get("TITLE") or "Событие",
                "start_at": start_dt.isoformat() if start_dt else None,
                "end_at": end_dt.isoformat() if end_dt else None,
                "updated_at": ev.get("DATE_CREATE"),
                "raw_payload": ev,
            }
        )
    supabase.upsert_events_cache(event_rows)

    def fmt_tasks(items):
        rows = []
        for item in items:
            deadline = item.get("DEADLINE")
            rows.append(f"- {item.get('TITLE')} (до {deadline or '—'})")
        return "\n".join(rows) if rows else "—"

    def fmt_events(items):
        rows = []
        for ev in items:
            rows.append(f"- {ev.get('NAME') or ev.get('TITLE') or 'Событие'} ({ev.get('DATE_FROM')} - {ev.get('DATE_TO')})")
        return "\n".join(rows) if rows else "—"

    text = (
        f"Задачи на сегодня (tz {tz}):\n{fmt_tasks(tasks_today)}\n\n"
        f"Просроченные:\n{fmt_tasks(tasks_overdue)}\n\n"
        f"События сегодня:\n{fmt_events(events_today)}"
    )
    return text


def register_today(router: Router, default_timezone: str) -> None:
    @router.message(commands={"today"})
    async def cmd_today(message: Message) -> None:
        bot = message.bot
        supabase = bot["supabase"]
        bitrix = bot["bitrix"]

        user = supabase.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала выполните /start <email> для привязки.")
            return

        text = await build_summary(supabase, bitrix, user, default_timezone)
        await message.answer(text)
