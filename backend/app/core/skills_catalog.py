"""
Master Skills Catalog & Taxonomy
Single source of truth for all selectable skills, AI gap evaluation pools,
and role benchmark requirements.
"""

from typing import List, Dict, Any, Optional
import re

SKILLS_BY_CATEGORY: List[Dict[str, Any]] = [
    {
        "category_id": "cybersecurity_ethical_hacking",
        "category_name": "Cybersecurity & Ethical Hacking",
        "skills": [
            "Penetration Testing & Ethical Hacking",
            "OWASP Top 10 Web Application Security",
            "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)",
            "Metasploit Framework & Exploit Execution",
            "Burp Suite & Web Proxy Interception",
            "Kali Linux & Penetration Testing Tools",
            "Privilege Escalation & Active Directory Exploitation",
            "Reverse Engineering & Binary Analysis",
            "SIEM Monitoring & Incident Response (Splunk, Wazuh)",
            "Identity & Access Management (IAM) & Zero Trust",
            "Threat Modeling & MITRE ATT&CK Framework",
            "Cryptography, PKI & SSL/TLS",
            "Cloud Security Hardening (AWS/GCP/Azure)",
            "Secure Code Review & Static Analysis (SAST/DAST)",
            "Wireless Network Security & WPA Cracking",
            "Social Engineering & Phishing Simulation",
            "Security Operations Center (SOC) Procedures",
            "Digital Forensics & Incident Response (DFIR)",
            "Malware Analysis & Sandboxing",
            "Application Security (AppSec) Engineering",
            "Vulnerability Management & CVE Tracking",
            "Cloud Security Posture Management (CSPM)"
        ]
    },
    {
        "category_id": "programming_languages",
        "category_name": "Programming Languages",
        "skills": [
            "Python",
            "JavaScript (ES6+)",
            "TypeScript",
            "Go (Golang)",
            "Rust",
            "Java",
            "C++",
            "C#",
            "SQL",
            "Bash / Shell Scripting",
            "R Programming",
            "Kotlin",
            "Swift",
            "PHP",
            "Ruby",
            "Scala",
            "Dart",
            "Julia"
        ]
    },
    {
        "category_id": "backend_apis_architecture",
        "category_name": "Backend, APIs & Architecture",
        "skills": [
            "FastAPI (Python)",
            "Node.js & Express.js",
            "Django / Django REST Framework",
            "Spring Boot (Java)",
            "RESTful API Design & Best Practices",
            "GraphQL Schema Design & Apollo",
            "gRPC & Protocol Buffers",
            "Microservices Architecture & Service Mesh",
            "Event-Driven Architecture & Message Queues (Kafka / RabbitMQ)",
            "Distributed Systems Design & Consensus",
            "System Design & Scalability",
            "Asynchronous Programming & Concurrency",
            "WebSockets & Real-Time Communication",
            "Redis Caching & In-Memory Storage",
            "Database Schema Design & Migration (Alembic/Prisma)",
            "Celery & Distributed Task Queues"
        ]
    },
    {
        "category_id": "frontend_web_mobile",
        "category_name": "Frontend, Web & Mobile",
        "skills": [
            "React.js & Modern Hooks",
            "Next.js & Server Components",
            "Vue.js & Nuxt",
            "Angular & RxJS",
            "Tailwind CSS & Modern UI Design",
            "HTML5 & CSS3 Responsive Layouts",
            "State Management (Redux Toolkit, Zustand)",
            "Web Performance Optimization & Core Web Vitals",
            "Mobile App Development (React Native / Flutter)",
            "Progressive Web Apps (PWA) & Service Workers",
            "Webpack & Vite Build Tooling",
            "Three.js & 3D Web Graphics",
            "WebAssembly (WASM)",
            "Frontend Testing (Jest, React Testing Library, Cypress)"
        ]
    },
    {
        "category_id": "cloud_devops_sre",
        "category_name": "Cloud, DevOps & SRE",
        "skills": [
            "Docker Containerization & Multi-Stage Builds",
            "Kubernetes Cluster Orchestration & Helm",
            "Terraform & Infrastructure as Code (IaC)",
            "CI/CD Pipelines (GitHub Actions / GitLab CI)",
            "Amazon Web Services (AWS) Core Services",
            "Google Cloud Platform (GCP)",
            "Microsoft Azure Cloud Infrastructure",
            "Linux Systems Administration & Hardening",
            "Observability & Monitoring (Prometheus & Grafana)",
            "Distributed Tracing & Logging (OpenTelemetry, ELK)",
            "Site Reliability Engineering (SRE) & Incident Management",
            "Serverless Computing (AWS Lambda, Vercel Functions)",
            "ArgoCD & GitOps Workflows",
            "Nginx Reverse Proxy & Load Balancing"
        ]
    },
    {
        "category_id": "databases_storage",
        "category_name": "Databases & Storage Engines",
        "skills": [
            "PostgreSQL Administration & Schema Design",
            "MySQL / MariaDB",
            "MongoDB & Document Stores",
            "Redis Caching & In-Memory Data Structures",
            "Apache Kafka Streaming",
            "Elasticsearch & Full-Text Search",
            "Database Indexing, Query Optimization & Partitioning",
            "Data Warehousing (Snowflake / BigQuery)",
            "Vector Databases & Semantic Embeddings",
            "Cassandra & Wide-Column NoSQL",
            "Neo4j & Graph Databases",
            "ClickHouse Real-Time Analytics"
        ]
    },
    {
        "category_id": "ai_machine_learning_data",
        "category_name": "AI, Machine Learning & Data Science",
        "skills": [
            "Machine Learning Algorithms (Scikit-Learn)",
            "Deep Learning & Neural Networks (PyTorch / TensorFlow)",
            "Large Language Models & Prompt Engineering",
            "RAG (Retrieval-Augmented Generation) Architectures",
            "MLOps, Model Registry & Serving (MLflow, Triton)",
            "Natural Language Processing (Hugging Face Transformers)",
            "Computer Vision & Object Detection (OpenCV, YOLO)",
            "Pandas, NumPy & Exploratory Data Analysis",
            "Data Engineering Pipelines (Apache Airflow, Spark)",
            "Statistical Inference, Hypothesis Testing & A/B Testing",
            "LangChain, LlamaIndex & Agentic AI Frameworks",
            "Model Quantization (GGUF, AWQ, LoRA Fine-Tuning)",
            "Generative AI Multimodal Solutions"
        ]
    },
    {
        "category_id": "software_engineering_practices",
        "category_name": "Software Engineering & QA",
        "skills": [
            "Data Structures & Algorithms",
            "Clean Code & Object-Oriented Design (OOP)",
            "Automated Testing & QA (PyTest, Jest, Cypress)",
            "Git & GitHub Collaborative Workflows",
            "Technical Documentation & API Specs (OpenAPI)",
            "Agile, Scrum & Sprint Delivery",
            "Technical Product Roadmapping & Requirement Analysis",
            "Test-Driven Development (TDD)",
            "Security by Design & Threat Mitigation"
        ]
    }
]

