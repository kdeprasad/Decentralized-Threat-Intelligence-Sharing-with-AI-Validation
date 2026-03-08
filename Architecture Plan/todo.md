# Project Development Plan

## Phase 1 – Data Collection Setup

Goal:
Create the data submission pipeline.

Tasks:
- Create Google Form for threat intelligence submission
- Define form fields (IP, domain, hash, threat type)
- Link form responses to Google Sheets
- Access responses using Google Sheets API
- Build simple Python script to fetch submissions

Deliverable:
System can read threat reports from Google Forms.

---

## Phase 2 – Backend and Data Storage

Goal:
Build backend services and database.

Tasks:
- Create FastAPI backend
- Design database schema
- Store submissions in PostgreSQL
- Create API endpoints for threat data
- Implement basic validation checks

Deliverable:
Backend service that processes and stores threat reports.

---

## Phase 3 – AI Validation Module

Goal:
Add automated threat validation.

Tasks:
- Prepare dataset for threat classification
- Train simple ML model
- Integrate model with backend
- Assign confidence score to submissions
- Store validation results

Deliverable:
System can automatically validate threat intelligence.

---

## Phase 4 – Deployment and Monitoring

Goal:
Prepare system for deployment and operations.

Tasks:
- Dockerize backend services
- Create Docker Compose setup
- Implement CI/CD pipeline using GitHub Actions
- Add monitoring using Prometheus and Grafana
- Add centralized logging

Deliverable:
Fully deployable and monitored system.