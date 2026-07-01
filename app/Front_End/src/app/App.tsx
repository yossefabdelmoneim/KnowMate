import { useState, useRef, useEffect, useCallback } from "react";
import {
  Plus, Search, ChevronLeft, ChevronRight, Send, Paperclip,
  Mic, Sun, Moon, FileText, FileSpreadsheet, FileImage,
  File, X, Check, Sparkles, BookOpen, Table, Zap,
  MessageSquare, Settings, LogOut, User, HelpCircle,
  ChevronDown, Loader2, AlertCircle
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import HomePage from "./components/HomePage";
import { AuthPage } from "./components/AuthPage";
import { SettingsPage } from "./components/SettingsPage";
import { ProfilePage } from "./components/ProfilePage";
import { ChatMessage } from "./components/ChatMessage";
import { FileCard } from "./components/FileCard";
import { TypingIndicator } from "./components/TypingIndicator";
import { ConversationGroup } from "./components/ConversationGroup";
import { useAuth } from "./contexts/AuthContext";
import { api } from "./services/api";
import type { Mode, UploadedFile, Message, Conversation } from "./types";

// ── Helpers ──────────────────────────────────────────────────────────────────

const fileIconMap: Record<string, string> = {
  pdf: "PDF", docx: "DOC", xlsx: "XLS", pptx: "PPT", csv: "CSV", txt: "TXT", img: "IMG",
};

const SUGGESTED_PROMPTS = [
  { icon: <BookOpen size={18} />, label: "Summarize document", desc: "Get a concise overview of any uploaded file" },
  { icon: <Table size={18} />, label: "Analyze spreadsheet", desc: "Extract insights from Excel or CSV data" },
  { icon: <Sparkles size={18} />, label: "Extract key insights", desc: "Pull out critical findings and themes" },
  { icon: <Zap size={18} />, label: "Compare documents", desc: "Find differences across multiple files" },
];

function fileTypeIcon(type: string) {
  if (type === "xlsx" || type === "csv") return <FileSpreadsheet size={16} />;
  if (type === "img") return <FileImage size={16} />;
  if (type === "pdf" || type === "docx" || type === "pptx" || type === "txt") return <FileText size={16} />;
  return <File size={16} />;
}

const fileColorMap: Record<string, string> = {
  pdf: "bg-red-500/10 text-red-600 dark:text-red-400",
  docx: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  xlsx: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
  pptx: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
  csv: "bg-green-500/10 text-green-600 dark:text-green-400",
  txt: "bg-gray-500/10 text-gray-600 dark:text-gray-400",
  img: "bg-purple-500/10 text-purple-600 dark:text-purple-400",
};

// ── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const { user, loading, logout: authLogout } = useAuth();
  const [dark, setDark] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mode, setMode] = useState<Mode>(user ? "welcome" : "home");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [messages, setMessages] = useState<Message[]>([]);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showUserMenu, setShowUserMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── Sessions (conversations) state ──
  const [sessions, setSessions] = useState<Conversation[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [sessionsError, setSessionsError] = useState("");
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // ── Recent documents for welcome page ──
  const [recentDocs, setRecentDocs] = useState<{ name: string; size: string; type: string; date: string }[]>([]);
  const [docsLoading, setDocsLoading] = useState(false);

  // ── Chat error state ──
  const [chatError, setChatError] = useState("");

  useEffect(() => {
    if (dark) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [dark]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    if (!loading) {
      if (!user && mode !== "login" && mode !== "register" && mode !== "home") {
        setMode("home");
      } else if (user && (mode === "login" || mode === "register" || mode === "home")) {
        setMode("welcome");
      }
    }
  }, [loading, user, mode]);

  // Load sessions from backend
  const loadSessions = useCallback(async () => {
    setSessionsLoading(true);
    setSessionsError("");
    try {
      const data = await api.get<{ id: string; title: string; updated_at: string; messages?: unknown[] }[]>("/sessions");
      const mapped: Conversation[] = (data || []).map((s: { id: string; title: string; updated_at: string; messages?: unknown[] }) => ({
        id: s.id,
        title: s.title || "Untitled",
        preview: `${Array.isArray(s.messages) ? s.messages.length : 0} messages`,
        date: new Date(s.updated_at || Date.now()),
      }));
      setSessions(mapped);
    } catch (e) {
      setSessionsError(e instanceof Error ? e.message : "Failed to load conversations");
    } finally {
      setSessionsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      loadSessions();
    }
  }, [user, loadSessions]);

  const groupedConvs = {
    today: sessions.filter(c => c.date.toDateString() === new Date().toDateString()),
    yesterday: sessions.filter(c => {
      const y = new Date(); y.setDate(y.getDate() - 1);
      return c.date.toDateString() === y.toDateString();
    }),
    last7: sessions.filter(c => {
      const diff = (Date.now() - c.date.getTime()) / 86400000;
      return diff > 1 && diff <= 7;
    }),
    older: sessions.filter(c => (Date.now() - c.date.getTime()) / 86400000 > 7),
  };

  // ── File Upload ──

  const uploadFile = useCallback(async (file: File): Promise<UploadedFile> => {
    const id = Math.random().toString(36).slice(2);
    const ext = file.name.split(".").pop()?.toLowerCase() || "txt";
    const types: UploadedFile["icon"][] = ["pdf", "docx", "xlsx", "pptx", "csv", "txt", "img"];
    const icon = types.includes(ext as UploadedFile["icon"]) ? ext as UploadedFile["icon"] : "txt";
    const sizeStr = file.size > 1024 * 1024
      ? `${(file.size / (1024 * 1024)).toFixed(1)} MB`
      : `${(file.size / 1024).toFixed(0)} KB`;

    const entry: UploadedFile = { id, name: file.name, size: sizeStr, type: "", status: "uploading", progress: 0, icon };

    setFiles(prev => [...prev, entry]);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("company_id", String(user?.company_id ?? 1));

      const result = await api.postForm<{ doc_id: string; chunks: number }>("/documents/upload", formData);

      setFiles(prev => prev.map(x => x.id === id ? { ...x, status: "ready", progress: 100, type: result.doc_id } : x));

      return { ...entry, status: "ready", progress: 100, type: result.doc_id };
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : "Upload failed";
      setFiles(prev => prev.map(x => x.id === id ? { ...x, status: "error", errorMessage: errMsg } : x));
      return { ...entry, status: "error", errorMessage: errMsg };
    }
  }, []);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    Array.from(e.dataTransfer.files).forEach(f => uploadFile(f));
    if (mode !== "chat") setMode("chat");
  }, [uploadFile, mode]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    Array.from(e.target.files ?? []).forEach(f => uploadFile(f));
    e.target.value = "";
    if (mode !== "chat") setMode("chat");
  }, [uploadFile, mode]);

  // ── Chat / Send Message ──

  const sendMessage = useCallback(async () => {
    const hasReadyFiles = files.filter(f => f.status === "ready").length > 0;
    if (!input.trim() && !hasReadyFiles) return;

    const userMsg: Message = {
      id: Math.random().toString(36).slice(2),
      role: "user",
      content: input || "Please analyze the uploaded document.",
      files: files.filter(f => f.status === "ready").map(f => f.name),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setChatError("");
    if (mode !== "chat") setMode("chat");
    setIsTyping(true);

    try {
      const data = await api.post<{ answer: string; sources: { source: string }[] }>("/api/chat", {
        question: input || "Please analyze the uploaded document.",
        company_id: String(user?.company_id ?? 1),
        agent_type: "default",
      });
      const aiMsg: Message = {
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
        citations: data.sources?.map((s, i) => ({ id: i + 1, source: s.source })) || [],
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : "An error occurred";
      setChatError(errMsg);
      const aiMsg: Message = {
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [input, files, mode, user]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const handleFeedback = (id: string, v: "up" | "down") => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, feedback: v } : m));
  };

  const startNewChat = () => {
    setMessages([]);
    setFiles([]);
    setInput("");
    setActiveConvId(null);
    setCurrentSessionId(null);
    setChatError("");
    setMode("welcome");
  };

  const selectConversation = async (id: string) => {
    setActiveConvId(id);
    setCurrentSessionId(id);
    setMode("chat");
    setMessages([]);
    try {
      const data = await api.get<{ id: string; title: string; messages: { role: string; content: string }[] }>(`/sessions/${id}`);
      if (data.messages) {
        const msgs: Message[] = data.messages.map((m: { role: string; content: string }) => ({
          id: Math.random().toString(36).slice(2),
          role: m.role as "user" | "assistant",
          content: m.content,
          timestamp: new Date(),
        }));
        setMessages(msgs);
      }
    } catch {
      setMessages([]);
    }
  };

  // ── Loading state ──

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">Loading KnowMate...</p>
        </div>
      </div>
    );
  }

  if (mode === "home") {
    return <HomePage onNavigate={(page) => { setMode(page as Mode); setAuthMode(page as "login" | "register"); }} />;
  }

  if (mode === "login" || mode === "register") {
    return (
      <AuthPage
        mode={mode === "login" ? authMode : "register"}
        onToggle={() => setAuthMode(m => m === "login" ? "register" : "login")}
        onSuccess={() => setMode("welcome")}
      />
    );
  }

  if (mode === "settings") {
    return <SettingsPage user={user} onBack={() => setMode("welcome")} />;
  }

  if (mode === "profile") {
    return <ProfilePage user={user} onBack={() => setMode("welcome")} />;
  }

  return (
    <div
      className="h-screen flex bg-background overflow-hidden font-[Inter,sans-serif]"
      style={{ fontFamily: "'Inter', sans-serif" }}
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleFileDrop}
    >
      {/* Drag overlay */}
      <AnimatePresence>
        {dragging && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 flex items-center justify-center bg-background/90 backdrop-blur-sm border-2 border-dashed border-primary/60 rounded-2xl m-3"
          >
            <div className="text-center">
              <Paperclip size={40} className="text-primary mx-auto mb-3" />
              <p className="text-lg font-semibold text-foreground">Drop files to upload</p>
              <p className="text-sm text-muted-foreground mt-1">PDF, Word, Excel, CSV, Images</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Sidebar ── */}
      <motion.aside
        animate={{ width: sidebarOpen ? 260 : 0 }}
        transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
        className="flex-shrink-0 h-full overflow-hidden bg-sidebar border-r border-sidebar-border flex flex-col"
      >
        <div className="flex-1 flex flex-col overflow-hidden" style={{ width: 260 }}>
          <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
                <Sparkles size={14} className="text-white" />
              </div>
              <span className="text-base font-bold text-sidebar-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
            </div>
            <button onClick={() => setSidebarOpen(false)} className="p-1.5 rounded-lg hover:bg-sidebar-accent text-muted-foreground hover:text-sidebar-foreground transition-colors">
              <ChevronLeft size={15} />
            </button>
          </div>

          <div className="p-3">
            <button
              onClick={startNewChat}
              className="w-full flex items-center gap-2.5 px-3 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              <Plus size={15} />
              New Conversation
            </button>
          </div>

          <div className="px-3 pb-3">
            <div className="flex items-center gap-2 px-3 py-2 bg-sidebar-accent rounded-xl">
              <Search size={13} className="text-muted-foreground flex-shrink-0" />
              <input
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search conversations..."
                className="flex-1 bg-transparent text-sm text-sidebar-foreground placeholder:text-muted-foreground focus:outline-none"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-2 py-1 scrollbar-none" style={{ scrollbarWidth: "none" }}>
            {sessionsLoading && (
              <div className="flex items-center justify-center py-6">
                <Loader2 size={16} className="animate-spin text-muted-foreground" />
              </div>
            )}
            {sessionsError && !sessionsLoading && (
              <div className="mx-2 mb-3 p-3 bg-destructive/10 border border-destructive/30 rounded-xl">
                <p className="text-xs text-destructive">{sessionsError}</p>
                <button onClick={loadSessions} className="text-xs text-primary hover:underline mt-1">Retry</button>
              </div>
            )}
            {!sessionsLoading && !sessionsError && sessions.length === 0 && (
              <div className="text-center py-8 px-4">
                <p className="text-xs text-muted-foreground">No conversations yet</p>
              </div>
            )}
            <ConversationGroup label="Today" items={groupedConvs.today} activeId={activeConvId} onSelect={selectConversation} />
            <ConversationGroup label="Yesterday" items={groupedConvs.yesterday} activeId={activeConvId} onSelect={selectConversation} />
            <ConversationGroup label="Last 7 Days" items={groupedConvs.last7} activeId={activeConvId} onSelect={selectConversation} />
            <ConversationGroup label="Older" items={groupedConvs.older} activeId={activeConvId} onSelect={selectConversation} />
          </div>

          <div className="border-t border-sidebar-border p-3 relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-sidebar-accent transition-colors group"
            >
              <div className="w-8 h-8 rounded-full bg-primary/15 flex items-center justify-center text-primary text-sm font-semibold flex-shrink-0">
                {user?.full_name ? user.full_name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2) : user?.email?.[0]?.toUpperCase() ?? "U"}
              </div>
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-medium text-sidebar-foreground truncate">{user?.full_name ?? user?.email ?? "User"}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email ?? ""}</p>
              </div>
              <ChevronDown size={13} className={`text-muted-foreground transition-transform ${showUserMenu ? "rotate-180" : ""}`} />
            </button>
            <AnimatePresence>
              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 4, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 4, scale: 0.97 }}
                  className="absolute bottom-full left-3 right-3 mb-2 bg-popover border border-border rounded-xl shadow-xl overflow-hidden z-10"
                >
                  {[
                    { icon: <User size={13} />, label: "Profile", action: () => { setMode("profile"); setShowUserMenu(false); } },
                    { icon: <Settings size={13} />, label: "Settings", action: () => { setMode("settings"); setShowUserMenu(false); } },
                    { icon: <HelpCircle size={13} />, label: "Help Center", action: () => setShowUserMenu(false) },
                  ].map((item) => (
                    <button key={item.label} onClick={item.action} className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-foreground hover:bg-muted transition-colors">
                      <span className="text-muted-foreground">{item.icon}</span>
                      {item.label}
                    </button>
                  ))}
                  <div className="border-t border-border">
                    <button
                      onClick={() => { authLogout(); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-destructive hover:bg-destructive/8 transition-colors"
                    >
                      <LogOut size={13} />
                      Sign Out
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.aside>

      {/* ── Main Workspace ── */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* Topbar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-background/80 backdrop-blur-sm flex-shrink-0">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-xl hover:bg-muted text-muted-foreground hover:text-foreground transition-colors">
                <ChevronRight size={16} />
              </button>
            )}
            {!sidebarOpen && (
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-primary flex items-center justify-center">
                  <Sparkles size={12} className="text-white" />
                </div>
                <span className="text-sm font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
              </div>
            )}
            {mode === "chat" && activeConvId && (
              <span className="text-sm text-muted-foreground hidden sm:block">
                {sessions.find(c => c.id === activeConvId)?.title ?? "New Conversation"}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setDark(!dark)}
              className="p-2 rounded-xl hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <button
              onClick={() => setMode("settings")}
              className="p-2 rounded-xl hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
              <Settings size={16} />
            </button>
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-hidden flex flex-col relative">
          {mode === "welcome" ? (
            /* ── Welcome ── */
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-2xl mx-auto px-6 py-14">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
                  <div className="flex justify-center mb-6">
                    <div className="w-14 h-14 rounded-2xl bg-primary/12 flex items-center justify-center">
                      <Sparkles size={28} className="text-primary" />
                    </div>
                  </div>
                  <h1 className="text-3xl font-bold text-center text-foreground mb-2" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
                    Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"}, {user?.full_name?.split(" ")[0] ?? "there"}
                  </h1>
                  <p className="text-center text-muted-foreground mb-10">What would you like to analyze today?</p>

                  {/* Suggested prompts */}
                  <div className="grid grid-cols-2 gap-3 mb-10">
                    {SUGGESTED_PROMPTS.map((p) => (
                      <button
                        key={p.label}
                        onClick={() => { setInput(p.label); setMode("chat"); }}
                        className="flex items-start gap-3 p-4 bg-card border border-border rounded-xl text-left hover:border-primary/40 hover:shadow-sm transition-all group"
                      >
                        <span className="text-primary mt-0.5 group-hover:scale-110 transition-transform">{p.icon}</span>
                        <div>
                          <p className="text-sm font-medium text-foreground">{p.label}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">{p.desc}</p>
                        </div>
                      </button>
                    ))}
                  </div>

                  {/* Recent conversations */}
                  {sessions.length > 0 && (
                    <div className="mb-8">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-semibold text-foreground">Recent conversations</h3>
                        <button onClick={() => sessions.length > 0 && selectConversation(sessions[0].id)} className="text-xs text-primary hover:underline">View all</button>
                      </div>
                      <div className="space-y-2">
                        {sessions.slice(0, 5).map((conv) => (
                          <button key={conv.id} onClick={() => selectConversation(conv.id)} className="w-full flex items-center gap-3 p-3 bg-card border border-border rounded-xl hover:border-primary/30 hover:shadow-sm transition-all text-left group">
                            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                              <MessageSquare size={15} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground truncate">{conv.title}</p>
                              <p className="text-xs text-muted-foreground">{conv.preview}</p>
                            </div>
                            <span className="text-xs text-muted-foreground">{conv.date.toLocaleDateString()}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Quick stats */}
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { label: "Conversations", value: String(sessions.length), sub: "total" },
                      { label: "Files uploaded", value: String(files.length), sub: "this session" },
                      { label: "Messages", value: String(messages.length), sub: "this session" },
                    ].map((s) => (
                      <div key={s.label} className="p-4 bg-card border border-border rounded-xl text-center">
                        <p className="text-xl font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>{s.value}</p>
                        <p className="text-xs font-medium text-foreground mt-0.5">{s.label}</p>
                        <p className="text-xs text-muted-foreground">{s.sub}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </div>
            </div>
          ) : (
            /* ── Chat ── */
            <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
              <div className="max-w-3xl mx-auto px-6 py-6 pb-2">
                {/* Document cards */}
                {files.length > 0 && (
                  <div className="mb-6">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2.5">Attached documents</p>
                    <div className="flex flex-wrap gap-2">
                      <AnimatePresence>
                        {files.map(f => (
                          <FileCard key={f.id} file={f} onRemove={id => setFiles(prev => prev.filter(x => x.id !== id))} />
                        ))}
                      </AnimatePresence>
                    </div>
                  </div>
                )}

                {/* Chat error banner */}
                {chatError && (
                  <div className="mb-4 flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-xl text-sm text-destructive">
                    <AlertCircle size={14} className="flex-shrink-0" />
                    {chatError}
                  </div>
                )}

                {/* Messages */}
                {messages.length === 0 && (
                  <div className="text-center py-16">
                    <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                      <MessageSquare size={22} className="text-primary" />
                    </div>
                    <p className="text-sm font-medium text-foreground">Start the conversation</p>
                    <p className="text-xs text-muted-foreground mt-1">Ask anything about your uploaded documents</p>
                  </div>
                )}

                {messages.map(msg => (
                  <ChatMessage key={msg.id} msg={msg} onFeedback={handleFeedback} />
                ))}

                {isTyping && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </div>
            </div>
          )}

          {/* ── Input Area ── */}
          <div className="flex-shrink-0 px-4 pb-5 pt-3 bg-gradient-to-t from-background via-background to-transparent">
            <div className="max-w-3xl mx-auto">
              <div className={`border rounded-2xl shadow-lg bg-card transition-all duration-200 ${dragging ? "border-primary/60 shadow-primary/20" : "border-border"}`}>
                <div className="px-4 pt-3.5 pb-2">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything about your documents\u2026 (Shift+Enter for new line)"
                    rows={1}
                    className="w-full resize-none bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none leading-relaxed"
                    style={{ minHeight: 44, maxHeight: 180, fontFamily: "'Inter', sans-serif" }}
                    onInput={e => {
                      const el = e.currentTarget;
                      el.style.height = "auto";
                      el.style.height = Math.min(el.scrollHeight, 180) + "px";
                    }}
                  />
                </div>
                <div className="flex items-center justify-between px-3 pb-3">
                  <div className="flex items-center gap-1">
                    <input ref={fileInputRef} type="file" multiple accept=".pdf,.docx,.xlsx,.pptx,.csv,.txt,.png,.jpg,.jpeg" className="hidden" onChange={handleFileInput} />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                      title="Attach file"
                    >
                      <Paperclip size={17} />
                    </button>
                    <button className="p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted transition-colors" title="Voice input">
                      <Mic size={17} />
                    </button>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">{input.length > 0 ? `${input.length}` : ""}</span>
                    <button
                      onClick={sendMessage}
                      disabled={!input.trim() && files.filter(f => f.status === "ready").length === 0}
                      className="w-9 h-9 rounded-xl bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 disabled:opacity-35 disabled:cursor-not-allowed transition-all"
                    >
                      <Send size={15} />
                    </button>
                  </div>
                </div>
              </div>
              <p className="text-center text-[11px] text-muted-foreground mt-2.5">
                KnowMate can analyze PDFs, Word, Excel, PowerPoint, CSV, and images &middot; <kbd className="font-mono">Enter</kbd> to send
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
