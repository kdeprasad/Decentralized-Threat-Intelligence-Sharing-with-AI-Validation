# Tech Stack

## Form Interface
Google Forms

Used for collecting threat intelligence submissions.

Example fields:
- IP Address
- Domain
- Malware Hash
- Threat Type
- Description

## Data Access

Google Forms responses will be accessed using:

- Google Sheets
- Google Sheets API

Google Forms automatically stores responses in a Google Sheet.

## Backend

Language:
Python

Framework:
FastAPI

Responsibilities:
- Fetch form responses
- Process threat data
- Run AI validation
- Store results
- Provide API access

## AI Validation Module

Libraries:
- scikit-learn
- pandas
- numpy

Purpose:
- classify threat indicators
- assign confidence score
- filter invalid or suspicious submissions

## Database

PostgreSQL

Stores:
- threat indicators
- validation results
- submission metadata

## Containerization

Docker

Used to package backend services for deployment.

## CI/CD

GitHub Actions

Used for:
- automated builds
- testing
- container image creation

## Monitoring

Prometheus  
Grafana

Used to monitor system metrics and service health.

## Logging

Loki or ELK Stack

Used to collect and visualize application logs.