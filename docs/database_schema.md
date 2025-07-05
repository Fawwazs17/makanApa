# Database Schema – makanApa

The bot persists data in a single SQLite file (`data/makanApa.db`). The schema is initialised automatically by [`database.py`](../database.py) when the application starts for the first time.

---

## Entity‐Relationship Diagram

```mermaid
erDiagram
    Customers ||--o{ Orders : places
    Runners ||--o{ Orders : delivers

    Customers {
        BIGINT user_id PK "Telegram user ID"
        VARCHAR username  "Telegram @username"
        BOOLEAN is_blocked
        TIMESTAMP created_at
    }

    Runners {
        BIGINT user_id PK
        VARCHAR username
        TIMESTAMP created_at
    }

    Orders {
        VARCHAR id PK "ORDER_YYMMDD_HHMMSS_<counter>"
        BIGINT customer_id FK
        BIGINT runner_id FK nullable
        VARCHAR delivery_type "food | item"
        TEXT from_location
        TEXT to_location
        TIMESTAMP order_time
        VARCHAR status "pending | accepted | cancelled"
        TIMESTAMP accept_time nullable
        TIMESTAMP cancelled_at nullable
        BIGINT customer_message_id nullable
        BIGINT runner_message_id nullable
    }
```

---

## Table Definitions

### Customers
| Column | Type | Description |
|--------|------|-------------|
| `user_id` | BIGINT, PK | Unique Telegram user ID |
| `username` | VARCHAR(255) | Telegram handle (may be **NULL** if the user hides it) |
| `is_blocked` | BOOLEAN | Whether the user is banned from ordering |
| `created_at` | TIMESTAMP | Defaults to current time |

### Runners
| Column | Type | Description |
|--------|------|-------------|
| `user_id` | BIGINT, PK | Unique Telegram user ID |
| `username` | VARCHAR(255) | Runner handle |
| `created_at` | TIMESTAMP | Defaults to current time |

### Orders
| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(255), PK | Generated order reference |
| `customer_id` | BIGINT, FK → Customers(user_id) | Person who placed the order |
| `runner_id` | BIGINT, FK → Runners(user_id) | Person who accepted the order |
| `delivery_type` | VARCHAR(50) | `food` or `item` |
| `from_location` | TEXT | Pickup spot |
| `to_location` | TEXT | Destination |
| `order_time` | TIMESTAMP | When the order was created |
| `status` | VARCHAR(50) | `pending`, `accepted`, `cancelled` |
| `accept_time` | TIMESTAMP | When a runner accepted |
| `cancelled_at` | TIMESTAMP | When the customer cancelled |
| `customer_message_id` | BIGINT | ID of the summary message in customer chat |
| `runner_message_id` | BIGINT | ID of the original post in runner group |

---

## Migration Strategy
SQLite is schema‐less by design; however if you need to add columns:
1. Create a new migration script that calls `ALTER TABLE … ADD COLUMN …`.
2. Ship it alongside the application; the bot will execute it on startup.

For major changes consider migrating to PostgreSQL and using an ORM such as SQLModel.