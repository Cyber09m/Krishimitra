import { useState, useEffect, useCallback, useRef } from "react";
import client from "../api/client";
import LiveIndicator from "../components/LiveIndicator";
import { useToast } from "../context/ToastContext";

const REFRESH_INTERVAL_SECONDS = 30;

const ADVISORY_STYLES = {
  warning: "border-red-400/40 text-red-300",
  caution: "border-turmeric/40 text-turmeric",
  ok: "border-green-400/40 text-green-300",
};

export default function Weather() {
  const { showToast } = useToast();
  const [locationInput, setLocationInput] = useState("");
  const [report, setReport] = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const activeLocationRef = useRef(""); // "" = use profile default

  const fetchWeather = useCallback(async (silently = false) => {
    if (!silently) setLoading(true);
    setError(null);
    try {
      const params = activeLocationRef.current ? { location: activeLocationRef.current } : {};
      const { data } = await client.get("/weather/current", { params });
      setReport(data);
      setLastUpdatedAt(Date.now());
    } catch (err) {
      const msg = err.response?.data?.error || "Couldn't load weather right now.";
      setError(msg);
      if (!silently) showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);

  const handleSearch = (e) => {
    e.preventDefault();
    activeLocationRef.current = locationInput.trim();
    fetchWeather();
  };

  const current = report?.current;

  return (
    <div className="max-w-3xl mx-auto px-6 py-14">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-2">
        <h1 className="font-display text-3xl">Weather &amp; farm advisory</h1>
        {lastUpdatedAt && (
          <LiveIndicator
            intervalSeconds={REFRESH_INTERVAL_SECONDS}
            lastUpdatedAt={lastUpdatedAt}
            onTick={() => fetchWeather(true)}
          />
        )}
      </div>
      <p className="text-wheat-dim mb-8">
        Auto-refreshes every {REFRESH_INTERVAL_SECONDS}s — the forecast model itself
        only updates hourly at the source, so this cadence reflects real data
        changes rather than reformatting the same numbers every second.
      </p>

      <form onSubmit={handleSearch} className="flex gap-3 mb-8">
        <input
          value={locationInput}
          onChange={(e) => setLocationInput(e.target.value)}
          placeholder="City or state (defaults to your profile)"
          className="flex-1 px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none text-sm"
        />
        <button type="submit"
          className="px-5 py-2.5 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors">
          Check
        </button>
      </form>

      {loading && <p className="text-wheat-dim">Loading…</p>}
      {error && <p className="text-sm text-red-400 mb-6">{error}</p>}

      {current && (
        <>
          <div className="bg-field-light border border-wheat/10 rounded-lg p-6 mb-6 flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-wheat-dim text-sm mb-1">{report.location}</p>
              <div className="flex items-baseline gap-3">
                <span className="text-5xl">{current.icon}</span>
                <span className="font-display text-4xl">{current.temperature_c}°C</span>
              </div>
              <p className="text-wheat-dim text-sm mt-1">{current.condition}</p>
            </div>
            <div className="grid grid-cols-2 gap-x-8 gap-y-2 font-mono text-sm">
              <div><span className="text-wheat-dim">Humidity</span><br />{current.humidity_pct}%</div>
              <div><span className="text-wheat-dim">Wind</span><br />{current.wind_speed_kmh} km/h</div>
              <div><span className="text-wheat-dim">Rain</span><br />{current.precipitation_mm} mm</div>
            </div>
          </div>

          <div className="space-y-3 mb-8">
            {report.advisory.map((a, i) => (
              <div key={i} className={`p-4 rounded-md border text-sm ${ADVISORY_STYLES[a.level] || ADVISORY_STYLES.ok}`}>
                {a.message}
              </div>
            ))}
          </div>

          <h2 className="font-display text-xl mb-3">Next 3 days</h2>
          <div className="grid grid-cols-3 gap-4">
            {report.daily_forecast.map((d) => (
              <div key={d.date} className="bg-field-light border border-wheat/10 rounded-lg p-4 text-center">
                <p className="text-xs text-wheat-dim mb-2">{d.date.slice(5)}</p>
                <p className="text-3xl mb-2">{d.icon}</p>
                <p className="font-mono text-sm">{d.min_temp_c}° / {d.max_temp_c}°</p>
                <p className="text-xs text-monsoon mt-1">{d.rain_probability_pct}% rain</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
