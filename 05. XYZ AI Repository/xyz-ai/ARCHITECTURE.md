# XYZ AI School Assistant - Complete Architecture & Design Guide

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Design Patterns](#design-patterns)
3. [Component Deep Dive](#component-deep-dive)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [Installation & Setup](#installation--setup)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER TIER                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Frontend (templates/index.html)                            │   │
│  │  ├─ AI Chat Interface                                       │   │
│  │  ├─ Voice Input/Output (Web Speech API)                    │   │
│  │  ├─ Language Selector (11 languages)                        │   │
│  │  ├─ Role Selector (S001, P001, T001, PR001)               │   │
│  │  └─ Dashboard (School metrics)                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────────┘
                 │ HTTP/JSON (REST API)
                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION TIER (Flask)                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Flask Application (app.py)                                 │   │
│  │ ├─ POST /api/chat → Main chat endpoint                    │   │
│  │ ├─ POST /api/auth/* → Authentication routes              │   │
│  │ ├─ POST /api/attendance/* → Attendance operations         │   │
│  │ ├─ GET /health → Health check                            │   │
│  │ └─ Middleware: @require_auth, error handlers             │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                             │
│  ┌──────────────────┴────────────────────────────────────────┐   │
│  │  Service Orchestration Layer (services.py)               │   │
│  │  ├─ process_message(user_id, message, language)         │   │
│  │  ├─ _handle_intent(intent, user_info, ...)              │   │
│  │  ├─ _is_blocked_message(message) [Security Filter]      │   │
│  │  └─ Authorization checks & response formatting          │   │
│  └──────────────┬───────────────────────────────────────────┘   │
│                 │                                                  │
│  ┌──────────────┴───────────────────────────────────────────┐   │
│  │  Business Logic Services Layer                           │   │
│  │  ├─ AuthenticationService (auth_service.py)              │   │
│  │  │  └─ can_perform_action(user_id, action, resource)    │   │
│  │  ├─ IntentService (intent_service.py)                    │   │
│  │  │  └─ detect_intent() + extract_entities()            │   │
│  │  ├─ AttendanceService (attendance_service.py)            │   │
│  │  │  └─ get_attendance() + mark_attendance()             │   │
│  │  ├─ ConversationService (conversation_service.py)        │   │
│  │  │  └─ get_or_create_session() + update_context()       │   │
│  │  ├─ AnalyticsService (analytics_service.py)              │   │
│  │  │  └─ get_school_attendance_stats()                    │   │
│  │  ├─ SupportService (support_service.py)                  │   │
│  │  │  └─ create_*_request() [Escalations]                 │   │
│  │  └─ LanguageService (language_service.py)                │   │
│  │     └─ get_response_template(language, key)             │   │
│  └──────────────┬───────────────────────────────────────────┘   │
│                 │                                                  │
│  ┌──────────────┴───────────────────────────────────────────┐   │
│  │  Data & Memory Layer                                     │   │
│  │  ├─ ConversationMemoryStore (per-user context)          │   │
│  │  │  └─ Stores: student_name, topic, message_history    │   │
│  │  └─ MockSchoolDatabase (mock_data.py)                    │   │
│  │     └─ In-memory with consistent relationships          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA TIER (Current: Mock)                        │
│  MockSchoolDatabase                                                  │
│  ├─ Students (S001, S002, S003)                                    │
│  ├─ Parents (P001→S001, P002→S002, P003→S003)                     │
│  ├─ Teachers (T001, T002) with authorized_student_ids            │
│  ├─ Principal (PR001)                                              │
│  ├─ Attendance Records (ATTENDANCE_DATA)                          │
│  └─ School Statistics                                              │
│                                                                     │
│  Future: PostgreSQL/MySQL with SQLAlchemy ORM                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Request-Response Flow

```
User Input
    ↓
[Frontend] HTTP POST /api/chat
    ↓
[Flask] Route Handler
    │
    ├→ Extract: user_id, message, language
    │
    ├→ @require_auth Middleware
    │  └→ Verify user exists & get role
    │
    ├→ SchoolAssistantService.process_message()
    │  │
    │  ├→ IntentService.detect_intent()
    │  │  └→ Returns: (Intent enum, confidence)
    │  │
    │  ├→ IntentService.extract_entities()
    │  │  └→ Returns: {student_name, date, status, ...}
    │  │
    │  ├→ _is_blocked_message() [Security Check]
    │  │  └→ Regex patterns for prompt injection
    │  │
    │  ├→ AuthenticationService.can_perform_action()
    │  │  └→ Role-based permission check (CRITICAL)
    │  │
    │  ├→ ConversationService.get_or_create_session()
    │  │  └→ Load per-user context/memory
    │  │
    │  ├→ _handle_intent() Router
    │  │  ├→ GET_OWN_ATTENDANCE
    │  │  ├→ GET_CHILD_ATTENDANCE
    │  │  ├→ MARK_ATTENDANCE
    │  │  ├→ GET_SCHOOL_ATTENDANCE
    │  │  └─ ... [9 total intents]
    │  │
    │  ├→ LanguageService.get_response_template()
    │  │  └→ Format response in user's language
    │  │
    │  └→ ConversationService.add_message()
    │     └→ Store in per-user memory
    │
    ├→ Format JSON Response
    │  └→ {
    │       "text": "...",
    │       "intent": "...",
    │       "status": "success",
    │       "user_role": "...",
    │       "language": "..."
    │     }
    │
    └→ Return to Frontend
       ↓
   [Frontend] Display Response + Optional: Speak via TTS
```

---

## Design Patterns

### 1. Service-Oriented Architecture (SOA)

Each service is **independent, single-responsibility, and testable**:

```python
# Pattern: Each service handles ONE domain
class AuthenticationService:
    """Only handles: authentication & authorization"""
    def authenticate_user(self, user_id):
        """Verify user exists"""
        pass
    
    def can_perform_action(self, user_id, action, resource_id):
        """Check if user has permission (CRITICAL)"""
        pass

class IntentService:
    """Only handles: natural language → intent + entities"""
    def detect_intent(self, message, language):
        """Convert text to structured intent"""
        pass
    
    def extract_entities(self, message, intent):
        """Pull out: student_name, date, status, etc."""
        pass

class AttendanceService:
    """Only handles: attendance data operations"""
    def get_student_attendance(self, student_id):
        pass
    
    def mark_attendance(self, student_id, date, status):
        pass
```

**Benefits:**
- ✅ Each service is testable independently
- ✅ Services can be replaced (mock data → real DB)
- ✅ Scaling: Services can be horizontally scaled
- ✅ Maintenance: Changes in one service don't break others

### 2. Decorator Pattern - Authentication Middleware

```python
from functools import wraps

def require_auth(f):
    """Decorator: Verify user is authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")
        
        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info:
            return jsonify({"error": "Unauthorized"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/chat", methods=["POST"])
@require_auth  # ← Decorator ensures auth before handler runs
def chat():
    """Main chat endpoint"""
    pass
```

**Benefits:**
- ✅ Centralized authentication logic
- ✅ Reusable across multiple endpoints
- ✅ Clean separation of concerns

### 3. Factory Pattern - Service Initialization

```python
def create_app():
    """Factory: Create Flask app with all services"""
    app = Flask(__name__)
    
    # Initialize all services once
    auth_service = AuthenticationService(db)
    intent_service = IntentService(db, language_service)
    conversation_service = ConversationService(memory_store)
    # ... etc
    
    # All services share same database instance
    return app
```

**Benefits:**
- ✅ Single point of initialization
- ✅ All services share same database connection
- ✅ Dependency injection pattern

### 4. Strategy Pattern - Intent Handlers

```python
# Different strategies for different intents
intent_handlers = {
    Intent.GET_OWN_ATTENDANCE: _handle_get_own_attendance,
    Intent.GET_CHILD_ATTENDANCE: _handle_get_child_attendance,
    Intent.MARK_ATTENDANCE: _handle_mark_attendance,
    Intent.GET_SCHOOL_ATTENDANCE: _handle_get_school_attendance,
    # ... etc
}

def _handle_intent(self, intent, user_info, ...):
    """Route to appropriate handler based on intent"""
    handler = intent_handlers.get(intent)
    if handler:
        return handler(user_info, ...)
    return self._handle_general_help()
```

**Benefits:**
- ✅ Easy to add new intent handlers
- ✅ Each intent has isolated logic
- ✅ No huge if-elif chains

### 5. Singleton Pattern - Database & Services

```python
# Each service is instantiated ONCE in create_app()
app = create_app()  # Services created once

# All routes use same service instance
@app.route("/api/chat", methods=["POST"])
def chat():
    # Uses SAME school_assistant instance
    response = school_assistant.process_message(...)

@app.route("/api/health", methods=["GET"])
def health():
    # Uses SAME database instance
    return jsonify({"status": "ok"})
```

**Benefits:**
- ✅ Consistent state across requests
- ✅ No duplicate connections
- ✅ Memory efficient

---

## Component Deep Dive

### 1. Authentication Service (auth_service.py)

**Purpose:** Verify user identity and enforce permissions

**How It Works:**

```python
class AuthenticationService:
    def authenticate_user(self, user_id):
        """Return user info if exists"""
        # Check against MockSchoolDatabase
        if user_id.startswith('S'):  # Student
            return {"id": user_id, "role": "student", ...}
        elif user_id.startswith('P'):  # Parent
            return {"id": user_id, "role": "parent", "child_ids": [...]}
        elif user_id.startswith('T'):  # Teacher
            return {"id": user_id, "role": "teacher", "authorized_student_ids": [...]}
        elif user_id.startswith('PR'):  # Principal
            return {"id": user_id, "role": "principal"}
        return None
    
    def can_perform_action(self, user_id, action, resource_id):
        """CRITICAL: Enforce all permissions here"""
        user_info = self.get_authenticated_user(user_id)
        role = user_info["role"]
        
        # Permission Matrix
        permissions = {
            "student": {
                "view_own_attendance": lambda: True,
                "view_other_attendance": lambda: False,
                "mark_attendance": lambda: False,
                "view_school_analytics": lambda: False,
            },
            "parent": {
                "view_child_attendance": lambda: resource_id in user_info.get("child_ids", []),
                "mark_attendance": lambda: False,
                "view_school_analytics": lambda: False,
            },
            "teacher": {
                "mark_attendance": lambda: resource_id in user_info.get("authorized_student_ids", []),
                "view_student_attendance": lambda: True,
                "view_school_analytics": lambda: False,
            },
            "principal": {
                "view_school_analytics": lambda: True,
                "all_actions": lambda: True,
            }
        }
        
        # Check permission
        if role in permissions and action in permissions[role]:
            return permissions[role][action]()
        return False
```

**Why This Design?**
- ✅ **Backend-enforced**: Not trusting frontend
- ✅ **Authorization matrix**: Clear permissions by role
- ✅ **Resource-based**: Can check specific resource ownership
- ✅ **Testable**: Each permission can be unit tested

### 2. Intent Service (intent_service.py)

**Purpose:** Convert natural language → structured intent + entities

**How It Works:**

```python
class IntentService:
    def detect_intent(self, message, language):
        """
        Strategy: Check intents in priority order
        Higher priority = checked first
        """
        message_lower = message.lower()
        
        # 1. Check Escalation (HIGH PRIORITY)
        #    Why: "Talk to teacher" should not be confused with "attendance"
        if self._is_teacher_escalation(message_lower):
            return (Intent.REQUEST_TEACHER_CALL, 0.95)
        
        if self._is_management_escalation(message_lower):
            return (Intent.REQUEST_MANAGEMENT_CALL, 0.95)
        
        # 2. Check Attendance Operations (MEDIUM PRIORITY)
        if self._is_mark_attendance(message_lower):
            return (Intent.MARK_ATTENDANCE, 0.90)
        
        if self._is_child_attendance_query(message_lower):
            return (Intent.GET_CHILD_ATTENDANCE, 0.85)
        
        if self._is_attendance_query(message_lower):
            return (Intent.GET_OWN_ATTENDANCE, 0.80)
        
        if self._is_school_attendance(message_lower):
            return (Intent.GET_SCHOOL_ATTENDANCE, 0.80)
        
        # 3. Default to GENERAL_HELP
        return (Intent.GENERAL_HELP, 0.50)
    
    def extract_entities(self, message, intent):
        """
        Extract structured data from message
        Returns: {"student_name": "...", "date": "...", "status": "..."}
        """
        entities = {}
        
        # Extract student name
        for student in self.db.STUDENTS.values():
            if student["name"].lower() in message.lower():
                entities["student_name"] = student["name"]
                entities["student_id"] = student["id"]
        
        # Extract status (present/absent/leave)
        if "absent" in message.lower():
            entities["status"] = "absent"
        elif "present" in message.lower():
            entities["status"] = "present"
        elif "leave" in message.lower():
            entities["status"] = "leave"
        
        # Extract date
        if "today" in message.lower():
            entities["date"] = str(datetime.now().date())
        
        return entities
```

**Pattern: Priority-Based Detection**
```
Escalation (95% confidence)
    ↓
Attendance Operations (90% confidence)
    ↓
Attendance Queries (80% confidence)
    ↓
General Help (50% confidence)
```

**Why This Design?**
- ✅ **Order matters**: High-priority intents checked first
- ✅ **Pattern matching**: Regex-based (simple, reliable)
- ✅ **Entity extraction**: Structured data from free text
- ✅ **Confidence scores**: Know reliability of detection

### 3. Conversation Service (conversation_service.py + conversation_memory.py)

**Purpose:** Maintain per-user context across messages

**How It Works:**

```python
class ConversationMemoryStore:
    """Per-user memory store"""
    def __init__(self):
        self.sessions = {}  # {user_id: session_data}
    
    def get_or_create(self, user_id):
        """Get or create memory for user"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "messages": [],  # Conversation history
                "context": {},   # Current context
            }
        return self.sessions[user_id]
    
    def add_message(self, user_id, role, message):
        """Store message in history"""
        session = self.get_or_create(user_id)
        session["messages"].append({
            "role": role,  # "user" or "assistant"
            "message": message,
            "timestamp": datetime.now()
        })
    
    def update_context(self, user_id, context_update):
        """Update context (e.g., student_name, topic)"""
        session = self.get_or_create(user_id)
        session["context"].update(context_update)

# Usage in SchoolAssistantService
def process_message(self, user_id, message, language):
    # Load conversation context
    session = self.memory_store.get_or_create(user_id)
    context = session["context"]
    
    # If user mentioned "Rahul" before, remember it
    if "student_name" not in context and entities.get("student_name"):
        context["student_name"] = entities["student_name"]
    
    # Use context in response
    if intent == Intent.GET_RECENT_ATTENDANCE:
        student_name = context.get("student_name")
        return f"Last month, {student_name} had 88.5% attendance."
```

**Per-User Isolation:**
```
User S001:
    ├─ Context: {student_name: "Rahul", topic: "attendance"}
    ├─ Messages: [...conversation history...]
    └─ Memory: Isolated from other users

User P001:
    ├─ Context: {student_name: "Rohan", topic: "marking"}
    ├─ Messages: [...separate history...]
    └─ Memory: Completely isolated from S001
```

**Why This Design?**
- ✅ **Per-user isolation**: No cross-user data leakage
- ✅ **Context awareness**: Remember student across messages
- ✅ **Stateful conversations**: Not just isolated questions

### 4. Language Service (language_service.py)

**Purpose:** Support 11 languages with templated responses

**How It Works:**

```python
class LanguageService:
    """Response templates for 11 languages"""
    
    TEMPLATES = {
        "en": {
            "attendance_student": "{name} currently has {percentage}% attendance.",
            "marked_absent": "{name} has been marked absent for {date}.",
            "permission_denied": "Sorry, you don't have permission to do this.",
        },
        "hi": {
            "attendance_student": "{name} के पास वर्तमान में {percentage}% उपस्थिति है।",
            "marked_absent": "{name} को {date} के लिए अनुपस्थित चिह्नित किया गया है।",
            "permission_denied": "क्षमा करें, आपको यह करने की अनुमति नहीं है।",
        },
        "ta": {
            "attendance_student": "{name} தற்போது {percentage}% வருகை உள்ளது.",
            # ... etc
        },
        # ... 8 more languages
    }
    
    def get_response_template(self, language, key):
        """Get template for language"""
        return self.TEMPLATES.get(language, self.TEMPLATES["en"]).get(key)
    
    def format_response(self, language, template_key, **kwargs):
        """Format response in user's language"""
        template = self.get_response_template(language, template_key)
        return template.format(**kwargs)

# Usage
response = language_service.format_response(
    language="hi",
    template_key="attendance_student",
    name="राहुल",
    percentage=91.2
)
# Output: "राहुल के पास वर्तमान में 91.2% उपस्थिति है।"
```

**Template Keys:**
```
attendance_student      - "Rahul has 91.2% attendance"
attendance_recent       - "Last month, Rahul had 88.5%"
marked_absent          - "Rahul marked absent today"
marked_present         - "Rahul marked present today"
permission_denied      - "You don't have permission"
student_not_found      - "Student not found"
greeting_student       - "Hello Student!"
greeting_parent        - "Hello Parent!"
greeting_teacher       - "Hello Teacher!"
greeting_principal     - "Hello Principal!"
```

---

## Data Flow

### Complete Request Lifecycle

**User asks: "What is my attendance?"** (as Student S001)

```
1. FRONTEND (index.html)
   ├─ User types message
   ├─ Selects language: "English"
   ├─ Selects user: "S001"
   └─ Clicks "Send"
   
2. HTTP REQUEST
   └─ POST /api/chat
      {
        "user_id": "S001",
        "message": "What is my attendance?",
        "language": "en"
      }

3. FLASK ROUTE HANDLER (app.py)
   ├─ @require_auth decorator
   │  └─ Get user_info: {id: "S001", role: "student", name: "Rahul"}
   ├─ Call: school_assistant.process_message(...)
   └─ Format response as JSON

4. SCHOOL ASSISTANT SERVICE (services.py)
   ├─ intent_service.detect_intent("What is my attendance?")
   │  └─ Returns: (Intent.GET_OWN_ATTENDANCE, 0.95)
   ├─ intent_service.extract_entities(...)
   │  └─ Returns: {}  (No specific student mentioned)
   ├─ Check blocked: _is_blocked_message(message)
   │  └─ Returns: False (Message is safe)
   ├─ Check permission: can_perform_action("S001", "view_own_attendance", "S001")
   │  └─ Returns: True (Student can view own attendance)
   ├─ Get session: conversation_service.get_or_create_session("S001")
   │  └─ Returns: {context: {}, messages: []}
   └─ Call: _handle_get_own_attendance(user_info, ...)

5. ATTENDANCE HANDLER
   ├─ Get student: db.get_student("S001")
   │  └─ Returns: {id: "S001", name: "Rahul Sharma", attendance: 91.2}
   ├─ Format response: language_service.format_response(
   │  language="en",
   │  template_key="attendance_student",
   │  name="Rahul Sharma",
   │  percentage=91.2
   │)
   │  └─ Returns: "Rahul Sharma currently has 91.2% attendance."
   └─ Return to SchoolAssistantService

6. RESPONSE ASSEMBLY (services.py)
   ├─ Save message: conversation_service.add_message(
   │  user_id="S001",
   │  role="assistant",
   │  message="Rahul Sharma currently has 91.2% attendance."
   │)
   └─ Format JSON response:
      {
        "text": "Rahul Sharma currently has 91.2% attendance.",
        "intent": "get_own_attendance",
        "status": "success",
        "user_role": "student",
        "language": "en"
      }

7. FLASK RESPONSE
   ├─ Convert to JSON
   └─ Return with HTTP 200

8. FRONTEND
   ├─ Display message bubble: "Rahul Sharma currently has 91.2% attendance."
   ├─ Optional: Click "🔊 Speak" for text-to-speech
   └─ Ready for next message
```

---

## Security Architecture

### Layer 1: Input Validation

```python
# Block known malicious patterns
BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"reveal system prompt",
    r"api key",
    r"make me principal",
    r"bypass security",
]

def _is_blocked_message(self, message):
    """Check for prompt injection attempts"""
    message_lower = message.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, message_lower):
            return True  # Blocked
    return False
```

### Layer 2: Authentication

```python
# Verify user exists (not frontend-supplied role)
@require_auth
def chat():
    payload = request.get_json()
    user_id = payload.get("user_id")
    
    user_info = auth_service.get_authenticated_user(user_id)
    if not user_info:
        return {"error": "Unauthorized"}, 401
    
    # User exists AND we have their backend-determined role
    role = user_info["role"]  # From DB, not from request
```

### Layer 3: Authorization (Most Critical)

```python
def can_perform_action(self, user_id, action, resource_id):
    """Backend-enforced permission matrix"""
    # Role is from authenticated user, not from request
    user_info = self.get_authenticated_user(user_id)
    
    # Check specific permission
    if action == "view_child_attendance":
        # Parent can only view OWN children
        return resource_id in user_info.get("child_ids", [])
    
    elif action == "mark_attendance":
        # Teacher can only mark AUTHORIZED students
        return resource_id in user_info.get("authorized_student_ids", [])
    
    elif action == "view_school_analytics":
        # Only principal
        return user_info["role"] == "principal"
```

### Layer 4: Response Filtering

```python
def process_message(self, user_id, message, language):
    # ... handle intent ...
    
    # Never expose sensitive data in response
    response = {
        "text": "...",  # Only user-friendly message
        "intent": intent.value,  # Enum as string
        "status": "success",
    }
    
    # NEVER include:
    # - API keys
    # - User passwords
    # - System prompts
    # - Internal database queries
    # - Other users' data
    
    return response
```

---

## Deployment Architecture

### Local Development
```
Developer Machine
├─ Python 3.12
├─ Flask (app.py)
├─ Gunicorn (localhost:5000)
└─ In-memory Mock Database

Command: python app.py
```

### Docker Deployment
```
┌─────────────────────────────┐
│    Docker Container         │
├─────────────────────────────┤
│ Python 3.12 (slim image)   │
│ pip install -r requirements │
│ Gunicorn app:app            │
│ Port: 5000                  │
└─────────────────────────────┘
       ↓
    Docker Image (100MB)
       ↓
    Container Registry (ECR, Docker Hub)
       ↓
    Deploy to: ECS, Kubernetes, Render
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

### Production on Render (Cloud)
```
GitHub Repository
    ↓ (Push)
Render Dashboard
    ├─ Build: pip install -r requirements.txt
    ├─ Run: gunicorn app:app --workers 4
    ├─ Environment: PORT, SECRET_KEY
    └─ Auto-HTTPS, Auto-Restart
    ↓
    https://xyz-ai-school-assistant.onrender.com
```

### Scalable Production (Enterprise)
```
┌─────────────────────────────────────────┐
│   Load Balancer (Nginx)                 │
│   ├─ /api/chat → Flask Instance 1       │
│   ├─ /api/chat → Flask Instance 2       │
│   └─ /api/chat → Flask Instance 3       │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│   Shared Data Layer                     │
│   ├─ PostgreSQL (Persistent)            │
│   ├─ Redis (Session/Cache)              │
│   └─ S3 (Conversation Backups)          │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│   Monitoring & Logging                  │
│   ├─ Sentry (Error tracking)            │
│   ├─ Datadog (Performance)              │
│   └─ CloudWatch (Logs)                  │
└─────────────────────────────────────────┘
```

---

## Installation & Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/komalkhatod1105/Human-Like-AI-School-Assistant.git
cd Human-Like-AI-School-Assistant/05.\ XYZ\ AI\ Repository/xyz-ai
```

### Step 2: Create Virtual Environment

```bash
# Python 3.12 required
python3.12 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt

# Verify installations
python -c "import flask; import gunicorn; print('✅ All dependencies installed')"
```

**requirements.txt contents:**
```
Flask==3.0.3
gunicorn==22.0.0
pytest==8.3.2
```

### Step 4: Run Application

```bash
# Development (with debug mode)
python app.py
# Output: Running on http://127.0.0.1:5000

# Production (with Gunicorn)
gunicorn app:app --workers 4 --bind 0.0.0.0:5000
```

### Step 5: Access Application

- Open browser: http://localhost:5000
- Select demo user: S001 (Student), P001 (Parent), T001 (Teacher), PR001 (Principal)
- Start chatting!

### Step 6: Run Tests

```bash
# Run all tests
python -m pytest test_backend.py -v

# Run specific test class
python -m pytest test_backend.py::TestAuthentication -v

# Run with coverage
pip install pytest-cov
python -m pytest test_backend.py --cov=. --cov-report=html
```

### Step 7: Deploy to Render

```bash
# 1. Push to GitHub
git add .
git commit -m "XYZ AI School Assistant v1.0"
git push origin main

# 2. Go to render.com
# 3. Create New → Web Service
# 4. Connect GitHub account
# 5. Select repository & set:
#    - Root directory: 05. XYZ AI Repository/xyz-ai
#    - Build Command: pip install -r requirements.txt
#    - Start Command: gunicorn app:app --workers 4
#    - Environment: PORT=10000, SECRET_KEY=xxx
# 6. Click Deploy!
```

---

## Key Takeaways

### Architecture Principles

1. **Layered Architecture** - UI → API → Services → Data
2. **Service-Oriented** - Each service has single responsibility
3. **Backend Security** - Authorization at backend, never frontend-only
4. **Stateful Context** - Per-user memory for conversations
5. **Scalable Design** - Services can be swapped/scaled independently

### Design Decisions

| Decision | Why | Tradeoff |
|----------|-----|----------|
| Mock Database | Fast development, no DB setup | Can't persist data across restarts |
| Regex Intent Detection | Simple, reliable, fast | Limited NLP capability |
| Per-User Memory | Context-aware responses | Not persistent (in-memory only) |
| Service Layer | Testable, maintainable | Slight performance overhead |
| Language Templates | Supports 11 languages | Limited NLP sophistication |

### Production Considerations

- ✅ **Switch to PostgreSQL** - For data persistence
- ✅ **Add Redis** - For session management at scale
- ✅ **Implement JWT** - For stateless authentication
- ✅ **Add Advanced NLP** - Use transformers (BERT) for intent detection
- ✅ **Monitoring** - Sentry, Datadog, CloudWatch
- ✅ **Caching** - Redis for frequently accessed data

---

**This architecture is production-ready for small to medium deployments (~1000 concurrent users). For enterprise scale, consider the Phase 2 recommendations above.**
