# SkillForge - EdTech Platform PRD

## Original Problem Statement
Build a hackathon-ready, scalable EdTech web application that helps college students gain real technical skills, interview confidence, and placement readiness for high-paying roles (SDE, Data Analyst, Data Scientist, ML Engineer).

## User Personas
1. **College Student (Primary)**: Preparing for tech placements, needs structured DSA learning
2. **Career Switcher**: Learning programming fundamentals for SDE roles
3. **Data Aspirant**: Targeting Data Analyst/Scientist/ML Engineer positions

## Core Requirements (Static)
- Domain-based authentication (college email validation)
- Role selection (SDE, Data Analyst, Data Scientist, ML Engineer)
- Task-based learning system with points & levels
- BRO AI mentor (text mode) using OpenAI GPT-5.2
- Built-in Python code editor
- Progress tracking and profile management

## What's Been Implemented (Phase 1) - December 2025

### Authentication System
- Email + password registration/login
- JWT token-based sessions (72hr expiry)
- Educational domain validation (.edu, .ac.in) + demo mode
- Secure password hashing (bcrypt)

### Role Selection
- One-time mandatory role selection after signup
- 4 roles: SDE, Data Analyst, Data Scientist, ML Engineer
- Role persists across sessions, editable later

### DSA Track - Arrays Module
- 5 coding tasks (Two Sum, Max Subarray, Rotate Array, Contains Duplicate, Product Except Self)
- 2 concept explanation tasks
- 1 debugging task
- Each task includes: description, starter code, hints, solution explanation
- Points: Easy (10), Medium (20-25), Hard (30)

### BRO AI Mentor
- OpenAI GPT-5.2 integration via Emergent LLM key
- Friendly senior engineer personality
- Guides without spoon-feeding answers
- Context-aware (knows current task)
- Chat history stored in MongoDB

### Code Editor
- Built-in Python editor with syntax highlighting
- Run code (mocked execution in demo)
- Submit for points
- Output panel for results

### Points & Levels System
- Beginner: 0-49 points
- Intermediate: 50-99 points
- Advanced: 100+ points
- Points awarded on first task completion

### UI/UX
- Light neutral theme (Slate/Blue palette)
- Manrope (headings), Inter (body), JetBrains Mono (code)
- Clean, professional EdTech dashboard design
- No flashy gradients or AI-styled layouts

## Tech Stack
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI (Python)
- Database: MongoDB
- AI: OpenAI GPT-5.2 via Emergent Integrations

## Prioritized Backlog

### P0 (Critical - Next Sprint)
- [ ] Real Python code execution (Pyodide integration)
- [ ] Test case validation for task submissions
- [ ] More Arrays problems (10-15 total)

### P1 (High Priority)
- [ ] Strings module for DSA track
- [ ] Linked Lists module
- [ ] Weekly activity tracking (GitHub, LinkedIn integration)
- [ ] Resume builder/uploader

### P2 (Medium Priority)
- [ ] Data Analyst track (SQL module)
- [ ] Data Scientist track (Statistics module)
- [ ] ML Engineer track (MLOps basics)
- [ ] Leaderboard system
- [ ] Study groups/community features

### P3 (Future Enhancements)
- [ ] BRO voice mode
- [ ] Mock interview system
- [ ] Company-specific preparation tracks
- [ ] Mobile app version

## API Endpoints
- POST /api/auth/register
- POST /api/auth/login
- GET /api/users/profile
- PUT /api/users/role
- GET /api/skills/dsa/arrays
- GET /api/skills/dsa/arrays/{task_id}
- POST /api/tasks/{task_id}/submit
- POST /api/bro/chat
- GET /api/bro/history
- POST /api/code/run

## Database Collections
- users: User profiles, progress, points
- chat_history: BRO conversation logs

## Environment Variables
- MONGO_URL: MongoDB connection string
- JWT_SECRET: Token signing key
- EMERGENT_LLM_KEY: Universal key for OpenAI GPT-5.2
