"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GitBranch, CheckCircle2, Circle, Clock, RotateCw, ArrowRight } from "lucide-react";

export default function LearningPathPage() {
  const [path, setPath] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);

  useEffect(() => {
    loadPath();
  }, []);

  const loadPath = async () => {
    try {
      setLoading(true);
      const res = await api.getMyLearningPath();
      setPath(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    try {
      setRecalculating(true);
      const res = await api.recalculateLearningPath();
      setPath(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRecalculating(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Generating Personalized Curriculum...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Personalized 5-Stage Learning Path</h1>
          <p className="text-xs text-slate-600 mt-1">
            Personalized developmental roadmap engineered dynamically around your active AI skill gaps and target career role.
          </p>
        </div>

        <button
          onClick={handleRecalculate}
          disabled={recalculating}
          className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition flex items-center space-x-1.5 shadow-xs"
        >
          <RotateCw className={`w-3.5 h-3.5 ${recalculating ? "animate-spin" : ""}`} />
          <span>Recalculate Learning Path</span>
        </button>
      </div>

      {/* Path Header Progress */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs space-y-3">
        <div className="flex justify-between items-center">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                Target Role: {path?.target_role || "Professional"}
              </span>
              <span className="text-xs font-semibold text-slate-500">Status: {path?.status || "ACTIVE"}</span>
            </div>
            <h2 className="text-base font-bold text-slate-900 mt-1.5">{path?.title}</h2>
            <p className="text-xs text-slate-500 mt-0.5">{path?.description}</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-slate-500">Curriculum Progress</span>
            <div className="text-xl font-black text-blue-700">{path?.overall_progress}%</div>
          </div>
        </div>

        <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
          <div
            className="bg-blue-600 h-full rounded-full transition-all duration-500"
            style={{ width: `${path?.overall_progress || 0}%` }}
          />
        </div>
      </div>

      {/* 5-Stage Curriculum Stepper */}
      <div className="space-y-4">
        {path?.items?.map((item: any) => (
          <div
            key={item.id}
            className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs flex items-start space-x-4 hover:border-blue-500 transition"
          >
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 shadow-inner ${
                item.status === "COMPLETED"
                  ? "bg-emerald-100 text-emerald-800"
                  : item.status === "IN_PROGRESS"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              {item.status === "COMPLETED" ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : item.stage_order}
            </div>

            <div className="flex-1 space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                  {item.stage_name}
                </span>
                <span className="text-[11px] text-slate-500 flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{item.estimated_minutes} mins</span>
                </span>
              </div>

              <h3 className="text-sm font-bold text-slate-900 mt-1">{item.title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>

              {item.competency_focus && (
                <div className="pt-2 flex items-center space-x-2">
                  <span className="text-[11px] font-medium text-slate-400">Target Competency:</span>
                  <span className="text-[11px] font-semibold bg-slate-100 text-slate-800 px-2 py-0.5 rounded">
                    {item.competency_focus}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
