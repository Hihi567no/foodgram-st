# 🚀 Foodgram Quick Start Guide

This guide provides the fastest way to get Foodgram up and running.

## 🐳 Docker Setup (Recommended - 5 minutes)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd foodgram-st/infra
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
- Test users with favorites and shopping cart data
- Admin user: `admin@foodgram.com`
- Ready for Postman API testing

## 🔧 Backend Only Setup (Development)

Choose between SQLite (simple) or PostgreSQL (production-like):

### Option A: SQLite (Recommended - 2 minutes)

**Automated Setup:**
```bash
cd backend_real
# Windows
setup_local_sqlite.bat

# macOS/Linux
./setup_local_sqlite.sh

# Or Python script (all platforms)
python setup_local_sqlite.py
```

**Manual Setup:**
```bash
cd backend_real
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

echo "USE_SQLITE=1" > .env
echo "DJANGO_DEBUG=True" >> .env
echo "DJANGO_SECRET_KEY=dev-secret-key" >> .env

python manage.py migrate
python manage.py load_ingredients
python manage.py load_initial_data
python setup_test_data.py
python manage.py runserver
```

**Benefits:** ✅ No database installation ✅ Instant setup ✅ Sample data included ✅ Test data for API filtering

### Option B: PostgreSQL (Production-like)

**1. Install PostgreSQL and create database:**
```sql
CREATE DATABASE foodgram;
CREATE USER foodgram_user WITH PASSWORD 'foodgram_password';
GRANT ALL PRIVILEGES ON DATABASE foodgram TO foodgram_user;
```

**2. Setup Environment:**
```bash
cd backend_real
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**3. Configure Environment:**
Create `.env` in `backend_real/`:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=dev-secret-key
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**4. Initialize and Run:**
```bash
python manage.py migrate
python manage.py load_ingredients
python manage.py load_initial_data
python setup_test_data.py
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
python setup_test_data.py

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

**Database connection error (PostgreSQL):**
- Check PostgreSQL is running
- Verify credentials in .env files
- Ensure database exists

**SQLite permission error:**
```bash
# Make sure you're in backend_real directory
cd backend_real
# Check if virtual environment is activated
venv\Scripts\activate  # Windows
```

**Static files not loading:**
```bash
# For Docker
docker-compose restart nginx

# For local development
python manage.py collectstatic --noinput
```

**Migration errors:**
```bash
# Reset migrations (SQLite)
rm db.sqlite3
python manage.py migrate

# Reset migrations (PostgreSQL)
python manage.py migrate --fake-initial
```

**Permission errors:**
```bash
# On Linux/macOS, you might need:
sudo docker-compose up
```

## 📱 Quick Test

After setup, test these URLs:

**Docker Setup:**
- http://localhost - React frontend
- http://localhost/api/ - DRF interface
- http://localhost/api/recipes/ - Recipes with images
- http://localhost/admin/ - Django admin

**Backend Only (SQLite/PostgreSQL):**
- http://localhost:8000/api/ - DRF interface
- http://localhost:8000/api/recipes/ - Recipes with images
- http://localhost:8000/api/recipes/?is_favorited=1 - Test filtering
- http://localhost:8000/api/recipes/?is_in_shopping_cart=1 - Test filtering
- http://localhost:8000/admin/ - Django admin

## 🎯 Database Comparison

| Feature | SQLite | PostgreSQL | Docker |
|---------|--------|------------|--------|
| **Setup Time** | 2 minutes | 10 minutes | 5 minutes |
| **Requirements** | Python only | PostgreSQL install | Docker install |
| **Best For** | Development, Learning | Production-like dev | Full deployment |
| **Sample Data** | ✅ Included | ✅ Included | ✅ Included |
| **Performance** | Good for dev | Production-ready | Production-ready |
| **Portability** | Single file | Network database | Containerized |

## 🎉 Next Steps

1. **Create an account** on the frontend
2. **Browse recipes** with sample data
3. **Create your first recipe** with an image
4. **Explore the API** at `/api/docs/`
5. **Check the admin panel** for data management

**For detailed setup guides:**
- **SQLite**: [LOCAL_SQLITE_SETUP.md](backend_real/LOCAL_SQLITE_SETUP.md)
- **Full Documentation**: [README.md](README.md)

Need help? Check the troubleshooting section above! 🚀
