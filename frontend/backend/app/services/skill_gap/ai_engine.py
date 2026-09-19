import json
import re
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.models.users import User
from app.services.ai.factory import get_llm_provider
from app.core.skills_catalog import ALL_SKILLS, get_domain_skills, snap_to_catalog

LEVEL_TO_SCORE = {
    "Foundation": 20.0,
    "Beginner": 40.0,
    "Intermediate": 60.0,
    "Advanced": 80.0,
    "Expert": 100.0,
}

SCORE_TO_LEVEL = [
    (20.0, "Foundation"),
    (40.0, "Beginner"),
    (60.0, "Intermediate"),
    (80.0, "Advanced"),
    (100.0, "Expert"),
]

# Canonical benchmarks - ALL skills exist in app.core.skills_catalog
ROLE_BENCHMARK_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Penetration Tester": {
        "domain": "Cybersecurity & Ethical Hacking",
        "benchmark_skills": [
            {"skill": "Penetration Testing & Ethical Hacking", "required_level": "Advanced", "score": 85.0, "importance": 1.5},
            {"skill": "Metasploit Framework & Exploit Execution", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "Burp Suite & Web Proxy Interception", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "OWASP Top 10 Web Application Security", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Kali Linux & Penetration Testing Tools", "required_level": "Intermediate", "score": 75.0, "importance": 1.2},
            {"skill": "Privilege Escalation & Active Directory Exploitation", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "Linux Systems Administration & Hardening", "required_level": "Intermediate", "score": 65.0, "importance": 1.1}
        ]
    },
    "Cybersecurity Analyst": {
        "domain": "Cybersecurity & Information Assurance",
        "benchmark_skills": [
            {"skill": "SIEM Monitoring & Incident Response (Splunk, Wazuh)", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "OWASP Top 10 Web Application Security", "required_level": "Intermediate", "score": 70.0, "importance": 1.3},
            {"skill": "Identity & Access Management (IAM) & Zero Trust", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "Threat Modeling & MITRE ATT&CK Framework", "required_level": "Intermediate", "score": 65.0, "importance": 1.2},
            {"skill": "Cryptography, PKI & SSL/TLS", "required_level": "Intermediate", "score": 65.0, "importance": 1.1}
        ]
    },
    "Full-Stack Engineer": {
        "domain": "Computer Science & Software",
        "benchmark_skills": [
            {"skill": "React.js & Modern Hooks", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "Next.js & Server Components", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "TypeScript", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "FastAPI (Python)", "required_level": "Intermediate", "score": 70.0, "importance": 1.3},
            {"skill": "PostgreSQL Administration & Schema Design", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "RESTful API Design & Best Practices", "required_level": "Advanced", "score": 80.0, "importance": 1.2},
            {"skill": "Docker Containerization & Multi-Stage Builds", "required_level": "Intermediate", "score": 65.0, "importance": 1.1},
            {"skill": "System Design & Scalability", "required_level": "Intermediate", "score": 65.0, "importance": 1.1}
        ]
    },
    "Backend Systems Engineer": {
        "domain": "Backend, APIs & Architecture",
        "benchmark_skills": [
            {"skill": "Python", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "FastAPI (Python)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "RESTful API Design & Best Practices", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Microservices Architecture & Service Mesh", "required_level": "Intermediate", "score": 75.0, "importance": 1.3},
            {"skill": "PostgreSQL Administration & Schema Design", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Redis Caching & In-Memory Data Structures", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "System Design & Scalability", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Automated Testing & QA (PyTest, Jest, Cypress)", "required_level": "Intermediate", "score": 70.0, "importance": 1.1}
        ]
    },
    "Cloud & DevOps Engineer": {
        "domain": "Cloud, DevOps & SRE",
        "benchmark_skills": [
            {"skill": "Docker Containerization & Multi-Stage Builds", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Kubernetes Cluster Orchestration & Helm", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Linux Systems Administration & Hardening", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Terraform & Infrastructure as Code (IaC)", "required_level": "Intermediate", "score": 75.0, "importance": 1.3},
            {"skill": "CI/CD Pipelines (GitHub Actions / GitLab CI)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Amazon Web Services (AWS) Core Services", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Observability & Monitoring (Prometheus & Grafana)", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "Site Reliability Engineering (SRE) & Incident Management", "required_level": "Intermediate", "score": 65.0, "importance": 1.1}
        ]
    },
    "Generative AI & LLM Solutions Engineer": {
        "domain": "AI, Machine Learning & Data Science",
        "benchmark_skills": [
            {"skill": "Large Language Models & Prompt Engineering", "required_level": "Advanced", "score": 85.0, "importance": 1.5},
            {"skill": "RAG (Retrieval-Augmented Generation) Architectures", "required_level": "Advanced", "score": 85.0, "importance": 1.5},
            {"skill": "Python", "required_level": "Expert", "score": 90.0, "importance": 1.4},
            {"skill": "Vector Databases & Semantic Embeddings", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "Natural Language Processing (Hugging Face Transformers)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Deep Learning & Neural Networks (PyTorch / TensorFlow)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "FastAPI (Python)", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "MLOps, Model Registry & Serving (MLflow, Triton)", "required_level": "Intermediate", "score": 70.0, "importance": 1.2}
        ]
    },
    "AI Engineer": {
        "domain": "AI, Machine Learning & Data Science",
        "benchmark_skills": [
            {"skill": "Large Language Models & Prompt Engineering", "required_level": "Advanced", "score": 85.0, "importance": 1.5},
            {"skill": "RAG (Retrieval-Augmented Generation) Architectures", "required_level": "Advanced", "score": 85.0, "importance": 1.5},
            {"skill": "Python", "required_level": "Expert", "score": 90.0, "importance": 1.4},
            {"skill": "Vector Databases & Semantic Embeddings", "required_level": "Advanced", "score": 80.0, "importance": 1.4},
            {"skill": "Deep Learning & Neural Networks (PyTorch / TensorFlow)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Natural Language Processing (Hugging Face Transformers)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "MLOps, Model Registry & Serving (MLflow, Triton)", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "FastAPI (Python)", "required_level": "Intermediate", "score": 70.0, "importance": 1.2}
        ]
    },
    "Data Engineer": {
        "domain": "Data Science & Big Data",
        "benchmark_skills": [
            {"skill": "Data Engineering Pipelines (Apache Airflow, Spark)", "required_level": "Advanced", "score": 85.0, "importance": 1.5},
            {"skill": "Data Warehousing (Snowflake / BigQuery)", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "SQL", "required_level": "Expert", "score": 90.0, "importance": 1.4},
            {"skill": "Python", "required_level": "Advanced", "score": 85.0, "importance": 1.3},
            {"skill": "Apache Kafka Streaming", "required_level": "Intermediate", "score": 75.0, "importance": 1.3},
            {"skill": "PostgreSQL Administration & Schema Design", "required_level": "Advanced", "score": 80.0, "importance": 1.2}
        ]
    },
    "Machine Learning Engineer": {
        "domain": "AI, Machine Learning & Data Science",
        "benchmark_skills": [
            {"skill": "Python", "required_level": "Expert", "score": 90.0, "importance": 1.5},
            {"skill": "Machine Learning Algorithms (Scikit-Learn)", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Deep Learning & Neural Networks (PyTorch / TensorFlow)", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Large Language Models & Prompt Engineering", "required_level": "Intermediate", "score": 75.0, "importance": 1.3},
            {"skill": "RAG (Retrieval-Augmented Generation) Architectures", "required_level": "Intermediate", "score": 75.0, "importance": 1.3},
            {"skill": "MLOps, Model Registry & Serving (MLflow, Triton)", "required_level": "Intermediate", "score": 70.0, "importance": 1.2},
            {"skill": "Pandas, NumPy & Exploratory Data Analysis", "required_level": "Advanced", "score": 80.0, "importance": 1.2}
        ]
    },
    "Data Scientist": {
        "domain": "AI, Machine Learning & Data Science",
        "benchmark_skills": [
            {"skill": "Python", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Pandas, NumPy & Exploratory Data Analysis", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Statistical Inference, Hypothesis Testing & A/B Testing", "required_level": "Advanced", "score": 85.0, "importance": 1.4},
            {"skill": "Machine Learning Algorithms (Scikit-Learn)", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "SQL", "required_level": "Advanced", "score": 80.0, "importance": 1.3},
            {"skill": "Data Warehousing (Snowflake / BigQuery)", "required_level": "Intermediate", "score": 70.0, "importance": 1.1}
        ]
    }
}


def score_from_level(level_name: str) -> float:
    for name, score in LEVEL_TO_SCORE.items():
        if name.lower() == str(level_name).lower():
            return score
    return 40.0


def find_matched_benchmark(target_role: str) -> Optional[Dict[str, Any]]:
    role_lower = target_role.lower().strip()
    
    # 1. AI / Generative AI / LLM / NLP / Vision / AI Engineer
    if re.search(r'\b(ai|genai|llm|nlp)\b', role_lower) or any(k in role_lower for k in ["generative", "llm", "prompt", "nlp", "vision", "ai engineer", "artificial intelligence", "ai research"]):
        return ROLE_BENCHMARK_TAXONOMY.get("AI Engineer") or ROLE_BENCHMARK_TAXONOMY["Generative AI & LLM Solutions Engineer"]
    if any(k in role_lower for k in ["machine learning", "deep learning", "mlops"]):
        return ROLE_BENCHMARK_TAXONOMY["Machine Learning Engineer"]
    if any(k in role_lower for k in ["data engineer", "etl", "pipeline"]):
        return ROLE_BENCHMARK_TAXONOMY["Data Engineer"]
    if any(k in role_lower for k in ["data scientist", "data science", "statistical", "data analyst"]):
        return ROLE_BENCHMARK_TAXONOMY["Data Scientist"]

    # 2. Cybersecurity & Penetration Testing (ONLY when security keywords are present!)
    if any(k in role_lower for k in ["penetrat", "pentest", "ethical hack", "red team", "exploit"]):
        return ROLE_BENCHMARK_TAXONOMY["Penetration Tester"]
    if any(k in role_lower for k in ["soc", "cyber", "security analyst", "infosec", "incident response", "appsec"]):
        return ROLE_BENCHMARK_TAXONOMY["Cybersecurity Analyst"]

    # 3. Full-Stack & Frontend
    if any(k in role_lower for k in ["full stack", "fullstack", "frontend", "web developer"]):
        return ROLE_BENCHMARK_TAXONOMY["Full-Stack Engineer"]

    # 4. Backend & APIs
    if any(k in role_lower for k in ["backend", "api", "microservice", "systems engineer"]):
        return ROLE_BENCHMARK_TAXONOMY["Backend Systems Engineer"]

    # 5. Cloud, DevOps & SRE
    if any(k in role_lower for k in ["devops", "cloud", "sre", "reliability", "infrastructure", "platform", "kubernetes"]):
        return ROLE_BENCHMARK_TAXONOMY["Cloud & DevOps Engineer"]

    # Exact or substring match in dictionary keys
    for name, data in ROLE_BENCHMARK_TAXONOMY.items():
        if name.lower() in role_lower or role_lower in name.lower():
            return data
            
    return None


async def evaluate_dynamic_skill_gaps_with_ai(
    target_role: str,
    industry_field: str,
    declared_skills: List[Dict[str, str]],
    years_experience: int = 0,
    career_goal: str = "",
    preferred_learning_style: str = "Hands-on projects & labs",
    weekly_hours: str = "10 hours/week",
    current_project_focus: str = "Full-stack development"
) -> Dict[str, Any]:
    """
    Calls Ollama Qwen3:8b to dynamically evaluate the target role against
    the user's declared skills and levels, strictly constrained to canonical catalog skills.
    """
    matched_benchmark = find_matched_benchmark(target_role)
    if matched_benchmark:
        target_skills = matched_benchmark.get("benchmark_skills", [])
        domain_name = matched_benchmark.get("domain", industry_field)
    else:
        domain_skills = get_domain_skills(f"{industry_field} {target_role}")
        domain_name = industry_field
        target_skills = [
            {"skill": s, "required_level": "Advanced", "score": 80.0, "importance": 1.2}
            for s in (domain_skills[:8] if len(domain_skills) >= 8 else domain_skills + ALL_SKILLS[:8])[:8]
        ]

    # Map declared skills to numeric scores
    user_skill_map = {}
    user_skill_levels = {}
    for s in declared_skills:
        s_name = s.get("skill", "").strip().lower()
        s_lvl = s.get("level", "Intermediate")
        score = LEVEL_TO_SCORE.get(s_lvl, 60.0)
        user_skill_map[s_name] = score
        user_skill_levels[s_name] = s_lvl

    benchmark_list_str = "\n".join([
        f"- {ts['skill']} (Required: {ts.get('required_level', 'Advanced')})"
        for ts in target_skills
    ])

    skills_formatted = "\n".join([
        f"- {s.get('skill')}: Level {s.get('level')}"
        for s in declared_skills
    ]) if declared_skills else "No skills declared yet."

    prompt = f"""You are a Principal AI Technical Evaluator.
Target Role: {target_role} ({domain_name})
Candidate Background: {years_experience} years experience, Career Goal: {career_goal or target_role}
Candidate Declared Skills:
{skills_formatted}

Target Benchmark Competencies:
{benchmark_list_str}

Provide a concise 2-sentence technical evaluation summary analyzing the candidate's current capabilities and critical gaps for this role.
Respond with valid JSON ONLY:
{{
  "ai_summary": "<concise 2-sentence technical evaluation>"
}}
"""

    llm = get_llm_provider()
    ai_summary = f"Dynamic AI evaluation for {target_role}: Identified key competency benchmarks."

    try:
        raw_res = await asyncio.wait_for(
            llm.generate(prompt, system_prompt="You are an expert AI skill advisor. Output valid JSON only.", max_tokens=250),
            timeout=12.0
        )
        json_match = re.search(r'(\{[\s\S]*\})', raw_res)
        if json_match:
            data = json.loads(json_match.group(1))
            ai_summary = data.get("ai_summary", ai_summary)
            logger.info(f"Groq Cloud AI generated live summary for {target_role}")
    except Exception as e:
        logger.warning(f"Groq live summary generation notice: {e}")

    total_req_points = 0.0
    earned_points = 0.0
    gaps = []
    strengths = []

    for ts in target_skills:
        req_name = ts["skill"]
        req_name_clean = req_name.strip().lower()
        req_lvl = ts.get("required_level", "Advanced")
        req_score = float(ts.get("score", 80.0))
        importance = float(ts.get("importance", 1.2))

        found_score = None
        found_lvl = "None"
        for u_skill, u_score in user_skill_map.items():
            if u_skill == req_name_clean or u_skill in req_name_clean or req_name_clean in u_skill:
                found_score = u_score
                found_lvl = user_skill_levels.get(u_skill, "Intermediate")
                break

        current_score = found_score if found_score is not None else 0.0
        gap_val = round(max(0.0, req_score - current_score), 1)
        is_missing = bool(found_score is None or current_score == 0.0)

        total_req_points += req_score * importance
        earned_points += min(current_score, req_score) * importance

        if gap_val >= 40.0:
            p_lvl = "CRITICAL"
        elif gap_val >= 20.0:
            p_lvl = "HIGH"
        elif gap_val > 0.0:
            p_lvl = "MEDIUM"
        else:
            p_lvl = "LOW"

        reason = f"{req_name} is essential for {target_role} benchmarks to ensure production reliability."
        action = f"Master {req_name} concepts, complete practical labs, and bridge level to {req_lvl}."

        item = {
            "skill": req_name,
            "domain": domain_name,
            "current_level": found_lvl,
            "required_level": req_lvl,
            "current_score": current_score,
            "required_score": req_score,
            "gap": gap_val,
            "priority_level": p_lvl,
            "is_missing": is_missing,
            "reason": reason,
            "recommended_action": action
        }

        if gap_val > 0.0:
            gaps.append(item)
        else:
            strengths.append({
                "skill": req_name,
                "level": found_lvl,
                "score": current_score
            })

    overall_score = round((earned_points / max(1.0, total_req_points)) * 100.0, 1)
    status = "Ready" if overall_score >= 80.0 else ("Near Ready" if overall_score >= 60.0 else "Needs Development")

    result = {
        "target_role": target_role,
        "industry_field": industry_field,
        "overall_readiness_percentage": overall_score,
        "readiness_status": status,
        "ai_summary": ai_summary,
        "gaps": gaps,
        "strengths": strengths,
        "declared_skills": declared_skills
    }
    logger.info(f"Dynamic gap evaluation complete for role '{target_role}': {len(gaps)} gaps, readiness={overall_score}%.")
    return result


def generate_deterministic_benchmark_gaps(
    target_role: str,
    industry_field: str,
    declared_skills: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Deterministic benchmark generator ensuring 100% uptime and 100% catalog conformity.
    """
    matched_benchmark = find_matched_benchmark(target_role)

    if not matched_benchmark:
        # Construct dynamic benchmark using ONLY canonical skills from the domain catalog
        domain_skills = get_domain_skills(f"{industry_field} {target_role}")
        selected_skills = domain_skills[:6] if len(domain_skills) >= 6 else (domain_skills + ALL_SKILLS[:6])[:6]
        
        benchmark_items = []
        for idx, s_name in enumerate(selected_skills):
            req_lvl = "Advanced" if idx < 2 else "Intermediate"
            req_sc = 80.0 if req_lvl == "Advanced" else 65.0
            benchmark_items.append({
                "skill": s_name,
                "required_level": req_lvl,
                "score": req_sc,
                "importance": 1.4 if idx < 2 else 1.2
            })
            
        matched_benchmark = {
            "domain": industry_field or "Technology",
            "benchmark_skills": benchmark_items
        }

    # Normalize user skills map (canonical snapping)
    user_skill_map: Dict[str, float] = {}
    user_skill_levels: Dict[str, str] = {}
    for item in declared_skills:
        raw_name = str(item.get("skill", "")).strip()
        canonical_name = snap_to_catalog(raw_name) or raw_name
        s_lvl = str(item.get("level", "Intermediate")).strip()
        user_skill_map[canonical_name.lower()] = score_from_level(s_lvl)
        user_skill_levels[canonical_name.lower()] = s_lvl

    gaps = []
    strengths = []
    total_req_points = 0.0
    earned_points = 0.0

    for req in matched_benchmark["benchmark_skills"]:
        req_name = req["skill"]
        req_score = float(req["score"])
        req_lvl = req["required_level"]
        importance = float(req.get("importance", 1.0))
        total_req_points += req_score * importance

        # Check if user has this canonical skill
        found_score = None
        found_lvl = "None"
        req_name_clean = req_name.lower()

        for u_skill, u_score in user_skill_map.items():
            if u_skill == req_name_clean or u_skill in req_name_clean or req_name_clean in u_skill:
                found_score = u_score
                found_lvl = user_skill_levels.get(u_skill, "Intermediate")
                break

        current_score = found_score if found_score is not None else 0.0
        earned_points += min(current_score, req_score) * importance
        gap = round(max(0.0, req_score - current_score), 1)

        if gap > 0:
            p_lvl = "CRITICAL" if gap >= 40.0 else ("HIGH" if gap >= 20.0 else "MEDIUM")
            gaps.append({
                "skill": req_name,
                "domain": matched_benchmark.get("domain", industry_field),
                "current_level": found_lvl,
                "required_level": req_lvl,
                "current_score": current_score,
                "required_score": req_score,
                "gap": gap,
                "priority_level": p_lvl,
                "is_missing": (found_score is None or current_score == 0),
                "reason": f"{req_name} is essential for {target_role} benchmarks to ensure production reliability.",
                "recommended_action": f"Master {req_name} concepts, complete practical labs, and bridge level to {req_lvl}."
            })
        else:
            strengths.append({
                "skill": req_name,
                "level": found_lvl,
                "score": current_score
            })

    overall_score = round((earned_points / max(1.0, total_req_points)) * 100.0, 1)
    status = "Ready" if overall_score >= 80 else ("Near Ready" if overall_score >= 60 else "Needs Development")

    return {
        "target_role": target_role,
        "industry_field": industry_field,
        "overall_readiness_percentage": overall_score,
        "readiness_status": status,
        "ai_summary": f"Identified {len(gaps)} key development areas for {target_role}. Current role readiness is {overall_score}%.",
        "gaps": gaps,
        "strengths": strengths,
        "declared_skills": declared_skills
    }


def save_user_ai_profile(db: Session, user: User, profile: Dict[str, Any]):
    user.ai_profile_json = json.dumps(profile)
    user.industry_field = profile.get("industry_field", user.industry_field)
    user.designation_name = profile.get("target_role", user.designation_name)
    db.commit()


def get_user_ai_profile(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.ai_profile_json:
        try:
            return json.loads(user.ai_profile_json)
        except Exception:
            return None
    return None
