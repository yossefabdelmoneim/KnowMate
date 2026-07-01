import { useState } from "react";
import { motion } from "motion/react";
import { Sparkles, AlertCircle, Loader2, Mail } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

export function AuthPage({ mode, onToggle, onSuccess }: { mode: "login" | "register"; onToggle: () => void; onSuccess: () => void }) {
  const { login, register } = useAuth();
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState("");

  const handleSubmit = async () => {
    setError("");
    if (mode === "login") {
      if (!email.trim() || !pw) { setError("Please fill in all fields"); return; }
      setSubmitting(true);
      try {
        await login(email, pw);
        onSuccess();
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Login failed");
      } finally {
        setSubmitting(false);
      }
    } else {
      if (!firstName.trim() || !lastName.trim() || !email.trim() || !pw || !companyName.trim()) {
        setError("Please fill in all fields"); return;
      }
      setSubmitting(true);
      try {
        const res = await register(companyName, firstName, lastName, email, pw);
        setVerificationEmail(res.email);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Registration failed");
      } finally {
        setSubmitting(false);
      }
    }
  };

  if (verificationEmail) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-sm text-center">
          <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-5">
            <Mail size={28} className="text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>Check your email</h1>
          <p className="text-sm text-muted-foreground mb-6">
            We sent a verification link to <strong className="text-foreground">{verificationEmail}</strong>
          </p>
          <p className="text-xs text-muted-foreground">Click the link in the email to activate your account, then sign in.</p>
          <button onClick={() => { onToggle(); setVerificationEmail(""); }} className="mt-6 text-sm text-primary hover:underline font-medium">
            Go to sign in
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <motion.div
        key={mode}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm"
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center">
              <Sparkles size={16} className="text-white" />
            </div>
            <span className="text-lg font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
          </div>
          <h1 className="text-2xl font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            {mode === "login" ? "Sign in to your KnowMate account" : "Start analyzing documents with AI"}
          </p>
        </div>
        {error && (
          <div className="mb-4 flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-xl text-sm text-destructive">
            <AlertCircle size={14} className="flex-shrink-0" />
            {error}
          </div>
        )}
        <div className="space-y-3">
          {mode === "register" && (
            <>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">Company Name</label>
                <input value={companyName} onChange={e => setCompanyName(e.target.value)} placeholder="Acme Corp" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1.5">First Name</label>
                  <input value={firstName} onChange={e => setFirstName(e.target.value)} placeholder="Jane" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1.5">Last Name</label>
                  <input value={lastName} onChange={e => setLastName(e.target.value)} placeholder="Doe" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
                </div>
              </div>
            </>
          )}
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Email</label>
            <input value={email} onChange={e => setEmail(e.target.value)} placeholder="you@company.com" type="email" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Password</label>
            <input value={pw} onChange={e => setPw(e.target.value)} placeholder="••••••••" type="password" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
          </div>
          {mode === "login" && (
            <div className="text-right">
              <button className="text-xs text-primary hover:underline">Forgot password?</button>
            </div>
          )}
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full py-3 bg-primary text-primary-foreground text-sm font-semibold rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mt-2 flex items-center justify-center gap-2"
          >
            {submitting && <Loader2 size={15} className="animate-spin" />}
            {submitting ? "Please wait\u2026" : (mode === "login" ? "Sign in" : "Create account")}
          </button>
        </div>
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center">
            <span className="px-3 bg-background text-xs text-muted-foreground">or continue with</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {["Google", "Microsoft"].map((p) => (
            <button key={p} className="flex items-center justify-center gap-2 py-2.5 bg-card border border-border rounded-xl text-sm font-medium text-foreground hover:bg-muted transition-colors">
              {p}
            </button>
          ))}
        </div>
        <p className="text-center text-sm text-muted-foreground mt-6">
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
          <button onClick={onToggle} className="text-primary hover:underline font-medium">
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>
      </motion.div>
    </div>
  );
}
