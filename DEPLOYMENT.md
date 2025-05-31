# Foodgram Deployment Guide

This document describes the deployment process for the Foodgram application using GitHub Actions and Docker.

## Overview

The application uses a CI/CD pipeline that:
1. Runs tests and code quality checks
2. Builds and pushes Docker images to DockerHub
3. Deploys to production server automatically

## Project Structure

```
foodgram-st/
├── backend_real/          # Main backend application
├── frontend/              # React frontend application
├── infra/                 # Infrastructure configuration
│   ├── docker-compose.yml           # Development setup
│   ├── docker-compose.production.yml # Production setup
│   ├── nginx.conf                   # Nginx configuration
│   ├── .env_backend                 # Backend environment variables
│   └── .env_db                      # Database environment variables
├── data/                  # Initial data (ingredients, etc.)
└── .github/workflows/main.yml       # CI/CD pipeline
```

## GitHub Secrets Required

Set up the following secrets in your GitHub repository:

### Docker Hub
- `DOCKER_USERNAME` - Your DockerHub username
- `DOCKER_PASSWORD` - Your DockerHub password or access token

### Server Deployment
- `HOST` - Your production server IP address
- `USER` - SSH username for the server
- `SSH_KEY` - Private SSH key for server access
- `SSH_PASSPHRASE` - Passphrase for the SSH key (if any)

## Environment Files

### `.env_backend`
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-change-this-in-production
DJANGO_ALLOWED_HOSTS=your-domain.com,your-server-ip

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### `.env_db`
```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
```

## Workflow Stages

### 1. Testing (`backend_tests_with_ruff`)
- Sets up Python 3.11 environment
- Installs dependencies from `backend_real/requirements.txt`
- Runs Ruff code quality checks
- Executes Django tests with PostgreSQL database

### 2. Build Backend (`build_and_push_backend_to_dockerhub`)
- Builds Docker image from `backend_real/`
- Pushes to DockerHub as `hetdro451595/foodgram_backend:latest`

### 3. Build Frontend (`build_and_push_frontend_to_dockerhub`)
- Builds Docker image from `frontend/`
- Pushes to DockerHub as `hetdro451595/foodgram_frontend:latest`

### 4. Deploy (`deploy`)
- Only runs on `main` branch
- Copies configuration files to server
- Pulls latest images and restarts services
- Automatically loads ingredients and initial data

## Local Development

### Development Setup
```bash
cd infra
docker-compose up --build
```

### Production Testing
```bash
cd infra
docker-compose -f docker-compose.production.yml up --build
```

## Features

### Automatic Data Loading
- **Ingredients**: 2,186+ ingredients loaded from CSV files
- **Initial Data**: Admin user and sample recipes created automatically
- **Static Files**: Django admin and DRF styling served by Nginx

### Services
- **Backend**: Django + Gunicorn (port 8000)
- **Frontend**: React SPA served by Nginx
- **Database**: PostgreSQL 15
- **Proxy**: Nginx with static file serving
- **SSL**: Ready for Let's Encrypt certificates

### URLs
- **Frontend**: http://localhost/
- **API**: http://localhost/api/
- **Admin**: http://localhost/admin/
- **API Documentation**: http://localhost/api/docs/

## Troubleshooting

### Check Service Status
```bash
docker-compose ps
docker-compose logs backend
docker-compose logs nginx
```

### Manual Data Loading
```bash
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py load_initial_data
```

### Reset Database
```bash
docker-compose down -v
docker-compose up --build
```

## Security Notes

1. Change default passwords in production
2. Use strong SECRET_KEY
3. Set up SSL certificates
4. Configure firewall rules
5. Regular security updates
