import { createContext, useContext, useState, useCallback, useRef } from "react";

const ToastContext = createContext(null);

const STYLES = {
  success: "border-green-400/40 text-green-300",
  error: "border-red-400/40 text-red-300",
  info: "border-monsoon/40 text-monsoon",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((t) => t.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback((message, type = "info", durationMs = 4000) => {
    const id = ++idRef.current;
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => dismiss(id), durationMs);
  }, [dismiss]);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`px-4 py-3 rounded-lg bg-field-light border shadow-lg text-sm animate-[fadein_0.2s_ease-out] ${STYLES[t.type] || STYLES.info}`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
