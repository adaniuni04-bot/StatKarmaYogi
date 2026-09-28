"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { CheckCircle2, Clock, Award, ArrowRight, Sparkles, Bot } from "lucide-react";

export default function AssessmentsPage() {
  const router = useRouter();
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = () => {
    setLoading(true);
    api.listAssessments()
      .then(setAssessments)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleGenerateAITest = async () => {
    setGenerating(true);
    try {
      const created = await api.generateGapAssessment();
      router.push(`/assessments/${created.id}`);
    } catch (err: any) {
      alert("Failed to generate AI test: " + err.message);
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Diagnostic Assessment Center</h1>
          <p className="text-xs text-slate-600 mt-1">
            Validate your proficiency through objective, scenario-based technical evaluations. Submitting tests automatically verifies and closes your skill gaps.
          </p>
        </div>

        <button
          type="button"
          onClick={handleGenerateAITest}
          disabled={generating}
          className="px-4 py-2.5 bg-blue-600 text-white rounded-xl font-bold text-xs hover:bg-blue-700 transition flex items-center space-x-2 shadow-xs cursor-pointer disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${generating ? "animate-spin" : ""}`} />
          <span>{generating ? "AI Generating Test..." : "Generate AI Test for My Gaps"}</span>
        </button>
      </div>

      {/* AI Test Banner */}
      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-start space-x-3">
          <Bot className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="text-xs text-slate-700">
            <span className="font-bold text-slate-900">Customized to your deficits:</span>{" "}
            Click the button above to have Groq Cloud AI (Qwen 3.8) dynamically create 5 practical scenario questions directly targeting your identified skill gaps.
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-xs text-slate-500">Loading assessments...</div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {assessments.map((a) => (
            <div
              key={a.id}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:border-blue-500 transition"
            >
              <div>
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100">
                    {a.assessment_type}
                  </span>
                  <span className="text-xs font-semibold text-slate-500">
                    Passing: {a.passing_score}%
                  </span>
                </div>

                <h2 className="text-base font-bold text-slate-900 mt-3">{a.title}</h2>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{a.description}</p>
              </div>

              <div className="pt-4 border-t border-slate-100 flex justify-between items-center text-xs">
                <div className="flex items-center space-x-3 text-slate-500">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{a.duration_minutes} Mins</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>{a.question_count} Questions</span>
                  </span>
                </div>

                <Link
                  href={`/assessments/${a.id}`}
                  className="px-4 py-2 bg-slate-900 text-white rounded-lg font-bold text-xs hover:bg-slate-800 transition flex items-center space-x-1.5 shadow-xs"
                >
                  <span>Start Assessment</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
