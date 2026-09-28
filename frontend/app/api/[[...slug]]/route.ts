import { NextRequest, NextResponse } from "next/server";

// Dynamic In-Memory Store for Serverless Lifetime & Sessions
interface StoredUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  field: string;
  position: string;
  department_id: string | null;
  department_name: string;
  designation_id: string | null;
  designation_name: string;
  organization: string;
  years_experience: number;
  education: string;
  current_assignment: string;
  career_goal: string;
  preferred_learning_style: string;
  weekly_hours: string;
  current_project_focus: string;
  skills: Array<{ skill: string; level: string; score?: number }>;
  preferred_language: string;
  status: string;
  created_at: string;
  ai_profile?: any;
}

const usersDb = new Map<string, StoredUser>();

// Pre-seed default test users
const defaultRahul: StoredUser = {
  id: "usr-rahul-001",
  email: "employee@example.com",
  first_name: "Rahul",
  last_name: "Sharma",
  role: "EMPLOYEE",
  field: "Computer Science & Software Engineering",
  position: "Full-Stack Engineer",
  department_id: null,
  department_name: "Computer Science & Software Engineering",
  designation_id: null,
  designation_name: "Full-Stack Engineer",
  organization: "Enterprise Tech",
  years_experience: 3,
  education: "Bachelor of Science in Computer Science",
  current_assignment: "Full-Stack Engineer - Web Platform",
  career_goal: "Lead Solutions Architect",
  preferred_learning_style: "Hands-on projects & labs",
  weekly_hours: "10-15 hours/week",
  current_project_focus: "Cloud microservices & modern web applications",
  skills: [
    { skill: "JavaScript", level: "Advanced", score: 80 },
    { skill: "Python", level: "Intermediate", score: 60 },
    { skill: "SQL", level: "Intermediate", score: 60 },
    { skill: "React.js & Modern Hooks", level: "Advanced", score: 80 }
  ],
  preferred_language: "en",
  status: "ACTIVE",
  created_at: new Date().toISOString()
};
usersDb.set("employee@example.com", defaultRahul);
usersDb.set("usr-rahul-001", defaultRahul);

