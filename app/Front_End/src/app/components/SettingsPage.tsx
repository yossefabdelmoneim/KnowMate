import { useState } from "react";
import { ChevronLeft, ChevronDown, User, Bell, Shield, Check } from "lucide-react";
import type { User as UserType } from "../services/auth";

export function SettingsPage({ user, onBack }: { user: UserType | null; onBack: () => void }) {
  const [activeTab, setActiveTab] = useState("account");
  const [notifications, setNotifications] = useState({ email: true, push: false, weekly: true });
  const [twofa, setTwofa] = useState(false);
  const [tabOpen, setTabOpen] = useState(false);

  const tabs = [
    { id: "account", label: "Account", icon: <User size={15} /> },
    { id: "notifications", label: "Notifications", icon: <Bell size={15} /> },
    { id: "security", label: "Security", icon: <Shield size={15} /> },
  ];

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="border-b border-border px-4 sm:px-8 py-5 flex items-center gap-4">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft size={16} />
          Back
        </button>
        <h1 className="text-lg font-semibold text-foreground">Settings</h1>
      </div>
      <div className="flex flex-1 overflow-hidden">
        {/* Mobile tab selector */}
        <div className="md:hidden relative border-b border-border px-4 py-3 flex-shrink-0">
          <button onClick={() => setTabOpen(!tabOpen)} className="w-full flex items-center justify-between gap-2 px-3 py-2.5 bg-card border border-border rounded-xl text-sm font-medium text-foreground">
            <span className="flex items-center gap-2">{tabs.find(t => t.id === activeTab)?.icon} {tabs.find(t => t.id === activeTab)?.label}</span>
            <ChevronDown size={14} className={`transition-transform ${tabOpen ? "rotate-180" : ""}`} />
          </button>
          {tabOpen && (
            <div className="absolute top-full left-4 right-4 z-10 mt-1 bg-popover border border-border rounded-xl shadow-xl overflow-hidden">
              {tabs.map((t) => (
                <button key={t.id} onClick={() => { setActiveTab(t.id); setTabOpen(false); }} className={`w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-left transition-colors ${activeTab === t.id ? "bg-primary/10 text-primary font-medium" : "text-foreground hover:bg-muted"}`}>
                  <span className="text-muted-foreground">{t.icon}</span>
                  {t.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <nav className="hidden md:block w-52 border-r border-border p-4 flex-shrink-0 overflow-y-auto">
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
                  </div>
                </div>
                <div className="space-y-4">
                  {[["Full Name", user?.full_name ?? "User"], ["Email", user?.email ?? ""], ["Company", user?.company_id ? `Company #${user.company_id}` : ""]].map(([label, val]) => (
                    <div key={label}>
                      <label className="block text-xs font-medium text-muted-foreground mb-1.5">{label}</label>
                      <input defaultValue={val} readOnly className="w-full px-3 py-2.5 text-sm bg-card border border-border rounded-xl text-foreground focus:outline-none" />
                    </div>
                  ))}
                </div>
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
