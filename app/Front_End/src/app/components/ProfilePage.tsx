import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { ChevronLeft, User, Mail, Calendar, Building, Shield, Loader2, AlertCircle } from "lucide-react";
import type { User as UserType } from "../services/auth";
import { api } from "../services/api";

export function ProfilePage({ user, onBack }: { user: UserType | null; onBack: () => void }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="border-b border-border px-8 py-5 flex items-center gap-4">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft size={16} />
          Back
        </button>
        <h1 className="text-lg font-semibold text-foreground">Profile</h1>
      </div>

      {error && (
        <div className="mx-8 mt-4 flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-xl text-sm text-destructive">
          <AlertCircle size={14} className="flex-shrink-0" />
          {error}
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-lg mx-auto">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 size={24} className="animate-spin text-primary" />
            </div>
          ) : (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="flex items-center gap-5 p-6 bg-card border border-border rounded-2xl">
                <div className="w-16 h-16 rounded-full bg-primary/15 flex items-center justify-center text-primary text-xl font-semibold">
                  {user?.full_name
                    ? user.full_name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
                    : user?.email?.[0]?.toUpperCase() ?? "U"}
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-foreground">{user?.full_name ?? "User"}</h2>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                  <span className="inline-flex items-center gap-1 mt-1.5 px-2.5 py-0.5 bg-primary/10 text-primary text-xs font-medium rounded-full">
                    <Shield size={10} />
                    {user?.role ?? "User"}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <ProfileField icon={<Mail size={15} />} label="Email" value={user?.email ?? "-"} />
                <ProfileField icon={<Building size={15} />} label="Company ID" value={user?.company_id ? String(user.company_id) : "Not assigned"} />
                <ProfileField icon={<User size={15} />} label="Role" value={user?.role ?? "User"} />
                <ProfileField icon={<Calendar size={15} />} label="Joined" value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : "-"} />
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}

function ProfileField({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 p-4 bg-card border border-border rounded-xl">
      <span className="text-muted-foreground">{icon}</span>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium text-foreground">{value}</p>
      </div>
    </div>
  );
}