// Canonical Role Benchmark Taxonomy
const ROLE_BENCHMARKS: Record<string, { domain: string; benchmark_skills: Array<{ skill: string; required_level: string; score: number; importance: number }> }> = {
  "Penetration Tester": {
    domain: "Cybersecurity & Ethical Hacking",
    benchmark_skills: [
      { skill: "Penetration Testing & Ethical Hacking", required_level: "Advanced", score: 85, importance: 1.5 },
      { skill: "Metasploit Framework & Exploit Execution", required_level: "Advanced", score: 80, importance: 1.4 },
      { skill: "Burp Suite & Web Proxy Interception", required_level: "Advanced", score: 80, importance: 1.4 },
      { skill: "OWASP Top 10 Web Application Security", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Kali Linux & Penetration Testing Tools", required_level: "Intermediate", score: 75, importance: 1.2 },
      { skill: "Privilege Escalation & Active Directory Exploitation", required_level: "Intermediate", score: 70, importance: 1.2 },
      { skill: "Linux Systems Administration & Hardening", required_level: "Intermediate", score: 65, importance: 1.1 }
    ]
  },
  "Cybersecurity Analyst": {
    domain: "Cybersecurity & Information Assurance",
    benchmark_skills: [
      { skill: "SIEM Monitoring & Incident Response (Splunk, Wazuh)", required_level: "Advanced", score: 80, importance: 1.4 },
      { skill: "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)", required_level: "Advanced", score: 80, importance: 1.4 },
      { skill: "OWASP Top 10 Web Application Security", required_level: "Intermediate", score: 70, importance: 1.3 },
      { skill: "Identity & Access Management (IAM) & Zero Trust", required_level: "Intermediate", score: 70, importance: 1.2 },
      { skill: "Threat Modeling & MITRE ATT&CK Framework", required_level: "Intermediate", score: 65, importance: 1.2 },
      { skill: "Cryptography, PKI & SSL/TLS", required_level: "Intermediate", score: 65, importance: 1.1 }
    ]
  },
  "Full-Stack Engineer": {
    domain: "Computer Science & Software Engineering",
    benchmark_skills: [
      { skill: "React.js & Modern Hooks", required_level: "Advanced", score: 80, importance: 1.4 },
      { skill: "Next.js & Server Components", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "TypeScript", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "FastAPI (Python)", required_level: "Intermediate", score: 70, importance: 1.3 },
      { skill: "PostgreSQL Administration & Schema Design", required_level: "Intermediate", score: 70, importance: 1.2 },
      { skill: "RESTful API Design & Best Practices", required_level: "Advanced", score: 80, importance: 1.2 },
      { skill: "Docker Containerization & Multi-Stage Builds", required_level: "Intermediate", score: 65, importance: 1.1 },
      { skill: "System Design & Scalability", required_level: "Intermediate", score: 65, importance: 1.1 }
    ]
  },
  "Backend Systems Engineer": {
    domain: "Backend, APIs & Architecture",
    benchmark_skills: [
      { skill: "Python", required_level: "Advanced", score: 85, importance: 1.4 },
      { skill: "FastAPI (Python)", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "RESTful API Design & Best Practices", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Microservices Architecture & Service Mesh", required_level: "Intermediate", score: 75, importance: 1.3 },
      { skill: "PostgreSQL Administration & Schema Design", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Redis Caching & In-Memory Data Structures", required_level: "Intermediate", score: 70, importance: 1.2 },
      { skill: "System Design & Scalability", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Automated Testing & QA (PyTest, Jest, Cypress)", required_level: "Intermediate", score: 70, importance: 1.1 }
    ]
  },
  "Cloud & DevOps Engineer": {
    domain: "Cloud, DevOps & SRE",
    benchmark_skills: [
      { skill: "Docker Containerization & Multi-Stage Builds", required_level: "Advanced", score: 85, importance: 1.4 },
      { skill: "Kubernetes Cluster Orchestration & Helm", required_level: "Advanced", score: 85, importance: 1.4 },
      { skill: "Linux Systems Administration & Hardening", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Terraform & Infrastructure as Code (IaC)", required_level: "Intermediate", score: 75, importance: 1.3 },
      { skill: "CI/CD Pipelines (GitHub Actions / GitLab CI)", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Amazon Web Services (AWS) Core Services", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Observability & Monitoring (Prometheus & Grafana)", required_level: "Intermediate", score: 70, importance: 1.2 },
      { skill: "Site Reliability Engineering (SRE) & Incident Management", required_level: "Intermediate", score: 65, importance: 1.1 }
    ]
  },
  "AI Engineer": {
    domain: "AI, Machine Learning & Data Science",
    benchmark_skills: [
      { skill: "Large Language Models & Prompt Engineering", required_level: "Advanced", score: 85, importance: 1.5 },
      { skill: "RAG (Retrieval-Augmented Generation) Architectures", required_level: "Advanced", score: 85, importance: 1.5 },
      { skill: "Python", required_level: "Expert", score: 90, importance: 1.4 },
      { skill: "Vector Databases & Semantic Embeddings", required_level: "Advanced", score: 80, importance: 1.4 },
      { skill: "Deep Learning & Neural Networks (PyTorch / TensorFlow)", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "Natural Language Processing (Hugging Face Transformers)", required_level: "Advanced", score: 80, importance: 1.3 },
      { skill: "MLOps, Model Registry & Serving (MLflow, Triton)", required_level: "Intermediate", score: 70, importance: 1.2 },
      { skill: "FastAPI (Python)", required_level: "Intermediate", score: 70, importance: 1.2 }
    ]
  },
  "Data Engineer": {
    domain: "Data Science & Big Data",
    benchmark_skills: [
      { skill: "Data Engineering Pipelines (Apache Airflow, Spark)", required_level: "Advanced", score: 85, importance: 1.5 },
      { skill: "Data Warehousing (Snowflake / BigQuery)", required_level: "Advanced", score: 85, importance: 1.4 },
      { skill: "SQL", required_level: "Expert", score: 90, importance: 1.4 },
      { skill: "Python", required_level: "Advanced", score: 85, importance: 1.3 },
      { skill: "Apache Kafka Streaming", required_level: "Intermediate", score: 75, importance: 1.3 },
      { skill: "PostgreSQL Administration & Schema Design", required_level: "Advanced", score: 80, importance: 1.2 }
    ]
  }
};

const LEVEL_SCORES: Record<string, number> = {
  Foundation: 20,
  Beginner: 40,
  Intermediate: 60,
  Advanced: 80,
  Expert: 100
};

// Find matching benchmark for any user position
function findBenchmark(position: string) {
  const p = position.toLowerCase();
  if (p.includes("penetrat") || p.includes("ethical hack") || p.includes("pentest") || p.includes("red team")) {
    return ROLE_BENCHMARKS["Penetration Tester"];
  }
  if (p.includes("cyber") || p.includes("soc") || p.includes("infosec") || p.includes("security")) {
    return ROLE_BENCHMARKS["Cybersecurity Analyst"];
  }
  if (p.includes("full") || p.includes("frontend") || p.includes("web developer")) {
    return ROLE_BENCHMARKS["Full-Stack Engineer"];
  }
  if (p.includes("backend") || p.includes("api") || p.includes("systems")) {
    return ROLE_BENCHMARKS["Backend Systems Engineer"];
  }
  if (p.includes("cloud") || p.includes("devops") || p.includes("sre") || p.includes("infra")) {
    return ROLE_BENCHMARKS["Cloud & DevOps Engineer"];
  }
  if (p.includes("ai") || p.includes("llm") || p.includes("machine learning") || p.includes("deep learning")) {
    return ROLE_BENCHMARKS["AI Engineer"];
  }
  if (p.includes("data engineer") || p.includes("etl") || p.includes("pipeline")) {
    return ROLE_BENCHMARKS["Data Engineer"];
  }
  return ROLE_BENCHMARKS["Full-Stack Engineer"];
}

// Call Groq Cloud API for AI evaluation & AI Tutor
async function callGroqAI(prompt: string, systemPrompt: string = "You are a Principal AI Technical Evaluator."): Promise<string | null> {
  const apiKey = process.env.GROQ_API_KEY || process.env.GROK_API_KEY;
  if (!apiKey || apiKey.length < 10) return null;

  try {
    const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey.trim()}`
      },
      body: JSON.stringify({
        model: process.env.GROQ_MODEL || "qwen/qwen3.8-27b",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 350
      })
    });

    if (!res.ok) return null;
    const data = await res.json();
    return data.choices?.[0]?.message?.content || null;
  } catch (err) {
    return null;
  }
}

// Compute dynamic gaps & readiness
async function evaluateUserGaps(user: StoredUser) {
  const benchmark = findBenchmark(user.position || user.designation_name);
  const targetSkills = benchmark.benchmark_skills;

  const userSkillMap: Record<string, number> = {};
  const userSkillLvl: Record<string, string> = {};

  (user.skills || []).forEach((s) => {
    const nameClean = s.skill.toLowerCase().trim();
    const score = LEVEL_SCORES[s.level] || 60;
    userSkillMap[nameClean] = score;
    userSkillLvl[nameClean] = s.level;
  });

  let totalReq = 0;
  let earned = 0;
  const gaps: any[] = [];
  const strengths: any[] = [];

  for (const ts of targetSkills) {
    const reqScore = ts.score;
    const imp = ts.importance;
    totalReq += reqScore * imp;

    const reqClean = ts.skill.toLowerCase().trim();
    let foundScore = 0;
    let foundLvl = "None";

    for (const [uSkill, uScore] of Object.entries(userSkillMap)) {
      if (uSkill === reqClean || uSkill.includes(reqClean) || reqClean.includes(uSkill)) {
        foundScore = uScore;
        foundLvl = userSkillLvl[uSkill] || "Intermediate";
        break;
      }
    }

    earned += Math.min(foundScore, reqScore) * imp;
    const gap = Math.max(0, reqScore - foundScore);

    let priority = "LOW";
    if (gap >= 40) priority = "CRITICAL";
    else if (gap >= 20) priority = "HIGH";
    else if (gap > 0) priority = "MEDIUM";

    const item = {
      skill: ts.skill,
      domain: benchmark.domain,
      current_level: foundLvl,
      required_level: ts.required_level,
      current_score: foundScore,
      required_score: reqScore,
      gap,
      priority_level: priority,
      is_missing: foundScore === 0,
      reason: `${ts.skill} is an essential benchmark competency for ${user.position}.`,
      recommended_action: `Complete targeted practical labs to bridge level to ${ts.required_level}.`
    };

    if (gap > 0) {
      gaps.push(item);
    } else {
      strengths.push({ skill: ts.skill, level: foundLvl, score: foundScore });
    }
  }

  const readiness = Math.round((earned / Math.max(1, totalReq)) * 100);
  const status = readiness >= 80 ? "Ready" : readiness >= 60 ? "Near Ready" : "Needs Development";

  let aiSummary = `Dynamic AI gap evaluation complete for ${user.position}: Evaluated against ${targetSkills.length} critical benchmarks with ${readiness}% baseline readiness.`;

  // Try calling Groq Qwen AI live
  const groqResult = await callGroqAI(
    `Candidate Profile: Role=${user.position}, Experience=${user.years_experience} yrs.
Declared Skills: ${(user.skills || []).map((s) => `${s.skill} (${s.level})`).join(", ")}.
Critical Gaps: ${gaps.slice(0, 3).map((g) => g.skill).join(", ")}.
Provide a concise 2-sentence executive technical evaluation.`,
    "You are a Principal AI Competency Advisor. Give concise, highly technical insights."
  );

  if (groqResult) {
    aiSummary = groqResult.trim();
  }

  return {
    user_id: user.id,
    target_role: user.position,
    industry_field: user.field,
    overall_readiness_percentage: readiness,
    status,
    total_competencies_evaluated: targetSkills.length,
    critical_gaps_count: gaps.filter((g) => g.priority_level === "CRITICAL").length,
    high_gaps_count: gaps.filter((g) => g.priority_level === "HIGH").length,
    gaps,
    strengths,
    ai_evaluation_summary: aiSummary
  };
}

// Generate targeted learning recommendations
function getRecommendationsForUser(user: StoredUser, gaps: any[]) {
  const topGaps = gaps.slice(0, 4);
  return topGaps.map((g, idx) => ({
    id: `rec-${idx + 1}`,
    resource_id: `res-${idx + 1}`,
    competency_id: `comp-${idx + 1}`,
    title: `${g.skill} Mastery & Production Implementation`,
    description: `Targeted interactive curriculum focused on bridging ${g.current_level} to ${g.required_level} through real-world projects and code reviews.`,
    provider: idx % 2 === 0 ? "iGOT Karmayogi" : "NSSTA Official Academy",
    course_type: "Interactive Course & Lab",
    url: "https://igotkarmayogi.gov.in",
    duration_hours: 12 + idx * 4,
    difficulty: g.required_level,
    score_impact_estimate: Math.min(25, g.gap),
    rationale: `Directly bridges your ${g.priority_level} gap in ${g.skill} for your target role as ${user.position}.`,
    is_enrolled: false
  }));
}

// Generate 4-Phase Learning Path
function getLearningPathForUser(user: StoredUser, gaps: any[]) {
  return {
    user_id: user.id,
    role_title: user.position,
    total_hours_estimated: 64,
    completed_hours: 12,
    progress_percentage: 18.5,
    phases: [
      {
        phase_number: 1,
        title: "Phase 1: Core Foundations & Fast-Track Bridging",
        status: "IN_PROGRESS",
        target_skills: gaps.slice(0, 2).map((g) => g.skill),
        estimated_weeks: 2
      },
      {
        phase_number: 2,
        title: "Phase 2: Architectural Deep Dive & Labs",
        status: "NOT_STARTED",
        target_skills: gaps.slice(2, 4).map((g) => g.skill),
        estimated_weeks: 3
      },
      {
        phase_number: 3,
        title: "Phase 3: Production Security, CI/CD & Reliability",
        status: "NOT_STARTED",
        target_skills: ["System Design & Scalability", "CI/CD Pipelines"],
        estimated_weeks: 3
      },
      {
        phase_number: 4,
        title: "Phase 4: Capstone Assessment & Lead Certification",
        status: "NOT_STARTED",
        target_skills: ["Capstone Architectural Review"],
        estimated_weeks: 2
      }
    ]
  };
}

// Global router handler for all HTTP methods
export async function GET(request: NextRequest, { params }: { params: { slug?: string[] } }) {
  return handleRequest(request, params, "GET");
}

export async function POST(request: NextRequest, { params }: { params: { slug?: string[] } }) {
  return handleRequest(request, params, "POST");
}

export async function PUT(request: NextRequest, { params }: { params: { slug?: string[] } }) {
  return handleRequest(request, params, "PUT");
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

async function handleRequest(request: NextRequest, params: { slug?: string[] }, method: string) {
  const rawSlug = params.slug || [];
  // Strip optional 'v1' prefix so /api/v1/auth/register and /api/auth/register both resolve to auth/register
  const slug = rawSlug.length > 0 && rawSlug[0] === "v1" ? rawSlug.slice(1) : rawSlug;
  const path = slug.join("/");

  const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  };

  // 1. Health Endpoint (/api/health or /api)
  if (!path || path === "health") {
    return NextResponse.json(
      {
        status: "ok",
        service: "StatKarmaYogi Skill Intelligence Platform",
        environment: "production",
        engine: "Next.js Native Edge + Groq Qwen AI"
      },
      { headers }
    );
  }

  // 2. Auth Options (/api/auth/options)
  if (path === "auth/options") {
    const options = {
      job_fields: [
        {
          field_name: "Cybersecurity & Information Assurance",
          positions: [
            "Penetration Tester / Ethical Hacker",
            "SOC Analyst (Level 1/2)",
            "Cybersecurity Incident Responder",
            "Application Security (AppSec) Engineer",
            "Cloud Security Architect",
            "Custom Position"
          ]
        },
        {
          field_name: "Computer Science & Software Engineering",
          positions: [
            "Full-Stack Engineer",
            "Backend Systems Engineer",
            "Frontend / UI Engineer",
            "DevOps & Platform Engineer",
            "Site Reliability Engineer (SRE)",
            "Custom Position"
          ]
        },
        {
          field_name: "AI, Machine Learning & Data Science",
          positions: [
            "AI / Generative AI Solutions Engineer",
            "Machine Learning Engineer",
            "Data Scientist / Statistical Analyst",
            "Data Platform / ETL Engineer",
            "Custom Position"
          ]
        }
      ],
      skills_by_category: [
        {
          category_name: "Cybersecurity & Ethical Hacking",
          skills: [
            "Penetration Testing & Ethical Hacking",
            "Metasploit Framework & Exploit Execution",
            "Burp Suite & Web Proxy Interception",
            "OWASP Top 10 Web Application Security",
            "Network Vulnerability Assessment & Port Scanning (Nmap, Wireshark)",
            "Kali Linux & Penetration Testing Tools",
            "SIEM Monitoring & Incident Response (Splunk, Wazuh)",
            "Privilege Escalation & Active Directory Exploitation",
            "Identity & Access Management (IAM) & Zero Trust",
            "Cryptography, PKI & SSL/TLS"
          ]
        },
        {
          category_name: "Programming Languages & Core Tech",
          skills: [
            "Python",
            "JavaScript",
            "TypeScript",
            "SQL",
            "Go (Golang)",
            "Rust",
            "Java & Spring Boot",
            "C++ Systems Programming",
            "Bash & Linux Shell Scripting",
            "HTML5 & Semantic Markup"
          ]
        },
        {
          category_name: "Backend, APIs & Architecture",
          skills: [
            "FastAPI (Python)",
            "Node.js & Express / NestJS",
            "RESTful API Design & Best Practices",
            "GraphQL APIs",
            "Microservices Architecture & Service Mesh",
            "System Design & Scalability",
            "Celery & Asynchronous Task Queues",
            "Redis Caching & In-Memory Data Structures",
            "RabbitMQ & Message Brokers",
            "WebSockets & Real-time Communication"
          ]
        },
        {
          category_name: "Frontend & Web Engineering",
          skills: [
            "React.js & Modern Hooks",
            "Next.js & Server Components",
            "Tailwind CSS & Responsive Layouts",
            "Redux Toolkit & State Management",
            "Vue.js (Composition API)",
            "Angular Framework",
            "CSS3, Flexbox & Grid Systems",
            "Web Performance & Core Web Vitals",
            "Web Accessibility (WCAG 2.1)",
            "Vite & Modern Frontend Tooling"
          ]
        },
        {
          category_name: "Cloud, DevOps & SRE",
          skills: [
            "Docker Containerization & Multi-Stage Builds",
            "Kubernetes Cluster Orchestration & Helm",
            "Amazon Web Services (AWS) Core Services",
            "Microsoft Azure Cloud Infrastructure",
            "Google Cloud Platform (GCP)",
            "CI/CD Pipelines (GitHub Actions / GitLab CI)",
            "Terraform & Infrastructure as Code (IaC)",
            "Linux Systems Administration & Hardening",
            "Observability & Monitoring (Prometheus & Grafana)",
            "Site Reliability Engineering (SRE) & Incident Management"
          ]
        },
        {
          category_name: "AI, Machine Learning & Data Science",
          skills: [
            "Large Language Models & Prompt Engineering",
            "RAG (Retrieval-Augmented Generation) Architectures",
            "PyTorch Deep Learning Framework",
            "TensorFlow & Keras",
            "Scikit-Learn Machine Learning Algorithms",
            "Natural Language Processing (Hugging Face Transformers)",
            "Vector Databases & Semantic Embeddings",
            "Pandas, NumPy & Exploratory Data Analysis",
            "MLOps, Model Registry & Serving (MLflow, Triton)",
            "Computer Vision (OpenCV & YOLO)"
          ]
        }
      ],
      proficiency_levels: [
        { code: "Foundation", name: "Foundation (Level 1)", numeric_score: 20 },
        { code: "Beginner", name: "Beginner (Level 2)", numeric_score: 40 },
        { code: "Intermediate", name: "Intermediate (Level 3)", numeric_score: 60 },
        { code: "Advanced", name: "Advanced (Level 4)", numeric_score: 80 },
        { code: "Expert", name: "Expert (Level 5)", numeric_score: 100 }
      ],
      qualifications: [
        "Bachelor of Science in Computer Science / Engineering",
        "Master of Science in Computer Science / AI / Data Science",
        "Bachelor of Technology (B.Tech / B.E.)",
        "Master of Technology (M.Tech)",
        "Bachelor's Degree in Mathematics / Statistics",
        "Master's Degree in Statistics / Econometrics",
        "Professional Coding Bootcamp Graduate",
        "Self-Taught / Open Source Contributor",
        "Ph.D. in Computer Science / Artificial Intelligence"
      ]
    };
    return NextResponse.json(options, { headers });
  }

  // Extract auth token if provided
  const authHeader = request.headers.get("authorization") || "";
  const token = authHeader.replace(/^Bearer\s+/i, "").trim();

  // 3. User Registration (/api/auth/register)
  if (path === "auth/register" && method === "POST") {
    try {
      const body = await request.json();
      const email = (body.email || "").toLowerCase().trim();
      if (!email) {
        return NextResponse.json({ detail: "Email address is required." }, { status: 400, headers });
      }

      const userId = "usr-" + Date.now().toString(36);
      const newUser: StoredUser = {
        id: userId,
        email,
        first_name: body.first_name || "Candidate",
        last_name: body.last_name || "",
        role: body.role || "EMPLOYEE",
        field: body.field || "Computer Science & Software Engineering",
        position: body.position || "Full-Stack Engineer",
        department_id: null,
        department_name: body.field || "Computer Science & Software Engineering",
        designation_id: null,
        designation_name: body.position || "Full-Stack Engineer",
        organization: body.organization || "Enterprise Tech",
        years_experience: Number(body.years_experience) || 0,
        education: body.education || "Bachelor of Science in Computer Science",
        current_assignment: `${body.position || "Full-Stack Engineer"} - ${body.field || "Tech"}`,
        career_goal: body.career_goal || body.position || "Lead Solutions Architect",
        preferred_learning_style: body.preferred_learning_style || "Hands-on projects & labs",
        weekly_hours: body.weekly_hours || "10-15 hours/week",
        current_project_focus: body.current_project_focus || "Building production web services & APIs",
        skills: body.skills || [],
        preferred_language: body.preferred_language || "en",
        status: "ACTIVE",
        created_at: new Date().toISOString()
      };

      // Run dynamic AI gap evaluation
      const evaluatedGaps = await evaluateUserGaps(newUser);
      newUser.ai_profile = evaluatedGaps;

      // Save user to memory store
      usersDb.set(email, newUser);
      usersDb.set(userId, newUser);

      const accessToken = `stat_jwt_${userId}_${Buffer.from(email).toString("base64")}`;
      usersDb.set(accessToken, newUser);

      return NextResponse.json(
        {
          access_token: accessToken,
          token_type: "bearer",
          user: newUser
        },
        { headers }
      );
    } catch (err: any) {
      return NextResponse.json({ detail: `Registration processing error: ${err.message}` }, { status: 500, headers });
    }
  }

  // 4. User Login (/api/auth/login)
  if (path === "auth/login" && method === "POST") {
    try {
      const body = await request.json();
      const email = (body.email || "").toLowerCase().trim();
      let user = usersDb.get(email) || defaultRahul;

      const accessToken = `stat_jwt_${user.id}_${Buffer.from(user.email).toString("base64")}`;
      usersDb.set(accessToken, user);

      return NextResponse.json(
        {
          access_token: accessToken,
          token_type: "bearer",
          user
        },
        { headers }
      );
    } catch (err: any) {
      return NextResponse.json({ detail: err.message }, { status: 500, headers });
    }
  }

  // Resolve active user from token or fallback to Rahul
  const activeUser = usersDb.get(token) || Array.from(usersDb.values()).pop() || defaultRahul;

  // 5. Current User Profile (/api/auth/me)
  if (path === "auth/me") {
    return NextResponse.json(activeUser, { headers });
  }

  // 6. User Competencies (/api/competencies/me)
  if (path === "competencies/me") {
    const gapsObj = activeUser.ai_profile || (await evaluateUserGaps(activeUser));
    const compList = (activeUser.skills || []).map((s, idx) => ({
      id: `comp-${idx + 1}`,
      competency_code: s.skill.toUpperCase().replace(/[^A-Z0-9]/g, "_").slice(0, 15),
      competency_name: s.skill,
      domain_name: activeUser.field,
      score: LEVEL_SCORES[s.level] || 60,
      level: s.level,
      confidence: 0.85,
      last_assessed: new Date().toISOString()
    }));
    return NextResponse.json(compList, { headers });
  }

  // 7. Skill Gaps (/api/skill-gaps/me or /api/skill-gaps/reanalyze)
  if (path === "skill-gaps/me" || path === "skill-gaps/reanalyze") {
    const gapsObj = await evaluateUserGaps(activeUser);
    activeUser.ai_profile = gapsObj;
    return NextResponse.json(gapsObj, { headers });
  }

  // 8. Recommendations (/api/recommendations/me or /api/recommendations/generate)
  if (path === "recommendations/me" || path === "recommendations/generate") {
    const gapsObj = activeUser.ai_profile || (await evaluateUserGaps(activeUser));
    const recs = getRecommendationsForUser(activeUser, gapsObj.gaps || []);
    return NextResponse.json(recs, { headers });
  }

  // 9. Learning Path (/api/learning/paths/me or /api/learning/paths/recalculate)
  if (path === "learning/paths/me" || path === "learning/paths/recalculate") {
    const gapsObj = activeUser.ai_profile || (await evaluateUserGaps(activeUser));
    const pathData = getLearningPathForUser(activeUser, gapsObj.gaps || []);
    return NextResponse.json(pathData, { headers });
  }

  // 10. Assessments List (/api/assessments)
  if (path === "assessments") {
    return NextResponse.json(
      [
        {
          id: "diag-eval-001",
          title: `${activeUser.position} Baseline Competency Assessment`,
          assessment_type: "DIAGNOSTIC",
          description: `Adaptive technical evaluation measuring production competency in ${activeUser.position}.`,
          question_count: 6,
          duration_minutes: 20,
          passing_score: 75.0,
          total_attempts: 1,
          is_active: true
        }
      ],
      { headers }
    );
  }

  // 11. Generate Assessment for Gaps (/api/assessments/generate-for-gaps)
  if (path === "assessments/generate-for-gaps") {
    const assessmentId = "assess-gen-" + Date.now();
    return NextResponse.json(
      {
        id: assessmentId,
        title: `Targeted Technical Assessment: ${activeUser.position}`,
        assessment_type: "GAP_ASSESSMENT",
        duration_minutes: 15,
        total_questions: 5
      },
      { headers }
    );
  }

  // 12. Assessment Detail (/api/assessments/[id])
  if (path.startsWith("assessments/")) {
    const id = path.split("/")[1];
    return NextResponse.json(
      {
        id,
        title: `${activeUser.position} Technical Assessment`,
        assessment_type: "DIAGNOSTIC",
        description: "Adaptive technical evaluation across your core benchmark competencies.",
        duration_minutes: 20,
        passing_score: 75,
        questions: [
          {
            id: "q-1",
            question_text: `In production environments for ${activeUser.position}, what is the primary architecture best practice to ensure high availability and zero-downtime deployments?`,
            difficulty: "INTERMEDIATE",
            options: [
              { id: "opt-1", option_text: "Blue-green or rolling deployments behind a load balancer with automated health checks", order_index: 0 },
              { id: "opt-2", option_text: "Directly restarting the single container instance during peak traffic", order_index: 1 },
              { id: "opt-3", option_text: "Hardcoding API secrets in git repositories for faster deployments", order_index: 2 },
              { id: "opt-4", option_text: "Disabling TLS certificate verification on public endpoints", order_index: 3 }
            ]
          },
          {
            id: "q-2",
            question_text: "Which mechanism provides the most robust protection against OWASP Top 10 SQL Injection and Cross-Site Scripting (XSS)?",
            difficulty: "INTERMEDIATE",
            options: [
              { id: "opt-5", option_text: "Parameterized queries with ORM abstraction and context-aware HTML output encoding", order_index: 0 },
              { id: "opt-6", option_text: "Disabling all client-side form validation", order_index: 1 },
              { id: "opt-7", option_text: "Using string concatenation to build raw SQL queries", order_index: 2 },
              { id: "opt-8", option_text: "Relying strictly on firewall port blocking", order_index: 3 }
            ]
          }
        ]
      },
      { headers }
    );
  }

  // 13. AI Tutor Chat (/api/tutor/chat)
  if (path === "tutor/chat" && method === "POST") {
    try {
      const body = await request.json();
      const userMessage = body.message || "";

      let answer = `As your Technical Mentor for **${activeUser.position}**, here is my guidance:\n\n${userMessage ? `Regarding your question about "${userMessage}":` : ""}\n\n1. **Core Concept**: Focus on modular, test-driven design and adhere strictly to enterprise production standards.\n2. **Hands-On Practice**: Build practical implementations and verify them using automated integration tests.\n3. **Production Tip**: Always monitor latency, error rates, and security boundaries.`;

      // Try live Groq Qwen AI
      const groqAnswer = await callGroqAI(
        `User is targeting role: ${activeUser.position} with ${activeUser.years_experience} years experience.
User question: "${userMessage}".
Answer as an authoritative, concise, and highly practical technical mentor. Provide actionable steps and code guidance where appropriate.`,
        `You are a Senior Principal Technical Architect and Mentor for ${activeUser.position}. Provide accurate, encouraging, and production-tested advice.`
      );

      if (groqAnswer) {
        answer = groqAnswer;
      }

      return NextResponse.json(
        {
          id: "tutor-" + Date.now(),
          role: "assistant",
          content: answer,
          confidence: 0.96,
          citations: ["Production Architecture Handbook", "Industry OWASP & Cloud Standards"],
          created_at: new Date().toISOString()
        },
        { headers }
      );
    } catch (err: any) {
      return NextResponse.json({ detail: err.message }, { status: 500, headers });
    }
  }

  // 14. Admin Endpoints
  if (path === "admin/dashboard") {
    return NextResponse.json(
      {
        total_employees: usersDb.size,
        overall_readiness_avg: 74.2,
        critical_skill_gaps_count: 8,
        total_assessments_taken: 142,
        active_learning_hours: 1240,
        departments_count: 4
      },
      { headers }
    );
  }

  if (path === "admin/heatmap") {
    return NextResponse.json(
      {
        domains: ["Cybersecurity", "Programming", "Cloud/DevOps", "AI/ML"],
        levels: ["Foundation", "Beginner", "Intermediate", "Advanced", "Expert"],
        matrix: [
          [10, 25, 45, 15, 5],
          [5, 20, 50, 20, 5],
          [15, 30, 35, 15, 5],
          [20, 35, 30, 10, 5]
        ]
      },
      { headers }
    );
  }

  // Default Fallback
  return NextResponse.json(
    {
      message: "StatKarmaYogi API Endpoint",
      path,
      user: activeUser.email
    },
    { headers }
  );
}
