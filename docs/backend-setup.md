# Backend setup

The backend exposes only the foundation endpoints in this increment.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/health` | Returns API readiness status. |
| `GET /api/v1/district` | Returns the complete fictional Sundarpur District profile. |
| `GET /api/v1/simulate?scenario=moderate` | Returns deterministic flood impacts. Scenarios: `moderate`, `severe`, `extreme`. |

The district profile contains 10 flood zones, 30 road links, 2 hospitals, 3 shelters, and 5 rescue teams. It is static operational context, not live emergency data.
