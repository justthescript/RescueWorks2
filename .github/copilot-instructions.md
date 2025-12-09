# RescueWorks AI Agent Instructions

## Architecture Overview

**RescueWorks** is a multi-tenant rescue management platform with three main components:
- **Backend**: FastAPI with SQLAlchemy ORM, SQLite database, OAuth2 token auth
- **Frontend**: React 18 with Vite, Axios for HTTP requests
- **Mobile**: React Native (Expo)

**Key architectural principles:**
- **Multi-tenancy via `org_id`**: Every major entity (users, pets, payments) is scoped to `org_id`. Always include org filters in queries.
- **Role-based access control (RBAC)**: 10 roles defined in `permissions.py` (admin, super_admin, pet_coordinator, etc.). Use `require_any_role()` dependency for endpoint protection.
- **Domain-driven structure**: Routers in `app/routers/` correspond to business domains (pets, payments, medical, events, tasks, messaging, etc.)

## Backend Key Patterns

### Adding New Endpoints
1. **Create in `app/routers/{domain}.py`** with router prefix matching domain
2. **Use role-based dependencies**:
   ```python
   require_any_role([ROLE_ADMIN, ROLE_PET_COORDINATOR])
   ```
3. **Always scope to user's org**: Filter by `user.org_id` from `get_current_user` dependency
4. **Pydantic schemas** in `schemas.py` with `orm_mode=True` for SQLAlchemy mapping
5. **Include in `app/main.py`** via `app.include_router()`

### Database Access Pattern
- Use `db: Session = Depends(get_db)` to access SQLAlchemy session
- Models in `app/models.py` use SQLAlchemy ORM with relationship mappings
- **Org-scoped queries**: `db.query(Model).filter(Model.org_id == user.org_id)`
- Commit after writes: `db.add(obj); db.commit(); db.refresh(obj)`

### Authentication Flow
- **Token generation**: `security.py` uses JWT with HS256, bcrypt for passwords
- **Protected endpoints**: Use `Depends(get_current_user)` from `deps.py`
- **JWT validation**: Decodes token to extract email as subject
- **Token expiry**: Configured as 24 hours in security module

### Audit Logging
- Use `audit.log_action()` in `app/audit.py` for entity changes (org_id, user_id, entity_type, action, details)
- Called manually in routers; not auto-tracked
- Essential for compliance in rescue operations

## Frontend Key Patterns

### API Integration
- **Axios instance** in `src/api.js` with baseURL pointing to localhost:8000
- **Auth token set via**: `setAuthToken(token)` - updates Authorization header
- **Token stored in client** (check `App.jsx` or localStorage pattern used)
- **CORS enabled** on backend for localhost:3000, 5173, 19006

### Component Structure
- Vite 5 + React 18 setup with fast refresh
- **Test setup**: Vitest + React Testing Library (`test/setup.js`)
- **Coverage**: @vitest/coverage-v8 configured

### Build & Run
```bash
npm install      # Install deps
npm run dev      # Start dev server on :3000
npm run build    # Production build
npm run test     # Run tests
npm run test:coverage  # Coverage report
npm run lint     # ESLint validation
```

## Backend Build & Run

### Development
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
```

### Docker
```bash
docker-compose up
# Backend: localhost:8000, Frontend: localhost:3000
```

### Testing
```bash
pytest              # Run all tests in backend/tests/
pytest tests/test_pets.py  # Specific test file
```

**Test fixtures** in `conftest.py`: in-memory SQLite, test_org, test_user, test_admin_user, auth_headers, test_pet

### Key Dependencies
- **FastAPI**: Web framework with automatic OpenAPI docs
- **SQLAlchemy**: ORM with declarative_base for models
- **python-jose**: JWT token handling
- **Stripe & PayPal**: Payment integrations (see `integrations/`)
- **Alembic**: Database migrations (configured in pyproject.toml)

## Integration Points

### Payment Processing
- **Stripe integration**: `integrations/payments_stripe.py` handles checkout sessions
- **Webhook handlers**: `routers/payment_webhooks.py` receives Stripe/PayPal events
- **Payment status flow**: pending → completed/failed/refunded in `models.PaymentStatus`
- **Coupons**: Separate model with discount_type (absolute/percentage) and validity dates

### External Services
- **PetFinder API**: `integrations/petfinder.py` for pet data enrichment
- **Email/Notifications**: `integrations/notifications.py` (implementation details in models)
- **All integrations scoped to org**: Include org_id in integration requests

## Project-Specific Conventions

### Naming & Formatting
- **isort config**: black profile, 88 line length, group first_party as "app"
- **Python 3.11** minimum (Dockerfile uses python:3.11-slim)
- **Enum patterns**: Models have enums (PetStatus, ApplicationStatus, TaskStatus, PaymentStatus, PaymentPurpose)

### File Upload Pattern
- **Upload directory**: `/app/uploads` (mounted as volume in Docker)
- **Router**: `routers/files.py` handles file operations with org scoping

### Common Data Structures
- **Created/updated timestamps**: Most entities have `created_at`, `updated_at` columns
- **Soft deletes**: Some entities track `is_active` boolean rather than hard deletes
- **Relationships**: Used for navigating one-to-many (org → users, pets → medical records, etc.)

## Critical Gotchas

1. **Org isolation**: Every query must filter by `user.org_id`. Missing this is a security/data leakage bug.
2. **Role checking**: Some endpoints require specific roles. Missing `require_any_role()` allows unauthorized access.
3. **SQLite limitations**: Database is file-based. In production, migrate to PostgreSQL (update DATABASE_URL and imports).
4. **Token expiry**: Access tokens expire after 24 hours. Frontend must refresh or re-authenticate.
5. **CORS origins**: Only localhost ports listed. Adding production domains requires config changes in `main.py`.
6. **Environment variables**: SECRET_KEY, DATABASE_URL set in docker-compose.yml—override for production.

## When Modifying This Codebase

- **New domain feature?** Create `routers/{domain}.py`, add models, schemas, endpoints with org/role checks
- **New payment method?** Add integration in `integrations/`, create webhook router, update PaymentPurpose enum
- **Database changes?** Use Alembic migrations, never alter schema directly
- **Frontend API calls?** Use axios instance from `api.js`, ensure Bearer token is set
- **Tests?** Follow pytest conftest patterns; use fixtures for db/client/users
