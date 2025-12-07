"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Lock, User } from "lucide-react";

export default function AdminSignInPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus("Signing in...");

    try {
      const res = await fetch("http://127.0.0.1:5000/api/admin/signin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (data.success) {
        setStatus("Login successful! Redirecting...");
        localStorage.setItem("isLoggedIn", "true");
        localStorage.setItem("userType", "admin");
        localStorage.setItem("username", data.user.username);

        setTimeout(() => {
          router.push("/admin/dashboard");
        }, 1000);
      } else {
        setStatus(data.error || "Invalid credentials");
      }
    } catch (err) {
      setStatus("Error connecting to server");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">Admin Portal</h1>
          </div>
          <p className="text-gray-300 text-sm">Sign in to access admin dashboard</p>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-white text-sm font-semibold mb-2">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  name="username"
                  type="text"
                  placeholder="Enter admin username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full bg-white/20 border-2 border-white/30 rounded-xl pl-12 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/50 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-white text-sm font-semibold mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  name="password"
                  type="password"
                  placeholder="Enter admin password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full bg-white/20 border-2 border-white/30 rounded-xl pl-12 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/50 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Signing In...
                </>
              ) : (
                <>
                  <Shield className="w-5 h-5" />
                  Sign In as Admin
                </>
              )}
            </button>
          </form>

          {status && (
            <div
              className={`mt-6 p-4 rounded-xl text-center border-2 ${
                status.includes("successful")
                  ? "bg-green-500/20 text-green-200 border-green-400/50"
                  : status.includes("Error") || status.includes("Invalid")
                  ? "bg-red-500/20 text-red-200 border-red-400/50"
                  : "bg-blue-500/20 text-blue-200 border-blue-400/50"
              }`}
            >
              {status}
            </div>
          )}
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => router.push("/")}
            className="text-gray-300 hover:text-white transition-colors text-sm"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
