import { useState, useEffect } from "react";
import Head from "next/head";
import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";
import ChatInterface from "../components/ChatInterface";
import { api } from "../services/api";
import { User } from "../types/task";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<"signin" | "signup">("signin");
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    const initAuth = async () => {
      setLoading(true);
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('user');
      if (storedToken && storedUser) {
        try {
          const userData = await api.getCurrentUser(storedToken);
          setUser(userData);
          api.setToken(storedToken);
        } catch (error) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          setShowAuth(true);
        }
      } else {
        setShowAuth(true);
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    try {
      const authResponse = await api.registerUser(authForm.email, authForm.name);
      const { access_token, user: userData } = authResponse;
      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      api.setToken(access_token);
      setShowAuth(false);
      setAuthForm({ name: "", email: "", password: "" });
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Access Denied");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setUser(null);
    api.setToken(null);
    setShowAuth(true);
  };

  if (loading) return null;

  if (showAuth || !user) {
    return (
      <div className="min-h-screen rev-bg flex items-center justify-center p-6">
        <div className="w-full max-w-md glass-morphism rounded-3xl p-10 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 animate-border-flow"></div>
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold tracking-tighter title-gradient mb-2">Revolutionary</h1>
            <p className="text-blue-400/60 text-xs tracking-[0.3em] uppercase font-medium">Systems Interface</p>
          </div>

          <form onSubmit={handleAuth} className="space-y-6">
            {authMode === "signup" && (
              <div className="relative">
                <input
                  type="text"
                  placeholder="Full Name"
                  value={authForm.name}
                  onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                  className="w-full px-5 py-4 bg-white/5 border border-white/10 rounded-2xl focus:outline-none focus:border-blue-500/50 text-white placeholder:text-gray-500 transition-all font-light"
                />
              </div>
            )}
            <input
              type="email"
              placeholder="System Identity (Email)"
              value={authForm.email}
              onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
              className="w-full px-5 py-4 bg-white/5 border border-white/10 rounded-2xl focus:outline-none focus:border-blue-500/50 text-white placeholder:text-gray-500 transition-all font-light"
            />
            {authError && <p className="text-red-400 text-[10px] text-center uppercase tracking-wider">{authError}</p>}
            <button type="submit" className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-2xl transition-all shadow-lg shadow-blue-500/20 active:scale-95">
              {authMode === "signup" ? "Initialize Protocol" : "Authorize Access"}
            </button>
            <button
              type="button"
              onClick={() => setAuthMode(authMode === "signup" ? "signin" : "signup")}
              className="w-full text-gray-500 text-xs hover:text-white transition-colors"
            >
              {authMode === "signup" ? "Existing identity? Sign In" : "Request new identity? Sign Up"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="rev-bg flex flex-col h-screen overflow-hidden text-white">
      <Head>
        <title>Revolutionary Todo</title>
      </Head>

      {/* High-End Header */}
      <header className="h-20 flex-shrink-0 border-b border-white/5 bg-black/40 backdrop-blur-md z-50">
        <div className="max-w-[1400px] mx-auto h-full px-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Revolutionary <span className="text-blue-500">Todo</span></h1>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Node-Alpha Active</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-8">
            <div className="hidden md:flex flex-col items-end">
              <span className="text-xs font-bold text-gray-200">{user.name}</span>
              <span className="text-[10px] text-gray-500 font-medium">Verified User</span>
            </div>
            <button
              onClick={handleLogout}
              className="p-3 bg-white/5 hover:bg-red-500/10 border border-white/10 rounded-xl transition-all hover:text-red-400 group"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Main Multi-Pane Layout */}
      <main className="flex-1 flex overflow-hidden">

        {/* Left Side: Tasks Dashboard */}
        <section className="flex-1 overflow-y-auto custom-scrollbar p-8">
          <div className="max-w-4xl mx-auto space-y-12">

            {/* Control Center */}
            <div className="space-y-6">
              <div className="flex flex-col gap-1">
                <h2 className="text-3xl font-bold title-gradient">Control Center</h2>
                <p className="text-gray-500 font-light">Revolutionize your workflow with high-precision task tracking.</p>
              </div>

              <div className="glass-morphism rounded-3xl p-1 relative overflow-hidden group">
                <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                <TaskForm userId={user.id} onTaskCreated={() => { }} />
              </div>
            </div>

            {/* Task Stream */}
            <div className="space-y-6">
              <TaskList userId={user.id} />
            </div>
          </div>
        </section>

        {/* Right Side: AI Intelligence Pane */}
        <aside className="w-[450px] border-l border-white/5 bg-black/20 flex flex-col relative">
          <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-blue-500/5 to-transparent"></div>
          <div className="p-6 border-b border-white/5 flex items-center justify-between relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
              <span className="text-xs font-bold uppercase tracking-widest text-blue-100">AI Intelligence</span>
            </div>
            <span className="text-[10px] text-gray-500 font-mono">v4.0.2</span>
          </div>
          <div className="flex-1 overflow-hidden relative z-10">
            <ChatInterface userId={user.id} />
          </div>
        </aside>

      </main>

      {/* Luxury Footer Bar */}
      <footer className="h-10 flex-shrink-0 border-t border-white/5 bg-black flex items-center justify-between px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-50"></div>
        <span className="text-[9px] text-gray-600 font-mono uppercase tracking-widest relative z-10">Revolutionary Systems // All rights reserved 2026</span>
        <div className="flex items-center gap-6 relative z-10">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
            <span className="text-[9px] text-gray-500 uppercase tracking-tighter">Connection Secure</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-[9px] text-gray-500 uppercase tracking-tighter">Sync Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
