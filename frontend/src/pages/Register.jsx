import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

const CATEGORIES = ["marginal", "small", "large"];

export default function Register() {
  const { register, error } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    state: "",
    primary_crop: "",
    land_size_acres: "",
    category: "small",
  });
  const [submitting, setSubmitting] = useState(false);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const ok = await register({
      name: form.name,
      email: form.email,
      password: form.password,
      profile: {
        state: form.state,
        primary_crop: form.primary_crop,
        land_size_acres: form.land_size_acres ? Number(form.land_size_acres) : null,
        category: form.category,
      },
    });
    setSubmitting(false);
    if (ok) {
      showToast("Account created — welcome to KrishiMitra!", "success");
      navigate("/dashboard");
    } else {
      showToast("Registration failed — please check the form.", "error");
    }
  };

  return (
    <div className="max-w-lg mx-auto px-6 py-16">
      <h1 className="font-display text-3xl mb-2">Create your account</h1>
      <p className="text-wheat-dim mb-8">
        Your profile powers scheme matching and the chatbot's recommendations —
        the more accurate it is, the better your results.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">Full name</label>
            <input required value={form.name} onChange={update("name")}
              className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
          </div>
          <div>
            <label className="block text-sm mb-1">Email</label>
            <input required type="email" value={form.email} onChange={update("email")}
              className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
          </div>
        </div>

        <div>
          <label className="block text-sm mb-1">Password</label>
          <input required type="password" minLength={6} value={form.password} onChange={update("password")}
            className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">State</label>
            <input placeholder="e.g. Uttar Pradesh" value={form.state} onChange={update("state")}
              className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
          </div>
          <div>
            <label className="block text-sm mb-1">Primary crop</label>
            <input placeholder="e.g. wheat" value={form.primary_crop} onChange={update("primary_crop")}
              className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">Land size (acres)</label>
            <input type="number" min="0" step="0.1" value={form.land_size_acres} onChange={update("land_size_acres")}
              className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none" />
          </div>
          <div>
            <label className="block text-sm mb-1">Farmer category</label>
            <select value={form.category} onChange={update("category")}
              className="w-full px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none">
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button type="submit" disabled={submitting}
          className="w-full py-2.5 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors disabled:opacity-60">
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-sm text-wheat-dim mt-6">
        Already have an account?{" "}
        <Link to="/login" className="text-turmeric hover:underline">Log in</Link>
      </p>
    </div>
  );
}
