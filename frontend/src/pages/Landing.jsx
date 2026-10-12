import { Link } from "react-router-dom";
import FurrowDivider from "../components/FurrowDivider";

const FEATURES = [
  {
    title: "Point. Scan. Know.",
    body: "Photograph a leaf and get a disease diagnosis with treatment guidance in seconds — powered by a trained vision model, not guesswork.",
    accentClass: "bg-turmeric",
  },
  {
    title: "Ask anything, in plain words",
    body: "A conversational assistant answers farming questions and tells you exactly which government schemes you actually qualify for — no scrolling through PDFs.",
    accentClass: "bg-monsoon",
  },
  {
    title: "Know before you sell",
    body: "See where mandi prices for your crop are heading, with an honest confidence range instead of a false-precision number.",
    accentClass: "bg-soil",
  },
];

export default function Landing() {
  return (
    <div>
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <p className="font-mono text-xs tracking-widest text-monsoon uppercase mb-4">
          Advisory for the field, not the office
        </p>
        <h1 className="font-display text-5xl md:text-6xl leading-tight mb-6">
          Your field has questions.
          <br />
          <span className="text-turmeric">KrishiMitra has answers.</span>
        </h1>
        <p className="text-wheat-dim max-w-2xl mx-auto text-lg mb-10">
          Disease diagnosis from a photo, a chatbot that speaks your language,
          real scheme eligibility, and price trends — one platform built for
          how farming actually works.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            to="/register"
            className="px-6 py-3 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors"
          >
            Get started free
          </Link>
          <Link
            to="/login"
            className="px-6 py-3 rounded-md border border-wheat/30 hover:border-turmeric transition-colors"
          >
            Log in
          </Link>
        </div>
      </section>

      <FurrowDivider />

      <section className="max-w-6xl mx-auto px-6 py-20 grid md:grid-cols-3 gap-10">
        {FEATURES.map((f) => (
          <div key={f.title} className="space-y-3">
            <div className={`w-10 h-1 rounded ${f.accentClass}`} />
            <h3 className="font-display text-2xl">{f.title}</h3>
            <p className="text-wheat-dim">{f.body}</p>
          </div>
        ))}
      </section>

      <FurrowDivider color="#3E8FB0" />

      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h2 className="font-display text-3xl mb-4">Built for the smallholder, not around them</h2>
        <p className="text-wheat-dim mb-8">
          Every recommendation — scheme eligibility, disease treatment, price direction —
          comes with a plain-language explanation of why, and how confident to be in it.
        </p>
        <Link
          to="/register"
          className="px-6 py-3 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors inline-block"
        >
          Create your free account
        </Link>
      </section>
    </div>
  );
}
