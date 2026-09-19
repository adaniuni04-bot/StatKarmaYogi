"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
  Upload,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  ArrowRight,
  BookOpen,
  FileCheck,
  RefreshCw,
} from "lucide-react";

export default function MaterialsPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upload Form
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Quiz Generation State
  const [generatingDocId, setGeneratingDocId] = useState<string | null>(null);
  const [generatedAssessment, setGeneratedAssessment] = useState<any | null>(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const docs = await api.listDocuments();
      setDocuments(docs || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) return;

    setUploading(true);
    setUploadSuccess(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    formData.append("authority_tier", "TIER_A");
    formData.append("source_organization", "StatKarmaYogi Learning Hub");

    try {
      await api.uploadDocument(formData);
      setUploadSuccess(`Successfully uploaded "${title}" and extracted text chunks!`);
      setFile(null);
      setTitle("");
      await fetchDocuments();
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateQuiz = async (docId: string) => {
    setGeneratingDocId(docId);
    setError(null);
    setGeneratedAssessment(null);

    try {
      const result = await api.generateQuizFromDocument(docId);
      setGeneratedAssessment(result);
    } catch (err: any) {
      setError(err.message || "AI Quiz generation failed");
    } finally {
      setGeneratingDocId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto py-4">
      {/* Simple Header Box */}
      <div className="bg-white border border-slate-300 p-6 space-y-2">
        <div className="inline-block px-2 py-0.5 bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold uppercase tracking-wider">
          Learning Material & AI Quiz Generator
        </div>
        <h1 className="text-xl font-bold text-slate-900">
          Upload Documents & Generate Diagnostic Quizzes
        </h1>
        <p className="text-xs text-slate-600 max-w-3xl leading-relaxed">
          Upload PDF, DOCX, or TXT materials. Our system extracts the text and uses Groq Cloud AI (Qwen 3.8) to generate 5 multiple-choice questions to evaluate your knowledge and update your competency profile.
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-300 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {uploadSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}

      {/* Assessment Generated Card */}
      {generatedAssessment && (
        <div className="p-4 bg-emerald-50 border border-emerald-400 text-emerald-900 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              Quiz Ready: {generatedAssessment.title}
            </div>
            <p className="text-xs text-emerald-700">
              {generatedAssessment.question_count} questions generated with answer keys and technical rationales.
            </p>
          </div>
          <button
            onClick={() => router.push(`/assessments/${generatedAssessment.assessment_id}`)}
            className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs border border-emerald-800 flex items-center gap-1.5 shrink-0"
          >
            Take Assessment Now
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Upload Form Column */}
        <div className="md:col-span-1">
          <div className="bg-white border border-slate-300 p-5 space-y-4">
            <div className="border-b border-slate-200 pb-2">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Upload className="w-4 h-4 text-blue-600" />
                Upload Technical Document
              </h2>
              <p className="text-[11px] text-slate-500">Supports PDF, DOCX, TXT</p>
            </div>

            <form onSubmit={handleUpload} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Document Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Linux System Administration"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Choose File *
                </label>
                <input
                  type="file"
                  required
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="w-full text-xs text-slate-700 border border-slate-300 p-2 bg-slate-50"
                />
                {file && (
                  <p className="text-[11px] text-slate-500 mt-1">
                    Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={uploading || !file || !title}
                className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-bold text-xs border border-blue-700 flex items-center justify-center gap-2 cursor-pointer"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    Processing & Chunking...
                  </>
                ) : (
                  <>
                    <Upload className="w-3.5 h-3.5" />
                    Upload & Ingest Document
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Document List Column */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-slate-700" />
              Ingested Documents Library ({documents.length})
            </h2>
            <button
              onClick={fetchDocuments}
              className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-bold"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading documents...</div>
          ) : documents.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-slate-300 bg-white space-y-2">
              <FileCheck className="w-8 h-8 text-slate-400 mx-auto" />
              <div className="text-xs font-bold text-slate-700">No documents uploaded yet</div>
              <p className="text-[11px] text-slate-500">
                Upload a document on the left to start generating AI diagnostic assessments.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => {
                const isGeneratingThis = generatingDocId === doc.id;
                return (
                  <div
                    key={doc.id}
                    className="p-4 bg-white border border-slate-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase bg-slate-100 border border-slate-300 text-slate-800">
                          {doc.file_type || "DOC"}
                        </span>
                        <span className="text-[11px] text-slate-500 flex items-center gap-1">
                          <Layers className="w-3 h-3" />
                          {doc.total_chunks || 0} chunks
                        </span>
                        <span className="text-[11px] text-slate-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-slate-900">{doc.title}</h3>
                      <p className="text-[11px] text-slate-500">
                        Filename: {doc.filename} • {((doc.file_size_bytes || 0) / 1024).toFixed(1)} KB
                      </p>
                    </div>

                    <button
                      onClick={() => handleGenerateQuiz(doc.id)}
                      disabled={isGeneratingThis || generatingDocId !== null}
                      className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-bold text-xs border border-blue-700 flex items-center gap-1.5 shrink-0 cursor-pointer"
                    >
                      {isGeneratingThis ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          Generating Quiz with Groq AI...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          Generate AI Quiz
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}