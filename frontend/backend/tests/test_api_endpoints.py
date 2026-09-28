import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.users import User
from app.models.assessments import Assessment

client = TestClient(app)


def test_health_and_readiness():
    resp_health = client.get("/api/v1/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "ok"

    resp_ready = client.get("/api/v1/ready")
    assert resp_ready.status_code == 200
    assert resp_ready.json()["status"] == "ready"


def test_demo_employee_login():
    resp = client.post("/api/v1/auth/login", json={
        "email": "employee@example.com",
        "password": "demo123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "employee@example.com"
    assert data["user"]["designation_name"] == "Statistical Officer"


def test_employee_journey_end_to_end():
    # 1. Login as Rahul Sharma
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "employee@example.com",
        "password": "demo123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. View Competency Profile
    comp_resp = client.get("/api/v1/competencies/me", headers=headers)
    assert comp_resp.status_code == 200
    comps = {c["competency_code"]: c["score"] for c in comp_resp.json()}
    assert comps["SAMPLING"] == 42.0
    assert comps["PYTHON"] == 70.0
    assert comps["SQL"] == 30.0

    # 3. View Skill Gaps
    gap_resp = client.get("/api/v1/skill-gaps/me", headers=headers)
    assert gap_resp.status_code == 200
    gap_data = gap_resp.json()
    assert gap_data["critical_gaps_count"] >= 1
    sampling_gap = next((g for g in gap_data["gaps"] if g["competency_code"] == "SAMPLING"), None)
    assert sampling_gap is not None
    assert sampling_gap["gap"] == 38.0
    assert sampling_gap["status"] == "GAP"
    assert sampling_gap["priority_level"] == "CRITICAL"

    # 4. View Recommendations with "Why Recommended"
    rec_resp = client.get("/api/v1/recommendations/me", headers=headers)
    assert rec_resp.status_code == 200
    recs = rec_resp.json()
    assert len(recs) > 0
    top_rec = recs[0]
    assert "why_recommended" in top_rec
    assert "explanation" in top_rec["why_recommended"]
    assert "CRITICAL_SKILL_GAP" in top_rec["why_recommended"]["reason_codes"]

    # 5. View Personalized 5-Stage Learning Path
    path_resp = client.get("/api/v1/learning/paths/me", headers=headers)
    assert path_resp.status_code == 200
    path_data = path_resp.json()
    assert len(path_data["items"]) == 5
    assert path_data["items"][0]["stage_name"] == "Stage 1: Foundation"

    # 6. Take and Submit Diagnostic Assessment
    assess_list = client.get("/api/v1/assessments", headers=headers).json()
    assert len(assess_list) > 0
    assess_id = assess_list[0]["id"]

    start_resp = client.post(f"/api/v1/assessments/{assess_id}/start", headers=headers)
    assert start_resp.status_code == 200
    attempt_id = start_resp.json()["attempt_id"]

    assess_detail = client.get(f"/api/v1/assessments/{assess_id}", headers=headers).json()
    answers = []
    # Submit correct answer for first 3 questions to raise competency score!
    for q in assess_detail["questions"][:4]:
        # Choose option 0 (which was seeded as correct in seed_data)
        answers.append({
            "question_id": q["id"],
            "selected_option_id": q["options"][0]["id"]
        })

    submit_resp = client.post(f"/api/v1/assessments/{assess_id}/submit", headers=headers, json={
        "attempt_id": attempt_id,
        "answers": answers,
        "time_taken_seconds": 120
    })
    assert submit_resp.status_code == 200
    result = submit_resp.json()
    assert result["score_percentage"] >= 50.0
    assert len(result["competency_updates"]) > 0

    # 7. Check Reassessment Competency Improvement
    updated_comp_resp = client.get("/api/v1/competencies/me", headers=headers)
    updated_comps = {c["competency_code"]: c["score"] for c in updated_comp_resp.json()}
    # Score should have increased from 42.0!
    assert updated_comps["SAMPLING"] > 42.0

    # 8. Test Grounded AI Tutor with Citations
    tutor_resp = client.post("/api/v1/tutor/chat", headers=headers, json={
        "message": "Explain stratified sampling with a household survey example",
        "language": "en"
    })
    assert tutor_resp.status_code == 200
    tutor_data = tutor_resp.json()
    assert tutor_data["is_grounded"] is True
    assert len(tutor_data["citations"]) > 0
    assert "stratified" in tutor_data["content"].lower()


def test_admin_dashboard():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "demo123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_resp = client.get("/api/v1/admin/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    data = dash_resp.json()
    assert data["total_employees"] >= 3
    assert data["total_competencies"] >= 20

    heatmap_resp = client.get("/api/v1/admin/heatmap", headers=headers)
    assert heatmap_resp.status_code == 200
    heatmap = heatmap_resp.json()
    assert len(heatmap["departments"]) > 0
    assert len(heatmap["competencies"]) > 0
