import { useState } from "react";
import { motion } from "motion/react";
import { Sparkles, AlertCircle, Loader2, Mail, ArrowLeft } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { forgotPassword as forgotPasswordApi } from "../services/auth";

export function AuthPage({ mode, onToggle, onSuccess, onForgotPassword, resetToken }: {
  mode: "login" | "register" | "forgot-password" | "reset-password";
  onToggle: () => void;
  onSuccess: () => void;
  onForgotPassword?: () => void;
  resetToken?: string;
}) {
  const { login, register } = useAuth();
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [verificationEmail, setVerificationEmail] = useState("");

  const handleSubmit = async () => {
    setError("");
    setSuccessMsg("");

    if (mode === "forgot-password") {
      if (!email.trim()) { setError("Please enter your email"); return; }
      setSubmitting(true);
      try {
        const res = await forgotPasswordApi(email);
        setSuccessMsg(res.message);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Request failed");
      } finally {
        setSubmitting(false);
      }
      return;
    }

    if (mode === "reset-password") {
      if (!newPw) { setError("Please enter a new password"); return; }
      if (newPw !== confirmPw) { setError("Passwords do not match"); return; }
      if (newPw.length < 6) { setError("Password must be at least 6 characters"); return; }
      setSubmitting(true);
      try {
        const { resetPassword } = await import("../services/auth");
        await resetPassword(resetToken || "", newPw);
        setSuccessMsg("Password reset successfully. You can now sign in.");
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Reset failed");
      } finally {
        setSubmitting(false);
      }
      return;
    }

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

  if (verificationEmail || successMsg) {
    const isReset = mode === "forgot-password" || mode === "reset-password";
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-sm text-center">
          <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-5">
            <Mail size={28} className="text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
            {isReset ? "Check your email" : "Check your email"}
          </h1>
          <p className="text-sm text-muted-foreground mb-6">
            {verificationEmail ? (
              <>We sent a verification link to <strong className="text-foreground">{verificationEmail}</strong></>
            ) : (
              successMsg
            )}
          </p>
          {verificationEmail && (
            <p className="text-xs text-muted-foreground">Click the link in the email to activate your account, then sign in.</p>
          )}
          <button onClick={() => { onToggle(); setVerificationEmail(""); setSuccessMsg(""); }} className="mt-6 text-sm text-primary hover:underline font-medium">
            {isReset ? "Back to sign in" : "Go to sign in"}
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
            {mode === "login" ? "Welcome back" : mode === "forgot-password" ? "Reset your password" : mode === "reset-password" ? "Set new password" : "Create your account"}
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            {mode === "login" ? "Sign in to your KnowMate account" : mode === "forgot-password" ? "Enter your email and we'll send you a reset link" : mode === "reset-password" ? "Choose a new password for your account" : "Start analyzing documents with AI"}
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
          {(mode === "login" || mode === "register" || mode === "forgot-password") && (
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Email</label>
              <input value={email} onChange={e => setEmail(e.target.value)} placeholder="you@company.com" type="email" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
            </div>
          )}
          {(mode === "login" || mode === "register") && (
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Password</label>
              <input value={pw} onChange={e => setPw(e.target.value)} placeholder="••••••••" type="password" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
            </div>
          )}
          {(mode === "reset-password") && (
            <>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">New Password</label>
                <input value={newPw} onChange={e => setNewPw(e.target.value)} placeholder="••••••••" type="password" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
              </div>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">Confirm Password</label>
                <input value={confirmPw} onChange={e => setConfirmPw(e.target.value)} placeholder="••••••••" type="password" className="w-full px-3.5 py-3 text-sm bg-card border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
              </div>
            </>
          )}
          {mode === "login" && (
            <div className="text-right">
              <button onClick={onForgotPassword} className="text-xs text-primary hover:underline">Forgot password?</button>
            </div>
          )}
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full py-3 bg-primary text-primary-foreground text-sm font-semibold rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mt-2 flex items-center justify-center gap-2"
          >
            {submitting && <Loader2 size={15} className="animate-spin" />}
            {submitting ? "Please wait\u2026" : (mode === "login" ? "Sign in" : mode === "forgot-password" ? "Send reset link" : mode === "reset-password" ? "Reset password" : "Create account")}
          </button>
        </div>
        {mode === "forgot-password" && (
          <p className="text-center text-sm text-muted-foreground mt-6">
            <button onClick={onToggle} className="text-primary hover:underline font-medium flex items-center gap-1 justify-center">
              <ArrowLeft size={14} /> Back to sign in
            </button>
          </p>
        )}
        {mode === "reset-password" && (
          <p className="text-center text-sm text-muted-foreground mt-6">
            <button onClick={onToggle} className="text-primary hover:underline font-medium flex items-center gap-1 justify-center">
              <ArrowLeft size={14} /> Back to sign in
            </button>
          </p>
        )}
        {(mode === "login" || mode === "register") && (
          <p className="text-center text-sm text-muted-foreground mt-6">
            {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
            <button onClick={onToggle} className="text-primary hover:underline font-medium">
              {mode === "login" ? "Sign up" : "Sign in"}
            </button>
          </p>
        )}
      </motion.div>
    </div>
  );
}
