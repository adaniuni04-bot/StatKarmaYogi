"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { AlertCircle, CheckCircle2, ArrowRight, Sparkles, Bot, Target } from "lucide-react";

export default function SkillGapsPage() {
  const router = useRouter();
  const [skillGaps, setSkillGaps] = useState<any>(null);
  const [filter, setFilter] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [reanalyzing, setReanalyzing] = useState(false);

  useEffect(() => {
    api.getMySkillGaps()
      .then(setSkillGaps)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleReanalyze = async () => {
    setReanalyzing(true);
    try {
      const updatedGaps = await api.reanalyzeSkillGaps({});
      setSkillGaps(updatedGaps);
    } catch (err: any) {
      alert("Failed to re-evaluate with Groq Cloud AI: " + err.message);
    } finally {
      setReanalyzing(false);
    }
  };

  const handleLaunchAITest = async () => {
    setGenerating(true);
    try {
      const assessment = await api.generateGapAssessment();
      router.push(`/assessments/${assessment.id}`);
    } catch (err: any) {
      alert("Failed to generate test: " + err.message);
      setGenerating(false);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-500">Evaluating AI Skill Gaps...</div>;
  }

  const allGaps = skillGaps?.gaps || [];
  const filteredGaps = allGaps.filter((g: any) => {
    if (filter === "ALL") return true;
    if (filter === "CRITICAL") return g.priority_level === "CRITICAL";
    if (filter === "MISSING") return g.is_missing || g.current_score === 0;
    if (filter === "GAP") return g.status === "GAP";
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Skill Gap Intelligence</h1>
          <p className="text-xs text-slate-600 mt-1">
            Dynamic role benchmark analysis comparing industry standards for <strong>{skillGaps?.designation_name}</strong> against your declared skills and proficiency levels.
          </p>
        </div>

        <div className="flex items-center space-x-2 flex-wrap gap-2">
          <div className="bg-white p-3 rounded-xl border border-slate-200 flex items-center space-x-3 text-xs shadow-xs">
            <span className="font-semibold text-slate-500">Readiness:</span>
            <span className="font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
              {skillGaps?.overall_readiness_percentage}% ({skillGaps?.readiness_status})
            </span>
          </div>

          <button
            type="button"
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="px-3.5 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold hover:bg-indigo-700 transition flex items-center space-x-1.5 shadow-xs cursor-pointer disabled:opacity-50"
            title="Trigger live Groq Cloud Qwen AI re-evaluation"
          >
            <Sparkles className={`w-3.5 h-3.5 text-amber-300 ${reanalyzing ? "animate-spin" : ""}`} />
            <span>{reanalyzing ? "Groq AI Evaluating..." : "⚡ Re-evaluate with Groq Qwen AI"}</span>
          </button>

          <button
            type="button"
            onClick={handleLaunchAITest}
            disabled={generating}
            className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 transition flex items-center space-x-1.5 shadow-xs cursor-pointer disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${generating ? "animate-spin" : ""}`} />
            <span>{generating ? "Generating..." : "Test My Gaps"}</span>
          </button>
        </div>
      </div>

      {/* AI Narrative Summary */}
      {skillGaps?.ai_summary && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 flex items-start space-x-3">
          <Bot className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="text-xs text-slate-700 leading-relaxed">
            <span className="font-bold text-slate-900">Groq Cloud AI (Qwen 3.8) Analysis: </span>
            {skillGaps.ai_summary}
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2 text-xs">
        <button
          onClick={() => setFilter("ALL")}
          className={`px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer ${
            filter === "ALL" ? "bg-slate-900 text-white" : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
          }`}
        >
          All Identified Gaps ({allGaps.length})
        </button>
        <button
          onClick={() => setFilter("CRITICAL")}
          className={`px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer ${
            filter === "CRITICAL" ? "bg-red-600 text-white" : "bg-white text-red-600 border border-red-200 hover:bg-red-50"
          }`}
        >
          Critical Priority ({skillGaps?.critical_gaps_count || 0})
        </button>
        <button
          onClick={() => setFilter("MISSING")}
          className={`px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer ${
            filter === "MISSING" ? "bg-amber-600 text-white" : "bg-white text-amber-700 border border-amber-200 hover:bg-amber-50"
          }`}
        >
          Missing Skills
        </button>
      </div>

      {/* Gaps Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-xs">
            <thead className="bg-slate-50 text-slate-700 font-semibold">
              <tr>
                <th className="px-4 py-3 text-left">Competency</th>
                <th className="px-4 py-3 text-left">Domain</th>
                <th className="px-4 py-3 text-center">Your Level</th>
                <th className="px-4 py-3 text-center">Required Level</th>
                <th className="px-4 py-3 text-center">Deficit</th>
                <th className="px-4 py-3 text-center">Priority</th>
                <th className="px-4 py-3 text-left">Technical Rationale & Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {filteredGaps.map((g: any, idx: number) => {
                const isMissing = g.is_missing || g.current_score === 0;
                return (
                  <tr key={idx} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3.5 font-bold text-slate-900">
                      <div>{g.competency_name}</div>
                      {isMissing && (
                        <span className="text-[9px] bg-red-100 text-red-700 px-1.5 py-0.2 rounded font-semibold uppercase">
                          Missing
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-slate-500">{g.domain_name}</td>
                    <td className="px-4 py-3.5 text-center font-semibold text-slate-700">
                      {g.current_level || (g.current_score > 0 ? `${g.current_score} pts` : "None")}
                    </td>
                    <td className="px-4 py-3.5 text-center font-bold text-blue-600">
                      {g.required_level || `${g.required_score} pts`}
                    </td>
                    <td className="px-4 py-3.5 text-center font-black text-red-600">
                      -{g.gap}
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span
                        className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          g.priority_level === "CRITICAL"
                            ? "bg-red-600 text-white"
                            : g.priority_level === "HIGH"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {g.priority_level}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-600 max-w-md">
                      <div className="font-medium text-slate-800">{g.reason}</div>
                      <div className="text-[11px] text-blue-600 mt-1 flex items-center space-x-1">
                        <Link href="/recommendations" className="hover:underline flex items-center space-x-1">
                          <span>{g.recommended_action}</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Strengths Met */}
      {skillGaps?.strengths && skillGaps.strengths.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center space-x-2 text-sm font-bold text-slate-900">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Benchmark Standards Satisfied ({skillGaps.strengths.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {skillGaps.strengths.map((s: any, i: number) => (
              <span
                key={i}
                className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1"
              >
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                <span>{s.skill || s.competency_name} ({s.level || "Proficient"})</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
