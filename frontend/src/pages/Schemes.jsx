import { useEffect, useState } from "react";
import client from "../api/client";

export default function Schemes() {
  const [allSchemes, setAllSchemes] = useState([]);
  const [matchedIds, setMatchedIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const [allRes, matchRes] = await Promise.all([
          client.get("/schemes/"),
          client.get("/schemes/match"),
        ]);
        setAllSchemes(allRes.data.schemes);
        setMatchedIds(new Set(matchRes.data.schemes.map((s) => s.id)));
      } catch (err) {
        setError(err.response?.data?.error || "Couldn't load schemes.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-14">
      <h1 className="font-display text-3xl mb-2">Government schemes</h1>
      <p className="text-wheat-dim mb-8">
        Highlighted cards match your saved profile (state, crop, land size, category).
      </p>

      {loading && <p className="text-wheat-dim">Loading…</p>}
      {error && <p className="text-red-400 text-sm">{error}</p>}

      <div className="grid sm:grid-cols-2 gap-5">
        {allSchemes.map((s) => {
          const isMatch = matchedIds.has(s.id);
          return (
            <div
              key={s.id}
              className={`p-5 rounded-lg border ${
                isMatch ? "border-turmeric bg-field-light" : "border-wheat/10 bg-field-light/50"
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="font-display text-lg">{s.name}</h3>
                {isMatch && (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-turmeric text-field whitespace-nowrap">
                    You qualify
                  </span>
                )}
              </div>
              <p className="text-wheat-dim text-sm mb-3">{s.description}</p>
              <a
                href={s.link}
                target="_blank"
                rel="noreferrer"
                className="text-monsoon text-sm hover:underline"
              >
                Learn more →
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
