# Development Plan

---

## Phase 1 – Frontend + API Integration

- Build login page
- Build threat submission form
- Build dashboard UI
- Create API endpoints:
  POST /submit
  GET /threats
- Connect frontend to API

---

## Phase 2 – Validation Pipeline

- Implement feature extraction
- Train ML model
- Integrate validation service
- Return confidence score
- Display score in UI

---

## Phase 3 – Database Integration

- Design schema
- Store threats
- Store validation results
- Link threats to users

---

## Phase 4 – Microservices Split

- Separate API service
- Separate validation service
- Ensure service communication

---

## Phase 5 – Containerization

- Write Dockerfiles
- Create docker-compose
- Run full system

---

## Phase 6 – Improvements

- Add authentication (JWT)
- Improve UI dashboard
- Add monitoring