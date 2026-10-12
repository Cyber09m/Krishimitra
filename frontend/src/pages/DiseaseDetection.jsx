import { useState, useRef } from "react";
import client from "../api/client";
import GrowthStepper from "../components/GrowthStepper";
import { useToast } from "../context/ToastContext";

const SEVERITY_STYLES = {
  high: "text-red-400 border-red-400/40",
  medium: "text-turmeric border-turmeric/40",
  low: "text-monsoon border-monsoon/40",
  none: "text-green-400 border-green-400/40",
  unknown: "text-wheat-dim border-wheat/20",
};

export default function DiseaseDetection() {
  const { showToast } = useToast();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [stage, setStage] = useState(0); // 0=idle/uploading, 1=analyzing, 2=diagnosing, 3=done
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setError(null);
    setResult(null);
    setStage(0);

    const formData = new FormData();
    formData.append("image", file);

    try {
      setStage(1);
      // Slight staged UX: real latency is the Gemini vision call itself, but we
      // move the stepper forward as soon as the request is in flight so the
      // farmer sees the pipeline progressing rather than a blank spinner.
      const analyzingTimer = setTimeout(() => setStage(2), 600);
      const { data } = await client.post("/disease/detect", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      clearTimeout(analyzingTimer);
      setStage(3);
      setResult(data);
      showToast(
        data.needs_review ? "Diagnosis complete — confidence is low, consider a second photo." : "Diagnosis complete.",
        data.needs_review ? "info" : "success"
      );
    } catch (err) {
      setStage(0);
      const msg = err.response?.data?.error || "Something went wrong analyzing this image.";
      setError(msg);
      showToast(msg, "error");
    }
  };

  const treatment = result?.scan?.treatment;
  const severityClass = SEVERITY_STYLES[treatment?.severity] || SEVERITY_STYLES.unknown;

  return (
    <div className="max-w-2xl mx-auto px-6 py-14">
      <h1 className="font-display text-3xl mb-2">Scan a leaf</h1>
      <p className="text-wheat-dim mb-8">
        Upload a clear, well-lit photo of the affected leaf. We'll identify the
        disease and give you a treatment plan.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div
          onClick={() => inputRef.current?.click()}
          className="border-2 border-dashed border-wheat/25 rounded-lg p-8 text-center cursor-pointer hover:border-turmeric/50 transition-colors"
        >
          {preview ? (
            <img src={preview} alt="Leaf preview" className="max-h-64 mx-auto rounded-md" />
          ) : (
            <p className="text-wheat-dim">Click to choose a photo, or drag one here.</p>
          )}
          <input ref={inputRef} type="file" accept="image/png,image/jpeg,image/webp" onChange={handleFile} className="hidden" />
        </div>

        <button
          type="submit"
          disabled={!file || (stage > 0 && stage < 3)}
          className="w-full py-2.5 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors disabled:opacity-60"
        >
          {stage > 0 && stage < 3 ? "Analyzing…" : "Diagnose this leaf"}
        </button>
      </form>

      {stage > 0 && (
        <div className="mt-10">
          <GrowthStepper currentIndex={stage} />
        </div>
      )}

      {error && (
        <div className="mt-8 p-4 rounded-md border border-red-400/40 text-red-300 text-sm">
          {error}
        </div>
      )}

      {result && treatment && (
        <div className="mt-10 p-6 rounded-lg bg-field-light border border-wheat/10">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-display text-2xl">{treatment.label}</h2>
            <span className={`text-xs font-mono px-2 py-1 rounded border ${severityClass}`}>
              {treatment.severity} severity
            </span>
          </div>
          <p className="font-mono text-sm text-wheat-dim mb-4">
            Confidence: {(result.scan.confidence * 100).toFixed(1)}%
          </p>
          {result.needs_review && (
            <div className="mb-4 p-3 rounded-md border border-turmeric/40 text-turmeric text-sm">
              {result.message}
            </div>
          )}
          <p className="text-wheat-dim mb-4">{treatment.description}</p>
          <h3 className="font-semibold mb-1">Recommended treatment</h3>
          <p className="text-wheat-dim">{treatment.treatment}</p>
        </div>
      )}
    </div>
  );
}
