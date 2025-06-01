# 🍽️ Foodgram - Recipe Sharing Platform

Foodgram is a modern web application for sharing and discovering recipes. Users can create, share, and explore culinary creations, manage their favorite recipes, create shopping lists, and follow other food enthusiasts.

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Technologies Used](#technologies-used)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running with Docker (Recommended)](#running-with-docker-recommended)
  - [Running Backend Separately](#running-backend-separately)
  - [Running Frontend Separately](#running-frontend-separately)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🎯 About the Project

Foodgram is a full-stack recipe sharing platform that allows users to:

- **Create and share recipes** with detailed instructions and images
- **Discover new recipes** from other users
- **Manage favorites** and create personal recipe collections
- **Generate shopping lists** based on selected recipes
- **Follow other users** and see their latest creations
- **Search and filter** recipes by ingredients, tags, and authors

The application features a modern React frontend with a robust Django REST API backend, containerized with Docker for easy deployment and development.

## 🛠️ Technologies Used

### Backend
- **Python 3.11** - Programming language
- **Django 4.2** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL 15** - Production database
- **SQLite** - Development database (built-in)
- **Gunicorn** - WSGI HTTP Server
- **Pillow** - Image processing
- **django-filter** - Advanced filtering
- **djoser** - Authentication system

### Frontend
- **React 18** - JavaScript library for building user interfaces
- **JavaScript (ES6+)** - Programming language
- **CSS3** - Styling
- **Axios** - HTTP client for API requests

### Infrastructure & DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** - Web server and reverse proxy
- **GitHub Actions** - CI/CD pipeline
- **DockerHub** - Container registry

### Development Tools
- **Ruff** - Python linter and formatter
- **pytest** - Testing framework
- **Git** - Version control

## ✨ Features

### 🔐 User Management
- User registration and authentication
- Profile management with avatars
- User subscriptions and followers
- Email-based authentication

### 📝 Recipe Management
- Create recipes with images and detailed instructions
- Rich ingredient database (2,186+ ingredients)
- Recipe categorization with tags
- Cooking time tracking
- Recipe publication controls

### 🔍 Discovery & Search
- Browse all published recipes
- Search by recipe name, author, or ingredients
- Filter by tags, cooking time, favorites, and shopping cart
- Advanced filtering with proper authentication handling
- Pagination for large result sets

### ❤️ Social Features
- Favorite recipes
- Follow/unfollow users
- View user profiles and their recipes
- Activity feeds

### 🛒 Shopping Lists
- Add recipes to shopping cart
- Generate consolidated shopping lists
- Download shopping lists as text files
- Automatic ingredient quantity calculation

## 📁 Project Structure

```
foodgram-st/
├── backend_real/              # Django backend application
│   ├── api/                   # API endpoints and serializers
│   ├── recipes/               # Recipe models and logic
│   ├── users/                 # User models and authentication
│   ├── data/                  # Initial data and sample images
│   ├── requirements.txt       # Python dependencies
│   └── manage.py              # Django management script
├── frontend/                  # React frontend application
│   ├── src/                   # Source code
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── Dockerfile             # Frontend container configuration
├── infra/                     # Infrastructure configuration
│   ├── docker-compose.yml     # Development setup
│   ├── docker-compose.production.yml  # Production setup
│   ├── nginx.conf             # Nginx configuration
│   └── .env files             # Environment variables
├── data/                      # Initial data (ingredients, etc.)
├── docs/                      # API documentation
└── .github/workflows/         # CI/CD pipeline
```

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (for full application deployment)
- **Python 3.11+** (for local backend development)
- **Node.js 16+** (for local frontend development)
- **PostgreSQL 15** (optional - for production-like local development)
- **SQLite** (built into Python - for simple local development)

### 🎯 Choose Your Setup

| Setup Type | Best For | Time | Requirements |
|------------|----------|------|--------------|
| **🐳 Docker** | Full deployment, production-like | 5 min | Docker |
| **🔧 SQLite Backend** | Development, learning, testing | 2 min | Python only |
| **🗄️ PostgreSQL Backend** | Production-like development | 10 min | Python + PostgreSQL |
| **⚛️ Frontend Only** | Frontend development | 3 min | Node.js |

### Running with Docker (Recommended)

This is the easiest way to run the entire application with all services.

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd foodgram-st
```

#### 2. Set Up Environment Variables
Create environment files in the `infra/` directory:

**`.env_backend`:**
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-change-this
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

**`.env_db`:**
```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
```

#### 3. Build and Run with Docker Compose
```bash
cd infra
docker-compose up --build
```

#### 4. Access the Application
- **Frontend**: http://localhost
- **API**: http://localhost/api/
- **Admin Panel**: http://localhost/admin/
- **API Documentation**: http://localhost/api/docs/

#### 5. Create Superuser (Optional)
```bash
docker exec foodgram_backend python manage.py createsuperuser
```

### Running Backend Separately

For backend development, you can run the Django application locally with either SQLite (simple) or PostgreSQL (production-like).

#### Option A: SQLite Setup (Recommended for Development)

**Quick Setup:**
```bash
cd backend_real
# Windows
setup_local_sqlite.bat

# macOS/Linux
./setup_local_sqlite.sh

# Or use Python script (all platforms)
python setup_local_sqlite.py
```

**Manual Setup:**
```bash
# 1. Set up Python environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 2. Create .env file
echo "USE_SQLITE=1" > .env
echo "DJANGO_DEBUG=True" >> .env
echo "DJANGO_SECRET_KEY=your-development-secret-key" >> .env
echo "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*" >> .env

# 3. Set up database and load data
python manage.py makemigrations
python manage.py migrate
python manage.py load_ingredients
python manage.py load_initial_data
python manage.py collectstatic --noinput

# 4. Start server
python manage.py runserver
```

**Benefits:**
- ✅ No database installation required
- ✅ Automatic setup with sample data and test users
- ✅ Perfect for development and testing
- ✅ Database is a single `db.sqlite3` file
- ✅ Includes test data for Postman API testing
- ✅ Pre-configured favorites and shopping cart data

#### Option B: PostgreSQL Setup (Production-like)

**1. Install and Configure PostgreSQL:**
```sql
CREATE DATABASE foodgram;
CREATE USER foodgram_user WITH PASSWORD 'foodgram_password';
GRANT ALL PRIVILEGES ON DATABASE foodgram TO foodgram_user;
```

**2. Set Up Python Environment:**
```bash
cd backend_real
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

**3. Configure Environment Variables:**
Create `.env` file in `backend_real/`:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-development-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**4. Set Up Database:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py load_ingredients
python manage.py load_initial_data
python manage.py collectstatic --noinput
```

**5. Start Development Server:**
```bash
python manage.py runserver
```

#### Backend Access Points

The API will be available at:
- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Recipe List**: http://localhost:8000/api/recipes/
- **Ingredients**: http://localhost:8000/api/ingredients/

#### Run Tests
```bash
python manage.py test
python -m ruff check .
```

For detailed SQLite setup instructions, see [LOCAL_SQLITE_SETUP.md](backend_real/LOCAL_SQLITE_SETUP.md).

### Running Frontend Separately

For frontend development, you can run the React application locally.

#### 1. Set Up Node.js Environment
```bash
cd frontend
npm install
```

#### 2. Configure API Endpoint
Update the API base URL in your frontend configuration to point to your backend:
```javascript
// In your API configuration file
const API_BASE_URL = 'http://localhost:8000/api/';
```

#### 3. Start Development Server
```bash
npm start
```

The frontend will be available at http://localhost:3000

#### 4. Build for Production
```bash
npm run build
```

## 📚 API Documentation

The API documentation is available at:
- **Interactive Docs**: http://localhost/api/docs/ (when running with Docker)
- **API Root**: http://localhost/api/ (browsable API interface)

### Key API Endpoints

- `GET /api/recipes/` - List all recipes
- `GET /api/recipes/?is_favorited=1` - Filter favorited recipes
- `GET /api/recipes/?is_in_shopping_cart=1` - Filter shopping cart recipes
- `GET /api/recipes/?author={id}` - Filter recipes by author
- `POST /api/recipes/` - Create a new recipe
- `GET /api/recipes/{id}/` - Get recipe details
- `POST /api/recipes/{id}/favorite/` - Add to favorites
- `POST /api/recipes/{id}/shopping_cart/` - Add to shopping cart
- `GET /api/ingredients/` - List ingredients
- `GET /api/ingredients/?name={prefix}` - Search ingredients by name prefix
- `GET /api/users/` - List users
- `GET /api/users/subscriptions/` - Get user subscriptions
- `POST /api/auth/users/` - User registration
- `POST /api/auth/token/login/` - User login

## 🔧 Development

### Code Quality
The project uses Ruff for Python code formatting and linting:
```bash
cd backend_real
python -m ruff check .
python -m ruff format .
```

### Testing
Run the test suite:
```bash
cd backend_real
python manage.py test
```

### Database Management
Useful Django commands:
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load sample data
python manage.py load_ingredients
python manage.py load_initial_data

# Set up test data for API testing
python setup_test_data.py

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

## 🚀 Deployment

The project includes automated deployment via GitHub Actions. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Production Deployment
```bash
cd infra
docker-compose -f docker-compose.production.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use Ruff for code formatting
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- Stack overflow

---

**Happy Cooking! 🍳👨‍🍳👩‍🍳**

MADE BY: 
Схрейдер Александр
