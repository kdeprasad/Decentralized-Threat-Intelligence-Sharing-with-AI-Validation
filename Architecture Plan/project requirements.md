# Project Requirements

## Project Title
Decentralized Threat Intelligence Sharing System with AI Validation for Google Forms

## Problem

Organizations often collect threat intelligence manually through reports, emails, or internal tools.  
This process is slow and difficult to scale. There is no easy way to collect threat reports from multiple sources and automatically validate them.

We need a system where users can submit threat indicators through a simple interface and the system can automatically:

- collect the reports
- validate them
- store them
- share verified intelligence with other users

Google Forms can be used as a lightweight submission interface for collecting threat intelligence data.

## Proposed System

The system will use Google Forms to collect threat intelligence submissions such as:

- malicious IP addresses
- suspicious domains
- malware hashes
- phishing URLs

The submitted data will be processed automatically by a backend service.

The backend will:

1. fetch responses from Google Forms
2. validate the threat indicators using an AI model
3. store verified indicators in a database
4. expose an API for retrieving verified threat intelligence

The system will also maintain logs for all submissions and validations.

## Functional Requirements

1. Users must be able to submit threat indicators through Google Forms.
2. The system must automatically fetch new form responses.
3. The system must validate threat indicators using an AI module.
4. The system must store validated threats in a database.
5. The system must expose APIs to access verified threat intelligence.
6. The system must log all submissions and validation results.

## Non-Functional Requirements

- The system should process submissions automatically.
- The system should support containerized deployment.
- The system should allow monitoring and logging.
- The system should be modular and scalable.

## Expected Output

- A working system that collects threat intelligence from Google Forms
- AI validation of threat indicators
- Database of validated threats
- API for accessing threat intelligence
- Containerized deployment

## Project Structure

The project will be organized as follows:

threat-intelligence-platform/

README.md  
PROJECT_REQUIREMENTS.md  
TECH_STACK.md  
TODO.md  

docker/  
    Dockerfile  
    docker-compose.yml  

backend/  
    app/  
        main.py  
        config.py  

        api/  
            routes_threats.py  
            routes_validation.py  

        services/  
            sheets_service.py  
            validation_service.py  
            threat_service.py  

        models/  
            threat_model.py  

        database/  
            db.py  
            schema.py  

        utils/  
            logger.py  

ml/  
    train_model.py  
    model.pkl  

monitoring/  
    prometheus.yml