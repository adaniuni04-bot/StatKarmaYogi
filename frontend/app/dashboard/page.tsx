"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
  Award,
  AlertTriangle,
  BookOpen,
  ArrowRight,
  Bot,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Briefcase,
  Layers,
  CheckCircle2
} from "lucide-react";

export default function UserDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [skillGaps, setSkillGaps] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingTest, setGeneratingTest] = useState(false);
  const [reanalyzing, setReanalyzing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [u, gaps, recs] = await Promise.all([
        api.getMe(),
        api.getMySkillGaps(),
        api.getMyRecommendations(),
      ]);
      setUser(u);
      setSkillGaps(gaps);
      setRecommendations(recs.slice(0, 4));
    } catch (err) {
      console.error("Dashboard load failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleReanalyze = async () => {
    setReanalyzing(true);
    try {
      const updatedGaps = await api.reanalyzeSkillGaps({});
      setSkillGaps(updatedGaps);
      try {
        const recs = await api.getMyRecommendations();
        setRecommendations(recs.slice(0, 4));
      } catch (_) {}
    } catch (err: any) {
      alert("Failed to re-evaluate with Groq Cloud AI: " + err.message);
    } finally {
      setReanalyzing(false);
    }
  };

  const handleLaunchAIAssessment = async () => {
    setGeneratingTest(true);
    try {
      const assessment = await api.generateGapAssessment();
      router.push(`/assessments/${assessment.id}`);
    } catch (err: any) {
      alert("Failed to generate AI assessment: " + err.message);
      setGeneratingTest(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500 font-medium">Loading AI Skill Intelligence...</p>
        </div>
      </div>
    );
  }

  const readinessStatus = skillGaps?.readiness_status || "Needs Development";
  const readinessPct = skillGaps?.overall_readiness_percentage ?? 50;

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-4">
      {/* Profile & Target Role Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
              Welcome, {user?.first_name} {user?.last_name}
            </h1>
            <span className="bg-blue-50 text-blue-700 text-xs px-2.5 py-0.5 rounded-md font-semibold border border-blue-200">
              {user?.position || user?.designation_name || "Software Professional"}
            </span>
            <span className="bg-emerald-50 text-emerald-800 text-xs px-2.5 py-0.5 rounded-md font-semibold border border-emerald-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Groq Cloud AI (Qwen 3.8 Active)
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-600 mt-2">
            <span className="flex items-center space-x-1">
              <Briefcase className="w-3.5 h-3.5 text-slate-400" />
              <span>{user?.field || user?.industry_field || "Computer Science & Software"}</span>
            </span>
            <span className="text-slate-300">•</span>
            <span>Experience: {user?.years_experience || 0} Years</span>
            <span className="text-slate-300">•</span>
            <span>Target Goal: <strong className="text-slate-800">{user?.career_goal || user?.position}</strong></span>
          </div>

          {skillGaps?.ai_summary && (
            <div className="mt-3 p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 max-w-2xl flex items-start space-x-2">
              <Bot className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <span className="leading-relaxed">{skillGaps.ai_summary}</span>
            </div>
          )}
        </div>

        {/* AI Role Readiness Score Card */}
        <div className="bg-slate-50 border border-slate-200 px-6 py-4 rounded-xl flex items-center space-x-4 shrink-0">
          <div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Role Readiness</div>
            <div className="text-3xl font-black text-slate-900">
              {readinessPct}%
            </div>
          </div>
          <div className="h-10 w-px bg-slate-200" />
          <div>
            <span
              className={`text-xs px-2.5 py-1 rounded-md font-bold ${
                readinessStatus === "Ready"
                  ? "bg-emerald-100 text-emerald-800"
                  : readinessStatus === "Near Ready"
                  ? "bg-amber-100 text-amber-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {readinessStatus}
            </span>
            <div className="text-[10px] text-slate-400 mt-1">
              {skillGaps?.gap_count || 0} gaps detected by AI
            </div>
          </div>
        </div>
      </div>

      {/* 3-Step AI Acceleration Workflow */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Link
          href="/skill-gaps"
          className="p-4 bg-white rounded-xl border border-slate-200 hover:border-blue-500 transition shadow-xs flex items-center justify-between group"
        >
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-blue-600">Step 1: Skill Gap Intelligence</div>
            <div className="text-xs font-bold text-slate-900 mt-0.5">Explore {skillGaps?.gap_count || 0} Identified Gaps</div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition" />
        </Link>

        <Link
          href="/recommendations"
          className="p-4 bg-white rounded-xl border border-slate-200 hover:border-blue-500 transition shadow-xs flex items-center justify-between group"
        >
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-blue-600">Step 2: Study Material</div>
            <div className="text-xs font-bold text-slate-900 mt-0.5">Curated Study Materials & Modules</div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition" />
        </Link>

        <button
          type="button"
          onClick={handleLaunchAIAssessment}
          disabled={generatingTest}
          className="p-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition shadow-xs flex items-center justify-between text-left cursor-pointer disabled:opacity-50"
        >
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-blue-200">Step 3: Test Knowledge</div>
            <div className="text-xs font-bold mt-0.5">
              {generatingTest ? "AI Generating Test..." : "Take AI Diagnostic Assessment"}
            </div>
          </div>
          <Sparkles className={`w-4 h-4 text-white ${generatingTest ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Main Content Grid: AI Skill Gaps & Study Material */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Dynamic Skill Gaps */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex justify-between items-center flex-wrap gap-2">
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>AI-Identified Skill Gaps</span>
            </h2>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={handleReanalyze}
                disabled={reanalyzing}
                className="px-2.5 py-1 bg-indigo-600 text-white hover:bg-indigo-700 text-xs font-bold transition flex items-center space-x-1 cursor-pointer disabled:opacity-50"
                title="Trigger live Groq Cloud Qwen AI re-evaluation"
              >
                <Sparkles className={`w-3.5 h-3.5 text-amber-300 ${reanalyzing ? "animate-spin" : ""}`} />
                <span>{reanalyzing ? "Groq AI Evaluating..." : "⚡ Re-evaluate with Groq Qwen AI"}</span>
              </button>
              <Link
                href="/skill-gaps"
                className="text-xs font-semibold text-blue-600 hover:underline flex items-center space-x-1"
              >
                <span>Detailed Breakdown</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          <div className="space-y-3">
            {skillGaps?.gaps?.slice(0, 5).map((gap: any, idx: number) => {
              const isCritical = gap.priority_level === "CRITICAL";
              const isMissing = gap.is_missing || gap.current_score === 0;

              return (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-white hover:border-slate-300 transition space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-slate-900">{gap.competency_name || gap.skill}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                          isMissing
                            ? "bg-red-100 text-red-700"
                            : isCritical
                            ? "bg-amber-100 text-amber-800"
                            : "bg-blue-50 text-blue-700"
                        }`}
                      >
                        {isMissing ? "Missing Skill" : `${gap.priority_level} Priority`}
                      </span>
                    </div>

                    <div className="text-xs text-slate-500">
                      Level: <span className="font-semibold text-slate-700">{gap.current_level || "None"}</span> → Target: <span className="font-bold text-blue-600">{gap.required_level || "Advanced"}</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden relative">
                    <div
                      className="bg-blue-600 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, gap.current_score)}%` }}
                    />
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-red-500"
                      style={{ left: `${Math.min(100, gap.required_score)}%` }}
                      title={`Target Score: ${gap.required_score}`}
                    />
                  </div>

                  {gap.reason && (
                    <div className="text-[11px] text-slate-600 pt-0.5">
                      <span className="font-semibold text-slate-800">Why needed: </span>
                      {gap.reason}
                    </div>
                  )}

                  <div className="flex justify-between items-center text-[11px] pt-1">
                    <span className="text-slate-400">{gap.recommended_action || "Complete training module"}</span>
                    <Link
                      href="/recommendations"
                      className="text-blue-600 hover:underline font-semibold"
                    >
                      Study Module →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Curated Study Material (iGOT Karmayogi) */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-blue-600" />
                <span>Targeted Study Material</span>
              </h2>
              <Link
                href="/recommendations"
                className="text-xs font-semibold text-blue-600 hover:underline"
              >
                Catalog →
              </Link>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Curated modules from iGOT Karmayogi and online academies matched to bridge your identified deficits.
            </p>

            <div className="space-y-3">
              {recommendations.map((rec: any) => (
                <div
                  key={rec.id}
                  className="p-3 rounded-xl border border-slate-200 hover:border-blue-500 transition bg-white space-y-1.5"
                >
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 mr-2">
                        {rec.provider}
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">
                        {rec.difficulty}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900 mt-1">{rec.title}</h4>
                    </div>
                    <span className="text-xs font-bold text-blue-600 shrink-0">
                      {rec.recommendation_score}% Match
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-600 line-clamp-2">{rec.description}</p>

                  <div className="flex justify-between items-center pt-1 text-[11px]">
                    <span className="text-slate-400">{rec.duration_minutes} mins</span>
                    <a
                      href={rec.url || "#"}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-600 hover:underline font-semibold flex items-center space-x-1"
                    >
                      <span>Open Course</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            type="button"
            onClick={handleLaunchAIAssessment}
            disabled={generatingTest}
            className="mt-4 w-full py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition flex items-center justify-center space-x-2 shadow-xs cursor-pointer disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${generatingTest ? "animate-spin" : ""}`} />
            <span>{generatingTest ? "Generating AI Test..." : "Generate AI Test for My Gaps"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
