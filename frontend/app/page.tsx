"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "@/lib/api";
import {
  User,
  Lock,
  Mail,
  Briefcase,
  Target,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Plus,
  Trash2,
  Search,
  Code2,
} from "lucide-react";

interface SkillItem {
  skill: string;
  level: string;
}

const DEFAULT_QUALIFICATIONS = [
  "Bachelor of Science in Computer Science / Engineering",
  "Master of Science in Computer Science / AI / Data Science",
  "Bachelor of Technology (B.Tech / B.E.)",
  "Master of Technology (M.Tech)",
  "Bachelor's Degree in Mathematics / Statistics",
  "Master's Degree in Statistics / Econometrics",
  "Professional Coding Bootcamp Graduate",
  "Self-Taught / Open Source Contributor",
  "Ph.D. in Computer Science / Artificial Intelligence",
];

const DEFAULT_JOB_FIELDS = [
  {
    id: "cs_software",
    name: "Computer Science & Software Engineering",
    popular_positions: [
      "Full-Stack Engineer",
      "Frontend Engineer",
      "Backend Engineer",
      "Mobile App Developer (iOS / Android)",
      "Systems Software Engineer",
      "Embedded Systems Engineer",
      "API & Platform Engineer",
    ],
  },
  {
    id: "ai_ml",
    name: "Artificial Intelligence & Machine Learning",
    popular_positions: [
      "AI Engineer",
      "Machine Learning Engineer",
      "AI Research Scientist",
      "Natural Language Processing (NLP) Engineer",
      "Computer Vision Engineer",
      "Generative AI & LLM Solutions Engineer",
      "MLOps Engineer",
    ],
  },
  {
    id: "cloud_devops",
    name: "Cloud Computing, DevOps & SRE",
    popular_positions: [
      "Cloud Solutions Architect",
      "DevOps Engineer",
      "Site Reliability Engineer (SRE)",
      "Platform & Infrastructure Engineer",
      "Kubernetes & Container Specialist",
    ],
  },
  {
    id: "data_analytics",
    name: "Data Science, Analytics & Big Data",
    popular_positions: [
      "Data Scientist",
      "Data Analyst",
      "Data Engineer",
      "Business Intelligence (BI) Architect",
      "Quantitative Analyst",
    ],
  },
  {
    id: "cybersecurity",
    name: "Cybersecurity & Information Assurance",
    popular_positions: [
      "Cybersecurity Analyst",
      "Penetration Tester / Ethical Hacker",
      "Security Operations Center (SOC) Specialist",
      "Cloud Security Architect",
      "Application Security (AppSec) Engineer",
    ],
  },
  {
    id: "product_tech_mgmt",
    name: "Product Management & Tech Leadership",
    popular_positions: [
      "Technical Product Manager",
      "Engineering Manager",
      "Scrum Master / Agile Coach",
      "Enterprise Solutions Consultant",
    ],
  },
  {
    id: "design_uiux",
    name: "UI/UX & Digital Product Design",
    popular_positions: [
      "Product Designer",
      "UI/UX Designer",
      "Design Systems Engineer",
      "User Experience Researcher",
    ],
  },
  {
    id: "finance_fintech",
    name: "Finance, FinTech & Quantitative Trading",
    popular_positions: [
      "Quantitative Developer",
      "FinTech Software Engineer",
      "Algorithmic Trading Analyst",
      "Financial Risk Data Modeler",
    ],
  },
];

const DEFAULT_PROFICIENCY_LEVELS = [
  { code: "Foundation", name: "Foundation (Level 1)", numeric_score: 20, description: "Basic theoretical knowledge and core terminology." },
  { code: "Beginner", name: "Beginner (Level 2)", numeric_score: 40, description: "Can perform standard tasks with guidance and code examples." },
  { code: "Intermediate", name: "Intermediate (Level 3)", numeric_score: 60, description: "Builds features and resolves issues independently in production." },
  { code: "Advanced", name: "Advanced (Level 4)", numeric_score: 80, description: "Deep architectural mastery, optimization, and code review leadership." },
  { code: "Expert", name: "Expert (Level 5)", numeric_score: 100, description: "Domain authority, complex innovation, and high-impact design." },
];

