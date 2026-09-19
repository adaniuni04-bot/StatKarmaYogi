const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://localhost:8000/api");

export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("stat_auth_token");
  }
  return null;
}

export function setToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("stat_auth_token", token);
    window.dispatchEvent(new Event("stat_auth_change"));
  }
}

export function removeToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("stat_auth_token");
    localStorage.removeItem("stat_active_user");
    window.dispatchEvent(new Event("stat_auth_change"));
  }
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const text = await res.text();
      try {
        const errJson = JSON.parse(text);
        if (typeof errJson.detail === "string") {
          errorDetail = errJson.detail;
        } else if (Array.isArray(errJson.detail)) {
          errorDetail = errJson.detail.map((d: any) => (d.loc ? `${d.loc.slice(-1)}: ${d.msg}` : d.msg)).join("; ");
        } else if (errJson.error?.message) {
          errorDetail = errJson.error.message;
        } else if (errJson.message) {
          errorDetail = errJson.message;
        } else {
          errorDetail = JSON.stringify(errJson);
        }
      } catch {
        // Not JSON: extract error from HTML title, pre, code, or plain text
        const titleMatch = text.match(/<title>([^<]+)<\/title>/i);
        const h1Match = text.match(/<h1[^>]*>([^<]+)<\/h1>/i);
        const preMatch = text.match(/<pre[^>]*>([\s\S]*?)<\/pre>/i);
        const codeMatch = text.match(/<code>([^<]+)<\/code>/i);

        if (preMatch && preMatch[1]) {
          errorDetail = `Server Error: ${preMatch[1].trim()}`;
        } else if (codeMatch && codeMatch[1]) {
          errorDetail = `Server Error: ${codeMatch[1].trim()}`;
        } else if (titleMatch && titleMatch[1]) {
          errorDetail = `Server Error: ${titleMatch[1].trim()}`;
        } else if (h1Match && h1Match[1]) {
          errorDetail = `Server Error: ${h1Match[1].trim()}`;
        } else if (text && text.trim().length > 0) {
          const cleanText = text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
          errorDetail = cleanText.length > 200 ? cleanText.substring(0, 200) + "..." : cleanText;
        } else if (res.statusText) {
          errorDetail = `${res.status}: ${res.statusText}`;
        }
      }
    } catch {
      errorDetail = res.statusText || `HTTP Error ${res.status}`;
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Auth & Live Registration
  login: (email: string, password: string) =>
    apiRequest<any>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (registrationData: any) =>
    apiRequest<any>("/auth/register", {
      method: "POST",
      body: JSON.stringify(registrationData),
    }),
  getRegistrationOptions: () => apiRequest<any>("/auth/options"),
  getMe: () => apiRequest<any>("/auth/me"),
  logout: () => apiRequest<any>("/auth/logout", { method: "POST" }),

  // Competencies
  getMyCompetencies: () => apiRequest<any[]>("/competencies/me"),
  getMyCompetencyHistory: () => apiRequest<any[]>("/competencies/history"),
  listCompetencyFramework: () => apiRequest<any[]>("/competencies"),

  // Skill Gaps
  getMySkillGaps: () => apiRequest<any>("/skill-gaps/me"),
  compareCareerRole: (target_designation_id: string) =>
    apiRequest<any>("/skill-gaps/career-compare", {
      method: "POST",
      body: JSON.stringify({ target_designation_id }),
    }),

  // Recommendations
  getMyRecommendations: () => apiRequest<any[]>("/recommendations/me"),
  generateRecommendations: () =>
    apiRequest<any[]>("/recommendations/generate", { method: "POST" }),

  // Learning Paths & Resources
  getMyLearningPath: () => apiRequest<any>("/learning/paths/me"),
  recalculateLearningPath: () =>
    apiRequest<any>("/learning/paths/recalculate", { method: "POST" }),
  listResources: (provider?: string) =>
    apiRequest<any[]>(`/learning/resources${provider ? `?provider=${provider}` : ""}`),
  enrollResource: (resource_id: string) =>
    apiRequest<any>(`/learning/resources/${resource_id}/enroll`, { method: "POST" }),

  // Assessments
  listAssessments: () => apiRequest<any[]>("/assessments"),
  getAssessmentDetail: (id: string) => apiRequest<any>(`/assessments/${id}`),
  generateGapAssessment: () =>
    apiRequest<any>("/assessments/generate-for-gaps", { method: "POST" }),
  reanalyzeSkillGaps: (data: any) =>
    apiRequest<any>("/skill-gaps/reanalyze", { method: "POST", body: JSON.stringify(data) }),
  startAssessment: (id: string) =>
    apiRequest<any>(`/assessments/${id}/start`, { method: "POST" }),
  submitAssessment: (id: string, attempt_id: string, answers: any[], time_taken_seconds: number) =>
    apiRequest<any>(`/assessments/${id}/submit`, {
      method: "POST",
      body: JSON.stringify({ attempt_id, answers, time_taken_seconds }),
    }),

  // AI Tutor
  chatTutor: (message: string, session_id?: string, language: string = "en") =>
    apiRequest<any>("/tutor/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id, language }),
    }),
  listTutorSessions: () => apiRequest<any[]>("/tutor/sessions"),
  getTutorSession: (id: string) => apiRequest<any>(`/tutor/sessions/${id}`),

  // Documents & RAG
  listDocuments: () => apiRequest<any[]>("/documents"),
  uploadDocument: (formData: FormData) =>
    apiRequest<any>("/documents/upload", {
      method: "POST",
      body: formData,
    }),
  generateQuizFromDocument: (documentId: string) =>
    apiRequest<any>(`/documents/${documentId}/generate-quiz`, {
      method: "POST",
    }),

  // AI Question Generation & Review
  generateQuestions: (competency_code: string, count: number = 3, difficulty: string = "INTERMEDIATE") =>
    apiRequest<any>("/quiz/generate", {
      method: "POST",
      body: JSON.stringify({ competency_code, count, difficulty }),
    }),
  listReviewQuestions: () => apiRequest<any[]>("/quiz/questions"),
  reviewQuestion: (question_id: string, action: string, edited_text?: string) =>
    apiRequest<any>(`/quiz/questions/${question_id}/review`, {
      method: "POST",
      body: JSON.stringify({ question_id, action, edited_text }),
    }),

  // Admin & Analytics
  getAdminDashboard: () => apiRequest<any>("/admin/dashboard"),
  getAdminHeatmap: () => apiRequest<any>("/admin/heatmap"),
  getDepartmentStats: () => apiRequest<any[]>("/admin/departments"),
  getFutureSkills: () => apiRequest<any[]>("/admin/future-skills"),
  getAuditLogs: () => apiRequest<any[]>("/admin/audit-logs"),
  listAllUsers: () => apiRequest<any[]>("/admin/users"),

  // Integrations
  getIntegrationStatus: () => apiRequest<any>("/integrations/status"),
  syncIgot: () => apiRequest<any>("/integrations/igot/sync", { method: "POST" }),
  syncNssta: () => apiRequest<any>("/integrations/nssta/sync", { method: "POST" }),
};
