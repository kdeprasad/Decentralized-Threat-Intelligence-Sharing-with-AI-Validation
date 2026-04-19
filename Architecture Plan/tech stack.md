# Tech Stack

## Frontend

- React (preferred)
- Axios

Purpose:
- User login
- Threat submission form
- Dashboard for viewing threats

---

## Backend

Language:
- Python

Framework:
- FastAPI

---

## Microservices

### API Service
- Handles REST API
- Receives submissions
- Communicates with validation service
- Stores results in database

### Validation Service
- Feature extraction
- ML model inference
- Returns confidence score

---

## AI Module

Libraries:
- scikit-learn
- pandas
- numpy

Models:
- Logistic Regression
- Random Forest

---

## Database

- PostgreSQL

Stores:
- threat data
- validation score
- user info

---

## Containerization

- Docker
- Docker Compose

---

## Optional Additions

### Authentication
- JWT-based login

### Monitoring
- Prometheus
- Grafana

### Queue (future)
- Redis