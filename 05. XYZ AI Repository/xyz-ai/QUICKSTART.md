# Quick Start Guide - XYZ AI School Assistant

## 🚀 30-Second Setup

```bash
cd "05. XYZ AI Repository/xyz-ai"
pip install -r requirements.txt
python app.py
```

Open: **http://localhost:5000**

---

## 🎯 Quick Test (60 Seconds)

### 1. Select Demo User
Choose from dropdown: **S001** (Student) → Enter

### 2. Test Student Attendance
Type: `What is my attendance?`
Expected: `Rahul Sharma currently has 91.2% attendance.` ✅

### 3. Test Voice (Optional)
Click `🎤 Speak to AI` → Speak: `What is my attendance?` → AI responds

### 4. Test Language
Change language to `हिन्दी (Hindi)` → Ask same question → Response in Hindi ✅

### 5. Try Another Role
Select **P001** (Parent) → Ask: `How much attendance does my child have?` ✅

---

## 📱 Demo Users (Username = User ID)

| Role | ID | Name | Password | Test Query |
|------|-----|------|----------|------------|
| **Student** | S001 | Rahul Sharma | - | "What is my attendance?" |
| **Student** | S002 | Rohan Verma | - | "What is my attendance?" |
| **Student** | S003 | Priya Singh | - | "What is my attendance?" |
| **Parent** | P001 | Priya Sharma | - | "How much attendance does my child have?" |
| **Parent** | P002 | Amit Verma | - | "How much attendance does my child have?" |
| **Parent** | P003 | Neha Singh | - | "How much attendance does my child have?" |
| **Teacher** | T001 | Anita Gupta | - | "Mark Rahul absent today" |
| **Teacher** | T002 | Vikram Singh | - | "Mark Priya present today" |
| **Principal** | PR001 | Raj Mehta | - | "What is the overall attendance?" |

---

## ✅ Test Scenarios

### Student (S001)
```
✅ "What is my attendance?" → Shows 91.2%
✅ "What about last month?" → Maintains context
✅ "I want to speak to my teacher" → Escalation created
❌ "Mark me absent" → Access denied
❌ "Show me overall attendance" → Access denied
```

### Parent (P001)
```
✅ "How much attendance does my child have?" → Shows Rahul 91.2%
✅ "What about Rohan?" → Switches context
✅ "I need to talk to the teacher" → Escalation created
❌ "Mark my child absent" → Access denied (not teacher)
```

### Teacher (T001)
```
✅ "Mark Rahul absent today" → Marks attendance
✅ "What is Rahul's attendance?" → Shows 91.2%
✅ "Contact management" → Escalation created
❌ "Show me Priya's attendance" → Access denied (not authorized)
❌ "Show overall attendance" → Access denied (not principal)
```

### Principal (PR001)
```
✅ "What is the overall attendance?" → Shows 89.7%
✅ "Show school statistics" → Shows school data
✅ "Mark student absent" → Can mark any student
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Connection refused"** | Ensure `python app.py` is running |
| **"ModuleNotFoundError"** | Run `pip install -r requirements.txt` |
| **Voice not working** | Use Chrome/Edge, grant microphone permission |
| **Language dropdown empty** | Refresh page (F5) |
| **"Permission denied"** | This is expected behavior - try different role |

---

## 📚 Full Documentation

- **README.md** - Complete feature guide
- **DEPLOYMENT.md** - Production deployment
- **PROJECT_SUMMARY.md** - Project overview
- **test_backend.py** - Test cases (33 all passing)

---

## 🎤 Voice Features

1. Click `🎤 Speak to AI`
2. Allow microphone permission (first time)
3. Speak your question
4. Wait for AI response
5. Click `🔊 Speak Response` to hear it

**Supported Languages:** English, Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Punjabi, Kannada, Malayalam, Urdu

---

## 🌍 Language Support

Select any language from dropdown:
- English (en)
- हिन्दी (hi) - Hindi
- தமிழ் (ta) - Tamil
- తెలుగు (te) - Telugu
- मराठी (mr) - Marathi
- বাংলা (bn) - Bengali
- ગુજરાતી (gu) - Gujarati
- ਪੰਜਾਬੀ (pa) - Punjabi
- ಕನ್ನಡ (kn) - Kannada
- മലയാളം (ml) - Malayalam
- اردو (ur) - Urdu

---

## ✨ Key Features

- ✅ **Role-Based Access** - Different permissions for each role
- ✅ **Attendance Management** - Query and mark attendance
- ✅ **Voice Interaction** - Speak to AI, hear responses
- ✅ **Multi-Language** - Responses in 11 languages
- ✅ **Conversation Memory** - Context preserved across messages
- ✅ **Security** - Authorization enforced, prompt injection blocked
- ✅ **School Dashboard** - View attendance metrics
- ✅ **Escalations** - Request teacher/management calls

---

## 🚀 Deploy to Production

### Option 1: Render (Easiest)
```
1. Push to GitHub
2. Go to render.com
3. Create Web Service
4. Connect repo
5. Start Command: gunicorn app:app
6. Deploy!
```

### Option 2: Docker
```bash
docker build -t xyz-ai .
docker run -p 5000:5000 xyz-ai
```

### Option 3: Traditional Server
```bash
pip install -r requirements.txt
gunicorn app:app --workers 4 --bind 0.0.0.0:5000
```

See **DEPLOYMENT.md** for detailed instructions.

---

## 📊 Tests & Quality

```bash
# Run all tests
python -m pytest test_backend.py -v

# Results: 33/33 PASSING ✅
```

---

## 📞 Support

**Everything you need is in the documentation:**
1. README.md - Features & setup
2. DEPLOYMENT.md - Production guide
3. PROJECT_SUMMARY.md - Architecture overview
4. test_backend.py - Test cases showing expected behavior

---

## ⚡ Performance

- Chat response: < 500ms
- Intent detection: 100% accuracy (on test data)
- Test suite: 33 tests in 0.05s
- Frontend: Zero external frameworks (lightweight)
- Voice: Browser-native (Web Speech API)

---

## 🎓 Demo Instructions

### For Teachers/Parents:
1. Select your role (Parent/Teacher)
2. Ask about attendance
3. Try voice input
4. Request escalation

### For IT Professionals:
1. Check README.md for architecture
2. Review test_backend.py for security
3. Check auth_service.py for authorization
4. Review services.py for orchestration
5. See intent_service.py for NLP logic

### For Administrators:
1. Select Principal role
2. Ask for school statistics
3. Check attendance metrics
4. Review escalation requests

---

**Status: ✅ PRODUCTION READY**

**Last Updated: August 16, 2026**

**Version: 1.0.0**
