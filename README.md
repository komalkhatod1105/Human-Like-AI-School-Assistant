# Human-Like AI School Assistant

XYZ AI is a mock, production-style school assistant for students, parents, teachers, and school leadership. The project demonstrates role-aware AI behavior, backend authorization, attendance workflows, escalation requests, and a polished chat UI without connecting to a real ERP or student database.

## Overview

This repository contains a demo school assistant with:

- Student attendance lookup
- Parent child-attendance lookup
- Teacher attendance marking with authorization checks
- Principal analytics access for school-wide metrics
- Prompt injection filtering and security boundaries
- Mock support/escalation requests
- Role-based session handling for demo authentication
- Browser-based chat UI and optional voice input

## Architecture

- Frontend: Flask templates + JavaScript in the browser
- Backend: Flask app with service-layer business logic
- Domain logic: attendance, permissions, escalation, intent routing
- Mock data: in-memory school records and relationships
- Security model: role-based authorization enforced in the backend service layer

## Tech Stack

- Python 3.12+
- Flask 3.0
- Gunicorn for Render-compatible production startup
- Pytest for automated backend tests

## Repository Structure

- `01. Student Repository/`
- `02. Parent Repository/`
- `03. Management Repository/`
- `04. Staff Repository/`
- `05. XYZ AI Repository/xyz-ai/`

Inside the app folder:

- `app.py` — Flask app factory and routes
- `services.py` — AI orchestration, intent detection, authorization, mock API logic
- `templates/index.html` — demo web UI
- `tests/test_ai_service.py` — backend verification tests
- `tests/conftest.py` — path setup for pytest

## Local Setup

```bash
cd "05. XYZ AI Repository/xyz-ai"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python app.py
```

Open:

- http://127.0.0.1:5000/

## Run with Gunicorn

```bash
gunicorn app:app
```

This is the correct Render/production style start command for this Flask app.

## Mock Users

- Student: Rahul Sharma (`S001`)
- Parent: Priya Sharma (`P001`), child `S001`
- Teacher: Anita Gupta (`T001`), authorized for `S001`, `S002`, `S003`
- Principal: Raj Mehta (`PR001`)

## Example Scenarios

- Student: "What is my attendance?"
- Parent: "How much attendance does my child have?"
- Teacher: "Mark Rahul absent today."
- Principal: "What is the overall attendance?"
- Parent: "I want to talk to my child's teacher."

## Security Design

The project explicitly does not trust user-supplied text alone for role or permission decisions. Role and authorization are checked in the backend service layer before any attendance or analytics action is allowed.

## Role Permissions

- Student: can view own attendance only
- Parent: can view child attendance only for their own child
- Teacher: can mark attendance only for authorized students
- Principal: can view school-wide analytics

## Deployment

Render-compatible startup command:

```bash
gunicorn app:app
```

## Known Limitations

- This is a mock school assistant demo, not a production ERP integration
- Voice features depend on browser support for Web Speech APIs
- Conversation memory is session-scoped and lightweight for demo use

## Demo Note

This project is intended for educational and prototype use. It is not connected to a live school database or real student records.