const DEFAULT_SKILLS_BY_CATEGORY = [
  {
    category_id: "cybersecurity_ethical_hacking",
    category_name: "Cybersecurity & Ethical Hacking",
    skills: [
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
      "Cloud Security Posture Management (CSPM)",
    ],
  },
  {
    category_id: "programming_languages",
    category_name: "Programming Languages",
    skills: [
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
      "Julia",
    ],
  },
  {
    category_id: "backend_apis_architecture",
    category_name: "Backend, APIs & Architecture",
    skills: [
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
      "Celery & Distributed Task Queues",
    ],
  },
  {
    category_id: "frontend_web_mobile",
    category_name: "Frontend, Web & Mobile",
    skills: [
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
      "Frontend Testing (Jest, React Testing Library, Cypress)",
    ],
  },
  {
    category_id: "cloud_devops_sre",
    category_name: "Cloud, DevOps & SRE",
    skills: [
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
      "Nginx Reverse Proxy & Load Balancing",
    ],
  },
  {
    category_id: "databases_storage",
    category_name: "Databases & Storage Engines",
    skills: [
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
      "ClickHouse Real-Time Analytics",
    ],
  },
  {
    category_id: "ai_machine_learning_data",
    category_name: "AI, Machine Learning & Data Science",
    skills: [
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
      "Generative AI Multimodal Solutions",
    ],
  },
  {
    category_id: "software_engineering_practices",
    category_name: "Software Engineering & QA",
    skills: [
      "Data Structures & Algorithms",
      "Clean Code & Object-Oriented Design (OOP)",
      "Automated Testing & QA (PyTest, Jest, Cypress)",
      "Git & GitHub Collaborative Workflows",
      "Technical Documentation & API Specs (OpenAPI)",
      "Agile, Scrum & Sprint Delivery",
      "Technical Product Roadmapping & Requirement Analysis",
      "Test-Driven Development (TDD)",
      "Security by Design & Threat Mitigation",
    ],
  },
];

