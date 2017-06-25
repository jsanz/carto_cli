
CURRENT_RUNNING = 'select * from pg_stat_activity where usename=current_user'

KILL_QUERY = '''
select pg_cancel_backend({})
  from pg_stat_activity
 where usename=current_user
'''

LIST_SCHEMAS = '''
select nspname as user
  from pg_catalog.pg_namespace
 where not nspowner = 10
 order by nspname
'''

LIST_TABLES = '''
select pg_class.relname as name,
       stats.relid,
       stats.seq_scan as stats_seq_scan,
       stats.n_live_tup as stats_live_tup,
       stats.last_analyze as stats_last_analyze,
       stats.last_vacuum as stats_last_vacuum
  from pg_class, pg_roles, pg_namespace, pg_stat_user_tables stats
 where pg_roles.oid = pg_class.relowner and
       pg_roles.rolname = current_user and
       pg_namespace.oid = pg_class.relnamespace and
       pg_class.relkind = 'r' and
       pg_class.relname = stats.relname and
       stats.schemaname like '{schema_name}' and
       pg_class.relname like '{table_name}'
 order by name
 '''

LIST_TABLES_HEADER = ['name','relid','stats_seq_scan','stats_live_tup',
                        'stats_last_analyze','stats_last_vacuum']

SCHEMA = '''
select a.attname as attribute,
       format_type(a.atttypid, a.atttypmod) as type
  from pg_attribute a
  join pg_class c on a.attrelid = c.oid
  join pg_roles on pg_roles.oid = c.relowner and pg_roles.rolname = current_user
 where c.relname = '{table_name}' and
       attisdropped = false and
       attnum > 0
 order by attnum
'''

TRIGGERS = '''
select tgname
  from pg_trigger a
  join pg_class c on a.tgrelid = c.oid
  join pg_roles on pg_roles.oid = c.relowner and pg_roles.rolname = current_user
 where c.relname = '{table_name}'
'''

INDEXES = '''
select i.relname as index_name,
       a.attname as column_name,
       am.amname as index_type
  from pg_class t
  join pg_attribute a on t.oid = a.attrelid
  join pg_index ix on ix.indrelid = t.oid
  join pg_class i
    on ix.indexrelid = i.oid and
       a.attnum = any(ix.indkey)
  join pg_am am on i.relam = am.oid
  join pg_roles on pg_roles.oid = t.relowner and pg_roles.rolname = current_user
 where t.relname = '{table_name}'
order by t.relname, i.relname;
'''


FUNCTIONS = '''
select pg_proc.oid as oid,
       pg_proc.proname as name, pg_proc.proargnames as arguments,
       pg_get_functiondef(pg_proc.oid) as definition
  from pg_proc, pg_roles
 where pg_proc.proowner = pg_roles.oid and
       pg_roles.rolname = current_user
'''
FUNCTIONS_HEADER = ['oid','name','arguments']