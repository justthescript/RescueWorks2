import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import (
    applications,
    auth,
    events,
    expenses,
    files,
    foster_coordinator,
    medical,
    messaging,
    orgs,
    payment_webhooks,
    payments,
    people,
    pets,
    portal,
    public,
    reports,
    settings,
    stats,
    tasks,
    vet,
)

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RescueWorks Backend")

# Read CORS origins from environment variable, fallback to localhost for development
cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:19006, https://rescue-works-frontend.vercel.app/"
)
origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Allow frontend to read all response headers
)

app.include_router(auth.router)
app.include_router(orgs.router)
app.include_router(pets.router)
app.include_router(people.router)
app.include_router(applications.router)
app.include_router(foster_coordinator.router)
app.include_router(medical.router)
app.include_router(events.router)
app.include_router(tasks.router)
app.include_router(expenses.router)
app.include_router(messaging.router)
app.include_router(payments.router)
app.include_router(public.router)
app.include_router(settings.router)
app.include_router(portal.router)
app.include_router(vet.router)
app.include_router(files.router)
app.include_router(stats.router)
app.include_router(reports.router)
app.include_router(payment_webhooks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
