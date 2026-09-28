# REST API Reference (/api/v1)

FastAPI automatically generates interactive OpenAPI/Swagger documentation at `/docs` and ReDoc at `/redoc`.

### Authentication
- `POST /auth/login`: Authenticate with email/password, returns JWT token.
- `POST /auth/register`: Register new official profile.
- `GET /auth/me`: Current authenticated user session.
- `POST /auth/logout`: Invalidate session and log audit event.

### User Profiles
- `GET /users/me`: Current user details, department, assignment, and experience.
- `PUT /users/me`: Update profile attributes (experience, education, career goals).
- `GET /users/{id}`: Detailed user profile.

### Competency Intelligence
- `GET /competencies`: Complete framework categorized by domains (Statistical, Technical, Governance, Behavioural).
- `GET /competencies/me`: Current user's verified competency scores, proficiency levels, and evidence count.
- `GET /competencies/history`: Historical audit trail of score improvements and delta reasons.
- `GET /competencies/roles/{designation_id}`: Statutory requirements for specified role.

### Skill Gap Engine
- `GET /skill-gaps/me`: Comprehensive gap report (`gap = required - current`), priority weights, and role readiness index.
- `POST /skill-gaps/career-compare`: Compare current skills with target role requirements (e.g. Statistical Officer -> Senior Statistical Officer).

### Assessment & Quiz Engine
- `GET /assessments`: Catalogue of active assessments.
- `GET /assessments/{id}`: Assessment questions and options.
- `POST /assessments/{id}/start`: Initiates an assessment attempt.
- `POST /assessments/{id}/submit`: Submits answers, scores objectively, and triggers deterministic competency updates.

### Recommendations & Learning Paths
- `GET /recommendations/me`: Multi-factor ranked recommendations from iGOT and NSSTA with explainable reasons.
- `POST /recommendations/generate`: Forces re-ranking of candidates.
- `GET /learning/paths/me`: 5-Stage personalized learning path.
- `POST /learning/paths/recalculate`: Recalculates curriculum based on latest scores.
- `GET /learning/resources`: Filterable resource library.
- `POST /learning/resources/{id}/enroll`: Enrolls in module.

### AI Tutor & RAG
- `POST /tutor/chat`: Grounded RAG conversational endpoint with source citations.
- `GET /tutor/sessions`: Previous discussion sessions.
- `GET /tutor/sessions/{id}`: Transcript with citation metadata.

### Document Management & RAG
- `POST /documents/upload`: Uploads and indexes official texts.
- `GET /documents`: Lists ingested corpus.
- `GET /documents/{id}`: Document chunk explorer.

### AI Question Studio
- `POST /quiz/generate`: Generates structured MCQs from official material.
- `GET /quiz/questions`: Questions awaiting trainer review.
- `POST /quiz/questions/{id}/review`: Approve, reject, edit, or publish questions.

### Admin & Analytics
- `GET /admin/dashboard`: Executive metrics and critical gap counts.
- `GET /admin/heatmap`: Matrix of competencies vs divisions.
- `GET /admin/departments`: Divisional readiness comparison.
- `GET /admin/future-skills`: Emerging 2026–2030 skill forecasts.
- `GET /admin/audit-logs`: Immutable security ledger.

### Integrations
- `GET /integrations/status`: Status of iGOT and NSSTA provider adapters.
- `POST /integrations/igot/sync`: Syncs mock or live iGOT courses.
- `POST /integrations/nssta/sync`: Syncs NSSTA academy calendar.
