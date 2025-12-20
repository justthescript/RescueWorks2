# RescueWorks - Animal Rescue Management System

A modern, full-stack application for animal rescue organizations, optimized for deployment on **Vercel** (frontend) and **Railway** (backend + database).

## Features

### Sprint 1: Foundation ✅
- **Animal Intake Form** with validation
- **Image Upload** functionality for animal photos
- **Basic Foster Assignment** backend
- **Database Schema** with PostgreSQL and CI/CD setup

### Sprint 2: Matching Logic ✅
- **Foster Coordinator Dashboard** with real-time statistics
- **Automated Matching Algorithm** for intelligent animal-foster pairing
- **Foster Profile Management** with detailed caregiver profiles
- **Animal-Foster Pairing Workflow** for complete placement lifecycle

### Sprint 3: Operations Dashboard ✅
- **Key Metrics Visualization** for operational insights
- **Foster Care Update Forms** for tracking progress
- **Search and Filter Capabilities** for advanced animal search
- **Report Generation** with statistics and analytics

### Sprint 4: Admin & Security ✅
- **User Role Management** (Admin, Coordinator, Foster, Staff)
- **Authentication and Authorization** with JWT tokens
- **System Configuration Settings** management
- **Production Deployment** configuration

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **JWT** - Authentication
- **Railway** - Hosting platform

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Axios** - HTTP client
- **React Router** - Navigation
- **Vercel** - Hosting platform

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Local Development

#### Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed test data
python seed_data.py

# Start server
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`
API docs at `http://localhost:8000/docs`

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env if needed (VITE_API_URL)

# Start dev server
npm run dev
```

Frontend will run on `http://localhost:5173`

## Deployment

### Deploy Backend to Railway

1. Create a new project on [Railway](https://railway.app)
2. Add a PostgreSQL database service
3. Add a new service from GitHub repo
4. Set environment variables:
   ```
   DATABASE_URL=(auto-set by Railway)
   SECRET_KEY=(generate with: openssl rand -hex 32)
   CORS_ORIGINS=https://your-frontend.vercel.app
   ENVIRONMENT=production
   ```
5. Railway will automatically:
   - Build the Docker container
   - Run database migrations
   - Deploy the API

### Deploy Frontend to Vercel

1. Push code to GitHub
2. Import project to [Vercel](https://vercel.com)
3. Set build settings:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Root Directory: `frontend`
4. Set environment variable:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```
5. Deploy!

## Test Credentials

After running `python seed_data.py`, you can login with:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@rescueworks.test | admin123 |
| Coordinator | coordinator@rescueworks.test | coord123 |
| Foster | foster1@rescueworks.test | foster1123 |
| Foster | foster2@rescueworks.test | foster2123 |
| Foster | foster3@rescueworks.test | foster3123 |

## Test Data

The seed script creates:
- 10 animals (various species, statuses, and attributes)
- 7 users (1 admin, 1 coordinator, 5 fosters)
- 5 foster profiles (different experience levels and capabilities)
- 3 foster placements (2 active, 1 completed/adopted)
- 4 care updates (medical, behavioral, and general)
- 4 system configuration settings

## API Documentation

Once the backend is running, visit `/docs` for interactive API documentation powered by Swagger UI.

### Main Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

**Animals (Sprint 1)**
- `POST /animals/` - Create animal intake
- `POST /animals/{id}/upload-photo` - Upload photo
- `GET /animals/` - List animals
- `PATCH /animals/{id}` - Update animal

**Foster Management (Sprint 2)**
- `POST /foster/profiles` - Create foster profile
- `GET /foster/profiles` - List foster profiles
- `GET /foster/matches` - Get suggested matches
- `POST /foster/placements` - Create placement
- `GET /foster/dashboard` - Dashboard statistics

**Operations (Sprint 3)**
- `POST /operations/care-updates` - Create care update
- `GET /operations/search/animals` - Advanced search
- `GET /operations/reports/animals` - Animal statistics

**Admin (Sprint 4)**
- `GET /admin/users` - List users
- `PATCH /admin/users/{id}/role` - Update user role
- `GET /admin/config` - System configuration

See full API documentation at `/docs` endpoint.

## Project Structure

```
rescueworks-new/
├── backend/
│   ├── app/
│   │   ├── routers/          # API route handlers
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── animals.py    # Animal management
│   │   │   ├── foster.py     # Foster management
│   │   │   ├── operations.py # Operations & reports
│   │   │   └── admin.py      # Admin functions
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── security.py       # Auth utilities
│   │   ├── database.py       # Database connection
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker configuration
│   └── seed_data.py          # Test data script
├── frontend/
│   ├── src/
│   │   ├── utils/
│   │   │   └── api.js        # API client
│   │   ├── App.jsx           # Main app component
│   │   ├── index.css         # Global styles
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   └── vercel.json           # Vercel configuration
├── railway.json              # Railway configuration
└── README.md                 # This file
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/rescueworks
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
ENVIRONMENT=development
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Database Schema

### Core Tables
- `organizations` - Organization/rescue information
- `users` - User accounts with role-based access
- `animals` - Animal records with intake information
- `foster_profiles` - Foster caregiver profiles and qualifications
- `foster_placements` - Foster placement history and tracking
- `care_updates` - Progress notes and care updates
- `system_config` - System configuration key-value pairs

### User Roles
- **admin** - Full system access
- **coordinator** - Manage fosters, placements, and operations
- **foster** - Foster caregiver access
- **staff** - Basic staff access

## Matching Algorithm

The automated matching algorithm scores potential animal-foster pairs based on:

1. **Availability & Capacity** (20 points)
2. **Species Preference Match** (30 points)
3. **Medical Needs Capability** (25 points)
4. **Behavioral Needs Capability** (25 points)
5. **Experience Level** (15 points)
6. **Success Track Record** (20 points)
7. **Foster Rating** (15 points)
8. **Workload Balancing** (15 points)

Matches with scores above 20 are displayed, sorted by score.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues or questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the README files in backend/ and frontend/ directories

## License

This project is licensed under the MIT License.

## Acknowledgments

Built with ❤️ for animal rescue organizations worldwide.
