import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import FurrowDivider from "./FurrowDivider";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="bg-field-light">
      <nav className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="font-display text-2xl text-turmeric tracking-tight">
          KrishiMitra
        </Link>
        <div className="flex items-center gap-6 font-body text-sm">
          {user ? (
            <>
              <Link to="/dashboard" className="hover:text-turmeric transition-colors">Dashboard</Link>
              <Link to="/weather" className="hover:text-turmeric transition-colors">Weather</Link>
              <Link to="/disease" className="hover:text-turmeric transition-colors">Disease Scan</Link>
              <Link to="/chatbot" className="hover:text-turmeric transition-colors">Ask KrishiMitra</Link>
              <Link to="/price" className="hover:text-turmeric transition-colors">Price Trends</Link>
              <Link to="/schemes" className="hover:text-turmeric transition-colors">Schemes</Link>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-md border border-wheat/30 hover:border-turmeric hover:text-turmeric transition-colors"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-turmeric transition-colors">Log in</Link>
              <Link
                to="/register"
                className="px-4 py-1.5 rounded-md bg-turmeric text-field font-medium hover:bg-turmeric-dark transition-colors"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </nav>
      <FurrowDivider />
    </header>
  );
}
