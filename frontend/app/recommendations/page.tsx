"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ExternalLink, RotateCw, BookOpen, Sparkles } from "lucide-react";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [providerFilter, setProviderFilter] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    loadRecs();
  }, []);

  const loadRecs = async () => {
    try {
      setLoading(true);
      const res = await api.getMyRecommendations();
      setRecommendations(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    try {
      setRegenerating(true);
      const res = await api.generateRecommendations();
      setRecommendations(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRegenerating(false);
    }
  };

  const filtered = recommendations.filter((r) => {
    if (providerFilter === "ALL") return true;
    if (providerFilter === "IGOT") return r.provider?.toLowerCase().includes("igot");
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Study Material & Learning Curricula</h1>
          <p className="text-xs text-slate-600 mt-1">
            Curated technical learning modules and global engineering curricula, dynamically prioritized by your AI-identified skill gaps.
          </p>
        </div>

        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          className="px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-xl hover:bg-slate-800 transition flex items-center space-x-1.5 shadow-xs cursor-pointer disabled:opacity-50"
        >
          <RotateCw className={`w-3.5 h-3.5 ${regenerating ? "animate-spin" : ""}`} />
          <span>Refresh Recommendations</span>
        </button>
      </div>

      {/* Provider Filter Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2 text-xs">
        <button
          onClick={() => setProviderFilter("ALL")}
          className={`px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer ${
            providerFilter === "ALL" ? "bg-slate-900 text-white" : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
          }`}
        >
          All Resources ({recommendations.length})
        </button>
        <button
          onClick={() => setProviderFilter("IGOT")}
          className={`px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer ${
            providerFilter === "IGOT" ? "bg-blue-600 text-white" : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
          }`}
        >
          iGOT Karmayogi Modules
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-xs text-slate-500">
          Loading targeted study material...
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {filtered.map((rec) => {
            const isIGOT = rec.provider?.toLowerCase().includes("igot");

            return (
              <div
                key={rec.id}
                className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:border-blue-500 transition"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          isIGOT
                            ? "bg-blue-50 text-blue-800 border-blue-200"
                            : "bg-slate-100 text-slate-700 border-slate-200"
                        }`}
                      >
                        {rec.provider}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {rec.difficulty}
                      </span>
                    </div>
                    <span className="text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded shrink-0">
                      {rec.recommendation_score}% Match
                    </span>
                  </div>

                  <h2 className="text-base font-bold text-slate-900 leading-snug">{rec.title}</h2>
                  <p className="text-xs text-slate-600 leading-relaxed">{rec.description}</p>

                  {/* Why Recommended Box */}
                  {rec.why_recommended?.explanation && (
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
                      <div className="font-semibold text-slate-800 text-[11px] flex items-center space-x-1">
                        <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                        <span>Why this is recommended:</span>
                      </div>
                      <p className="text-slate-600 leading-relaxed text-[11px]">
                        {rec.why_recommended.explanation}
                      </p>
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 text-xs">
                  <div className="text-slate-500 text-[11px]">
                    {rec.duration_minutes} Mins • {rec.source_organization}
                  </div>

                  <a
                    href={rec.url || "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white rounded-lg font-bold text-xs hover:bg-blue-700 transition flex items-center justify-center space-x-1.5 shadow-xs"
                  >
                    <span>Access Course</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
