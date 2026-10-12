import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot } from "recharts";
import client from "../api/client";
import { useToast } from "../context/ToastContext";

const CROPS = ["wheat", "rice", "onion", "tomato", "cotton"];

export default function PricePrediction() {
  const { showToast } = useToast();
  const [crop, setCrop] = useState("wheat");
  const [daysAhead, setDaysAhead] = useState(14);
  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [histRes, predRes] = await Promise.all([
        client.get("/price/history", { params: { crop } }),
        client.get("/price/predict", { params: { crop, days_ahead: daysAhead } }),
      ]);
      setHistory(histRes.data.history);
      setPrediction(predRes.data);
    } catch (err) {
      const msg = err.response?.data?.error || "Couldn't load price data.";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  const chartData = history.map((h) => ({
    date: h.date.slice(5),
    price: h.price_per_quintal,
  }));

  return (
    <div className="max-w-4xl mx-auto px-6 py-14">
      <h1 className="font-display text-3xl mb-2">Price trends</h1>
      <p className="text-wheat-dim mb-8">
        A directional estimate from recent mandi prices — not a guarantee.
      </p>

      <div className="flex flex-wrap items-end gap-4 mb-8">
        <div>
          <label className="block text-sm mb-1">Crop</label>
          <select value={crop} onChange={(e) => setCrop(e.target.value)}
            className="px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none">
            {CROPS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm mb-1">Predict days ahead</label>
          <input type="number" min="1" max="90" value={daysAhead}
            onChange={(e) => setDaysAhead(Number(e.target.value))}
            className="w-28 px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
        </div>
        <button onClick={fetchData} disabled={loading}
          className="px-5 py-2.5 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors disabled:opacity-60">
          {loading ? "Loading…" : "Check trend"}
        </button>
      </div>

      {error && <p className="text-sm text-red-400 mb-6">{error}</p>}

      {chartData.length > 0 && (
        <div className="bg-field-light border border-wheat/10 rounded-lg p-6 mb-6">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1EAD7" strokeOpacity={0.08} />
              <XAxis dataKey="date" stroke="#C9C2AF" fontSize={11} tick={{ fill: "#C9C2AF" }} />
              <YAxis stroke="#C9C2AF" fontSize={11} tick={{ fill: "#C9C2AF" }} />
              <Tooltip
                contentStyle={{ background: "#1F4038", border: "1px solid #E8A93D40", borderRadius: 8, fontSize: 12 }}
              />
              <Line type="monotone" dataKey="price" stroke="#E8A93D" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {prediction && (
        <div className="bg-field-light border border-monsoon/30 rounded-lg p-6">
          <div className="flex flex-wrap items-baseline justify-between gap-2 mb-3">
            <h2 className="font-display text-xl capitalize">{prediction.crop} — {prediction.trend} trend</h2>
            <span className="font-mono text-xs text-wheat-dim">as of {prediction.last_known_date}</span>
          </div>
          <div className="grid sm:grid-cols-3 gap-4 font-mono text-sm mb-4">
            <div>
              <p className="text-wheat-dim text-xs mb-1">Last known price</p>
              <p className="text-lg">₹{prediction.last_known_price}/quintal</p>
            </div>
            <div>
              <p className="text-wheat-dim text-xs mb-1">Predicted ({prediction.predicted_for_days_ahead}d)</p>
              <p className="text-lg text-turmeric">₹{prediction.predicted_price}/quintal</p>
            </div>
            <div>
              <p className="text-wheat-dim text-xs mb-1">Confidence range</p>
              <p className="text-lg">₹{prediction.confidence_range.low} – ₹{prediction.confidence_range.high}</p>
            </div>
          </div>
          <p className="text-xs text-wheat-dim italic">{prediction.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
