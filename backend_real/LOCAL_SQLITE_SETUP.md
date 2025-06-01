# 🍽️ Foodgram Backend - Local SQLite Setup

This guide explains how to run the Foodgram backend locally using SQLite instead of PostgreSQL. This is perfect for development, testing, or when you don't want to set up a full PostgreSQL database.

## 🎯 Why SQLite?

- **No Database Installation**: SQLite is built into Python
- **Lightweight**: Perfect for development and testing
- **Portable**: Database is a single file
- **Fast Setup**: No configuration needed
- **Same Features**: All Foodgram features work the same way

## ⚙️ How It Works

The backend automatically detects which database to use based on the `USE_SQLITE=1` environment variable:

- **With `USE_SQLITE=1`**: Uses SQLite database (`db.sqlite3` file)
- **Without `USE_SQLITE=1`**: Uses PostgreSQL with connection settings from environment variables

This allows you to easily switch between SQLite (development) and PostgreSQL (production) without changing any code.

## 🚀 Quick Setup (Automated)

### Option 1: Windows
```cmd
cd backend_real
setup_local_sqlite.bat
```

### Option 2: macOS/Linux
```bash
cd backend_real
chmod +x setup_local_sqlite.sh
./setup_local_sqlite.sh
```

### Option 3: Python Script (All Platforms)
```bash
cd backend_real
python setup_local_sqlite.py
```

## 🔧 Manual Setup

If you prefer to set up manually or want to understand each step:

### 1. Create Virtual Environment
```bash
cd backend_real
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Environment File
Create `.env` file in `backend_real/`:
```env
USE_SQLITE=1
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-local-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*
```

**Important**: The `USE_SQLITE=1` variable tells Django to use SQLite instead of PostgreSQL.

### 4. Set Up Database
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Load ingredients (2,186+ ingredients)
python manage.py load_ingredients

# Load sample data (users and recipes with images)
python manage.py load_initial_data

# Set up test data for API testing (favorites, shopping cart)
python setup_test_data.py

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```

## 🌐 Access Your Application

Once the server is running, you can access:

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Recipe List**: http://localhost:8000/api/recipes/
- **Favorited Recipes**: http://localhost:8000/api/recipes/?is_favorited=1
- **Shopping Cart Recipes**: http://localhost:8000/api/recipes/?is_in_shopping_cart=1
- **Ingredients**: http://localhost:8000/api/ingredients/
- **Users**: http://localhost:8000/api/users/

## 📁 File Structure

After setup, you'll have:

```
backend_real/
├── db.sqlite3              # SQLite database file
├── media/                  # User-uploaded files
│   └── recipes/images/     # Recipe images
├── collected_static/       # Django static files
├── .env                    # Environment variables
└── venv/                   # Virtual environment
```

## 🔄 Database Management

### View Database
You can use any SQLite browser or Django admin:
- **Django Admin**: http://localhost:8000/admin/
- **SQLite Browser**: Download from https://sqlitebrowser.org/

### Reset Database
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
python manage.py load_ingredients
python manage.py load_initial_data
python setup_test_data.py
```

### Backup Database
```bash
# Simple file copy
cp db.sqlite3 db_backup.sqlite3
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Check code quality:
```bash
python -m ruff check .
```

## 🔧 Development Tips

### 1. Auto-reload
The development server automatically reloads when you change Python files.

### 2. Debug Mode
With `DEBUG=True`, you get:
- Detailed error pages
- SQLite database (automatic)
- Static files served by Django
- Debug toolbar (if installed)

### 3. API Testing
Use tools like:
- **Browser**: http://localhost:8000/api/ (Django REST Framework interface)
- **curl**: `curl http://localhost:8000/api/recipes/`
- **Postman**: Import the API endpoints
- **httpie**: `http localhost:8000/api/recipes/`

### 4. Sample Data
The setup includes:
- **2,186+ ingredients** from CSV files
- **Sample users**: admin, john.doe, jane.smith, chef.gordon
- **Test users**: testuser5, testuser6, testuser7 (for API testing)
- **Sample recipes** with images
- **Test data**: Favorites and shopping cart entries for filtering tests
- **Admin user**: admin@foodgram.com

## 🔄 Switching Back to PostgreSQL

To switch back to PostgreSQL (for production):

1. Set `DJANGO_DEBUG=False` in `.env`
2. Configure PostgreSQL settings in `.env`
3. Run migrations: `python manage.py migrate`

## 🐛 Troubleshooting

### Common Issues

**1. Import Error**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

**2. Migration Error**
```bash
# Delete migrations and recreate
rm */migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

**3. Static Files Not Loading**
```bash
python manage.py collectstatic --noinput
```

**4. Django tries to connect to PostgreSQL instead of SQLite**
```bash
# Make sure your .env file contains:
USE_SQLITE=1
DJANGO_DEBUG=True
```

**5. Permission Error**
```bash
# On Windows, run as administrator
# On macOS/Linux, check file permissions
```

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Ensure virtual environment is activated
3. Verify all dependencies are installed
4. Check that you're in the `backend_real` directory

## 📊 Performance Notes

SQLite is perfect for development but has some limitations:
- **Single Writer**: Only one write operation at a time
- **No Network Access**: Database is local only
- **Size Limits**: Practical limit around 1TB
- **Concurrency**: Limited compared to PostgreSQL

For production, use PostgreSQL with Docker as described in the main README.

## 🎉 Success!

You now have a fully functional Foodgram backend running locally with SQLite! 

The setup includes everything you need:
- ✅ Complete ingredient database
- ✅ Sample recipes with images
- ✅ User authentication system
- ✅ Admin interface
- ✅ REST API endpoints
- ✅ File upload handling
- ✅ Test data for API filtering (favorites, shopping cart)
- ✅ Ready for Postman API testing

Happy coding! 🚀
