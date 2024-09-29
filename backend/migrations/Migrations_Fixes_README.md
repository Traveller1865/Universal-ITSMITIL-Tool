# Manual Database Changes

Due to migration issues during development, the following columns were added manually to the `incident` table in the database:

- escalation_level (VARCHAR(50))
- escalated_at (TIMESTAMP)
- is_sla_breached (BOOLEAN)
- breached_at (TIMESTAMP)

Please ensure these changes are reflected in any future migration scripts.
