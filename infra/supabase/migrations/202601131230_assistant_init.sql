-- Schema for wookiee-ai-assistant
create schema if not exists assistant;

create table if not exists assistant.users (
  id uuid primary key default gen_random_uuid(),
  telegram_id bigint not null unique,
  telegram_chat_id bigint not null,
  bitrix_user_id bigint not null,
  email text not null unique,
  timezone text not null default 'Europe/Moscow',
  notifications_enabled boolean not null default true,
  morning_time time not null default '08:00',
  evening_time time not null default '18:00',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists assistant.auth_codes (
  id bigserial primary key,
  telegram_id bigint not null,
  email text not null,
  code_hash text not null,
  expires_at timestamptz not null,
  attempts smallint not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists assistant.tasks_cache (
  id bigserial primary key,
  bitrix_task_id bigint not null unique,
  bitrix_user_id bigint not null,
  title text not null,
  status text not null,
  deadline timestamptz,
  updated_at timestamptz,
  raw_payload jsonb
);

create table if not exists assistant.events_cache (
  id bigserial primary key,
  bitrix_event_id bigint not null unique,
  bitrix_user_id bigint not null,
  title text not null,
  start_at timestamptz not null,
  end_at timestamptz not null,
  updated_at timestamptz,
  raw_payload jsonb
);

create table if not exists assistant.sync_state (
  id bigserial primary key,
  bitrix_user_id bigint not null,
  entity_type text not null check (entity_type in ('task','event','user')),
  last_synced_at timestamptz,
  unique (bitrix_user_id, entity_type)
);

create table if not exists assistant.notification_outbox (
  id bigserial primary key,
  dedupe_key text not null unique,
  telegram_chat_id bigint not null,
  payload jsonb not null,
  sent_at timestamptz not null default now()
);

create index if not exists idx_tasks_deadline on assistant.tasks_cache (deadline);
create index if not exists idx_events_start on assistant.events_cache (start_at);
create index if not exists idx_sync_state_user on assistant.sync_state (bitrix_user_id);
