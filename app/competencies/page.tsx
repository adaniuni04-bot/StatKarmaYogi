"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Award, History, CheckCircle2, TrendingUp, Layers } from "lucide-react";

export default function CompetenciesPage() {
  const [competencies, setCompetencies] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [activeDomain, setActiveDomain] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getMyCompetencies(),
      api.getMyCompetencyHistory(),
    ])
      .then(([comps, hist]) => {
        setCompetencies(comps);
        setHistory(hist);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const domains = [
    { code: "ALL", label: "All Domains" },
    { code: "STATISTICAL", label: "Statistical Methods" },
    { code: "TECHNICAL", label: "Technical & Computational" },
    { code: "DIGITAL_GOVERNANCE", label: "Digital Governance" },
    { code: "BEHAVIOURAL", label: "Behavioural & Managerial" },
  ];

  const filteredCompetencies = activeDomain === "ALL"
    ? competencies
    : competencies.filter((c) => c.domain_code === activeDomain);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Competency Profile...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gov-navy">Competency Framework & Profile</h1>
        <p className="text-xs text-slate-600 mt-1">
          Deterministic competency scores calculated from diagnostic tests, knowledge evaluations, practical tasks, and training evidence.
        </p>
      </div>

      {/* Domain Navigation Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {domains.map((d) => (
          <button
            key={d.code}
            onClick={() => setActiveDomain(d.code)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeDomain === d.code
                ? "bg-gov-navy text-white shadow-xs"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            }`}
          >
            {d.label}
          </button>
        ))}
      </div>

      {/* Competencies Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCompetencies.map((comp) => (
          <div
            key={comp.id}
            className="bg-white p-5 rounded-xl border border-gov-border shadow-2xs space-y-3"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  {comp.domain_name}
                </span>
                <h3 className="text-sm font-bold text-slate-900 mt-0.5">{comp.competency_name}</h3>
              </div>
              <span
                className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold ${
                  comp.level >= 4
                    ? "bg-emerald-100 text-emerald-800"
                    : comp.level === 3
                    ? "bg-blue-100 text-gov-blue"
                    : "bg-amber-100 text-amber-800"
                }`}
              >
                Level {comp.level} • {comp.level_name}
              </span>
            </div>

            {/* Score Bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-600">Mastery Score</span>
                <span className="text-gov-navy font-bold">{comp.score} / 100</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-gov-blue h-full rounded-full transition-all duration-500"
                  style={{ width: `${comp.score}%` }}
                />
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-[11px] text-slate-500">
              <span>Confidence: {(comp.confidence * 100).toFixed(0)}%</span>
              <span>Evidence: {comp.evidence_count} source(s)</span>
            </div>
          </div>
        ))}
      </div>

      {/* Historical Audit Ledger of Competency Improvements */}
      <div className="bg-white p-6 rounded-xl border border-gov-border shadow-2xs space-y-4">
        <h2 className="text-base font-bold text-gov-navy flex items-center space-x-2">
          <History className="w-4 h-4 text-gov-blue" />
          <span>Competency Evolution & Improvement Ledger</span>
        </h2>

        {history.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No previous assessments recorded yet. Complete an assessment to see evolution.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs">
              <thead className="bg-slate-50 text-slate-700 font-semibold">
                <tr>
                  <th className="px-4 py-2.5 text-left">Competency</th>
                  <th className="px-4 py-2.5 text-left">Previous</th>
                  <th className="px-4 py-2.5 text-left">New Score</th>
                  <th className="px-4 py-2.5 text-left">Delta</th>
                  <th className="px-4 py-2.5 text-left">Reason / Assessment Reference</th>
                  <th className="px-4 py-2.5 text-left">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-2.5 font-bold text-slate-900">{h.competency_name}</td>
                    <td className="px-4 py-2.5 text-slate-600">{h.previous_score}</td>
                    <td className="px-4 py-2.5 font-bold text-gov-blue">{h.new_score}</td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded font-bold ${h.delta >= 0 ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"}`}>
                        {h.delta >= 0 ? `+${h.delta}` : h.delta}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-slate-600">{h.reason}</td>
                    <td className="px-4 py-2.5 text-slate-400">{new Date(h.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
