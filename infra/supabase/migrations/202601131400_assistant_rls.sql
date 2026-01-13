-- Enable RLS
alter table assistant.users enable row level security;
alter table assistant.auth_codes enable row level security;
alter table assistant.tasks_cache enable row level security;
alter table assistant.events_cache enable row level security;
alter table assistant.sync_state enable row level security;
alter table assistant.notification_outbox enable row level security;

-- Service role full access
do $$
begin
  if not exists (select 1 from pg_policies where polname = 'assistant_users_service_role') then
    create policy assistant_users_service_role on assistant.users for all
      to public using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
  end if;
  if not exists (select 1 from pg_policies where polname = 'assistant_auth_codes_service_role') then
    create policy assistant_auth_codes_service_role on assistant.auth_codes for all
      to public using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
  end if;
  if not exists (select 1 from pg_policies where polname = 'assistant_tasks_cache_service_role') then
    create policy assistant_tasks_cache_service_role on assistant.tasks_cache for all
      to public using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
  end if;
  if not exists (select 1 from pg_policies where polname = 'assistant_events_cache_service_role') then
    create policy assistant_events_cache_service_role on assistant.events_cache for all
      to public using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
  end if;
  if not exists (select 1 from pg_policies where polname = 'assistant_sync_state_service_role') then
    create policy assistant_sync_state_service_role on assistant.sync_state for all
      to public using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
  end if;
  if not exists (select 1 from pg_policies where polname = 'assistant_notification_outbox_service_role') then
    create policy assistant_notification_outbox_service_role on assistant.notification_outbox for all
      to public using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
  end if;
end $$;
