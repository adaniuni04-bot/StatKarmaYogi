"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  SlidersHorizontal,
  Users,
  Grid,
  TrendingUp,
  Cpu,
  FileText,
  CheckSquare,
  Shield,
  Upload,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Sparkles
} from "lucide-react";

export default function AdminTrainerPage() {
  const [activeTab, setActiveTab] = useState<string>("OVERVIEW");
  const [dashboard, setDashboard] = useState<any>(null);
  const [heatmap, setHeatmap] = useState<any>(null);
  const [departments, setDepartments] = useState<any[]>([]);
  const [futureSkills, setFutureSkills] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [reviewQuestions, setReviewQuestions] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Question generator state
  const [genCompCode, setGenCompCode] = useState("SAMPLING");
  const [genCount, setGenCount] = useState(2);
  const [generating, setGenerating] = useState(false);

  // Document upload state
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [dash, heat, depts, fut, logs, qList, docs] = await Promise.all([
        api.getAdminDashboard().catch(() => null),
        api.getAdminHeatmap().catch(() => null),
        api.getDepartmentStats().catch(() => []),
        api.getFutureSkills().catch(() => []),
        api.getAuditLogs().catch(() => []),
        api.listReviewQuestions().catch(() => []),
        api.listDocuments().catch(() => []),
      ]);
      setDashboard(dash);
      setHeatmap(heat);
      setDepartments(depts);
      setFutureSkills(fut);
      setAuditLogs(logs);
      setReviewQuestions(qList);
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuestions = async () => {
    try {
      setGenerating(true);
      await api.generateQuestions(genCompCode, genCount);
      const updated = await api.listReviewQuestions();
      setReviewQuestions(updated);
      alert("Generated and validated questions successfully!");
    } catch (err: any) {
      alert("Generation failed: " + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleReview = async (qId: string, action: string) => {
    try {
      await api.reviewQuestion(qId, action);
      const updated = await api.listReviewQuestions();
      setReviewQuestions(updated);
    } catch (err: any) {
      alert("Action failed: " + err.message);
    }
  };

  const handleUploadDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle) return;
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("title", uploadTitle);
      formData.append("authority_tier", "TIER_A");
      formData.append("source_organization", "MoSPI");

      await api.uploadDocument(formData);
      const updated = await api.listDocuments();
      setDocuments(updated);
      setUploadTitle("");
      setUploadFile(null);
      alert("Document uploaded, normalized, chunked, and vector-indexed!");
    } catch (err: any) {
      alert("Upload failed: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Admin & Trainer Studio...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gov-navy flex items-center space-x-2">
            <SlidersHorizontal className="w-6 h-6 text-gov-saffron" />
            <span>Official Statistical Administration & Training Studio</span>
          </h1>
          <p className="text-xs text-slate-600 mt-1">
            Organization-wide skill intelligence, departmental heatmaps, training effectiveness metrics, and AI question review.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2 text-xs">
        {[
          { id: "OVERVIEW", label: "Executive Overview", icon: Users },
          { id: "HEATMAP", label: "Organization Heatmap", icon: Grid },
          { id: "EFFECTIVENESS", label: "Training Effectiveness", icon: TrendingUp },
          { id: "FUTURE", label: "Future Skills Forecasting", icon: Cpu },
          { id: "QUESTIONS", label: "AI Question Studio", icon: CheckSquare },
          { id: "DOCS", label: "Documents & RAG", icon: FileText },
          { id: "AUDIT", label: "Security & Audit Logs", icon: Shield },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-2 rounded-lg font-bold flex items-center space-x-1.5 transition ${
                activeTab === tab.id
                  ? "bg-gov-navy text-white shadow-xs"
                  : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "OVERVIEW" && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-gov-border shadow-2xs">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Total Officials</div>
              <div className="text-3xl font-black text-gov-navy mt-1">{dashboard?.total_employees || 0}</div>
              <div className="text-[11px] text-slate-500 mt-1">Across 4 key divisions</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-gov-border shadow-2xs">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Org Readiness</div>
              <div className="text-3xl font-black text-gov-blue mt-1">{dashboard?.org_average_readiness || 0}%</div>
              <div className="text-[11px] text-slate-500 mt-1">Weighted statutory readiness</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-gov-border shadow-2xs">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Critical Gaps</div>
              <div className="text-3xl font-black text-red-600 mt-1">{dashboard?.critical_gaps_total || 0}</div>
              <div className="text-[11px] text-slate-500 mt-1">Requiring priority training</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-gov-border shadow-2xs">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Active Learning Paths</div>
              <div className="text-3xl font-black text-emerald-700 mt-1">{dashboard?.active_learning_paths || 0}</div>
              <div className="text-[11px] text-slate-500 mt-1">Enrolled in upskilling</div>
            </div>
          </div>

          {/* Department Breakdown */}
          <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
            <h2 className="text-base font-bold text-slate-900">Divisional Readiness Comparison</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {departments.map((dept) => (
                <div key={dept.department_id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 text-xs">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-slate-900">{dept.department_name}</h3>
                    <span className="font-bold text-gov-blue bg-blue-100 px-2 py-0.5 rounded">
                      {dept.avg_role_readiness}% Ready
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-600 pt-1">
                    <span>Officials: {dept.employee_count}</span>
                    <span>Avg Score: {dept.avg_competency_score}</span>
                    <span>Critical Gaps: {dept.critical_gaps_count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: HEATMAP */}
      {activeTab === "HEATMAP" && (
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Organization Competency Heatmap</h2>
            <p className="text-xs text-slate-500">Rows represent competencies; columns represent divisions. Color intensity signals proficiency.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs">
              <thead className="bg-slate-50 text-slate-700 font-bold">
                <tr>
                  <th className="px-4 py-3 text-left">Competency</th>
                  {heatmap?.departments?.map((d: string) => (
                    <th key={d} className="px-4 py-3 text-center">{d}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {heatmap?.competencies?.map((compName: string) => (
                  <tr key={compName}>
                    <td className="px-4 py-2.5 font-bold text-slate-900">{compName}</td>
                    {heatmap?.departments?.map((deptName: string) => {
                      const cell = heatmap.matrix?.find(
                        (m: any) => m.competency_name === compName && m.department_name === deptName
                      );
                      const score = cell?.average_score || 45;
                      const isMet = score >= 65;
                      return (
                        <td key={deptName} className="px-4 py-2.5 text-center">
                          <span
                            className={`inline-block px-2.5 py-1 rounded font-bold ${
                              score >= 70
                                ? "bg-emerald-100 text-emerald-800"
                                : score >= 50
                                ? "bg-blue-100 text-gov-blue"
                                : score >= 35
                                ? "bg-amber-100 text-amber-800"
                                : "bg-red-100 text-red-800"
                            }`}
                          >
                            {score}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: TRAINING EFFECTIVENESS */}
      {activeTab === "EFFECTIVENESS" && (
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Training Effectiveness (Before vs. After Delta)</h2>
            <p className="text-xs text-slate-500">Demonstrating measurable competency score growth before and after completed iGOT and NSSTA programmes.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs">
              <thead className="bg-slate-50 text-slate-700 font-bold">
                <tr>
                  <th className="px-4 py-3 text-left">Competency</th>
                  <th className="px-4 py-3 text-left">Domain</th>
                  <th className="px-4 py-3 text-center">Before Training</th>
                  <th className="px-4 py-3 text-center">After Training</th>
                  <th className="px-4 py-3 text-center">Net Improvement</th>
                  <th className="px-4 py-3 text-center">Completion Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {dashboard?.training_effectiveness?.map((item: any) => (
                  <tr key={item.competency_name} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-bold text-slate-900">{item.competency_name}</td>
                    <td className="px-4 py-3 text-slate-500">{item.domain_name}</td>
                    <td className="px-4 py-3 text-center font-semibold text-slate-600">{item.before_training_score}</td>
                    <td className="px-4 py-3 text-center font-bold text-gov-blue">{item.after_training_score}</td>
                    <td className="px-4 py-3 text-center">
                      <span className="px-2.5 py-0.5 rounded font-black bg-emerald-100 text-emerald-800">
                        +{item.improvement} pts
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center font-medium text-slate-700">{item.completion_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: FUTURE SKILLS */}
      {activeTab === "FUTURE" && (
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Future Skills Intelligence & Trend Forecasting</h2>
            <p className="text-xs text-slate-500">Forecasting emerging technological requirements for official statistics over 2026–2030.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {futureSkills.map((f) => (
              <div key={f.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/40 space-y-2 text-xs">
                <div className="flex justify-between items-start">
                  <h3 className="font-bold text-slate-900 text-sm">{f.name}</h3>
                  <span className="bg-red-100 text-red-700 font-bold px-2 py-0.5 rounded text-[10px]">
                    {f.priority} PRIORITY
                  </span>
                </div>
                <div className="text-slate-500 text-[11px]">Domain: {f.domain} • Source: {f.trend_source}</div>

                <div className="grid grid-cols-3 gap-2 py-1 text-center bg-white p-2 rounded border border-slate-200">
                  <div>
                    <div className="text-[9px] text-slate-400 uppercase">Current Readiness</div>
                    <div className="font-bold text-slate-700">{f.current_readiness}%</div>
                  </div>
                  <div>
                    <div className="text-[9px] text-slate-400 uppercase">Expected Target</div>
                    <div className="font-bold text-gov-blue">{f.expected_importance}%</div>
                  </div>
                  <div>
                    <div className="text-[9px] text-slate-400 uppercase">Projected Gap</div>
                    <div className="font-bold text-red-600">{f.gap}%</div>
                  </div>
                </div>

                <div className="text-[11px] text-slate-600 pt-1">
                  <span className="font-semibold text-slate-800">Target Training: </span>
                  {f.recommended_training}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: QUESTION STUDIO */}
      {activeTab === "QUESTIONS" && (
        <div className="space-y-6">
          {/* AI Generator Box */}
          <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
            <h2 className="text-base font-bold text-gov-navy flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-gov-saffron" />
              <span>AI Question Generation Engine</span>
            </h2>
            <p className="text-xs text-slate-600">
              Generate structured multiple choice questions from authoritative official statistical texts with automatic structural validation.
            </p>

            <div className="grid sm:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Competency</label>
                <select
                  value={genCompCode}
                  onChange={(e) => setGenCompCode(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:outline-hidden"
                >
                  <option value="SAMPLING">Sampling Techniques</option>
                  <option value="SURVEY_DESIGN">Survey Design</option>
                  <option value="DATA_QUALITY">Data Quality (NQAF)</option>
                  <option value="NATIONAL_ACCOUNTS">National Accounts</option>
                  <option value="SQL">SQL for Statistical Data</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Question Count</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={genCount}
                  onChange={(e) => setGenCount(parseInt(e.target.value) || 2)}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:outline-hidden"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={handleGenerateQuestions}
                  disabled={generating}
                  className="w-full py-2 bg-gov-blue text-white font-bold rounded-lg hover:bg-blue-800 transition disabled:opacity-50"
                >
                  {generating ? "Generating & Validating..." : "Generate AI Questions"}
                </button>
              </div>
            </div>
          </div>

          {/* Question Review Studio */}
          <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
            <h2 className="text-base font-bold text-slate-900">Trainer Review & Approval Queue</h2>
            <div className="space-y-4">
              {reviewQuestions.map((q) => (
                <div key={q.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3 text-xs">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="bg-blue-100 text-gov-blue px-2 py-0.5 rounded font-bold text-[10px] mr-2">
                        {q.competency_name}
                      </span>
                      <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                        q.validation_status === "PUBLISHED"
                          ? "bg-emerald-100 text-emerald-800"
                          : q.validation_status === "APPROVED"
                          ? "bg-blue-100 text-gov-blue"
                          : "bg-amber-100 text-amber-800"
                      }`}>
                        {q.validation_status}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-500">AI Validation: {(q.ai_validation_score * 100).toFixed(0)}%</span>
                  </div>

                  <h3 className="font-bold text-slate-900 text-sm leading-snug">{q.question_text}</h3>

                  <div className="grid sm:grid-cols-2 gap-2">
                    {q.options?.map((opt: any, idx: number) => (
                      <div
                        key={opt.id || idx}
                        className={`p-2 rounded border ${
                          opt.is_correct ? "bg-emerald-50 border-emerald-300 font-bold text-emerald-900" : "bg-white border-slate-200 text-slate-700"
                        }`}
                      >
                        {opt.text} {opt.is_correct && "✓ (Correct)"}
                      </div>
                    ))}
                  </div>

                  <div className="pt-2 border-t border-slate-200 flex justify-between items-center">
                    <span className="text-[11px] text-slate-500">{q.source_reference}</span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleReview(q.id, "PUBLISH")}
                        className="px-3 py-1 bg-emerald-700 text-white rounded font-bold text-[11px] hover:bg-emerald-800"
                      >
                        Publish to Bank
                      </button>
                      <button
                        onClick={() => handleReview(q.id, "REJECT")}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded font-bold text-[11px] hover:bg-red-200"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: DOCUMENTS & RAG */}
      {activeTab === "DOCS" && (
        <div className="space-y-6">
          {/* Upload Box */}
          <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
            <h2 className="text-base font-bold text-gov-navy flex items-center space-x-2">
              <Upload className="w-4 h-4 text-gov-blue" />
              <span>Ingest Authoritative Statistical Documentation</span>
            </h2>
            <p className="text-xs text-slate-600">
              Uploaded files are sanitized, extracted, normalized, chunked, and vector-embedded for RAG tutoring and MCQ generation.
            </p>

            <form onSubmit={handleUploadDocument} className="grid sm:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Document Title</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g., MoSPI Price Index Manual"
                  className="w-full p-2 border border-slate-300 rounded-lg focus:outline-hidden"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">File (PDF / DOCX / TXT)</label>
                <input
                  type="file"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full p-1.5 border border-slate-300 rounded-lg focus:outline-hidden text-xs"
                  required
                />
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={uploading}
                  className="w-full py-2 bg-gov-navy text-white font-bold rounded-lg hover:bg-slate-800 transition disabled:opacity-50"
                >
                  {uploading ? "Ingesting Document..." : "Ingest to Knowledge Base"}
                </button>
              </div>
            </form>
          </div>

          {/* Ingested Documents List */}
          <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
            <h2 className="text-base font-bold text-slate-900">Ingested Authoritative Corpus</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-xs">
                <thead className="bg-slate-50 text-slate-700 font-bold">
                  <tr>
                    <th className="px-4 py-3 text-left">Document Title</th>
                    <th className="px-4 py-3 text-left">Organization</th>
                    <th className="px-4 py-3 text-center">Format</th>
                    <th className="px-4 py-3 text-center">Authority</th>
                    <th className="px-4 py-3 text-center">Chunks</th>
                    <th className="px-4 py-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td className="px-4 py-3 font-bold text-slate-900">{doc.title}</td>
                      <td className="px-4 py-3 text-slate-600">{doc.source_organization}</td>
                      <td className="px-4 py-3 text-center">{doc.file_type}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-blue-100 text-gov-blue px-2 py-0.5 rounded font-bold text-[10px]">
                          {doc.authority_tier}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center font-bold">{doc.total_chunks}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold text-[10px]">
                          {doc.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 7: AUDIT LOGS */}
      {activeTab === "AUDIT" && (
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Security & Assessment Audit Trail</h2>
            <p className="text-xs text-slate-500">Immutable ledger capturing authentications, assessment completions, score recalculations, and administrative events.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs">
              <thead className="bg-slate-50 text-slate-700 font-bold">
                <tr>
                  <th className="px-4 py-2.5 text-left">Actor</th>
                  <th className="px-4 py-2.5 text-left">Action</th>
                  <th className="px-4 py-2.5 text-left">Resource</th>
                  <th className="px-4 py-2.5 text-left">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-mono text-[11px]">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-2 text-slate-800">{log.actor_email || "System"}</td>
                    <td className="px-4 py-2 font-bold text-gov-blue">{log.action}</td>
                    <td className="px-4 py-2 text-slate-600">{log.resource}</td>
                    <td className="px-4 py-2 text-slate-400">{new Date(log.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
