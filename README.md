# Human-Like AI School Assistant

XYZ AI is a school assistant prototype that behaves like a real human support assistant for students, parents, teachers, and school management. It supports attendance queries, teacher actions, escalation to school staff, and role-based access control in a mock ERP environment.

## Project Overview

This repository is designed as a demonstration project for an Applied AI school workflow. The application acts like a real school assistant and includes:

- Student attendance queries
- Parent child-attendance queries
- Teacher attendance marking
- Principal school attendance summary
- Authorization and security checks
- Escalation to teacher or management
- Chat-based interaction and browser voice input

## Repository Structure

- 01. Student Repository/student-portal
- 02. Parent Repository/parent-portal
- 03. Management Repository/management-portal
- 04. Staff Repository/staff-portal
- 05. XYZ AI Repository/xyz-ai

## Main Features

- Role-based assistant behavior
- Natural language processing for school queries
- Mock API-style service layer
- Safety filters for prompt injection and unauthorized data access
- Attendance update workflow for teachers
- Support request escalation to human staff
- Browser-based chat UI with voice capability

## Local Setup

```bash
cd "05. XYZ AI Repository/xyz-ai"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python app.py
```

Open in the browser:

- http://127.0.0.1:5000/

## Example Use Cases

- Student: "What is my attendance?"
- Parent: "How much attendance does my child have?"
- Teacher: "Mark Rahul absent today."
- Principal: "What is the overall attendance?"
- Parent: "I am not satisfied. I want to talk to my child's teacher."

## Deployment Guide

### Option 1: Deploy on Render

1. Push the project to GitHub.
2. Create a new Web Service on Render.
3. Connect the GitHub repository.
4. Set the root directory to:
   - `05. XYZ AI Repository/xyz-ai`
5. Use the runtime as Python.
6. Set build command:
   ```bash
   pip install -r requirements.txt
   ```
7. Set start command:
   ```bash
   gunicorn app:app
   ```
8. Add environment variables if needed.
9. Deploy the service.

### Option 2: Deploy on Railway / Render / VPS

1. Install Python and pip on the server.
2. Clone the repository.
3. Go to the app directory.
4. Create virtual environment.
5. Run:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
6. Use a reverse proxy like Nginx if needed.
7. Expose the app through port 5000 or configure a production WSGI server.

### Production Notes

- For production, replace the Flask dev server with Gunicorn or uWSGI.
- Use environment variables for secrets and config.
- Add authentication and real school ERP integration for real deployment.

## Legal / Demo Note

This project is a mock educational AI demo and is intended for learning, prototyping, and presentation use. It is not connected to a live school database or real student record system.