export default function AuthPortalPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "register">("register");

  // Multi-step registration (1: Personal, 2: Career, 3: Skills, 4: Review)
  const [regStep, setRegStep] = useState<1 | 2 | 3 | 4>(1);

  // Login state
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Dynamic Options from API with comprehensive defaults
  const [jobFields, setJobFields] = useState<any[]>(DEFAULT_JOB_FIELDS);
  const [skillsByCategory, setSkillsByCategory] = useState<any[]>(DEFAULT_SKILLS_BY_CATEGORY);
  const [proficiencyLevels, setProficiencyLevels] = useState<any[]>(DEFAULT_PROFICIENCY_LEVELS);
  const [qualifications, setQualifications] = useState<string[]>(DEFAULT_QUALIFICATIONS);

  // Registration state
  const [regData, setRegData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    confirm_password: "",
    field: "Computer Science & Software Engineering",
    custom_field: "",
    position: "Full-Stack Engineer",
    custom_position: "",
    years_experience: 2,
    education: "Bachelor of Science in Computer Science / Engineering",
    career_goal: "Lead Systems Architect",
    preferred_learning_style: "Hands-on projects & labs",
    weekly_hours: "10-15 hours/week",
    current_project_focus: "Building production web services & APIs",
    skills: [
      { skill: "JavaScript", level: "Intermediate" },
      { skill: "Python", level: "Intermediate" },
      { skill: "SQL", level: "Beginner" },
    ] as SkillItem[],
  });

  const [activeCategory, setActiveCategory] = useState("All");
  const [skillSearch, setSkillSearch] = useState("");
  const [customSkillInput, setCustomSkillInput] = useState("");

  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getRegistrationOptions()
      .then((data) => {
        if (data) {
          if (data.job_fields && data.job_fields.length > 0) {
            setJobFields(data.job_fields);
          }
          if (data.skills_by_category && data.skills_by_category.length > 0) {
            setSkillsByCategory(data.skills_by_category);
          }
          if (data.proficiency_levels && data.proficiency_levels.length > 0) {
            setProficiencyLevels(data.proficiency_levels);
          }
          if (data.qualifications && data.qualifications.length > 0) {
            setQualifications(data.qualifications);
          }
        }
      })
      .catch((err) => console.warn("Options fetch failed:", err));
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError(null);
    try {
      const res = await api.login(loginEmail, loginPassword);
      setToken(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setLoginError(err.message || "Invalid email or password.");
    } finally {
      setLoginLoading(false);
    }
  };

  const currentFieldObj = jobFields.find((f) => f.name === regData.field);
  const availablePositions = currentFieldObj ? currentFieldObj.popular_positions : [];

  const handleToggleOrAddSkill = (skillName: string) => {
    const exists = regData.skills.find((s) => s.skill.toLowerCase() === skillName.toLowerCase());
    if (exists) {
      setRegData({
        ...regData,
        skills: regData.skills.filter((s) => s.skill.toLowerCase() !== skillName.toLowerCase()),
      });
    } else {
      setRegData({
        ...regData,
        skills: [...regData.skills, { skill: skillName, level: "Intermediate" }],
      });
    }
  };

  const handleUpdateSkillLevel = (skillName: string, newLevel: string) => {
    setRegData({
      ...regData,
      skills: regData.skills.map((s) =>
        s.skill.toLowerCase() === skillName.toLowerCase() ? { ...s, level: newLevel } : s
      ),
    });
  };

  const handleAddCustomSkill = () => {
    const trimmed = customSkillInput.trim();
    if (!trimmed) return;
    if (!regData.skills.some((s) => s.skill.toLowerCase() === trimmed.toLowerCase())) {
      setRegData({
        ...regData,
        skills: [...regData.skills, { skill: trimmed, level: "Intermediate" }],
      });
    }
    setCustomSkillInput("");
  };

  // Step 1 Validation
  const validateStep1 = () => {
    if (!regData.first_name.trim() || !regData.last_name.trim()) {
      setRegError("Please enter your first and last name.");
      return false;
    }
    if (!regData.email.trim() || !regData.email.includes("@")) {
      setRegError("Please enter a valid email address.");
      return false;
    }
    if (regData.password.length < 6) {
      setRegError("Password must be at least 6 characters long.");
      return false;
    }
    if (regData.password !== regData.confirm_password) {
      setRegError("Passwords do not match. Please check again.");
      return false;
    }
    setRegError(null);
    return true;
  };

  // Step 2 Validation
  const validateStep2 = () => {
    const field = regData.custom_field.trim() || regData.field;
    const pos = regData.custom_position.trim() || regData.position;
    if (!field || !pos) {
      setRegError("Please specify your domain and target position.");
      return false;
    }
    setRegError(null);
    return true;
  };

  // Step 3 Validation
  const validateStep3 = () => {
    if (regData.skills.length === 0) {
      setRegError("Please select at least 1 known skill to establish your baseline.");
      return false;
    }
    setRegError(null);
    return true;
  };

  const handleNextStep = () => {
    if (regStep === 1 && validateStep1()) {
      setRegStep(2);
    } else if (regStep === 2 && validateStep2()) {
      setRegStep(3);
    } else if (regStep === 3 && validateStep3()) {
      setRegStep(4);
    }
  };

  const handlePrevStep = () => {
    setRegError(null);
    if (regStep > 1) {
      setRegStep((prev) => (prev - 1) as any);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError(null);

    if (!validateStep1() || !validateStep2() || !validateStep3()) {
      return;
    }

    const finalField = regData.custom_field.trim() || regData.field;
    const finalPosition = regData.custom_position.trim() || regData.position;

    setRegLoading(true);
    try {
      const payload = {
        first_name: regData.first_name.trim(),
        last_name: regData.last_name.trim(),
        email: regData.email.trim().toLowerCase(),
        password: regData.password,
        role: "EMPLOYEE",
        field: finalField,
        position: finalPosition,
        skills: regData.skills,
        years_experience: Number(regData.years_experience) || 0,
        education: regData.education,
        career_goal: regData.career_goal || finalPosition,
        preferred_learning_style: regData.preferred_learning_style,
        weekly_hours: regData.weekly_hours,
        current_project_focus: regData.current_project_focus,
      };

      const res = await api.register(payload);
      setToken(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setRegError(err.message || "Registration failed. Please review inputs.");
    } finally {
      setRegLoading(false);
    }
  };

  // Filter skills by category and search
  const allSkillsList: { category: string; skill: string }[] = [];
  skillsByCategory.forEach((cat) => {
    cat.skills.forEach((s: string) => {
      allSkillsList.push({ category: cat.category_name, skill: s });
    });
  });

  const filteredSkills = allSkillsList.filter((item) => {
    const matchesCat = activeCategory === "All" || item.category === activeCategory;
    const matchesSearch =
      !skillSearch.trim() || item.skill.toLowerCase().includes(skillSearch.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-white text-slate-900 py-8 px-4 sm:px-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Simple Human-Made Header */}
        <div className="border border-slate-300 p-6 bg-white text-center space-y-2">
          <div className="inline-block px-2.5 py-1 bg-slate-100 border border-slate-300 text-slate-700 text-xs font-semibold uppercase tracking-wider">
            StatKarmaYogi Platform
          </div>
          <h1 className="text-2xl font-bold text-slate-900">
            Skill Intelligence & Competency Platform
          </h1>
          <p className="text-xs text-slate-600 max-w-xl mx-auto">
            Analyze skill gaps, take technical diagnostic quizzes, track your learning roadmap, and ask technical questions to our Groq Cloud AI tutor.
          </p>

          {/* Simple Tab Switcher */}
          <div className="pt-3 flex justify-center gap-2">
            <button
              onClick={() => {
                setTab("login");
                setRegError(null);
              }}
              className={`px-5 py-2 text-xs font-bold border transition ${
                tab === "login"
                  ? "bg-blue-600 text-white border-blue-700"
                  : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
              }`}
            >
              Sign In (Existing User)
            </button>
            <button
              onClick={() => {
                setTab("register");
                setLoginError(null);
              }}
              className={`px-5 py-2 text-xs font-bold border transition ${
                tab === "register"
                  ? "bg-blue-600 text-white border-blue-700"
                  : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
              }`}
            >
              Register (New User)
            </button>
          </div>
        </div>

        {/* ===================== LOGIN VIEW ===================== */}
        {tab === "login" && (
          <div className="border border-slate-300 p-6 bg-white max-w-md mx-auto space-y-4">
            <div className="border-b border-slate-200 pb-3">
              <h2 className="text-base font-bold text-slate-900">Sign In to Your Account</h2>
              <p className="text-xs text-slate-600">Enter your registered email and password.</p>
            </div>

            {loginError && (
              <div className="p-3 bg-red-50 border border-red-300 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="name@domain.com"
                  className="w-full px-3 py-2 text-xs bg-white border border-slate-300 text-slate-900 focus:outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 text-xs bg-white border border-slate-300 text-slate-900 focus:outline-none focus:border-blue-600"
                />
              </div>

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-bold text-xs border border-blue-700 cursor-pointer transition flex items-center justify-center gap-2"
              >
                {loginLoading ? "Checking credentials..." : "Sign In to Workspace"}
              </button>
            </form>
          </div>
        )}

        {/* ===================== STEP-BY-STEP REGISTRATION VIEW ===================== */}
        {tab === "register" && (
          <div className="border border-slate-300 p-6 bg-white space-y-6">
            {/* Step Progress Indicators (Square Corners) */}
            <div className="grid grid-cols-4 border border-slate-300 text-xs">
              {[
                { num: 1, title: "1. Profile" },
                { num: 2, title: "2. Career" },
                { num: 3, title: "3. Skills" },
                { num: 4, title: "4. Review" },
              ].map((s) => {
                const isCurrent = regStep === s.num;
                const isDone = regStep > s.num;
                return (
                  <div
                    key={s.num}
                    className={`py-2 px-3 text-center font-bold border-r last:border-r-0 ${
                      isCurrent
                        ? "bg-blue-600 text-white border-blue-700"
                        : isDone
                        ? "bg-emerald-100 text-emerald-800 border-slate-300"
                        : "bg-slate-100 text-slate-500 border-slate-300"
                    }`}
                  >
                    {s.title}
                  </div>
                );
              })}
            </div>

            {/* Error Display */}
            {regError && (
              <div className="p-3 bg-red-50 border border-red-300 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{regError}</span>
              </div>
            )}

            {/* STEP 1: PERSONAL PROFILE */}
            {regStep === 1 && (
              <div className="space-y-4">
                <div className="border-b border-slate-200 pb-2">
                  <h3 className="text-sm font-bold text-slate-900">Step 1: Personal Details & Education</h3>
                  <p className="text-xs text-slate-600">Please enter your basic information.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      First Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={regData.first_name}
                      onChange={(e) => setRegData({ ...regData, first_name: e.target.value })}
                      placeholder="e.g. John"
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={regData.last_name}
                      onChange={(e) => setRegData({ ...regData, last_name: e.target.value })}
                      placeholder="e.g. Doe"
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    required
                    value={regData.email}
                    onChange={(e) => setRegData({ ...regData, email: e.target.value })}
                    placeholder="john.doe@example.com"
                    className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Password (min. 6 characters) *
                    </label>
                    <input
                      type="password"
                      required
                      value={regData.password}
                      onChange={(e) => setRegData({ ...regData, password: e.target.value })}
                      placeholder="••••••••"
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Confirm Password *
                    </label>
                    <input
                      type="password"
                      required
                      value={regData.confirm_password}
                      onChange={(e) =>
                        setRegData({ ...regData, confirm_password: e.target.value })
                      }
                      placeholder="••••••••"
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Highest Qualification / Degree
                    </label>
                    <select
                      value={regData.education}
                      onChange={(e) => setRegData({ ...regData, education: e.target.value })}
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    >
                      {qualifications.map((q, idx) => (
                        <option key={idx} value={q}>
                          {q}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Years of Experience
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="40"
                      value={regData.years_experience}
                      onChange={(e) =>
                        setRegData({ ...regData, years_experience: parseInt(e.target.value) || 0 })
                      }
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    />
                  </div>
                </div>

                <div className="pt-4 flex justify-end">
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs border border-blue-700 cursor-pointer flex items-center gap-2"
                  >
                    Next: Career Targets
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {/* STEP 2: CAREER TARGETS & LEARNING PREFERENCES */}
            {regStep === 2 && (
              <div className="space-y-4">
                <div className="border-b border-slate-200 pb-2">
                  <h3 className="text-sm font-bold text-slate-900">Step 2: Career Targets & Learning Style</h3>
                  <p className="text-xs text-slate-600">
                    Select your domain and target position so the AI can compute accurate skill gaps.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Primary Technical Domain *
                    </label>
                    <select
                      value={regData.field}
                      onChange={(e) => {
                        const newF = e.target.value;
                        const found = jobFields.find((f) => f.name === newF);
                        const firstPos = found?.popular_positions[0] || "Software Engineer";
                        setRegData({
                          ...regData,
                          field: newF,
                          position: firstPos,
                          custom_field: "",
                        });
                      }}
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    >
                      {jobFields.map((f) => (
                        <option key={f.id} value={f.name}>
                          {f.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Target Role / Position *
                    </label>
                    <select
                      value={regData.position}
                      onChange={(e) =>
                        setRegData({ ...regData, position: e.target.value, custom_position: "" })
                      }
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    >
                      {availablePositions.map((pos: string, idx: number) => (
                        <option key={idx} value={pos}>
                          {pos}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[11px] text-slate-600 mb-1">
                      Custom Field (Optional)
                    </label>
                    <input
                      type="text"
                      value={regData.custom_field}
                      onChange={(e) => setRegData({ ...regData, custom_field: e.target.value })}
                      placeholder="e.g. Distributed Systems"
                      className="w-full px-3 py-1.5 text-xs border border-slate-300 bg-white text-slate-900"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-slate-600 mb-1">
                      Custom Role (Optional)
                    </label>
                    <input
                      type="text"
                      value={regData.custom_position}
                      onChange={(e) =>
                        setRegData({ ...regData, custom_position: e.target.value })
                      }
                      placeholder="e.g. AI Systems Architect"
                      className="w-full px-3 py-1.5 text-xs border border-slate-300 bg-white text-slate-900"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Preferred Learning Method
                    </label>
                    <select
                      value={regData.preferred_learning_style}
                      onChange={(e) =>
                        setRegData({ ...regData, preferred_learning_style: e.target.value })
                      }
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    >
                      <option value="Hands-on projects & labs">Hands-on projects & labs</option>
                      <option value="Interactive code challenges">Interactive coding challenges</option>
                      <option value="System architecture deep dives">Architecture deep dives</option>
                      <option value="Visual diagram & video tutorials">Visual diagrams & video tutorials</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Weekly Study Hours
                    </label>
                    <select
                      value={regData.weekly_hours}
                      onChange={(e) => setRegData({ ...regData, weekly_hours: e.target.value })}
                      className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                    >
                      <option value="5-10 hours/week">5 - 10 hours/week</option>
                      <option value="10-15 hours/week">10 - 15 hours/week</option>
                      <option value="15-25 hours/week">15 - 25 hours/week</option>
                      <option value="25+ hours/week">25+ hours/week</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Current Project Focus / Goal
                  </label>
                  <input
                    type="text"
                    value={regData.current_project_focus}
                    onChange={(e) =>
                      setRegData({ ...regData, current_project_focus: e.target.value })
                    }
                    placeholder="e.g. Building an automated web vulnerability scanner in Python"
                    className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div className="pt-4 flex justify-between">
                  <button
                    type="button"
                    onClick={handlePrevStep}
                    className="px-4 py-2 border border-slate-400 bg-white hover:bg-slate-100 text-slate-800 font-bold text-xs flex items-center gap-1.5"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs border border-blue-700 flex items-center gap-1.5"
                  >
                    Next: Technical Skills
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}

            {/* STEP 3: TECHNICAL SKILLS BASELINE */}
            {regStep === 3 && (
              <div className="space-y-4">
                <div className="border-b border-slate-200 pb-2">
                  <h3 className="text-sm font-bold text-slate-900">Step 3: Choose Your Current Skills</h3>
                  <p className="text-xs text-slate-600">
                    Click skills you know to add them to your profile. The AI will calculate missing skills strictly against this catalog.
                  </p>
                </div>

                {/* Categories */}
                <div className="flex flex-wrap gap-1 border-b border-slate-200 pb-2">
                  {["All", ...skillsByCategory.map((c) => c.category_name)].map((catName) => (
                    <button
                      type="button"
                      key={catName}
                      onClick={() => setActiveCategory(catName)}
                      className={`px-2.5 py-1 text-[11px] font-bold border ${
                        activeCategory === catName
                          ? "bg-slate-800 text-white border-slate-900"
                          : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
                      }`}
                    >
                      {catName}
                    </button>
                  ))}
                </div>

                {/* Search & Custom Add */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    type="text"
                    value={skillSearch}
                    onChange={(e) => setSkillSearch(e.target.value)}
                    placeholder="Search skills (e.g. Python, Docker, Nmap)..."
                    className="w-full px-3 py-1.5 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                  />

                  <div className="flex gap-1">
                    <input
                      type="text"
                      value={customSkillInput}
                      onChange={(e) => setCustomSkillInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddCustomSkill();
                        }
                      }}
                      placeholder="Add custom skill name..."
                      className="flex-1 px-3 py-1.5 text-xs border border-slate-300 bg-white text-slate-900"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomSkill}
                      className="px-3 py-1.5 bg-slate-800 text-white text-xs font-bold border border-slate-900 hover:bg-slate-700"
                    >
                      Add
                    </button>
                  </div>
                </div>

                {/* Skills Grid */}
                <div className="border border-slate-300 p-3 max-h-52 overflow-y-auto bg-slate-50">
                  <div className="flex flex-wrap gap-1.5">
                    {filteredSkills.slice(0, 60).map(({ skill }) => {
                      const isSelected = regData.skills.some(
                        (s) => s.skill.toLowerCase() === skill.toLowerCase()
                      );
                      return (
                        <button
                          type="button"
                          key={skill}
                          onClick={() => handleToggleOrAddSkill(skill)}
                          className={`px-2.5 py-1 text-xs font-medium border transition ${
                            isSelected
                              ? "bg-blue-600 text-white border-blue-700 font-bold"
                              : "bg-white text-slate-800 border-slate-300 hover:bg-slate-100"
                          }`}
                        >
                          {isSelected ? `✓ ${skill}` : `+ ${skill}`}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Selected Skills List */}
                <div className="space-y-2 pt-2">
                  <div className="text-xs font-bold text-slate-900">
                    Selected Skills ({regData.skills.length}) - Set Proficiency:
                  </div>

                  <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                    {regData.skills.map((s) => (
                      <div
                        key={s.skill}
                        className="flex items-center justify-between p-2 bg-white border border-slate-300 text-xs"
                      >
                        <span className="font-bold text-slate-800">{s.skill}</span>
                        <div className="flex items-center gap-2">
                          <select
                            value={s.level}
                            onChange={(e) => handleUpdateSkillLevel(s.skill, e.target.value)}
                            className="px-2 py-1 text-xs border border-slate-300 bg-white text-slate-800"
                          >
                            <option value="Foundation">Foundation (20%)</option>
                            <option value="Beginner">Beginner (40%)</option>
                            <option value="Intermediate">Intermediate (60%)</option>
                            <option value="Advanced">Advanced (80%)</option>
                            <option value="Expert">Expert (100%)</option>
                          </select>
                          <button
                            type="button"
                            onClick={() => handleToggleOrAddSkill(s.skill)}
                            className="text-red-600 hover:underline text-xs font-bold"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 flex justify-between">
                  <button
                    type="button"
                    onClick={handlePrevStep}
                    className="px-4 py-2 border border-slate-400 bg-white hover:bg-slate-100 text-slate-800 font-bold text-xs flex items-center gap-1.5"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs border border-blue-700 flex items-center gap-1.5"
                  >
                    Next: Review & Submit
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}

            {/* STEP 4: REVIEW & LAUNCH */}
            {regStep === 4 && (
              <div className="space-y-4">
                <div className="border-b border-slate-200 pb-2">
                  <h3 className="text-sm font-bold text-slate-900">Step 4: Review Your Information</h3>
                  <p className="text-xs text-slate-600">
                    Verify everything below before creating your account and running the AI gap analysis.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="border border-slate-300 p-3 bg-slate-50 space-y-1.5">
                    <div className="font-bold text-slate-900 border-b border-slate-200 pb-1">
                      Candidate Details
                    </div>
                    <div><strong>Name:</strong> {regData.first_name} {regData.last_name}</div>
                    <div><strong>Email:</strong> {regData.email}</div>
                    <div><strong>Education:</strong> {regData.education}</div>
                    <div><strong>Experience:</strong> {regData.years_experience} Years</div>
                  </div>

                  <div className="border border-slate-300 p-3 bg-slate-50 space-y-1.5">
                    <div className="font-bold text-slate-900 border-b border-slate-200 pb-1">
                      Target & Preferences
                    </div>
                    <div><strong>Target Role:</strong> {regData.custom_position.trim() || regData.position}</div>
                    <div><strong>Domain:</strong> {regData.custom_field.trim() || regData.field}</div>
                    <div><strong>Learning Style:</strong> {regData.preferred_learning_style}</div>
                    <div><strong>Weekly Time:</strong> {regData.weekly_hours}</div>
                    <div><strong>Current Focus:</strong> {regData.current_project_focus}</div>
                  </div>
                </div>

                <div className="border border-slate-300 p-3 bg-slate-50 text-xs space-y-2">
                  <div className="font-bold text-slate-900">
                    Selected Skills ({regData.skills.length}):
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {regData.skills.map((s) => (
                      <span
                        key={s.skill}
                        className="px-2 py-1 bg-white border border-slate-300 text-slate-800"
                      >
                        <strong>{s.skill}</strong> ({s.level})
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-4 flex justify-between items-center">
                  <button
                    type="button"
                    disabled={regLoading}
                    onClick={handlePrevStep}
                    className="px-4 py-2 border border-slate-400 bg-white hover:bg-slate-100 text-slate-800 font-bold text-xs flex items-center gap-1.5"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    Back
                  </button>

                  <button
                    type="button"
                    disabled={regLoading}
                    onClick={handleRegisterSubmit}
                    className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-bold text-xs border border-blue-700 flex items-center gap-2 cursor-pointer"
                  >
                    {regLoading ? "Running AI Evaluation with Groq Cloud (Qwen 3.8)..." : "Register & Generate AI Profile"}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}