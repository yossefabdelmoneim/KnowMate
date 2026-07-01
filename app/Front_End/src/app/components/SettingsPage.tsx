import { useState } from "react";
import { ChevronLeft, User, Bell, BarChart2, Shield, Key, Lock, Check } from "lucide-react";
import type { User as UserType } from "../services/auth";

export function SettingsPage({ user, onBack }: { user: UserType | null; onBack: () => void }) {
  const [activeTab, setActiveTab] = useState("account");
  const [notifications, setNotifications] = useState({ email: true, push: false, weekly: true });
  const [twofa, setTwofa] = useState(false);

  const tabs = [
    { id: "account", label: "Account", icon: <User size={15} /> },
    { id: "notifications", label: "Notifications", icon: <Bell size={15} /> },
    { id: "billing", label: "Billing", icon: <BarChart2 size={15} /> },
    { id: "security", label: "Security", icon: <Shield size={15} /> },
    { id: "api", label: "API Keys", icon: <Key size={15} /> },
    { id: "privacy", label: "Privacy", icon: <Lock size={15} /> },
  ];

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="border-b border-border px-8 py-5 flex items-center gap-4">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft size={16} />
          Back
        </button>
        <h1 className="text-lg font-semibold text-foreground">Settings</h1>
      </div>
      <div className="flex flex-1 overflow-hidden">
        <nav className="w-52 border-r border-border p-4 flex-shrink-0 overflow-y-auto">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm transition-colors mb-1 ${activeTab === t.id ? "bg-primary/10 text-primary font-medium" : "text-muted-foreground hover:text-foreground hover:bg-muted"}`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </nav>
        <div className="flex-1 overflow-y-auto p-8">
          {activeTab === "account" && (
            <div className="max-w-lg space-y-6">
              <div>
                <h2 className="text-base font-semibold text-foreground mb-4">Profile</h2>
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-full bg-primary/15 flex items-center justify-center text-primary text-xl font-semibold">
                    {user?.full_name
                      ? user.full_name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
                      : user?.email?.[0]?.toUpperCase() ?? "U"}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{user?.full_name ?? "User"}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                    <button className="text-xs text-primary hover:underline mt-1">Change photo</button>
                  </div>
                </div>
                <div className="space-y-4">
                  {[["Full Name", user?.full_name ?? "User"], ["Email", user?.email ?? ""], ["Company", user?.company_id ? `Company #${user.company_id}` : ""]].map(([label, val]) => (
                    <div key={label}>
                      <label className="block text-xs font-medium text-muted-foreground mb-1.5">{label}</label>
                      <input defaultValue={val} className="w-full px-3 py-2.5 text-sm bg-card border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-colors" />
                    </div>
                  ))}
                </div>
                <button className="mt-4 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-xl hover:bg-primary/90 transition-colors">
                  Save Changes
                </button>
              </div>
            </div>
          )}
          {activeTab === "notifications" && (
            <div className="max-w-lg space-y-4">
              <h2 className="text-base font-semibold text-foreground mb-4">Notifications</h2>
              {[
                { key: "email" as const, label: "Email notifications", desc: "Receive analysis complete emails" },
                { key: "push" as const, label: "Push notifications", desc: "Browser notifications for long tasks" },
                { key: "weekly" as const, label: "Weekly digest", desc: "Summary of your document activity" },
              ].map(({ key, label, desc }) => (
                <div key={key} className="flex items-start justify-between p-4 bg-card border border-border rounded-xl">
                  <div>
                    <p className="text-sm font-medium text-foreground">{label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
                  </div>
                  <button
                    onClick={() => setNotifications(n => ({ ...n, [key]: !n[key] }))}
                    className={`relative inline-flex h-5 w-9 flex-shrink-0 rounded-full transition-colors duration-200 mt-0.5 ${notifications[key] ? "bg-primary" : "bg-muted"}`}
                  >
                    <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform duration-200 mt-0.5 ${notifications[key] ? "translate-x-4" : "translate-x-0.5"}`} />
                  </button>
                </div>
              ))}
            </div>
          )}
          {activeTab === "billing" && (
            <div className="max-w-lg">
              <h2 className="text-base font-semibold text-foreground mb-4">Subscription & Billing</h2>
              <div className="p-5 bg-primary/8 border border-primary/20 rounded-xl mb-6">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-foreground">Pro Plan</span>
                  <span className="px-2 py-0.5 bg-primary/15 text-primary text-xs font-semibold rounded-full">Active</span>
                </div>
                <p className="text-2xl font-bold text-foreground">$29<span className="text-sm font-normal text-muted-foreground">/month</span></p>
                <p className="text-xs text-muted-foreground mt-1">Renews monthly</p>
                <div className="mt-4 pt-4 border-t border-primary/20 space-y-2">
                  {["500 document pages/mo", "50 conversations", "Priority AI processing", "Advanced analytics"].map(f => (
                    <div key={f} className="flex items-center gap-2 text-sm text-foreground/80">
                      <Check size={13} className="text-primary flex-shrink-0" />
                      {f}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          {activeTab === "security" && (
            <div className="max-w-lg space-y-5">
              <h2 className="text-base font-semibold text-foreground mb-4">Security</h2>
              <div className="p-4 bg-card border border-border rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-foreground">Two-Factor Authentication</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Add an extra layer of security</p>
                  </div>
                  <button
                    onClick={() => setTwofa(!twofa)}
                    className={`relative inline-flex h-5 w-9 flex-shrink-0 rounded-full transition-colors ${twofa ? "bg-primary" : "bg-muted"}`}
                  >
                    <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform mt-0.5 ${twofa ? "translate-x-4" : "translate-x-0.5"}`} />
                  </button>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-3">Change Password</h3>
                {["Current password", "New password", "Confirm new password"].map((p) => (
                  <div key={p} className="mb-3">
                    <label className="block text-xs font-medium text-muted-foreground mb-1.5">{p}</label>
                    <input type="password" placeholder="••••••••" className="w-full px-3 py-2.5 text-sm bg-card border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 transition-colors" />
                  </div>
                ))}
                <button className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-xl hover:bg-primary/90 transition-colors">
                  Update Password
                </button>
              </div>
            </div>
          )}
          {activeTab === "api" && (
            <div className="max-w-lg">
              <h2 className="text-base font-semibold text-foreground mb-4">API Keys</h2>
              <p className="text-sm text-muted-foreground mb-5">Use API keys to integrate KnowMate into your own applications.</p>
              <div className="space-y-3 mb-5">
                {[
                  { name: "Production Key", key: "km_prod_••••••••••••••••ab3f", created: "Jun 1, 2026" },
                  { name: "Development Key", key: "km_dev_••••••••••••••••9c12", created: "May 15, 2026" },
                ].map((k) => (
                  <div key={k.name} className="p-4 bg-card border border-border rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-foreground">{k.name}</p>
                      <button className="text-xs text-destructive hover:underline">Revoke</button>
                    </div>
                    <code className="text-xs font-mono text-muted-foreground bg-muted px-2 py-1 rounded-lg">{k.key}</code>
                    <p className="text-xs text-muted-foreground mt-2">Created {k.created}</p>
                  </div>
                ))}
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-xl hover:bg-primary/90 transition-colors">
                <PlusIcon /> Generate New Key
              </button>
            </div>
          )}
          {activeTab === "privacy" && (
            <div className="max-w-lg space-y-4">
              <h2 className="text-base font-semibold text-foreground mb-4">Privacy Settings</h2>
              {[
                { label: "Share analytics with KnowMate", desc: "Help us improve with anonymous usage data" },
                { label: "Allow document processing for model training", desc: "Documents are anonymized before any use" },
                { label: "Show my profile to team members", desc: "Others in your workspace can see your name" },
              ].map(({ label, desc }, i) => (
                <div key={i} className="flex items-start justify-between p-4 bg-card border border-border rounded-xl">
                  <div>
                    <p className="text-sm font-medium text-foreground">{label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
                  </div>
                  <button className="relative inline-flex h-5 w-9 flex-shrink-0 rounded-full bg-primary transition-colors mt-0.5">
                    <span className="inline-block h-4 w-4 rounded-full bg-white shadow translate-x-4 mt-0.5 transition-transform" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PlusIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}