ALL_SKILLS: List[str] = []
_seen = set()
for cat in SKILLS_BY_CATEGORY:
    for s in cat["skills"]:
        s_clean = s.strip()
        if s_clean.lower() not in _seen:
            _seen.add(s_clean.lower())
            ALL_SKILLS.append(s_clean)


def get_all_skills() -> List[str]:
    return list(ALL_SKILLS)


def get_skills_by_category() -> List[Dict[str, Any]]:
    return SKILLS_BY_CATEGORY


def get_domain_skills(domain_query: str) -> List[str]:
    q = domain_query.lower().strip()
    
    # 1. AI, Machine Learning, Deep Learning, LLMs & Data Science
    if (
        re.search(r'\b(ai|ml|llm|llms|nlp|gpt|genai)\b', q) or
        any(k in q for k in ["artificial intelligence", "machine learning", "deep learning", "generative", "neural", "computer vision", "prompt engineering", "data science"])
    ):
        ai_skills = [s for cat in SKILLS_BY_CATEGORY if cat["category_id"] == "ai_machine_learning_data" for s in cat["skills"]]
        ai_skills += ["Python", "Vector Databases & Semantic Embeddings", "FastAPI (Python)", "Docker Containerization & Multi-Stage Builds", "SQL"]
        seen = set()
        out = []
        for s in ai_skills:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    # 2. Cybersecurity, Penetration Testing & Ethical Hacking
    if any(k in q for k in ["security", "cyber", "penetrat", "pentest", "ethical hack", "soc", "infosec", "vulnerability", "appsec"]):
        sec_skills = [s for cat in SKILLS_BY_CATEGORY if cat["category_id"] == "cybersecurity_ethical_hacking" for s in cat["skills"]]
        sec_skills += ["Python", "Linux Systems Administration & Hardening", "Bash / Shell Scripting", "Docker Containerization & Multi-Stage Builds"]
        return sec_skills

    # 3. Cloud, DevOps, SRE & Infrastructure
    if any(k in q for k in ["cloud", "devops", "sre", "reliability", "infrastructure", "kubernetes", "platform", "terraform", "ci/cd"]):
        devops_skills = [s for cat in SKILLS_BY_CATEGORY if cat["category_id"] == "cloud_devops_sre" for s in cat["skills"]]
        devops_skills += ["Docker Containerization & Multi-Stage Builds", "Linux Systems Administration & Hardening", "Python", "Go (Golang)", "Bash / Shell Scripting"]
        return devops_skills

    # 4. Frontend, Web & Mobile Development
    if any(k in q for k in ["frontend", "front-end", "web", "react", "next.js", "ui", "ux", "mobile", "ios", "android", "flutter", "vue", "angular"]):
        fe_skills = [s for cat in SKILLS_BY_CATEGORY if cat["category_id"] == "frontend_web_mobile" for s in cat["skills"]]
        fe_skills += ["TypeScript", "JavaScript (ES6+)", "RESTful API Design & Best Practices", "Git & GitHub Collaborative Workflows"]
        return fe_skills

    # 5. Data Engineering & Big Data
    if any(k in q for k in ["data engineer", "analytics", "big data", "bi", "data warehouse", "spark", "kafka"]):
        return [
            "Data Engineering Pipelines (Apache Airflow, Spark)",
            "Data Warehousing (Snowflake / BigQuery)",
            "Apache Kafka Streaming",
            "SQL",
            "Python",
            "PostgreSQL Administration & Schema Design",
            "Pandas, NumPy & Exploratory Data Analysis"
        ]

    # 6. Backend & Systems Architecture
    if any(k in q for k in ["backend", "back-end", "api", "microservice", "distributed", "systems", "database", "sql"]):
        be_skills = [s for cat in SKILLS_BY_CATEGORY if cat["category_id"] in ["backend_apis_architecture", "databases_storage"] for s in cat["skills"]]
        be_skills += ["Python", "PostgreSQL Administration & Schema Design", "Docker Containerization & Multi-Stage Builds", "System Design & Scalability"]
        return be_skills

    # Fallback to general software engineering
    return [s for cat in SKILLS_BY_CATEGORY if cat["category_id"] in ["programming_languages", "backend_apis_architecture", "software_engineering_practices"] for s in cat["skills"]]


