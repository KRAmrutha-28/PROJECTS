# Chanakya University Portal

This repository contains the university portal's React frontend and Django REST backend.

## Project structure

- `frontend/` - React application
- `backend/` - Django project and API applications

## Run the backend

Use Python 3. From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install django djangorestframework django-cors-headers python-dotenv
python manage.py migrate
python manage.py runserver
```

The Django development server runs at `http://127.0.0.1:8000`.

## Run the frontend

In a second terminal, from the repository root:

```powershell
cd frontend
npm install
npm start
```

The React development server runs at `http://localhost:3000`.
