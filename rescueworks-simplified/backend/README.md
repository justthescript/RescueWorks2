# RescueWorks Backend

FastAPI backend for animal rescue management system, optimized for Railway deployment.

## Features

### Sprint 1: Foundation
- Animal intake form with validation
- Image upload functionality
- Basic foster assignment backend
- Database schema with PostgreSQL

### Sprint 2: Matching Logic
- Foster coordinator dashboard
- Automated matching algorithm
- Foster profile management
- Animal-foster pairing workflow

### Sprint 3: Operations Dashboard
- Key metrics visualization
- Foster care update forms
- Search and filter capabilities
- Report generation

### Sprint 4: Admin & Security
- User role management
- Authentication and authorization
- System configuration settings

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Seed test data:
```bash
python seed_data.py
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Railway Deployment

1. Create a new project on Railway
2. Add PostgreSQL database service
3. Add this backend service
4. Set environment variables:
   - `DATABASE_URL` (auto-set by Railway)
   - `SECRET_KEY` (generate with `openssl rand -hex 32`)
   - `CORS_ORIGINS` (your Vercel frontend URL)
   - `ENVIRONMENT=production`

5. Deploy! Railway will automatically:
   - Build the Docker container
   - Run database migrations
   - Start the API server

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### Animals (Sprint 1)
- `POST /animals` - Create animal intake
- `POST /animals/{id}/upload-photo` - Upload photo
- `GET /animals` - List animals (with filters)
- `GET /animals/{id}` - Get animal details
- `PATCH /animals/{id}` - Update animal
- `DELETE /animals/{id}` - Delete animal (admin)

### Foster Management (Sprint 2)
- `POST /foster/profiles` - Create foster profile
- `GET /foster/profiles` - List foster profiles
- `GET /foster/profiles/me` - Get my profile
- `PATCH /foster/profiles/me` - Update my profile
- `GET /foster/matches` - Get suggested matches
- `POST /foster/placements` - Create placement
- `GET /foster/placements` - List placements
- `PATCH /foster/placements/{id}` - Update placement
- `GET /foster/dashboard` - Dashboard stats

### Operations (Sprint 3)
- `POST /operations/care-updates` - Create care update
- `GET /operations/care-updates` - List care updates
- `GET /operations/search/animals` - Advanced animal search
- `GET /operations/reports/animals` - Animal statistics report
- `GET /operations/reports/foster-performance` - Foster performance report
- `GET /operations/reports/dashboard-summary` - Dashboard summary

### Admin (Sprint 4)
- `GET /admin/users` - List users
- `PATCH /admin/users/{id}/role` - Update user role
- `PATCH /admin/users/{id}/status` - Activate/deactivate user
- `GET /admin/config` - List config settings
- `POST /admin/config` - Create config setting
- `PATCH /admin/config/{key}` - Update config setting
- `GET /admin/organization` - Get organization info

## Test Data

Run `python seed_data.py` to create:
- 10 animals (various species and statuses)
- 7 users (admin, coordinator, 5 fosters)
- 5 foster profiles (different experience levels)
- 3 placements (2 active, 1 completed)
- 4 care updates
- 4 system configuration settings

### Test Credentials
- Admin: `admin@rescueworks.test / admin123`
- Coordinator: `coordinator@rescueworks.test / coord123`
- Foster: `foster1@rescueworks.test / foster1123`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | http://localhost:5173 |
| `ENVIRONMENT` | Environment name | development |

## Database Schema

See `app/models.py` for complete schema definition.

Main tables:
- `organizations` - Organization details
- `users` - User accounts with roles
- `animals` - Animal records
- `foster_profiles` - Foster caregiver profiles
- `foster_placements` - Foster placement history
- `care_updates` - Care notes and updates
- `system_config` - System configuration

## User Roles

- `admin` - Full system access
- `coordinator` - Manage fosters and placements
- `foster` - Foster caregiver access
- `staff` - Basic staff access
