import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import DiseaseDetection from "./pages/DiseaseDetection";
import Chatbot from "./pages/Chatbot";
import PricePrediction from "./pages/PricePrediction";
import Schemes from "./pages/Schemes";
import Weather from "./pages/Weather";

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
        />
        <Route
          path="/disease"
          element={<ProtectedRoute><DiseaseDetection /></ProtectedRoute>}
        />
        <Route
          path="/chatbot"
          element={<ProtectedRoute><Chatbot /></ProtectedRoute>}
        />
        <Route
          path="/price"
          element={<ProtectedRoute><PricePrediction /></ProtectedRoute>}
        />
        <Route
          path="/schemes"
          element={<ProtectedRoute><Schemes /></ProtectedRoute>}
        />
        <Route
          path="/weather"
          element={<ProtectedRoute><Weather /></ProtectedRoute>}
        />
      </Routes>
    </div>
  );
}
