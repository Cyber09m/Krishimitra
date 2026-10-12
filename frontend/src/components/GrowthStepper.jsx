/**
 * A real sequence — a crop's growth stages — used to represent progress
 * through the disease-scan pipeline (upload -> analyze -> diagnose -> done).
 * This is the one place a "numbered steps" pattern is justified: the order
 * genuinely carries information the farmer would recognize from field life.
 */
const STAGES = [
  { key: "seed", label: "Uploading", emoji: "🌱" },
  { key: "sprout", label: "Analyzing leaf", emoji: "🌿" },
  { key: "bloom", label: "Diagnosing", emoji: "🌾" },
  { key: "harvest", label: "Done", emoji: "✅" },
];

export default function GrowthStepper({ currentIndex = 0 }) {
  return (
    <div className="flex items-center justify-between w-full max-w-md mx-auto">
      {STAGES.map((stage, i) => (
        <div key={stage.key} className="flex items-center flex-1 last:flex-none">
          <div className="flex flex-col items-center gap-2">
            <div
              className={`w-11 h-11 rounded-full flex items-center justify-center text-lg border-2 transition-colors duration-300
                ${i <= currentIndex
                  ? "bg-turmeric border-turmeric text-field"
                  : "bg-transparent border-wheat/30 text-wheat/40"}`}
            >
              {stage.emoji}
            </div>
            <span
              className={`text-xs font-body ${i <= currentIndex ? "text-wheat" : "text-wheat/40"}`}
            >
              {stage.label}
            </span>
          </div>
          {i < STAGES.length - 1 && (
            <div
              className={`h-0.5 flex-1 mx-2 mb-6 transition-colors duration-300 ${
                i < currentIndex ? "bg-turmeric" : "bg-wheat/20"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}
