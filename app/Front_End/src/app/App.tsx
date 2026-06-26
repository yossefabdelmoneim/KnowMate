import { useState, useRef, useEffect, type ReactNode } from "react";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import {
  Search, Bell, Plus, Send, Paperclip,
  FileText, File, FileSpreadsheet, Upload, Trash2, MoreVertical,
  Users, BarChart2, Settings, MessageSquare, BookOpen, Shield,
  Building2, Zap, Globe, CheckCircle, ArrowRight, Menu, X,
  Star, Brain, HeadphonesIcon, TrendingUp, Download, RefreshCw,
  Filter, Eye, Edit3, LogOut,
  Clock, AlertCircle, ChevronLeft, Cpu, Lock, Palette,
  CreditCard, Key, UserPlus,
  ThumbsUp, Copy, RotateCcw, ExternalLink, PanelRight, PanelRightClose,
  ChevronRight, FileText as FileIcon2, Database, Sparkles,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

type View = "landing" | "login" | "register" | "forgot" | "dashboard";
type SubView = "ai" | "documents" | "users" | "analytics" | "settings";
type AgentType = "cs" | "analyst";
type SettingsTab = "profile" | "security" | "ai" | "branding" | "billing";

// ─── Data ────────────────────────────────────────────────────────────────────

const queryData = [
  { day: "Mon", queries: 142, resolved: 128 },
  { day: "Tue", queries: 198, resolved: 187 },
  { day: "Wed", queries: 167, resolved: 154 },
  { day: "Thu", queries: 231, resolved: 219 },
  { day: "Fri", queries: 289, resolved: 271 },
  { day: "Sat", queries: 94, resolved: 89 },
  { day: "Sun", queries: 78, resolved: 74 },
];

const docCategoryData = [
  { category: "HR", count: 48 },
  { category: "Technical", count: 72 },
  { category: "SOPs", count: 35 },
  { category: "Compliance", count: 29 },
  { category: "Training", count: 54 },
];

const agentUsageData = [
  { name: "CS Agent", value: 62, color: "#2563EB" },
  { name: "Data Analyst", value: 38, color: "#6366F1" },
];

const chatHistory = [
  { id: "1", title: "Vacation policy clarification", date: "Today", agent: "cs" as AgentType },
  { id: "2", title: "Q3 revenue breakdown by product", date: "Today", agent: "analyst" as AgentType },
  { id: "3", title: "Remote work equipment policy", date: "Yesterday", agent: "cs" as AgentType },
  { id: "4", title: "Compliance training deadline", date: "Yesterday", agent: "cs" as AgentType },
  { id: "5", title: "Sales performance Jan–Jun", date: "Jun 20", agent: "analyst" as AgentType },
];

type Citation = { doc: string; page: number; excerpt: string };
type Message = { role: "user" | "ai"; content: string; citations?: Citation[] };

const initialMessages: Message[] = [
  { role: "user", content: "How many vacation days am I entitled to as a senior employee?" },
  {
    role: "ai",
    content: "Based on the HR Policy Manual (2024), senior employees with 5+ years of tenure are entitled to **25 vacation days per year**. This increases to 28 days after 8 years of service.\n\nKey points:\n• Days can be carried over (max 10 days)\n• Approval required 2 weeks in advance\n• Blackout periods: Q4 financial close (Nov 15–Dec 5)",
    citations: [
      { doc: "HR Policy Manual 2024", page: 14, excerpt: "Senior employees (Grade 7+) accrue 25 PTO days annually per the compensation framework..." },
    ],
  },
];

const documents = [
  { id: "1", name: "HR Policy Manual 2024.pdf", type: "pdf", size: "4.2 MB", pages: 87, status: "ready", date: "Jun 15, 2024", category: "HR", progress: 100 },
  { id: "2", name: "Employee Onboarding SOP v3.docx", type: "docx", size: "1.8 MB", pages: 34, status: "ready", date: "Jun 10, 2024", category: "SOPs", progress: 100 },
  { id: "3", name: "Q3 2024 Financial Report.pdf", type: "pdf", size: "2.1 MB", pages: 52, status: "ready", date: "Jun 8, 2024", category: "Finance", progress: 100 },
  { id: "4", name: "IT Security Guidelines.pdf", type: "pdf", size: "3.4 MB", pages: 64, status: "processing", date: "Jun 22, 2024", category: "Technical", progress: 67 },
  { id: "5", name: "Customer Support Playbook.docx", type: "docx", size: "2.9 MB", pages: 45, status: "ready", date: "Jun 1, 2024", category: "SOPs", progress: 100 },
  { id: "6", name: "2024 Benefits Overview.xlsx", type: "xlsx", size: "0.8 MB", pages: 12, status: "ready", date: "May 28, 2024", category: "HR", progress: 100 },
  { id: "7", name: "Product Roadmap H2 2024.pdf", type: "pdf", size: "5.1 MB", pages: 28, status: "queued", date: "Jun 23, 2024", category: "Technical", progress: 0 },
  { id: "8", name: "Compliance Training Manual.docx", type: "docx", size: "1.2 MB", pages: 41, status: "error", date: "Jun 21, 2024", category: "Compliance", progress: 0 },
];

const users = [
  { id: "1", name: "Sarah Chen", email: "s.chen@acmecorp.com", role: "Admin", status: "active", dept: "Engineering", joined: "Jan 12, 2024", avatar: "SC", queries: 342 },
  { id: "2", name: "Marcus Johnson", email: "m.johnson@acmecorp.com", role: "Manager", status: "active", dept: "Sales", joined: "Feb 3, 2024", avatar: "MJ", queries: 218 },
  { id: "3", name: "Priya Patel", email: "p.patel@acmecorp.com", role: "Employee", status: "active", dept: "HR", joined: "Mar 7, 2024", avatar: "PP", queries: 156 },
  { id: "4", name: "David Kim", email: "d.kim@acmecorp.com", role: "Support", status: "active", dept: "Customer Success", joined: "Jan 20, 2024", avatar: "DK", queries: 489 },
  { id: "5", name: "Aisha Williams", email: "a.williams@acmecorp.com", role: "Employee", status: "inactive", dept: "Finance", joined: "Apr 15, 2024", avatar: "AW", queries: 87 },
  { id: "6", name: "James Liu", email: "j.liu@acmecorp.com", role: "Manager", status: "active", dept: "Engineering", joined: "Feb 28, 2024", avatar: "JL", queries: 203 },
  { id: "7", name: "Elena Rossi", email: "e.rossi@acmecorp.com", role: "Support", status: "active", dept: "Customer Success", joined: "Mar 19, 2024", avatar: "ER", queries: 374 },
];

const activityFeed = [
  { user: "Sarah Chen", action: "uploaded", target: "Product Roadmap H2 2024.pdf", time: "2m ago", color: "bg-blue-100 text-blue-600" },
  { user: "David Kim", action: "queried", target: "CS Agent — refund policy", time: "8m ago", color: "bg-indigo-100 text-indigo-600" },
  { user: "Marcus Johnson", action: "queried", target: "Data Analyst — Q3 revenue", time: "15m ago", color: "bg-violet-100 text-violet-600" },
  { user: "Priya Patel", action: "uploaded", target: "Compliance Training Manual.docx", time: "1h ago", color: "bg-blue-100 text-blue-600" },
  { user: "Elena Rossi", action: "queried", target: "CS Agent — escalation procedure", time: "2h ago", color: "bg-indigo-100 text-indigo-600" },
  { user: "James Liu", action: "invited", target: "t.morgan@acmecorp.com", time: "3h ago", color: "bg-emerald-100 text-emerald-600" },
];

const features = [
  { icon: Brain, title: "RAG-Powered AI Agents", desc: "Two specialized agents — CS and Data Analyst — trained on your internal documents with retrieval-augmented generation for cited, accurate answers.", color: "text-blue-600", bg: "bg-blue-50" },
  { icon: Database, title: "Multi-Tenant Knowledge Base", desc: "Each company gets a fully isolated workspace. Documents, users, and AI models are siloed with enterprise-grade access control.", color: "text-indigo-600", bg: "bg-indigo-50" },
  { icon: FileIcon2, title: "Universal Document Ingestion", desc: "Upload PDFs, DOCX, XLSX, PowerPoints, and more. Our pipeline extracts, chunks, and indexes content for real-time retrieval.", color: "text-sky-600", bg: "bg-sky-50" },
  { icon: Shield, title: "Enterprise Security", desc: "SOC 2 Type II certified. SSO/SAML, RBAC, audit logs, and AES-256 encryption at rest and in transit.", color: "text-emerald-600", bg: "bg-emerald-50" },
  { icon: BarChart2, title: "Usage Analytics", desc: "Track query volumes, top topics, agent performance, and document utilization across your entire organization.", color: "text-violet-600", bg: "bg-violet-50" },
  { icon: Globe, title: "API-First Architecture", desc: "Headless API embeds KnowMate into Slack, Teams, Confluence, Salesforce, or any custom internal tool.", color: "text-orange-600", bg: "bg-orange-50" },
];

const testimonials = [
  { quote: "KnowMate cut our support ticket resolution time by 68%. The CS agent answers policy questions our team used to spend hours researching.", author: "Rachel Torres", role: "VP Customer Success", company: "Meridian Health", avatar: "RT" },
  { quote: "As a data analyst, having an AI that queries our financial reports in natural language is transformative. The citation panel makes every answer auditable.", author: "Samuel Park", role: "Head of Analytics", company: "Vertex Capital", avatar: "SP" },
  { quote: "Onboarding 200 new employees used to take 3 weeks. KnowMate's document Q&A got us to self-serve onboarding in days.", author: "Lena Hoffmann", role: "CHRO", company: "Nexwave AG", avatar: "LH" },
];

const suggestedQuestions = [
  "What is the remote work equipment reimbursement policy?",
  "How do I submit an expense report?",
  "What are the Q4 2024 sales targets?",
  "Explain the onboarding process for new hires",
];

// ─── Shared UI ────────────────────────────────────────────────────────────────

function Chip({ children, variant = "default" }: { children: ReactNode; variant?: string }) {
  const map: Record<string, string> = {
    default: "bg-blue-100 text-blue-700",
    ready: "bg-emerald-100 text-emerald-700",
    processing: "bg-amber-100 text-amber-700",
    queued: "bg-slate-100 text-slate-600",
    error: "bg-red-100 text-red-700",
    admin: "bg-violet-100 text-violet-700",
    manager: "bg-blue-100 text-blue-700",
    employee: "bg-slate-100 text-slate-600",
    support: "bg-cyan-100 text-cyan-700",
    active: "bg-emerald-100 text-emerald-700",
    inactive: "bg-slate-100 text-slate-500",
    cs: "bg-blue-100 text-blue-700",
    analyst: "bg-indigo-100 text-indigo-700",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-semibold uppercase tracking-wide ${map[variant] ?? map.default}`}>
      {children}
    </span>
  );
}

function DocIcon({ type }: { type: string }) {
  if (type === "pdf") return <div className="w-8 h-8 rounded bg-red-100 flex items-center justify-center flex-shrink-0"><FileText size={15} className="text-red-600" /></div>;
  if (type === "docx") return <div className="w-8 h-8 rounded bg-blue-100 flex items-center justify-center flex-shrink-0"><File size={15} className="text-blue-600" /></div>;
  if (type === "xlsx") return <div className="w-8 h-8 rounded bg-green-100 flex items-center justify-center flex-shrink-0"><FileSpreadsheet size={15} className="text-green-600" /></div>;
  return <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center flex-shrink-0"><File size={15} className="text-slate-500" /></div>;
}

function Av({ initials, size = "md", bg = "bg-blue-600" }: { initials: string; size?: "sm" | "md" | "lg"; bg?: string }) {
  const sz = { sm: "w-7 h-7 text-xs", md: "w-9 h-9 text-sm", lg: "w-11 h-11 text-base" }[size];
  return (
    <div className={`${sz} ${bg} text-white rounded-full flex items-center justify-center font-semibold font-["Plus_Jakarta_Sans"] flex-shrink-0`}>
      {initials}
    </div>
  );
}

// ─── Landing Page ─────────────────────────────────────────────────────────────

function LandingPage({ go }: { go: (v: View) => void }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white font-['DM_Sans']" style={{ overflowX: "hidden" }}>
      {/* Navbar */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-xl text-slate-900 tracking-tight">KnowMate</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            {["Features", "Solutions", "Pricing", "Docs"].map(l => (
              <a key={l} href="#" className="text-sm text-slate-600 hover:text-blue-600 transition-colors font-medium">{l}</a>
            ))}
          </div>
          <div className="hidden md:flex items-center gap-3">
            <button onClick={() => go("login")} className="text-sm text-slate-700 hover:text-blue-600 font-semibold transition-colors">Sign in</button>
            <button onClick={() => go("register")} className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-semibold shadow-sm">
              Start free trial
            </button>
          </div>
          <button className="md:hidden p-1" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu">
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {mobileOpen && (
          <div className="md:hidden bg-white border-t border-slate-100 px-4 py-4 flex flex-col gap-4">
            {["Features", "Solutions", "Pricing", "Docs"].map(l => (
              <a key={l} href="#" className="text-slate-700 font-medium">{l}</a>
            ))}
            <button onClick={() => go("login")} className="text-left text-slate-700 font-semibold">Sign in</button>
            <button onClick={() => go("register")} className="bg-blue-600 text-white px-4 py-2.5 rounded-lg font-semibold">Start free trial</button>
          </div>
        )}
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-full px-4 py-1.5 mb-6">
              <Sparkles size={13} className="text-blue-600" />
              <span className="text-sm text-blue-700 font-semibold">Now with GPT-4o and Claude 3.5 support</span>
            </div>
            <h1 className="font-['Plus_Jakarta_Sans'] text-5xl sm:text-6xl font-extrabold text-slate-900 leading-[1.1] mb-6">
              Your company&apos;s knowledge,{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                intelligently connected
              </span>
            </h1>
            <p className="text-xl text-slate-600 leading-relaxed mb-8 max-w-lg">
              Upload your internal documents and let AI agents answer questions, surface insights, and accelerate decisions — with every answer cited to the source.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <button onClick={() => go("register")} className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3.5 rounded-xl font-semibold transition-all shadow-lg shadow-blue-600/20">
                Start free 14-day trial <ArrowRight size={17} />
              </button>
              <button onClick={() => go("dashboard")} className="flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-6 py-3.5 rounded-xl font-semibold transition-colors">
                View live demo
              </button>
            </div>
          </div>

          {/* Browser mockup */}
          <div className="relative hidden lg:block">
            <div className="absolute -inset-4 bg-gradient-to-br from-blue-600/10 to-indigo-600/10 rounded-3xl blur-2xl" />
            <div className="relative bg-white rounded-2xl border border-slate-200 shadow-2xl overflow-hidden">
              <div className="bg-slate-900 px-4 py-2.5 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" /><div className="w-3 h-3 rounded-full bg-amber-400" /><div className="w-3 h-3 rounded-full bg-emerald-400" />
                </div>
                <div className="flex-1 text-center"><span className="text-xs text-slate-500 font-mono">app.knowmate.ai/assistant</span></div>
              </div>
              <div className="flex" style={{ height: 360 }}>
                <div className="w-12 bg-slate-900 flex flex-col items-center pt-4 gap-3.5">
                  <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center"><Brain size={12} className="text-white" /></div>
                  {[MessageSquare, FileText, Users, BarChart2, Settings].map((Icon, i) => (
                    <div key={i} className={`w-7 h-7 rounded-md flex items-center justify-center ${i === 0 ? "bg-blue-600" : ""}`}>
                      <Icon size={13} className={i === 0 ? "text-white" : "text-slate-600"} />
                    </div>
                  ))}
                </div>
                <div className="w-36 bg-white border-r border-slate-100 p-2.5">
                  <button className="w-full bg-blue-600 text-white text-xs font-semibold py-1.5 rounded-lg mb-3 flex items-center justify-center gap-1">
                    <Plus size={10} /> New Chat
                  </button>
                  <p className="text-xs text-slate-400 mb-1.5 font-mono uppercase tracking-widest" style={{ fontSize: 9 }}>Today</p>
                  {["Vacation policy", "Q3 revenue data", "Remote work policy"].map((t, i) => (
                    <div key={i} className={`px-2 py-1.5 rounded-lg mb-1 cursor-pointer ${i === 0 ? "bg-blue-50" : ""}`}>
                      <p className="text-slate-700 leading-tight" style={{ fontSize: 10 }}>{t}</p>
                    </div>
                  ))}
                </div>
                <div className="flex-1 bg-slate-50 flex flex-col">
                  <div className="flex-1 p-3 space-y-3 overflow-hidden">
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white rounded-xl rounded-br-sm px-2.5 py-1.5 max-w-28" style={{ fontSize: 10 }}>
                        What is the parental leave policy?
                      </div>
                    </div>
                    <div className="flex gap-1.5 items-start">
                      <div className="w-5 h-5 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <Brain size={9} className="text-white" />
                      </div>
                      <div className="bg-white border border-slate-200 rounded-xl rounded-bl-sm px-2.5 py-2 shadow-sm max-w-40">
                        <p className="text-slate-800 leading-snug font-semibold mb-1" style={{ fontSize: 10 }}>Parental Leave</p>
                        <p className="text-slate-600 leading-snug" style={{ fontSize: 10 }}>Primary caregivers get <strong>16 weeks</strong> paid leave. <span className="text-blue-600">[HR p.23]</span></p>
                      </div>
                    </div>
                  </div>
                  <div className="p-2.5">
                    <div className="bg-white border border-slate-200 rounded-xl px-2.5 py-2 flex items-center gap-2">
                      <span className="text-slate-400 flex-1" style={{ fontSize: 10 }}>Ask anything...</span>
                      <div className="w-5 h-5 bg-blue-600 rounded-md flex items-center justify-center"><Send size={8} className="text-white" /></div>
                    </div>
                  </div>
                </div>
                <div className="w-24 bg-white border-l border-slate-100 p-2">
                  <p className="text-slate-500 font-semibold mb-2 font-['Plus_Jakarta_Sans']" style={{ fontSize: 9 }}>SOURCES</p>
                  {["HR Manual 2024 p.23", "Benefits Guide p.8"].map((s, i) => (
                    <div key={i} className="bg-blue-50 border border-blue-100 rounded-lg p-1.5 mb-1.5">
                      <div className="flex items-start gap-1">
                        <FileText size={8} className="text-blue-600 mt-0.5 flex-shrink-0" />
                        <p className="text-slate-700 leading-tight" style={{ fontSize: 9 }}>{s}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="text-center mb-14">
          <h2 className="font-['Plus_Jakarta_Sans'] text-4xl font-extrabold text-slate-900 mb-4">Everything your enterprise needs</h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">Built for complex organizations with serious security requirements and demanding workflows.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc, color, bg }) => (
            <div key={title} className="bg-white border border-slate-100 rounded-2xl p-7 hover:shadow-lg hover:border-blue-100 transition-all group cursor-pointer">
              <div className={`w-11 h-11 ${bg} rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                <Icon size={21} className={color} />
              </div>
              <h3 className="font-['Plus_Jakarta_Sans'] text-lg font-bold text-slate-900 mb-2">{title}</h3>
              <p className="text-slate-500 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Agents */}
      <section className="py-20 bg-slate-900 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="font-['Plus_Jakarta_Sans'] text-4xl font-extrabold text-white mb-4">Two specialized AI agents</h2>
            <p className="text-slate-400 text-lg max-w-xl mx-auto">Purpose-built for customer operations and data intelligence.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                icon: HeadphonesIcon, name: "Customer Service Agent", gradient: "from-blue-600 to-blue-500",
                desc: "Trained on your policies, SOPs, and support documentation. Handles employee and customer queries with precision.",
                tags: ["Policy Q&A", "Escalation routing", "HR inquiries", "Onboarding", "Ticket deflection"],
              },
              {
                icon: TrendingUp, name: "Data Analyst Agent", gradient: "from-indigo-600 to-violet-600",
                desc: "Parses financial reports, spreadsheets, and structured data to deliver insight-rich answers with full citation trails.",
                tags: ["Revenue analysis", "KPI extraction", "Trend identification", "Comparative reports", "Forecast queries"],
              },
            ].map(({ icon: Icon, name, gradient, desc, tags }) => (
              <div key={name} className="bg-slate-800 border border-slate-700 rounded-2xl p-8">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-5`}>
                  <Icon size={22} className="text-white" />
                </div>
                <h3 className="font-['Plus_Jakarta_Sans'] text-xl font-bold text-white mb-3">{name}</h3>
                <p className="text-slate-400 text-sm leading-relaxed mb-5">{desc}</p>
                <div className="flex flex-wrap gap-2">
                  {tags.map(t => <span key={t} className="text-xs bg-slate-700 text-slate-300 px-3 py-1 rounded-full">{t}</span>)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="font-['Plus_Jakarta_Sans'] text-4xl font-extrabold text-slate-900 mb-4">What enterprise teams say</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map(({ quote, author, role, company, avatar }) => (
            <div key={author} className="bg-white border border-slate-100 rounded-2xl p-7 hover:shadow-lg transition-shadow">
              <div className="flex gap-0.5 mb-5">
                {[...Array(5)].map((_, i) => <Star key={i} size={14} className="text-amber-400 fill-amber-400" />)}
              </div>
              <p className="text-slate-700 text-sm leading-relaxed mb-6">&ldquo;{quote}&rdquo;</p>
              <div className="flex items-center gap-3">
                <Av initials={avatar} size="md" />
                <div>
                  <p className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900 text-sm">{author}</p>
                  <p className="text-slate-500 text-xs">{role} · {company}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 bg-gradient-to-br from-blue-600 to-indigo-700">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="font-['Plus_Jakarta_Sans'] text-4xl font-extrabold text-white mb-5">Ready to unlock your knowledge base?</h2>
          <p className="text-blue-100 text-lg mb-8">Set up your workspace in minutes. No credit card required for the 14-day trial.</p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button onClick={() => go("register")} className="bg-white text-blue-700 hover:bg-blue-50 px-8 py-3.5 rounded-xl font-bold font-['Plus_Jakarta_Sans'] transition-colors shadow-xl">
              Start free trial
            </button>
            <button className="border border-blue-400 text-white hover:bg-blue-700 px-8 py-3.5 rounded-xl font-bold font-['Plus_Jakarta_Sans'] transition-colors">
              Schedule a demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 px-4 sm:px-6 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-8 mb-10">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center"><Brain size={13} className="text-white" /></div>
                <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-white">KnowMate</span>
              </div>
              <p className="text-sm leading-relaxed">Enterprise AI knowledge management for teams that move fast.</p>
            </div>
            {[
              { title: "Product", links: ["Features", "Pricing", "Changelog", "Roadmap"] },
              { title: "Company", links: ["About", "Blog", "Careers", "Press"] },
              { title: "Legal", links: ["Privacy", "Terms", "Security", "GDPR"] },
            ].map(({ title, links }) => (
              <div key={title}>
                <p className="text-white font-semibold mb-4 text-sm font-['Plus_Jakarta_Sans']">{title}</p>
                <div className="flex flex-col gap-2">
                  {links.map(l => <a key={l} href="#" className="text-sm hover:text-white transition-colors">{l}</a>)}
                </div>
              </div>
            ))}
          </div>
         <div className="border-t border-slate-800 pt-6 text-sm text-center">
  &copy; {new Date().getFullYear()} KnowMate Inc. All rights reserved.
</div>
        </div>
      </footer>
    </div>
  );
}

// ─── Auth Pages ───────────────────────────────────────────────────────────────

function LoginPage({ go }: { go: (v: View) => void }) {
  return (
    <div className="min-h-screen bg-slate-50 flex font-['DM_Sans']">
      <div className="hidden lg:flex flex-col justify-between w-[480px] bg-slate-900 text-white p-12 relative overflow-hidden flex-shrink-0">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/40 to-indigo-900/20" />
        <div className="relative">
          <div className="flex items-center gap-2.5 mb-14">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"><Brain size={16} className="text-white" /></div>
            <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-xl">KnowMate</span>
          </div>
          <h2 className="font-['Plus_Jakarta_Sans'] text-3xl font-bold leading-snug mb-4">Your company&apos;s intelligence hub awaits</h2>
          <p className="text-slate-400">Answers from your documents. Cited, accurate, instant.</p>
        </div>
        <div className="relative space-y-4">
          {[
            { icon: Shield, text: "SOC 2 Type II certified infrastructure" },
            { icon: Lock, text: "AES-256 encryption at rest and in transit" },
            { icon: Globe, text: "99.9% uptime SLA with global CDN" },
          ].map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-3 text-sm text-slate-300">
              <Icon size={15} className="text-blue-400 flex-shrink-0" /> {text}
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"><Brain size={16} className="text-white" /></div>
            <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-xl text-slate-900">KnowMate</span>
          </div>
          <h1 className="font-['Plus_Jakarta_Sans'] text-2xl font-bold text-slate-900 mb-1">Welcome back</h1>
          <p className="text-slate-500 mb-8">Sign in to your workspace</p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Work email</label>
              <input type="email" defaultValue="s.chen@acmecorp.com" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-semibold text-slate-700">Password</label>
                <button onClick={() => go("forgot")} className="text-sm text-blue-600 hover:text-blue-700 font-medium">Forgot password?</button>
              </div>
              <input type="password" defaultValue="••••••••••••" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition" />
            </div>
            <button onClick={() => go("dashboard")} className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold transition-colors shadow-lg shadow-blue-600/20">
              Sign in to workspace
            </button>
          </div>
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-slate-200" /><span className="text-sm text-slate-400">or</span><div className="flex-1 h-px bg-slate-200" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {["Google", "Microsoft"].map(p => (
              <button key={p} className="flex items-center justify-center gap-2 bg-white border border-slate-200 rounded-xl py-2.5 text-sm text-slate-700 font-semibold hover:bg-slate-50 transition-colors">
                <Globe size={15} className="text-slate-400" /> {p}
              </button>
            ))}
          </div>
          <p className="text-center text-sm text-slate-500 mt-8">
            Don&apos;t have an account?{" "}
            <button onClick={() => go("register")} className="text-blue-600 hover:text-blue-700 font-bold">Create workspace</button>
          </p>
        </div>
      </div>
    </div>
  );
}

function RegisterPage({ go }: { go: (v: View) => void }) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-['DM_Sans']">
      <div className="w-full max-w-lg bg-white rounded-2xl border border-slate-200 shadow-xl p-10">
        <div className="flex items-center gap-2.5 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"><Brain size={16} className="text-white" /></div>
          <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-xl text-slate-900">KnowMate</span>
        </div>
        <h1 className="font-['Plus_Jakarta_Sans'] text-2xl font-bold text-slate-900 mb-1">Create your workspace</h1>
        <p className="text-slate-500 mb-7">Start your 14-day free trial. No credit card required.</p>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">First name</label>
              <input placeholder="Sarah" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Last name</label>
              <input placeholder="Chen" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Work email</label>
            <input type="email" placeholder="you@company.com" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Company name</label>
            <input placeholder="Acme Corporation" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
            <input type="password" placeholder="Min. 12 characters" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Team size</label>
            <select className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer">
              <option>1–10 employees</option><option>11–50 employees</option><option>51–200 employees</option><option>201–1000 employees</option><option>1000+ employees</option>
            </select>
          </div>
          <button onClick={() => go("dashboard")} className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold transition-colors shadow-lg shadow-blue-600/20">
            Create workspace →
          </button>
        </div>
        <p className="text-center text-xs text-slate-500 mt-5">
          By signing up, you agree to our <a href="#" className="text-blue-600 font-medium">Terms</a> and <a href="#" className="text-blue-600 font-medium">Privacy Policy</a>.
        </p>
        <p className="text-center text-sm text-slate-500 mt-3">
          Already have an account?{" "}
          <button onClick={() => go("login")} className="text-blue-600 font-bold">Sign in</button>
        </p>
      </div>
    </div>
  );
}

function ForgotPage({ go }: { go: (v: View) => void }) {
  const [sent, setSent] = useState(false);
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-['DM_Sans']">
      <div className="w-full max-w-md bg-white rounded-2xl border border-slate-200 shadow-xl p-10">
        <div className="flex items-center gap-2.5 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"><Brain size={16} className="text-white" /></div>
          <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-xl text-slate-900">KnowMate</span>
        </div>
        {!sent ? (
          <>
            <h1 className="font-['Plus_Jakarta_Sans'] text-2xl font-bold text-slate-900 mb-1">Forgot password?</h1>
            <p className="text-slate-500 mb-7">Enter your work email and we&apos;ll send a reset link.</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Work email</label>
                <input type="email" placeholder="you@company.com" className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
              </div>
              <button onClick={() => setSent(true)} className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold transition-colors">Send reset link</button>
            </div>
          </>
        ) : (
          <div className="text-center py-4">
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-5">
              <CheckCircle size={28} className="text-emerald-600" />
            </div>
            <h2 className="font-['Plus_Jakarta_Sans'] text-xl font-bold text-slate-900 mb-2">Check your inbox</h2>
            <p className="text-slate-500 text-sm">We sent a password reset link to your email. It expires in 15 minutes.</p>
          </div>
        )}
        <button onClick={() => go("login")} className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-blue-600 mt-6 mx-auto w-fit transition-colors">
          <ChevronLeft size={15} /> Back to sign in
        </button>
      </div>
    </div>
  );
}

// ─── Dashboard: Sidebar ───────────────────────────────────────────────────────

const navItems = [
  { id: "ai", icon: MessageSquare, label: "AI Assistant" },
  { id: "documents", icon: FileText, label: "Documents" },
  { id: "users", icon: Users, label: "Users" },
  { id: "analytics", icon: BarChart2, label: "Analytics" },
  { id: "settings", icon: Settings, label: "Settings" },
];

function Sidebar({
  subView, setSubView, collapsed, setCollapsed, go,
}: {
  subView: SubView; setSubView: (v: SubView) => void;
  collapsed: boolean; setCollapsed: (v: boolean) => void;
  go: (v: View) => void;
}) {
  return (
    <aside className={`flex flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border flex-shrink-0 transition-all duration-300 ${collapsed ? "w-16" : "w-60"}`}>
      <div className="h-16 flex items-center px-3 border-b border-sidebar-border gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <Brain size={15} className="text-white" />
        </div>
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <p className="font-['Plus_Jakarta_Sans'] font-extrabold text-white text-sm leading-tight">KnowMate</p>
            <p className="text-xs text-slate-500 truncate">Acme Corporation</p>
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="text-slate-600 hover:text-white transition-colors flex-shrink-0 ml-auto" aria-label="Toggle sidebar">
          {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
        </button>
      </div>

      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto pt-3">
        {!collapsed && <p className="text-xs text-slate-600 uppercase tracking-widest px-2 pb-2 font-['Plus_Jakarta_Sans'] font-semibold" style={{ fontSize: 10 }}>Workspace</p>}
        {navItems.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setSubView(id as SubView)}
            aria-label={label}
            title={collapsed ? label : undefined}
            className={`w-full flex items-center gap-3 px-2.5 py-2.5 rounded-lg text-sm font-semibold transition-all font-['Plus_Jakarta_Sans'] ${subView === id ? "bg-sidebar-primary text-white" : "text-sidebar-accent-foreground hover:bg-sidebar-accent hover:text-white"} ${collapsed ? "justify-center" : ""}`}
          >
            <Icon size={16} className="flex-shrink-0" />
            {!collapsed && label}
          </button>
        ))}
      </nav>

      <div className={`border-t border-sidebar-border p-3 ${collapsed ? "flex justify-center" : ""}`}>
        {collapsed
          ? <Av initials="SC" size="sm" />
          : (
            <div className="flex items-center gap-2.5">
              <Av initials="SC" size="sm" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-white truncate font-['Plus_Jakarta_Sans']">Sarah Chen</p>
                <p className="text-xs text-slate-500 truncate">Administrator</p>
              </div>
              <button onClick={() => go("landing")} className="text-slate-600 hover:text-red-400 transition-colors" aria-label="Sign out">
                <LogOut size={14} />
              </button>
            </div>
          )}
      </div>
    </aside>
  );
}

// ─── Dashboard: TopBar ────────────────────────────────────────────────────────

function TopBar({ subView, agent, setAgent }: { subView: SubView; agent: AgentType; setAgent: (a: AgentType) => void }) {
  const labels: Record<SubView, string> = { ai: "AI Assistant", documents: "Documents", users: "User Management", analytics: "Analytics", settings: "Settings" };
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center gap-4 px-6 flex-shrink-0">
      <div>
        <h1 className="font-['Plus_Jakarta_Sans'] font-extrabold text-slate-900 text-base leading-tight">{labels[subView]}</h1>
        <p className="text-xs text-slate-400">Acme Corporation Workspace</p>
      </div>
      {subView === "ai" && (
        <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-1 ml-4">
          {[
            { id: "cs", icon: HeadphonesIcon, label: "CS Agent" },
            { id: "analyst", icon: TrendingUp, label: "Data Analyst" },
          ].map(({ id, icon: Icon, label }) => (
            <button key={id} onClick={() => setAgent(id as AgentType)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-semibold transition-all ${agent === id ? "bg-white text-blue-700 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}>
              <Icon size={13} /> {label}
            </button>
          ))}
        </div>
      )}
      <div className="ml-auto flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 bg-slate-100 rounded-lg px-3 py-2 w-52">
          <Search size={13} className="text-slate-400 flex-shrink-0" />
          <input placeholder="Search..." className="bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none w-full" />
        </div>
        <button className="relative w-9 h-9 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors" aria-label="Notifications">
          <Bell size={16} className="text-slate-500" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        <Av initials="SC" size="sm" />
      </div>
    </header>
  );
}

// ─── AI Assistant ─────────────────────────────────────────────────────────────

function AIAssistantPage({ agent }: { agent: AgentType }) {
  const [msgs, setMsgs] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [showCitations, setShowCitations] = useState(true);
  const [histCollapsed, setHistCollapsed] = useState(false);
  const [activeChatId, setActiveChatId] = useState("1");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, typing]);

  const citations = msgs.filter(m => m.role === "ai" && m.citations).flatMap(m => m.citations!);

  const send = () => {
    if (!input.trim()) return;
    setMsgs(prev => [...prev, { role: "user", content: input }]);
    setInput("");
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      setMsgs(prev => [...prev, {
        role: "ai",
        content: "Based on the documents in your knowledge base, I found the following information relevant to your query. I have cross-referenced multiple sources to ensure accuracy.\n\nPlease verify critical information directly in the source document before making decisions.",
        citations: [{ doc: "HR Policy Manual 2024", page: 22, excerpt: "Section 5.1 — Comprehensive policy guidelines for workplace entitlements..." }],
      }]);
    }, 1800);
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* History panel */}
      <div className={`flex flex-col bg-white border-r border-slate-200 transition-all duration-300 flex-shrink-0 ${histCollapsed ? "w-0 overflow-hidden" : "w-60"}`}>
        <div className="p-3 border-b border-slate-100 flex-shrink-0">
          <button className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold py-2.5 rounded-xl transition-colors">
            <Plus size={15} /> New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {[
            { label: "Today", items: chatHistory.filter(c => c.date === "Today") },
            { label: "Yesterday", items: chatHistory.filter(c => c.date === "Yesterday") },
            { label: "Earlier", items: chatHistory.filter(c => !["Today", "Yesterday"].includes(c.date)) },
          ].map(({ label, items }) => items.length > 0 && (
            <div key={label} className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-widest px-2 mb-1.5 font-['Plus_Jakarta_Sans'] font-semibold" style={{ fontSize: 9 }}>{label}</p>
              {items.map(chat => (
                <button key={chat.id} onClick={() => setActiveChatId(chat.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-xl transition-colors mb-0.5 ${activeChatId === chat.id ? "bg-blue-50" : "hover:bg-slate-50"}`}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <Chip variant={chat.agent}>{chat.agent === "cs" ? "CS" : "DA"}</Chip>
                  </div>
                  <p className={`text-xs leading-snug line-clamp-2 font-medium ${activeChatId === chat.id ? "text-blue-700" : "text-slate-600"}`}>{chat.title}</p>
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50">
        {/* Chat topbar */}
        <div className="h-12 bg-white border-b border-slate-200 flex items-center gap-3 px-4 flex-shrink-0">
          <button onClick={() => setHistCollapsed(!histCollapsed)} className="text-slate-400 hover:text-slate-600 transition-colors" aria-label="Toggle history">
            <Menu size={17} />
          </button>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-100 rounded-lg">
            {agent === "cs" ? <HeadphonesIcon size={13} className="text-blue-600" /> : <TrendingUp size={13} className="text-indigo-600" />}
            <span className="text-sm font-bold text-blue-700 font-['Plus_Jakarta_Sans']">
              {agent === "cs" ? "Customer Service Agent" : "Data Analyst Agent"}
            </span>
          </div>
          <button onClick={() => setShowCitations(v => !v)} className="ml-auto flex items-center gap-1.5 text-sm text-slate-500 hover:text-blue-600 transition-colors px-2 py-1 rounded-lg hover:bg-slate-100" aria-label="Toggle citations">
            {showCitations ? <PanelRightClose size={15} /> : <PanelRight size={15} />}
            <span className="hidden sm:inline text-xs font-semibold">Sources</span>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 max-w-3xl w-full mx-auto">
          {msgs.length === 0 && (
            <div className="text-center py-20">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-5">
                {agent === "cs" ? <HeadphonesIcon size={28} className="text-blue-600" /> : <TrendingUp size={28} className="text-indigo-600" />}
              </div>
              <h3 className="font-['Plus_Jakarta_Sans'] text-xl font-bold text-slate-800 mb-2">
                {agent === "cs" ? "Customer Service Agent" : "Data Analyst Agent"}
              </h3>
              <p className="text-slate-500 text-sm max-w-sm mx-auto">
                {agent === "cs" ? "Ask about policies, HR procedures, onboarding, benefits, or employee questions." : "Ask me to analyze reports, extract KPIs, compare datasets, or identify business trends."}
              </p>
            </div>
          )}

          {msgs.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "ai" && (
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <Brain size={13} className="text-white" />
                </div>
              )}
              <div className="max-w-2xl">
                {msg.role === "ai" && (
                  <p className="text-xs font-semibold text-slate-500 mb-1.5 font-['Plus_Jakarta_Sans']">
                    {agent === "cs" ? "CS Agent" : "Data Analyst"}
                  </p>
                )}
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === "user" ? "bg-blue-600 text-white rounded-br-sm" : "bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm"}`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.role === "ai" && msg.citations && (
                    <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-slate-100">
                      {msg.citations.map((c, j) => (
                        <button key={j} className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded-full hover:bg-blue-100 transition-colors font-mono">
                          [{j + 1}] {c.doc}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {msg.role === "ai" && (
                  <div className="flex items-center gap-3 mt-1.5">
                    {[{ icon: ThumbsUp, label: "Helpful" }, { icon: Copy, label: "Copy" }, { icon: RotateCcw, label: "Retry" }].map(({ icon: Icon, label }) => (
                      <button key={label} aria-label={label} className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 transition-colors">
                        <Icon size={11} /> {label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === "user" && <Av initials="SC" size="sm" bg="bg-slate-700" />}
            </div>
          ))}

          {typing && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Brain size={13} className="text-white" />
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <div className="flex items-center gap-1">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggested */}
        {msgs.length <= 2 && (
          <div className="px-4 pb-2 max-w-3xl mx-auto w-full">
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide font-['Plus_Jakarta_Sans'] font-semibold" style={{ fontSize: 10 }}>Suggested</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.slice(0, 3).map(q => (
                <button key={q} onClick={() => setInput(q)}
                  className="text-xs bg-white border border-slate-200 text-slate-600 hover:border-blue-300 hover:text-blue-700 px-3 py-1.5 rounded-full transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="px-4 pb-5 max-w-3xl mx-auto w-full">
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
              placeholder="Ask anything about your company documents..."
              rows={3}
              className="w-full px-5 pt-4 pb-2 text-sm text-slate-800 placeholder-slate-400 bg-transparent resize-none focus:outline-none leading-relaxed"
            />
            <div className="flex items-center justify-between px-4 pb-3">
              <div className="flex items-center gap-2">
                <button aria-label="Attach file" className="text-slate-400 hover:text-blue-600 transition-colors"><Paperclip size={15} /></button>
                <span className="text-xs text-slate-400 font-mono">{input.length}/4000</span>
              </div>
              <button onClick={send} disabled={!input.trim()}
                className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-bold px-4 py-2 rounded-xl transition-colors" aria-label="Send">
                <Send size={13} /> Send
              </button>
            </div>
          </div>
          <p className="text-center text-xs text-slate-400 mt-2">AI responses are grounded in your documents. Verify critical information at the source.</p>
        </div>
      </div>

      {/* Citations panel */}
      {showCitations && (
        <div className="hidden lg:flex w-72 flex-shrink-0 bg-white border-l border-slate-200 flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
            <h3 className="font-['Plus_Jakarta_Sans'] text-sm font-bold text-slate-800">Source Citations</h3>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-mono">{citations.length}</span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {citations.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen size={26} className="text-slate-300 mx-auto mb-3" />
                <p className="text-xs text-slate-400 leading-relaxed">Sources will appear here when AI references your documents</p>
              </div>
            ) : citations.map((c, i) => (
              <div key={i} className="bg-slate-50 border border-slate-200 rounded-xl p-3 hover:border-blue-200 transition-colors">
                <div className="flex items-start gap-2 mb-2">
                  <div className="w-5 h-5 bg-blue-100 rounded flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-mono font-bold text-blue-700">{i + 1}</span>
                  </div>
                  <p className="text-sm font-bold text-slate-800 leading-tight font-['Plus_Jakarta_Sans']">{c.doc}</p>
                </div>
                <p className="text-xs font-mono text-slate-500 mb-2">Page {c.page}</p>
                <p className="text-xs text-slate-600 leading-relaxed italic">&ldquo;{c.excerpt}&rdquo;</p>
                <button className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 mt-2 transition-colors">
                  <ExternalLink size={10} /> View document
                </button>
              </div>
            ))}
          </div>
          <div className="border-t border-slate-100 p-3 flex-shrink-0">
            <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3">
              <p className="text-xs text-indigo-700 font-bold font-['Plus_Jakarta_Sans'] mb-1.5">Relevance score</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-indigo-200 rounded-full h-1.5">
                  <div className="bg-indigo-600 h-1.5 rounded-full" style={{ width: "87%" }} />
                </div>
                <span className="text-xs font-mono text-indigo-700 font-bold">87%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Documents ────────────────────────────────────────────────────────────────

function DocumentsPage() {
  const [dragOver, setDragOver] = useState(false);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [docList, setDocList] = useState(documents);

  const filtered = docList.filter(d => {
    const ms = d.name.toLowerCase().includes(search.toLowerCase());
    const mst = filterStatus === "all" || d.status === filterStatus;
    return ms && mst;
  });

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="font-['Plus_Jakarta_Sans'] text-xl font-extrabold text-slate-900">Knowledge Base</h2>
          <p className="text-sm text-slate-500">{docList.length} documents · {docList.filter(d => d.status === "ready").length} indexed</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-1.5 border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors">
            <Download size={14} /> Export
          </button>
          <button className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
            <Upload size={14} /> Upload Docs
          </button>
        </div>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); }}
        className={`border-2 border-dashed rounded-2xl p-10 flex flex-col items-center cursor-pointer transition-all ${dragOver ? "border-blue-500 bg-blue-50" : "border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50"}`}
      >
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-colors ${dragOver ? "bg-blue-100" : "bg-slate-100"}`}>
          <Upload size={22} className={dragOver ? "text-blue-600" : "text-slate-400"} />
        </div>
        <p className="font-['Plus_Jakarta_Sans'] font-bold text-slate-700 mb-1">{dragOver ? "Drop files to upload" : "Drag & drop files here"}</p>
        <p className="text-sm text-slate-500 mb-4">or click to browse — PDF, DOCX, XLSX, PPTX up to 50 MB</p>
        <button className="text-sm bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 px-5 py-2 rounded-lg font-semibold transition-colors">Browse files</button>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-3 py-2.5 flex-1">
          <Search size={14} className="text-slate-400 flex-shrink-0" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search documents..." className="bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none flex-1" />
        </div>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-700 focus:outline-none cursor-pointer">
          <option value="all">All Status</option>
          <option value="ready">Ready</option>
          <option value="processing">Processing</option>
          <option value="queued">Queued</option>
          <option value="error">Error</option>
        </select>
      </div>

      {/* Document table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-100 grid grid-cols-12 gap-3 text-xs font-bold text-slate-400 uppercase tracking-widest font-['Plus_Jakarta_Sans']" style={{ fontSize: 10 }}>
          <div className="col-span-5">Document</div>
          <div className="col-span-2 hidden md:block">Category</div>
          <div className="col-span-2 hidden sm:block">Uploaded</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-1 text-right">Act.</div>
        </div>
        {filtered.length === 0 ? (
          <div className="text-center py-14">
            <FileText size={30} className="text-slate-300 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No documents match your filters</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filtered.map(doc => (
              <div key={doc.id} className="px-4 py-3.5 grid grid-cols-12 gap-3 items-center hover:bg-slate-50 transition-colors group">
                <div className="col-span-5 flex items-center gap-3 min-w-0">
                  <DocIcon type={doc.type} />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-800 truncate">{doc.name}</p>
                    <p className="text-xs text-slate-500 font-mono">{doc.size} · {doc.pages}p</p>
                    {doc.status === "processing" && (
                      <div className="mt-1.5 flex items-center gap-2">
                        <div className="w-20 bg-amber-100 rounded-full h-1.5">
                          <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${doc.progress}%` }} />
                        </div>
                        <span className="text-xs font-mono text-amber-700">{doc.progress}%</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="col-span-2 hidden md:block">
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">{doc.category}</span>
                </div>
                <div className="col-span-2 hidden sm:block">
                  <p className="text-xs text-slate-500">{doc.date}</p>
                </div>
                <div className="col-span-2">
                  <Chip variant={doc.status}>{doc.status}</Chip>
                </div>
                <div className="col-span-1 flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button aria-label="View" className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"><Eye size={12} /></button>
                  <button aria-label="Delete" onClick={() => setDocList(p => p.filter(d => d.id !== doc.id))} className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-red-100 text-slate-500 hover:text-red-600 transition-colors"><Trash2 size={12} /></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Documents", value: docList.length, icon: FileText, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Indexed & Ready", value: docList.filter(d => d.status === "ready").length, icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-50" },
          { label: "Processing", value: docList.filter(d => d.status === "processing").length, icon: RefreshCw, color: "text-amber-600", bg: "bg-amber-50" },
          { label: "Errors", value: docList.filter(d => d.status === "error").length, icon: AlertCircle, color: "text-red-600", bg: "bg-red-50" },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className={`w-9 h-9 ${bg} rounded-lg flex items-center justify-center flex-shrink-0`}>
              <Icon size={16} className={color} />
            </div>
            <div>
              <p className="font-['Plus_Jakarta_Sans'] text-xl font-extrabold text-slate-900">{value}</p>
              <p className="text-xs text-slate-500">{label}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── User Management ──────────────────────────────────────────────────────────

function UsersPage() {
  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("all");

  const filtered = users.filter(u => {
    const ms = u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase());
    const mr = filterRole === "all" || u.role.toLowerCase() === filterRole;
    return ms && mr;
  });

  const roleBg: Record<string, string> = { Admin: "bg-violet-600", Manager: "bg-blue-600", Employee: "bg-slate-600", Support: "bg-cyan-600" };

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="font-['Plus_Jakarta_Sans'] text-xl font-extrabold text-slate-900">Team Members</h2>
          <p className="text-sm text-slate-500">{users.length} users · {users.filter(u => u.status === "active").length} active</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
          <UserPlus size={14} /> Invite Member
        </button>
      </div>

      {/* Role cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { role: "Admin", desc: "Full access: billing, settings, and user management", icon: Shield, bg: "bg-violet-50", icon_color: "text-violet-600", count: users.filter(u => u.role === "Admin").length },
          { role: "Manager", desc: "Analytics, document uploads, and team oversight", icon: Eye, bg: "bg-blue-50", icon_color: "text-blue-600", count: users.filter(u => u.role === "Manager").length },
          { role: "Employee", desc: "AI chat access, personal uploads, read-only reports", icon: Users, bg: "bg-slate-100", icon_color: "text-slate-600", count: users.filter(u => u.role === "Employee").length },
          { role: "Support", desc: "CS Agent access, customer-facing document queries", icon: HeadphonesIcon, bg: "bg-cyan-50", icon_color: "text-cyan-600", count: users.filter(u => u.role === "Support").length },
        ].map(({ role, desc, icon: Icon, bg, icon_color, count }) => (
          <div key={role} className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-9 h-9 ${bg} rounded-lg flex items-center justify-center`}>
                <Icon size={17} className={icon_color} />
              </div>
              <span className="font-['Plus_Jakarta_Sans'] text-2xl font-extrabold text-slate-900">{count}</span>
            </div>
            <p className="font-['Plus_Jakarta_Sans'] font-bold text-slate-800 text-sm mb-1">{role}</p>
            <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      {/* Search + filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-3 py-2.5 flex-1">
          <Search size={14} className="text-slate-400 flex-shrink-0" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name or email..." className="bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none flex-1" />
        </div>
        <select value={filterRole} onChange={e => setFilterRole(e.target.value)} className="bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-700 focus:outline-none cursor-pointer">
          <option value="all">All Roles</option>
          <option value="admin">Admin</option>
          <option value="manager">Manager</option>
          <option value="employee">Employee</option>
          <option value="support">Support</option>
        </select>
      </div>

      {/* User table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-100 grid grid-cols-12 gap-3 text-xs font-bold text-slate-400 uppercase tracking-widest font-['Plus_Jakarta_Sans']" style={{ fontSize: 10 }}>
          <div className="col-span-4">User</div>
          <div className="col-span-2 hidden md:block">Department</div>
          <div className="col-span-2">Role</div>
          <div className="col-span-2 hidden sm:block">Queries</div>
          <div className="col-span-1 hidden md:block">Status</div>
          <div className="col-span-1 text-right">Act.</div>
        </div>
        <div className="divide-y divide-slate-100">
          {filtered.map(user => (
            <div key={user.id} className="px-4 py-3.5 grid grid-cols-12 gap-3 items-center hover:bg-slate-50 transition-colors group">
              <div className="col-span-4 flex items-center gap-3 min-w-0">
                <Av initials={user.avatar} size="sm" bg={roleBg[user.role] || "bg-blue-600"} />
                <div className="min-w-0">
                  <p className="text-sm font-bold text-slate-800 truncate font-['Plus_Jakarta_Sans']">{user.name}</p>
                  <p className="text-xs text-slate-500 truncate font-mono">{user.email}</p>
                </div>
              </div>
              <div className="col-span-2 hidden md:block">
                <p className="text-xs text-slate-600">{user.dept}</p>
              </div>
              <div className="col-span-2">
                <Chip variant={user.role.toLowerCase()}>{user.role}</Chip>
              </div>
              <div className="col-span-2 hidden sm:block">
                <p className="text-sm font-mono font-bold text-slate-700">{user.queries.toLocaleString()}</p>
              </div>
              <div className="col-span-1 hidden md:block">
                <Chip variant={user.status}>{user.status}</Chip>
              </div>
              <div className="col-span-1 flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button aria-label="Edit" className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"><Edit3 size={12} /></button>
                <button aria-label="More" className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"><MoreVertical size={12} /></button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Analytics ────────────────────────────────────────────────────────────────

function AnalyticsPage() {
  const kpis = [
    { label: "Total Queries (30d)", value: "12,847", delta: "+23%", icon: MessageSquare, ic: "text-blue-600", bg: "bg-blue-50" },
    { label: "Documents Indexed", value: "238", delta: "+18 this week", icon: FileText, ic: "text-indigo-600", bg: "bg-indigo-50" },
    { label: "Active Users", value: "341", delta: "+7% MoM", icon: Users, ic: "text-emerald-600", bg: "bg-emerald-50" },
    { label: "Avg. Response", value: "1.4s", delta: "-0.3s MoM", icon: Zap, ic: "text-amber-600", bg: "bg-amber-50" },
  ];
  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      <div>
        <h2 className="font-['Plus_Jakarta_Sans'] text-xl font-extrabold text-slate-900">Analytics Overview</h2>
        <p className="text-sm text-slate-500">Last 30 days · Acme Corporation workspace</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map(({ label, value, delta, icon: Icon, ic, bg }) => (
          <div key={label} className="bg-white border border-slate-200 rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div className={`w-9 h-9 ${bg} rounded-lg flex items-center justify-center`}>
                <Icon size={16} className={ic} />
              </div>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">{delta}</span>
            </div>
            <p className="font-['Plus_Jakarta_Sans'] text-2xl font-extrabold text-slate-900 mb-0.5">{value}</p>
            <p className="text-xs text-slate-500">{label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-800">Query Volume</h3>
            <select className="text-xs border border-slate-200 rounded-lg px-2 py-1 text-slate-600 bg-white focus:outline-none cursor-pointer">
              <option>Last 7 days</option><option>Last 30 days</option>
            </select>
          </div>
          <ResponsiveContainer width="100%" height={210}>
            <AreaChart data={queryData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="gBlue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gIndigo" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Area type="monotone" dataKey="queries" stroke="#2563EB" strokeWidth={2} fill="url(#gBlue)" name="Total" dot={false} />
              <Area type="monotone" dataKey="resolved" stroke="#6366F1" strokeWidth={2} fill="url(#gIndigo)" name="Resolved" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5">
          <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-800 mb-4">Agent Usage Split</h3>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={agentUsageData} cx="50%" cy="50%" innerRadius={46} outerRadius={70} paddingAngle={4} dataKey="value">
                {agentUsageData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip formatter={(v) => `${v}%`} contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-2">
            {agentUsageData.map(({ name, value, color }) => (
              <div key={name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                  <span className="text-xs text-slate-600">{name}</span>
                </div>
                <span className="text-xs font-mono font-bold text-slate-800">{value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Doc categories + Activity */}
      <div className="grid lg:grid-cols-2 gap-5">
        <div className="bg-white border border-slate-200 rounded-2xl p-5">
          <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-800 mb-4">Documents by Category</h3>
          <ResponsiveContainer width="100%" height={190}>
            <BarChart data={docCategoryData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }} barSize={16}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="category" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }} />
              <Bar dataKey="count" fill="#2563EB" radius={[4, 4, 0, 0]} name="Documents" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5">
          <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-800 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {activityFeed.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`w-7 h-7 ${item.color} rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 bg-opacity-20`} style={{ backgroundColor: item.color.includes("blue") ? "#DBEAFE" : item.color.includes("indigo") ? "#E0E7FF" : item.color.includes("violet") ? "#EDE9FE" : "#D1FAE5" }}>
                  <span className="text-xs font-bold">{item.user[0]}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-700 leading-snug">
                    <span className="font-bold text-slate-900">{item.user}</span>{" "}
                    <span className="text-slate-500">{item.action}</span>{" "}
                    <span className="text-slate-700 truncate">{item.target}</span>
                  </p>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top queries */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-800">Top Queries This Week</h3>
        </div>
        <div className="divide-y divide-slate-100">
          {[
            { query: "What is the remote work equipment reimbursement policy?", count: 147, agent: "cs", trend: "+12%" },
            { query: "How do I submit an expense report?", count: 134, agent: "cs", trend: "+8%" },
            { query: "Q3 revenue breakdown by product line", count: 98, agent: "analyst", trend: "+31%" },
            { query: "Parental leave entitlements for senior employees", count: 87, agent: "cs", trend: "+5%" },
            { query: "Headcount vs budget variance Q3 vs Q4", count: 74, agent: "analyst", trend: "+19%" },
          ].map(({ query, count, agent, trend }, i) => (
            <div key={i} className="px-5 py-3.5 flex items-center gap-4">
              <span className="text-xs font-mono text-slate-400 w-4 flex-shrink-0">{i + 1}</span>
              <p className="flex-1 text-sm text-slate-700 min-w-0 truncate">{query}</p>
              <Chip variant={agent}>{agent === "cs" ? "CS" : "Analyst"}</Chip>
              <span className="text-xs font-mono font-bold text-slate-700 w-8 text-right flex-shrink-0">{count}</span>
              <span className="text-xs font-mono text-emerald-600 w-10 text-right flex-shrink-0">{trend}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Settings ─────────────────────────────────────────────────────────────────

function SettingsPage() {
  const [tab, setTab] = useState<SettingsTab>("profile");
  const tabs: { id: SettingsTab; icon: any; label: string }[] = [
    { id: "profile", icon: Building2, label: "Company Profile" },
    { id: "security", icon: Lock, label: "Security" },
    { id: "ai", icon: Cpu, label: "AI Config" },
    { id: "branding", icon: Palette, label: "Branding" },
    { id: "billing", icon: CreditCard, label: "Billing" },
  ];
  const [toggles, setToggles] = useState({ mfa: true, sso: false, timeout: true, audit: true });

  return (
    <div className="p-6 overflow-auto h-full">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h2 className="font-['Plus_Jakarta_Sans'] text-xl font-extrabold text-slate-900">Settings</h2>
          <p className="text-sm text-slate-500">Workspace, security, and AI configuration</p>
        </div>
        <div className="flex gap-6">
          {/* Settings nav */}
          <nav className="w-48 flex-shrink-0 space-y-0.5">
            {tabs.map(({ id, icon: Icon, label }) => (
              <button key={id} onClick={() => setTab(id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all text-left font-['Plus_Jakarta_Sans'] ${tab === id ? "bg-blue-50 text-blue-700" : "text-slate-600 hover:bg-slate-100"}`}>
                <Icon size={15} className={tab === id ? "text-blue-600" : "text-slate-400"} />
                {label}
              </button>
            ))}
          </nav>

          {/* Content */}
          <div className="flex-1 space-y-4">
            {tab === "profile" && (
              <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-5">
                <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900">Company Profile</h3>
                <div className="flex items-center gap-4 pb-5 border-b border-slate-100">
                  <div className="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Brain size={24} className="text-white" />
                  </div>
                  <div>
                    <p className="font-bold text-slate-800 font-['Plus_Jakarta_Sans']">Acme Corporation</p>
                    <p className="text-sm text-slate-500">acmecorp.knowmate.ai</p>
                    <button className="text-sm text-blue-600 hover:text-blue-700 mt-1">Change logo</button>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: "Company Name", value: "Acme Corporation" },
                    { label: "Industry", value: "Technology" },
                    { label: "Company Size", value: "201–1000 employees" },
                    { label: "Workspace URL", value: "acmecorp.knowmate.ai" },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">{label}</label>
                      <input defaultValue={value} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:bg-white transition" />
                    </div>
                  ))}
                  <div className="col-span-2">
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5">HQ Address</label>
                    <input defaultValue="123 Market Street, San Francisco, CA 94105" className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:bg-white transition" />
                  </div>
                </div>
                <div className="flex justify-end">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-5 py-2.5 rounded-xl transition-colors">Save Changes</button>
                </div>
              </div>
            )}

            {tab === "security" && (
              <div className="space-y-3">
                {[
                  { key: "mfa" as const, icon: Shield, title: "Two-Factor Authentication", desc: "Require 2FA for all workspace members" },
                  { key: "sso" as const, icon: Key, title: "Single Sign-On (SSO/SAML)", desc: "Connect Okta, Azure AD, or Google Workspace" },
                  { key: "timeout" as const, icon: Clock, title: "Session Timeout", desc: "Auto sign-out inactive users after 30 minutes" },
                  { key: "audit" as const, icon: Eye, title: "Audit Log", desc: "Full trail of user and AI actions in your workspace" },
                ].map(({ key, icon: Icon, title, desc }) => (
                  <div key={key} className="bg-white border border-slate-200 rounded-2xl p-5 flex items-center gap-4">
                    <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Icon size={17} className="text-slate-500" />
                    </div>
                    <div className="flex-1">
                      <p className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900 text-sm">{title}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
                    </div>
                    <button onClick={() => setToggles(t => ({ ...t, [key]: !t[key] }))}
                      className={`w-11 h-6 rounded-full relative transition-colors flex-shrink-0 ${toggles[key] ? "bg-blue-600" : "bg-slate-300"}`}
                      aria-checked={toggles[key]} role="switch" aria-label={title}>
                      <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-all ${toggles[key] ? "left-5" : "left-0.5"}`} />
                    </button>
                  </div>
                ))}
                <div className="bg-white border border-slate-200 rounded-2xl p-5">
                  <h4 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900 mb-4">API Keys</h4>
                  <div className="space-y-2">
                    {[
                      { name: "Production Key", created: "Jun 1, 2024", last: "2 minutes ago" },
                      { name: "Development Key", created: "Apr 15, 2024", last: "3 days ago" },
                    ].map(({ name, created, last }) => (
                      <div key={name} className="flex items-center gap-4 p-3 bg-slate-50 rounded-xl">
                        <Key size={14} className="text-slate-500 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-slate-800">{name}</p>
                          <p className="text-xs text-slate-500 font-mono">Created {created} · Last used {last}</p>
                        </div>
                        <button className="text-xs text-red-600 hover:text-red-700 font-semibold">Revoke</button>
                      </div>
                    ))}
                  </div>
                  <button className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 mt-3 font-semibold">
                    <Plus size={14} /> Generate new key
                  </button>
                </div>
              </div>
            )}

            {tab === "ai" && (
              <div className="space-y-4">
                <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-5">
                  <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900">AI Model Configuration</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">Base Model</label>
                      <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 cursor-pointer">
                        <option>GPT-4o (Recommended)</option>
                        <option>Claude 3.5 Sonnet</option>
                        <option>GPT-4 Turbo</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">Embedding Model</label>
                      <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 cursor-pointer">
                        <option>text-embedding-3-large</option>
                        <option>text-embedding-3-small</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5">Response Temperature <span className="font-mono text-blue-600">0.3</span></label>
                    <input type="range" min="0" max="1" step="0.1" defaultValue="0.3" className="w-full accent-blue-600" />
                    <div className="flex justify-between text-xs text-slate-400 mt-1"><span>Precise</span><span>Balanced</span><span>Creative</span></div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">Context Window</label>
                      <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 cursor-pointer">
                        <option>8,192 tokens</option><option>16,384 tokens</option><option>128,000 tokens</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">Top-K Retrieval</label>
                      <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 cursor-pointer">
                        <option>5 results</option><option>10 results</option><option>15 results</option>
                      </select>
                    </div>
                  </div>
                </div>
                {[
                  { name: "Customer Service Agent", icon: HeadphonesIcon, persona: "You are a helpful, empathetic customer service assistant. Always respond professionally and warmly. Cite company policies accurately and escalate when unsure.", bg: "bg-blue-100", ic: "text-blue-600" },
                  { name: "Data Analyst Agent", icon: TrendingUp, persona: "You are a precise data analyst. Provide structured, quantitative answers with tables where relevant. Always cite the exact document and page number for every data point.", bg: "bg-indigo-100", ic: "text-indigo-600" },
                ].map(({ name, icon: Icon, persona, bg, ic }) => (
                  <div key={name} className="bg-white border border-slate-200 rounded-2xl p-5">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-9 h-9 ${bg} rounded-xl flex items-center justify-center`}><Icon size={16} className={ic} /></div>
                      <p className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900">{name}</p>
                    </div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5">System Prompt / Persona</label>
                    <textarea defaultValue={persona} rows={3} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:bg-white transition resize-none" />
                  </div>
                ))}
                <div className="flex justify-end">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-5 py-2.5 rounded-xl transition-colors">Save AI Settings</button>
                </div>
              </div>
            )}

            {tab === "branding" && (
              <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6">
                <h3 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900">Branding</h3>
                <div className="grid grid-cols-2 gap-6">
                  {[{ label: "Primary Color", value: "#2563EB" }, { label: "Accent Color", value: "#6366F1" }].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-sm font-semibold text-slate-700 mb-3">{label}</p>
                      <div className="flex items-center gap-3">
                        <input type="color" defaultValue={value} className="w-12 h-12 rounded-xl border-0 cursor-pointer" />
                        <input defaultValue={value} className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-mono text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                    </div>
                  ))}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-3">Workspace Logo</p>
                  <div className="border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center hover:border-blue-300 transition-colors cursor-pointer">
                    <Upload size={22} className="text-slate-400 mx-auto mb-2" />
                    <p className="text-sm text-slate-600 font-medium">Drop your logo here or click to upload</p>
                    <p className="text-xs text-slate-400 mt-1">SVG, PNG — max 2 MB, transparent background recommended</p>
                  </div>
                </div>
                <div className="flex justify-end">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-5 py-2.5 rounded-xl transition-colors">Save Branding</button>
                </div>
              </div>
            )}

            {tab === "billing" && (
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 text-white">
                  <div className="flex items-center justify-between mb-4">
                    <p className="font-['Plus_Jakarta_Sans'] font-bold text-lg">Enterprise Plan</p>
                    <span className="bg-white/20 text-white text-xs font-mono font-bold px-3 py-1 rounded-full">ACTIVE</span>
                  </div>
                  <p className="text-blue-100 text-sm mb-4">Unlimited users · 50 GB storage · Priority support · Custom SLAs</p>
                  <p className="font-['Plus_Jakarta_Sans'] text-3xl font-extrabold">$1,200<span className="text-blue-200 text-base font-normal">/month</span></p>
                  <p className="text-blue-200 text-xs mt-1">Next billing: August 1, 2024</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-5">
                  <h4 className="font-['Plus_Jakarta_Sans'] font-bold text-slate-900 mb-4">Usage This Cycle</h4>
                  {[
                    { label: "API Queries", used: 12847, limit: 50000 },
                    { label: "Storage", used: 24, limit: 50, unit: "GB" },
                    { label: "Active Users", used: 341, limit: 500 },
                  ].map(({ label, used, limit, unit }) => (
                    <div key={label} className="mb-4">
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="text-slate-600">{label}</span>
                        <span className="font-mono text-slate-700 font-semibold">{used.toLocaleString()}{unit || ""} / {limit.toLocaleString()}{unit || ""}</span>
                      </div>
                      <div className="bg-slate-100 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${(used / limit) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Dashboard Layout ─────────────────────────────────────────────────────────

function DashboardLayout({ go }: { go: (v: View) => void }) {
  const [subView, setSubView] = useState<SubView>("ai");
  const [agent, setAgent] = useState<AgentType>("cs");
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const content = () => {
    switch (subView) {
      case "ai": return <AIAssistantPage agent={agent} />;
      case "documents": return <DocumentsPage />;
      case "users": return <UsersPage />;
      case "analytics": return <AnalyticsPage />;
      case "settings": return <SettingsPage />;
    }
  };

  return (
    <div className="h-screen flex overflow-hidden bg-background font-['DM_Sans']">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}
      {/* Mobile sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 lg:hidden transition-transform duration-300 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <Sidebar subView={subView} setSubView={v => { setSubView(v); setMobileOpen(false); }} collapsed={false} setCollapsed={() => { }} go={go} />
      </div>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex">
        <Sidebar subView={subView} setSubView={setSubView} collapsed={collapsed} setCollapsed={setCollapsed} go={go} />
      </div>

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Mobile topbar */}
        <div className="lg:hidden h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3 flex-shrink-0">
          <button onClick={() => setMobileOpen(true)} aria-label="Open menu" className="text-slate-500 hover:text-slate-700">
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center"><Brain size={13} className="text-white" /></div>
            <span className="font-['Plus_Jakarta_Sans'] font-extrabold text-slate-900">KnowMate</span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <button className="relative w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors" aria-label="Notifications">
              <Bell size={16} className="text-slate-500" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            <Av initials="SC" size="sm" />
          </div>
        </div>
        {/* Desktop topbar */}
        <div className="hidden lg:block">
          <TopBar subView={subView} agent={agent} setAgent={setAgent} />
        </div>

        <main className="flex-1 overflow-hidden">
          {content()}
        </main>
      </div>
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState<View>("landing");
  const go = (v: View) => setView(v);

  switch (view) {
    case "landing": return <LandingPage go={go} />;
    case "login": return <LoginPage go={go} />;
    case "register": return <RegisterPage go={go} />;
    case "forgot": return <ForgotPage go={go} />;
    case "dashboard": return <DashboardLayout go={go} />;
  }
}
