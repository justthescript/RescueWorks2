# RescueWorks Deployment Guide

This guide covers deployment of RescueWorks to production environments.

## Prerequisites

- Docker and Docker Compose installed
- A server with at least 2GB RAM and 20GB disk space
- Domain name (optional, but recommended for production)
- SSL certificate (Let's Encrypt recommended)

## Production Deployment

### 1. Initial Setup

Clone the repository to your production server:

```bash
git clone <your-repo-url>
cd RescueWorks2
```

### 2. Environment Configuration

Create a production environment file:

```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` and set secure values:

```bash
# Generate a secure SECRET_KEY
openssl rand -hex 32

# Set strong database password
# Update CORS_ORIGINS with your domain
# Configure other settings as needed
```

**CRITICAL SECURITY SETTINGS:**
- `SECRET_KEY`: Generate a secure random key using `openssl rand -hex 32`
- `POSTGRES_PASSWORD`: Use a strong, unique password
- `CORS_ORIGINS`: Only include your production domain(s)

### 3. Deploy with Docker Compose

Start the production stack:

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

This will:
1. Start PostgreSQL database
2. Run database migrations automatically
3. Start the FastAPI backend
4. Start the React frontend with Nginx

### 4. Initial Data Setup

Create the default roles:

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.database import SessionLocal
from app.models import Role
from app.permissions import *

db = SessionLocal()

roles = [
    {'name': ROLE_SUPER_ADMIN, 'description': 'Full system access'},
    {'name': ROLE_ADMIN, 'description': 'Administrative access'},
    {'name': ROLE_APPLICATION_SCREENER, 'description': 'Review applications'},
    {'name': ROLE_PET_COORDINATOR, 'description': 'Manage pets'},
    {'name': ROLE_EVENT_COORDINATOR, 'description': 'Manage events'},
    {'name': ROLE_VETERINARIAN, 'description': 'Medical records access'},
    {'name': ROLE_BILLING_MANAGER, 'description': 'Financial management'},
    {'name': ROLE_ADOPTER, 'description': 'Adopter portal access'},
    {'name': ROLE_FOSTER, 'description': 'Foster portal access'},
    {'name': ROLE_VOLUNTEER, 'description': 'Volunteer access'},
    {'name': ROLE_BOARD_MEMBER, 'description': 'Board member access'},
]

for role_data in roles:
    role = db.query(Role).filter(Role.name == role_data['name']).first()
    if not role:
        role = Role(**role_data)
        db.add(role)

db.commit()
print('Roles created successfully!')
"
```

### 5. Create First Admin User

Register your first user through the UI, then assign admin role:

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.database import SessionLocal
from app.models import User, Role, UserRole
from app.permissions import ROLE_SUPER_ADMIN

db = SessionLocal()

# Replace with your email
user = db.query(User).filter(User.email == 'your-email@example.com').first()
admin_role = db.query(Role).filter(Role.name == ROLE_SUPER_ADMIN).first()

if user and admin_role:
    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()
    print(f'Admin role assigned to {user.email}')
else:
    print('User or role not found')
"
```

## Database Migrations

### Creating New Migrations

When you modify models, create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

Migrations are applied automatically on container startup. To manually apply:

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Rolling Back Migrations

To roll back the last migration:

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

## SSL/HTTPS Setup

For production, you should use HTTPS. Here's how to set it up with Let's Encrypt:

1. Install certbot on your server
2. Obtain certificates:
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com
   ```
3. Update `frontend/nginx.conf` to include SSL configuration
4. Rebuild the frontend container

## Monitoring and Logs

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f db
```

### Health Checks

Check service health:

```bash
docker-compose -f docker-compose.prod.yml ps
```

## Backup and Restore

### Backup Database

```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U rescueworks rescueworks > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U rescueworks rescueworks
```

### Backup Uploaded Files

```bash
docker cp $(docker-compose -f docker-compose.prod.yml ps -q backend):/app/uploads ./uploads-backup
```

## Updating the Application

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart containers:
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

## Troubleshooting

### Backend Won't Start

Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

Common issues:
- Database connection failed: Check `DATABASE_URL` in `.env.prod`
- Migration errors: Try running migrations manually
- Port conflicts: Ensure ports 80 and 5432 are available

### Database Connection Issues

Verify database is running:
```bash
docker-compose -f docker-compose.prod.yml exec db pg_isready
```

### Frontend Shows API Errors

Check that backend is healthy:
```bash
curl http://localhost:8000/health
```

Verify CORS_ORIGINS includes your domain.

## Security Checklist

- [ ] Changed default `SECRET_KEY`
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Updated `CORS_ORIGINS` to production domain only
- [ ] Enabled HTTPS with valid SSL certificate
- [ ] Configured firewall to only allow ports 80, 443, and 22
- [ ] Set up regular database backups
- [ ] Configured log rotation
- [ ] Reviewed and assigned user roles appropriately
- [ ] Disabled debug mode (DEBUG=false in backend)

## Support

For issues or questions, please open an issue on GitHub.
