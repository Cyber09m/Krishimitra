import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import FurrowDivider from "../components/FurrowDivider";

const CARDS = [
  { to: "/weather", title: "Weather & advisory", body: "Live conditions and a rule-based farm advisory for your area.", accentClass: "bg-monsoon" },
  { to: "/disease", title: "Scan a leaf", body: "Diagnose crop disease from a photo.", accentClass: "bg-turmeric" },
  { to: "/chatbot", title: "Ask KrishiMitra", body: "Get answers and matched government schemes.", accentClass: "bg-monsoon" },
  { to: "/price", title: "Check price trends", body: "See where your crop's mandi price is heading.", accentClass: "bg-soil" },
  { to: "/schemes", title: "Browse all schemes", body: "See every scheme and what you're eligible for.", accentClass: "bg-turmeric" },
];

export default function Dashboard() {
  const { user } = useAuth();
  return (
    <div className="max-w-5xl mx-auto px-6 py-14">
      <h1 className="font-display text-3xl mb-1">Namaste, {user?.name?.split(" ")[0] || "Farmer"}</h1>
      <p className="text-wheat-dim mb-10">What would you like to do today?</p>

      <div className="grid sm:grid-cols-2 gap-6">
        {CARDS.map((c) => (
          <Link
            key={c.to}
            to={c.to}
            className="block p-6 rounded-lg bg-field-light border border-wheat/10 hover:border-turmeric/60 transition-colors"
          >
            <div className={`w-8 h-1 rounded mb-4 ${c.accentClass}`} />
            <h3 className="font-display text-xl mb-1">{c.title}</h3>
            <p className="text-wheat-dim text-sm">{c.body}</p>
          </Link>
        ))}
      </div>

      <FurrowDivider className="mt-14" />
    </div>
  );
}
