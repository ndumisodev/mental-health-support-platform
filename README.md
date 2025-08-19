# Mental Health Counselling API

## Project Overview

This is an online counselling API designed to address the problem of limited access to affordable, timely, and stigma-free mental health support in South Africa. The platform simplifies the process of finding, booking, and managing counselling sessions for clients, while providing counsellors with the necessary tools to manage their appointments, availability, and client communication.

The primary goal is to create a secure, accessible, and user-friendly platform that connects clients with qualified mental health professionals.

## Key Features

### MVP
- **Authentication & Roles**
  - JWT-based authentication with Djoser
  - Roles: Client, Counselor, Admin
- **Profiles**
  - Counselor: specialties, languages, availability, bio, level
  - Client: profile picture, bio, address, preferences
- **Session Booking**
  - Book, confirm, cancel, and complete sessions
  - Integration with Google Calendar API (planned)
- **Messaging**
  - Real-time chat with Django Channels/WebSockets
  - Anonymous mode for stigma-sensitive users
- **Emergency Support**
  - SADAG/Lifeline hotline API integration
- **Audit Logging**
  - Track user actions for accountability and compliance

### Stretch Goals
- AI-powered triage questionnaire (basic NLP)
- SMS reminders via Twilio
- Multilingual support

---

## 🗄 Database Schema

The database is designed using **DBML** with clear entity relationships.

![Database Schema](docs/db_schema.png)

**Key Tables:**
- `User` → Stores core user details and roles
- `CounselorProfile` / `ClientProfile` → Extended profile info
- `Session` → Session booking details
- `ChatRoom` / `Message` → Real-time communication
- `Review` → Feedback from clients
- `EmergencyHotline` → Hotline contact info
- `AuditLog` → Action tracking

---

## 📍 API Endpoints

### Authentication
- `POST /api/auth/register` → Register new user
- `POST /api/auth/login` → Login (JWT)
- `GET /api/users/:id` → Get current user profile

### Counselors
- `GET /api/counselors` → List all counselors (with filters)
- `GET /api/counselors/{id}` → Get counselor profile
- `POST /api/counselors/{id}/reviews` → Add review

### Clients
- `GET /api/clients/{id}` → Get client profile
- `PUT /api/clients/{id}` → Update client profile

### Sessions
- `POST /api/sessions` → Book a session
- `GET /api/sessions` → List sessions
- `PUT /api/sessions/{id}` → Update session status

### Messaging
- `POST /api/chatrooms` → Create chatroom
- `GET /api/chatrooms/{id}/messages` → Get messages
- `POST /api/chatrooms/{id}/messages` → Send message

### Emergency Hotline
- `GET /api/hotlines` → List hotlines

---

## 🛠 Tech Stack
- **Backend:** Django REST Framework, Django Channels
- **Auth:** Djoser + JWT
- **Database:** mySQL
- **APIs:** Google Calendar API, SADAG Hotline API, Twilio (planned)
- **Real-time:** WebSockets
- **Deployment:** Docker (planned)

---

## 📋 User Stories & Progress
User stories are documented in the GitHub Issues backlog, including:
- Authentication (Register/Login)
- Profile Management
- Session Booking
- Reviews
- Chat
- Emergency Requests
- Audit Logs

---

## 🖥 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Virtual environment tool (venv, pipenv, poetry)

### Steps
```bash
# Clone the repository
git clone https://github.com/yourusername/online-counselling-api.git
cd online-counselling-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Update DB credentials and API keys in .env

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
