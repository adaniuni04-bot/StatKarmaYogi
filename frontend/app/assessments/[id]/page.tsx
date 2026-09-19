"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Clock, CheckCircle2, XCircle, ArrowLeft, ArrowRight, Award, RotateCcw } from "lucide-react";

export default function AssessmentTakePage() {
  const params = useParams();
  const router = useRouter();
  const assessmentId = params.id as string;

  const [assessment, setAssessment] = useState<any>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    initAssessment();
  }, [assessmentId]);

  const initAssessment = async () => {
    try {
      setLoading(true);
      const detail = await api.getAssessmentDetail(assessmentId);
      setAssessment(detail);
      const startRes = await api.startAssessment(assessmentId);
      setAttemptId(startRes.attempt_id);
    } catch (err) {
      console.error("Failed to load assessment:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId: string, optionId: string) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [questionId]: optionId,
    }));
  };

  const handleSubmit = async () => {
    if (!attemptId || !assessment) return;
    setSubmitting(true);
    try {
      const answers = assessment.questions.map((q: any) => ({
        question_id: q.id,
        selected_option_id: selectedOptions[q.id] || null,
      }));

      const res = await api.submitAssessment(assessmentId, attemptId, answers, 180);
      setResult(res);
    } catch (err: any) {
      alert("Submission failed: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Preparing Assessment Session...</div>;
  }

  // Result View
  if (result) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-sm text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
            <Award className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-gov-navy">Assessment Evaluated</h1>
          <p className="text-xs text-slate-600">
            {result.assessment_title} • Deterministic scoring completed.
          </p>

          <div className="inline-flex items-center space-x-6 py-3 px-6 bg-slate-50 border border-slate-200 rounded-xl my-3">
            <div>
              <div className="text-[10px] font-semibold text-slate-500 uppercase">Score</div>
              <div className="text-2xl font-black text-gov-navy">{result.score_percentage}%</div>
            </div>
            <div className="h-8 w-px bg-slate-300" />
            <div>
              <div className="text-[10px] font-semibold text-slate-500 uppercase">Status</div>
              <div className={`text-sm font-bold ${result.passed ? "text-emerald-700" : "text-red-700"}`}>
                {result.passed ? "PASSED" : "FAILED"}
              </div>
            </div>
            <div className="h-8 w-px bg-slate-300" />
            <div>
              <div className="text-[10px] font-semibold text-slate-500 uppercase">Points</div>
              <div className="text-sm font-bold text-slate-700">{result.points_earned} / {result.total_points}</div>
            </div>
          </div>

          {/* Competency Updates Callout */}
          {result.competency_updates?.length > 0 && (
            <div className="max-w-md mx-auto p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-left text-xs space-y-2">
              <div className="font-bold text-emerald-900 flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Competency Score Recalculated</span>
              </div>
              {result.competency_updates.map((up: any) => (
                <div key={up.competency_id} className="flex justify-between items-center text-emerald-800">
                  <span>{up.competency_name}</span>
                  <span className="font-bold">
                    {up.previous_score} → {up.new_score} ({up.delta >= 0 ? `+${up.delta}` : up.delta})
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="pt-4 flex justify-center space-x-4">
            <button
              onClick={() => router.push("/dashboard")}
              className="px-5 py-2.5 bg-gov-navy text-white text-xs font-bold rounded-lg hover:bg-slate-800 transition"
            >
              Return to Intelligence Dashboard
            </button>
            <button
              onClick={() => {
                setResult(null);
                initAssessment();
              }}
              className="px-4 py-2.5 bg-slate-100 text-slate-700 text-xs font-bold rounded-lg hover:bg-slate-200 transition flex items-center space-x-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retake</span>
            </button>
          </div>
        </div>

        {/* Question by Question Review */}
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900">Question Evaluation & Authoritative Explanations</h2>
          <div className="space-y-4">
            {result.question_results?.map((qr: any, idx: number) => (
              <div
                key={qr.question_id}
                className={`p-4 rounded-lg border text-xs space-y-2 ${
                  qr.is_correct ? "bg-emerald-50/40 border-emerald-200" : "bg-red-50/40 border-red-200"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="font-bold text-slate-900">
                    Q{idx + 1}. {qr.question_text}
                  </div>
                  {qr.is_correct ? (
                    <span className="text-emerald-700 font-bold flex items-center space-x-1">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Correct</span>
                    </span>
                  ) : (
                    <span className="text-red-700 font-bold flex items-center space-x-1">
                      <XCircle className="w-4 h-4" />
                      <span>Incorrect</span>
                    </span>
                  )}
                </div>

                <div className="text-slate-600 leading-relaxed pt-1">
                  <span className="font-semibold text-slate-800">Explanation: </span>
                  {qr.explanation}
                </div>

                {qr.source_reference && (
                  <div className="text-[11px] text-gov-blue font-medium pt-1">
                    Source: {qr.source_reference} (Tier {qr.source_tier})
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Question Taking View
  const questions = assessment?.questions || [];
  const currentQ = questions[currentIdx];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Assessment Header */}
      <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-gov-border">
        <div>
          <h1 className="text-base font-bold text-gov-navy">{assessment?.title}</h1>
          <div className="text-xs text-slate-500">
            Question {currentIdx + 1} of {questions.length}
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-700 bg-slate-100 px-3 py-1.5 rounded-lg">
          <Clock className="w-4 h-4 text-gov-blue" />
          <span>{assessment?.duration_minutes}:00</span>
        </div>
      </div>

      {/* Question Card */}
      {currentQ && (
        <div className="bg-white p-6 rounded-xl border border-gov-border shadow-sm space-y-6">
          <div className="space-y-2">
            <span className="text-[10px] font-bold text-gov-blue bg-blue-50 px-2.5 py-1 rounded-full uppercase tracking-wider">
              {currentQ.difficulty} Difficulty
            </span>
            <h2 className="text-base font-bold text-slate-900 leading-relaxed mt-2">
              {currentQ.question_text}
            </h2>
          </div>

          {/* Options */}
          <div className="space-y-3">
            {currentQ.options?.map((opt: any) => {
              const isSelected = selectedOptions[currentQ.id] === opt.id;
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => handleSelectOption(currentQ.id, opt.id)}
                  className={`w-full text-left p-3.5 rounded-lg border text-xs font-medium transition flex items-start space-x-3 ${
                    isSelected
                      ? "border-gov-blue bg-blue-50/50 text-gov-blue ring-1 ring-gov-blue"
                      : "border-slate-200 hover:bg-slate-50 text-slate-700"
                  }`}
                >
                  <div
                    className={`w-4 h-4 mt-0.5 rounded-full border flex items-center justify-center ${
                      isSelected ? "border-gov-blue bg-gov-blue" : "border-slate-300"
                    }`}
                  >
                    {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                  </div>
                  <span className="flex-1 leading-relaxed">{opt.option_text}</span>
                </button>
              );
            })}
          </div>

          {/* Controls */}
          <div className="pt-4 border-t border-slate-100 flex justify-between items-center">
            <button
              onClick={() => setCurrentIdx((p) => Math.max(0, p - 1))}
              disabled={currentIdx === 0}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50 disabled:opacity-40"
            >
              Previous
            </button>

            {currentIdx < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIdx((p) => Math.min(questions.length - 1, p + 1))}
                className="px-4 py-2 bg-gov-blue text-white rounded-lg text-xs font-semibold hover:bg-blue-800 transition"
              >
                Next Question
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-5 py-2 bg-emerald-700 text-white rounded-lg text-xs font-bold hover:bg-emerald-800 transition shadow-xs"
              >
                {submitting ? "Evaluating..." : "Submit Assessment"}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
