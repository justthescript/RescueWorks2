FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Collect static files (for Django)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command (Railway will override this with railway.json)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:application"]