def snap_to_catalog(skill_name: str) -> Optional[str]:
    if not skill_name:
        return None

    clean_target = skill_name.strip()
    clean_lower = clean_target.lower()

    # 1. Exact match
    for s in ALL_SKILLS:
        if s.lower() == clean_lower:
            return s

    # 2. Key phrase mappings
    KEYWORD_MAPPINGS = {
        "penetration test": "Penetration Testing & Ethical Hacking",
        "ethical hack": "Penetration Testing & Ethical Hacking",
        "metasploit": "Metasploit Framework & Exploit Execution",
        "burp": "Burp Suite & Web Proxy Interception",
        "burpsuite": "Burp Suite & Web Proxy Interception",
        "owasp": "OWASP Top 10 Web Application Security",
        "nmap": "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)",
        "wireshark": "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)",
        "network vulnerabilit": "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)",
        "port scan": "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)",
        "kali": "Kali Linux & Penetration Testing Tools",
        "privilege escalation": "Privilege Escalation & Active Directory Exploitation",
        "active directory": "Privilege Escalation & Active Directory Exploitation",
        "reverse engineering": "Reverse Engineering & Binary Analysis",
        "siem": "SIEM Monitoring & Incident Response (Splunk, Wazuh)",
        "incident response": "SIEM Monitoring & Incident Response (Splunk, Wazuh)",
        "iam": "Identity & Access Management (IAM) & Zero Trust",
        "zero trust": "Identity & Access Management (IAM) & Zero Trust",
        "threat model": "Threat Modeling & MITRE ATT&CK Framework",
        "mitre": "Threat Modeling & MITRE ATT&CK Framework",
        "cryptography": "Cryptography, PKI & SSL/TLS",
        "ssl": "Cryptography, PKI & SSL/TLS",
        "tls": "Cryptography, PKI & SSL/TLS",
        "docker": "Docker Containerization & Multi-Stage Builds",
        "kubernetes": "Kubernetes Cluster Orchestration & Helm",
        "k8s": "Kubernetes Cluster Orchestration & Helm",
        "terraform": "Terraform & Infrastructure as Code (IaC)",
        "ci/cd": "CI/CD Pipelines (GitHub Actions / GitLab CI)",
        "github actions": "CI/CD Pipelines (GitHub Actions / GitLab CI)",
        "aws": "Amazon Web Services (AWS) Core Services",
        "gcp": "Google Cloud Platform (GCP)",
        "azure": "Microsoft Azure Cloud Infrastructure",
        "linux": "Linux Systems Administration & Hardening",
        "prometheus": "Observability & Monitoring (Prometheus & Grafana)",
        "grafana": "Observability & Monitoring (Prometheus & Grafana)",
        "react": "React.js & Modern Hooks",
        "next": "Next.js & Server Components",
        "typescript": "TypeScript",
        "javascript": "JavaScript (ES6+)",
        "python": "Python",
        "fastapi": "FastAPI (Python)",
        "node": "Node.js & Express.js",
        "express": "Node.js & Express.js",
        "django": "Django / Django REST Framework",
        "spring": "Spring Boot (Java)",
        "restful": "RESTful API Design & Best Practices",
        "api design": "RESTful API Design & Best Practices",
        "graphql": "GraphQL Schema Design & Apollo",
        "grpc": "gRPC & Protocol Buffers",
        "microservices": "Microservices Architecture & Service Mesh",
        "distributed systems": "Distributed Systems Design & Consensus",
        "system design": "System Design & Scalability",
        "scalability": "System Design & Scalability",
        "sql": "SQL",
        "postgres": "PostgreSQL Administration & Schema Design",
        "mysql": "MySQL / MariaDB",
        "mongodb": "MongoDB & Document Stores",
        "redis": "Redis Caching & In-Memory Data Structures",
        "kafka": "Apache Kafka Streaming",
        "machine learning": "Machine Learning Algorithms (Scikit-Learn)",
        "deep learning": "Deep Learning & Neural Networks (PyTorch / TensorFlow)",
        "pytorch": "Deep Learning & Neural Networks (PyTorch / TensorFlow)",
        "tensorflow": "Deep Learning & Neural Networks (PyTorch / TensorFlow)",
        "llm": "Large Language Models & Prompt Engineering",
        "rag": "RAG (Retrieval-Augmented Generation) Architectures",
        "mlops": "MLOps, Model Registry & Serving (MLflow, Triton)",
        "testing": "Automated Testing & QA (PyTest, Jest, Cypress)",
        "data structures": "Data Structures & Algorithms",
        "algorithms": "Data Structures & Algorithms",
    }

    for key, canonical in KEYWORD_MAPPINGS.items():
        if key in clean_lower:
            return canonical

    for s in ALL_SKILLS:
        if s.lower() in clean_lower or clean_lower in s.lower():
            return s

    return None
