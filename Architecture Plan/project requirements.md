# Project Requirements

## Project Title
Threat Intelligence Sharing Platform (Frontend-Driven, Microservices-Based)

---

## Problem Statement

Organizations need a structured way to report, validate, and analyze cybersecurity threats.

Current challenges:

- No unified platform for threat submission
- Manual validation of threat indicators
- Inconsistent and low-quality threat data
- Lack of real-time feedback on submitted threats
- Poor integration between users and backend systems

---

## Proposed Solution

Develop a web-based platform where organizations:

1. Log in to the system
2. Submit threat indicators via a frontend UI
3. Receive an AI-generated validation score for each submission
4. View stored threats and their validation status

The system uses a microservices architecture where all submissions go through a validation pipeline before being stored.

---

## System Overview

Primary flow:

User → Frontend → API Service → Validation Service → Database → Frontend

Each threat submission is:

- received via API
- processed for feature extraction
- validated using AI model
- assigned a confidence score
- stored in the database
- displayed in the UI

---

## Functional Requirements

### User Management
- Organizations can log in (basic authentication)
- Each submission is associated with a user

### Threat Submission
- Users can submit:
  - IP address
  - domain
  - malware hash
  - threat type
  - description

### Validation
- System extracts features from input
- AI model assigns confidence score
- Threat is classified:
  - valid
  - suspicious
  - invalid

### Threat Viewing
- Users can view all submitted threats
- Each threat shows:
  - original data
  - validation score
  - validation status

### API
- GET /threats
- POST /submit

---

## Non-Functional Requirements

- Modular microservices architecture
- Containerized deployment
- Scalable design
- Fast API response
- Clear separation of concerns

---

## Architecture

Primary Flow:

User  
↓  
Frontend  
↓  
API Service  
↓  
Validation Service  
↓  
Database  
↓  
Frontend  

---

## Microservices Breakdown

### Frontend Service
- Handles UI
- Sends requests to API

### API Service
- Receives submissions
- Sends data to validation service
- Stores validated results

### Validation Service
- Performs feature extraction
- Runs ML model
- Returns confidence score

### Database
- Stores threats and validation results

---

## Project Structure

threat-intelligence-platform/

frontend/  
services/  
  api-service/  
  validation-service/  
docker/  
ml/  
monitoring/  

---

## Expected Output

- Web application with login and dashboard
- Threat submission interface
- AI-based validation scoring
- Stored threat intelligence
- Containerized deployment