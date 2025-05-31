# 🚀 Foodgram Quick Start Guide

This guide provides the fastest way to get Foodgram up and running.

## 🐳 Docker Setup (Recommended - 5 minutes)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd foodgram-st/food-real/infra
```

### 2. Create Environment Files
Create `.env_backend`:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Create `.env_db`:
```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
```

### 3. Start Everything
```bash
docker-compose up --build
```

### 4. Access the App
- **Frontend**: http://localhost
- **API**: http://localhost/api/
- **Admin**: http://localhost/admin/

**Done! 🎉** The app includes:
- 2,186+ ingredients loaded automatically
- Sample recipes with images
- Admin user: `admin@foodgram.com`

## 🔧 Backend Only Setup (Development)

### 1. Setup Environment
```bash
cd backend_real
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Setup Database
Install PostgreSQL and create database:
```sql
CREATE DATABASE foodgram;
CREATE USER foodgram_user WITH PASSWORD 'foodgram_password';
GRANT ALL PRIVILEGES ON DATABASE foodgram TO foodgram_user;
```

### 3. Configure Environment
Create `.env` in `backend_real/`:
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Initialize and Run
```bash
python manage.py migrate
python manage.py load_ingredients
python manage.py load_initial_data
python manage.py runserver
```

**Backend API**: http://localhost:8000/api/

## 🎯 Common Commands

### Docker Commands
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs backend
docker-compose logs nginx

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build

# Execute commands in container
docker exec foodgram_backend python manage.py createsuperuser
```

### Django Commands
```bash
# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Check code quality
python -m ruff check .

# Load data
python manage.py load_ingredients
python manage.py load_initial_data

# Database operations
python manage.py makemigrations
python manage.py migrate
```

## 🔍 Troubleshooting

### Common Issues

**Port already in use:**
```bash
docker-compose down
# Or change ports in docker-compose.yml
```

**Database connection error:**
- Check PostgreSQL is running
- Verify credentials in .env files
- Ensure database exists

**Static files not loading:**
```bash
docker-compose restart nginx
# Or check nginx logs
docker-compose logs nginx
```

**Permission errors:**
```bash
# On Linux/macOS, you might need:
sudo docker-compose up
```

## 📱 Quick Test

After setup, test these URLs:
- http://localhost - Should show React frontend
- http://localhost/api/ - Should show DRF interface
- http://localhost/api/recipes/ - Should show recipes with images
- http://localhost/admin/ - Should show Django admin (styled)

## 🎉 Next Steps

1. **Create an account** on the frontend
2. **Browse recipes** with sample data
3. **Create your first recipe** with an image
4. **Explore the API** at `/api/docs/`
5. **Check the admin panel** for data management

Need help? Check the full [README.md](README.md) for detailed documentation!
