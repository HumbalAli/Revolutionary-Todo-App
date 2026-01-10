import { useState, useEffect } from "react";
import Head from "next/head";
import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";
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
    // Initialize with proper authentication flow
    const initAuth = async () => {
      setLoading(true);

      // Check if user is already logged in via localStorage
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedUser) {
        try {
          // Validate the stored token by fetching user info
          const userData = await api.getCurrentUser(storedToken);
          setUser(userData);
          api.setToken(storedToken);
        } catch (error) {
          // Token invalid, clear stored data
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          // Show auth screen
          setShowAuth(true);
        }
      } else {
        // No stored credentials, show auth screen
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
      // Register or authenticate user via backend API
      const authResponse = await api.registerUser(authForm.email, authForm.name);

      // Store the token and user data
      const { access_token, user } = authResponse;
      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      // Set the user and token in the app state
      setUser(user);
      api.setToken(access_token);

      // Hide auth modal
      setShowAuth(false);
      setAuthForm({ name: "", email: "", password: "" });
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Authentication failed");
    }
  };

  const handleLogout = () => {
    // Clear stored credentials
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');

    // Clear app state
    setUser(null);
    api.setToken(null);

    // Show auth screen

    // Demo authentication - in production, use Better Auth
    if (authMode === "signup" && !authForm.name.trim()) {
      setAuthError("Name is required for signup");
      return;
    }

    // Simulate successful auth
    const newUser: User = {
      id: 1,
      email: authForm.email,
      name: authForm.name || "User",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setUser(newUser);
    api.setToken("demo-token");
    setShowAuth(false);
    setAuthForm({ name: "", email: "", password: "" });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <>
        <Head>
          <title>Todo App - Sign In</title>
        </Head>
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
          <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <h1 className="text-2xl font-bold text-center mb-6">Todo App</h1>

            {showAuth ? (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-center">
                  {authMode === "signup" ? "Create Account" : "Sign In"}
                </h2>

                {authError && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {authError}
                  </div>
                )}

                <form onSubmit={handleAuth}>
                  {authMode === "signup" && (
                    <div className="mb-4">
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                        Name
                      </label>
                      <input
                        type="text"
                        id="name"
                        value={authForm.name}
                        onChange={(e) => setAuthForm({...authForm, name: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your name"
                      />
                    </div>
                  )}

                  <div className="mb-4">
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      id="email"
                      value={authForm.email}
                      onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter your email"
                    />
                  </div>

                  <div className="mb-6">
                    <button
                      type="submit"
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {authMode === "signup" ? "Sign Up" : "Sign In"}
                    </button>
                  </div>
                </form>

                <div className="text-center">
                  <button
                    onClick={() => setAuthMode(authMode === "signup" ? "signin" : "signup")}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    {authMode === "signup"
                      ? "Already have an account? Sign In"
                      : "Don't have an account? Sign Up"}
                  </button>
                </div>
              </div>
            ) : (
              <>
                <p className="text-gray-600 text-center mb-6">Sign in to manage your tasks</p>

                <div className="flex gap-2 mb-6">
                  <button
                    onClick={() => { setAuthMode("signin"); setShowAuth(true); }}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => { setAuthMode("signup"); setShowAuth(true); }}
                    className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                  >
                    Sign Up
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>Todo App - {user.name}</title>
      </Head>
      <div className="min-h-screen bg-gray-100">
        <header className="bg-white shadow">
          <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">Todo App</h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">Welcome, {user.name}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Sign Out
              </button>
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="grid gap-8 md:grid-cols-2">
            <div>
              <TaskForm userId={user.id} onTaskCreated={() => {}} />
            </div>
            <div>
              <TaskList userId={user.id} />
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
