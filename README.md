# Hospital Appointment System (Flet + Flask)

## Prerequisites
- Python 3.9+

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # on macOS/Linux
pip install -r requirements.txt
```

## Run Backend API
```bash
python run_backend.py
```
API base: `http://127.0.0.1:5000/api`

## Run Patient App
```bash
python apps/patient/main.py
```

## Run Doctor App
```bash
python apps/doctor/main.py
```

## Environment
Optional `.env`:
```
DATABASE_URL=sqlite:////Users/naveenworld/Desktop/asupatri_application/app.db
JWT_SECRET_KEY=change-me
```

## Notes
- Seed initial data (hospitals/doctors) via DB or add endpoints.
- Nearby hospitals use a basic haversine calculation.
