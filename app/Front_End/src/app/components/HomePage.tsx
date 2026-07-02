import { useState } from "react";
import { motion } from "motion/react";
import {
  Sparkles, ChevronDown, Menu, X, ArrowRight,
  BookOpen, MessageSquare, FileText, Shield, Search, Lock,
  Check, Layers, Server, Clock, Bot, Users
} from "lucide-react";

interface HomePageProps {
  onNavigate: (page: "login" | "register") => void;
}

const NAV_ITEMS = [
  { label: "Features", href: "features" },
  { label: "Solutions", href: "solutions" },
  { label: "About", href: "about" },
  { label: "Contact", href: "contact" },
];

const features = [
  {
    icon: <FileText size={20} />,
    title: "Document Intelligence",
    desc: "Upload PDFs, Word documents, spreadsheets, and presentations. KnowMate extracts and indexes every piece of information automatically.",
  },
  {
    icon: <MessageSquare size={20} />,
    title: "Conversational Search",
    desc: "Ask questions in natural language and get precise answers grounded in your documents, with source citations for verification.",
  },
  {
    icon: <Search size={20} />,
    title: "Cross-Document Reasoning",
    desc: "Compare information across multiple files. KnowMate connects related content from different documents to give you a complete picture.",
  },
  {
    icon: <Users size={20} />,
    title: "Department Agents",
    desc: "Dedicated AI agents for HR, Marketing, and Data Analysis — each trained with domain-specific prompts and knowledge bases.",
  },
  {
    icon: <Shield size={20} />,
    title: "Enterprise Security",
    desc: "Deploy on your own infrastructure. All data stays within your network. Encrypted at rest and in transit. No third-party model training.",
  },
  {
    icon: <Layers size={20} />,
    title: "Session Memory",
    desc: "Conversations persist across sessions. Pick up where you left off, with full chat history and contextual awareness.",
  },
];

const steps = [
  {
    number: "1",
    title: "Connect your documents",
    desc: "Upload files or point KnowMate to your document repository. We support all major business formats.",
  },
  {
    number: "2",
    title: "Ask anything",
    desc: "Type a question in plain English. Your words are matched against the indexed content using semantic search.",
  },
  {
    number: "3",
    title: "Get answers with sources",
    desc: "Receive precise answers alongside the source documents they came from, so you can verify every claim.",
  },
];

const differentiators = [
  {
    icon: <Server size={18} />,
    title: "Self-hosted deployment",
    desc: "Run entirely on your own infrastructure. No data ever leaves your network.",
  },
  {
    icon: <Bot size={18} />,
    title: "Local AI inference",
    desc: "Uses Ollama for on-premise LLM inference. No external API calls, no per-token costs.",
  },
  {
    icon: <Clock size={18} />,
    title: "Persistent conversations",
    desc: "All chat history is saved and indexed. Every session is a permanent, searchable record.",
  },
];

const faqs = [
  {
    q: "What file formats are supported?",
    a: "KnowMate supports PDF, DOCX, TXT, Excel (XLSX/XLS), and CSV files.",
  },
  {
    q: "Where is my data stored?",
    a: "KnowMate can be deployed entirely on your own infrastructure. All document processing, vector storage, and LLM inference happens locally. No data is sent to external services.",
  },
  {
    q: "How does the AI ensure accuracy?",
    a: "Answers are generated using Retrieval-Augmented Generation (RAG). Every response is grounded in your actual documents with source citations, reducing hallucination risks significantly.",
  },
  {
    q: "Can I try KnowMate before purchasing?",
    a: "Yes. Our Starter plan is free and includes full access to all features with a reasonable usage limit. No credit card is required.",
  },
  {
    q: "What infrastructure do I need?",
    a: "KnowMate requires a server with Docker support and at least 16 GB of RAM for the LLM models. We provide one-command deployment scripts for Linux and Windows.",
  },
];

function Navbar({ onNavigate, scrollTo }: { onNavigate: (page: "login" | "register") => void; scrollTo: (id: string) => void }) {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/60 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-10">
          <div className="flex items-center gap-2.5 flex-shrink-0">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
              <Sparkles size={14} className="text-white" />
            </div>
            <span className="text-base font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
          </div>
          <div className="hidden lg:flex items-center gap-8">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.label}
                onClick={() => scrollTo(item.href)}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-3">
          <button
            onClick={() => onNavigate("login")}
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-4 py-2"
          >
            Sign in
          </button>
          <button
            onClick={() => onNavigate("register")}
            className="text-sm font-semibold bg-primary text-primary-foreground px-5 py-2.5 rounded-[10px] hover:bg-primary/90 transition-all"
          >
            Get Started
          </button>
        </div>
        <button onClick={() => setOpen(!open)} className="lg:hidden p-2 rounded-lg hover:bg-muted transition-colors">
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>
      {open && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="lg:hidden border-t border-border bg-background px-6 py-4 space-y-3">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.label}
              onClick={() => { scrollTo(item.href); setOpen(false); }}
              className="block w-full text-left text-sm text-muted-foreground hover:text-foreground py-2 transition-colors"
            >
              {item.label}
            </button>
          ))}
          <div className="pt-3 border-t border-border space-y-2">
            <button onClick={() => { onNavigate("login"); setOpen(false); }} className="w-full text-sm font-medium text-center py-2.5 rounded-xl border border-border hover:bg-muted transition-colors">
              Sign in
            </button>
            <button onClick={() => { onNavigate("register"); setOpen(false); }} className="w-full text-sm font-semibold text-center py-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
              Get Started
            </button>
          </div>
        </motion.div>
      )}
    </nav>
  );
}

function SectionHeading({ label, title, desc }: { label?: string; title: string; desc?: string }) {
  return (
    <div className="text-center mb-14">
      {label && (
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-primary/8 border border-primary/15 rounded-full text-xs font-medium text-primary mb-5">
          {label}
        </div>
      )}
      <h2 className="text-3xl sm:text-4xl font-bold text-foreground tracking-tight" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
        {title}
      </h2>
      {desc && <p className="text-muted-foreground mt-4 max-w-xl mx-auto leading-relaxed">{desc}</p>}
    </div>
  );
}

export default function HomePage({ onNavigate }: HomePageProps) {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar onNavigate={onNavigate} scrollTo={scrollTo} />

      {/* ── Hero ── */}
      <section className="pt-28 pb-20 px-6 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-primary/8 border border-primary/15 rounded-full text-xs font-medium text-primary mb-6">
                <Sparkles size={12} />
                Enterprise knowledge platform
              </div>
              <h1 className="text-4xl sm:text-5xl font-bold text-foreground leading-[1.1] tracking-tight mb-5" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
                Document intelligence for your entire organization
              </h1>
              <p className="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-lg mb-8">
                KnowMate indexes your documents, spreadsheets, and reports — then lets your team ask questions
                in natural language and get answers grounded in your data.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={() => onNavigate("register")}
                  className="inline-flex items-center gap-2 text-sm font-semibold bg-primary text-primary-foreground px-6 py-3 rounded-[10px] hover:bg-primary/90 transition-all shadow-sm"
                >
                  Get Started
                  <ArrowRight size={15} />
                </button>
                <button
                  onClick={() => scrollTo("features")}
                  className="inline-flex items-center gap-2 text-sm font-medium text-foreground px-6 py-3 rounded-[10px] border border-border hover:bg-muted transition-colors"
                >
                  Book a Demo
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.15 }}
              className="relative"
            >
              <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
                {/* Browser chrome */}
                <div className="flex items-center gap-1.5 px-4 h-9 border-b border-border bg-muted/30">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-400/70" />
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow-400/70" />
                  <div className="w-2.5 h-2.5 rounded-full bg-green-400/70" />
                  <div className="ml-3 px-2 py-0.5 rounded-md bg-muted/80 text-[11px] text-muted-foreground font-mono">app.knowmate.io</div>
                </div>
                {/* Mockup content */}
                <div className="p-5 space-y-3">
                  <div className="flex items-center gap-3 pb-3 border-b border-border">
                    <div className="w-6 h-6 rounded-md bg-primary/15 flex items-center justify-center">
                      <Sparkles size={12} className="text-primary" />
                    </div>
                    <span className="text-sm font-semibold text-foreground">KnowMate</span>
                    <div className="ml-auto px-3 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-400">
                      Data Analysis
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-6 h-6 rounded-full bg-primary/15 flex items-center justify-center text-primary text-xs font-semibold flex-shrink-0 mt-1">
                      Y
                    </div>
                    <div className="flex-1">
                      <div className="bg-primary/10 rounded-2xl rounded-tr-md px-4 py-2.5 max-w-[85%]">
                        <p className="text-sm text-foreground">What were our Q4 sales numbers?</p>
                      </div>
                      <div className="mt-3 bg-muted/40 rounded-2xl rounded-tl-md px-4 py-2.5 max-w-[90%] border border-border/50">
                        <p className="text-sm text-foreground/90">
                          Q4 sales totaled <strong>$2.4M</strong>, a 12% increase from Q3. The growth was driven primarily by
                          the Enterprise segment, which grew 18% quarter over quarter.
                        </p>
                        <div className="mt-2 pt-2 border-t border-border/50 flex gap-2">
                          <span className="text-[11px] px-2 py-0.5 rounded bg-muted text-muted-foreground">[1] Q4_Report_2025.xlsx</span>
                          <span className="text-[11px] px-2 py-0.5 rounded bg-muted text-muted-foreground">[2] Sales_Summary.pdf</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── Trusted by Teams ── */}
      <section className="py-14 px-6 border-y border-border/40">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-widest mb-6">Trusted by modern teams</p>
          <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
            {["Company", "Organization", "Enterprise", "Team", "Business"].map((name) => (
              <div key={name} className="flex items-center gap-2 text-muted-foreground/50">
                <div className="w-6 h-6 rounded-md bg-muted/50" />
                <span className="text-sm font-medium text-muted-foreground/40">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <SectionHeading
            label="Features"
            title="Everything you need to manage enterprise knowledge"
            desc="A single platform for document ingestion, semantic search, and AI-powered Q&A — designed for security-conscious organizations."
          />
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ delay: i * 0.06, duration: 0.35 }}
                className="p-6 bg-card border border-border rounded-xl hover:border-border/80 hover:shadow-sm transition-all"
              >
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
                  {f.icon}
                </div>
                <h3 className="text-sm font-semibold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="py-20 px-6 bg-muted/30">
        <div className="max-w-5xl mx-auto">
          <SectionHeading
            title="How it works"
            desc="Three steps to turn your documents into an intelligent knowledge base."
          />
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ delay: i * 0.1, duration: 0.35 }}
                className="relative"
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-bold text-primary">{step.number}</span>
                  </div>
                  {i < steps.length - 1 && (
                    <div className="hidden md:block absolute top-4 left-9 w-[calc(100%-2.25rem)] h-px bg-border -z-10" />
                  )}
                </div>
                <h3 className="text-base font-semibold text-foreground mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Why Choose KnowMate ── */}
      <section id="solutions" className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <SectionHeading
            title="Why organizations choose KnowMate"
            desc="Built for teams that need enterprise-grade document intelligence without compromising on security or privacy."
          />
          <div className="grid md:grid-cols-3 gap-6">
            {differentiators.map((d, i) => (
              <motion.div
                key={d.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ delay: i * 0.08, duration: 0.35 }}
                className="p-6 bg-card border border-border rounded-xl"
              >
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
                  {d.icon}
                </div>
                <h3 className="text-sm font-semibold text-foreground mb-2">{d.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{d.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Security & Privacy ── */}
      <section id="about" className="py-20 px-6 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <SectionHeading
            label="Security"
            title="Your data stays yours"
            desc="KnowMate is designed from the ground up with enterprise security and data privacy as core requirements."
          />
          <div className="grid sm:grid-cols-2 gap-5">
            {[
              { icon: <Lock size={18} />, title: "Encrypted at rest and in transit", desc: "All data is encrypted using industry-standard AES-256 encryption. TLS 1.3 for all network communication." },
              { icon: <Server size={18} />, title: "Self-hosted deployment", desc: "Deploy on your own infrastructure — on-premises or in your private cloud. No third-party access to your data." },
              { icon: <Shield size={18} />, title: "No external model training", desc: "Your documents are never used to train or improve third-party models. All processing happens locally." },
              { icon: <Users size={18} />, title: "Role-based access control", desc: "Granular permissions for teams and departments. Full audit logging for compliance requirements." },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ delay: i * 0.06, duration: 0.35 }}
                className="flex gap-4 p-5 bg-card border border-border rounded-xl"
              >
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                  {item.icon}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-1">{item.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section id="contact" className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <SectionHeading
            title="Frequently asked questions"
          />
          <div className="space-y-2">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-border rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between px-5 py-4 text-left text-sm font-medium text-foreground hover:bg-muted/50 transition-colors"
                >
                  {faq.q}
                  <ChevronDown size={14} className={`text-muted-foreground transition-transform flex-shrink-0 ml-2 ${openFaq === i ? "rotate-180" : ""}`} />
                </button>
                {openFaq === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <p className="px-5 pb-4 text-sm text-muted-foreground leading-relaxed">{faq.a}</p>
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="py-20 px-6 border-t border-border/40">
        <div className="max-w-2xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4 tracking-tight" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
              Ready to get started?
            </h2>
            <p className="text-muted-foreground mb-8 max-w-md mx-auto leading-relaxed">
              Start using KnowMate today. No credit card required.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={() => onNavigate("register")}
                className="inline-flex items-center gap-2 text-sm font-semibold bg-primary text-primary-foreground px-6 py-3 rounded-[10px] hover:bg-primary/90 transition-all shadow-sm"
              >
                Get Started
                <ArrowRight size={15} />
              </button>
              <button
                onClick={() => scrollTo("features")}
                className="inline-flex items-center gap-2 text-sm font-medium text-foreground px-6 py-3 rounded-[10px] border border-border hover:bg-muted transition-colors"
              >
                Contact Sales
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border/60 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-8 mb-10">
            <div className="lg:col-span-2">
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-6 h-6 rounded-lg bg-primary flex items-center justify-center">
                  <Sparkles size={12} className="text-white" />
                </div>
                <span className="text-sm font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
              </div>
              <p className="text-sm text-muted-foreground max-w-xs leading-relaxed">
                Document intelligence platform for enterprise teams.
              </p>
            </div>
            {[
              { title: "Product", links: ["Features", "Integrations", "Changelog"] },
              { title: "Company", links: ["About", "Blog", "Careers", "Contact"] },
              { title: "Legal", links: ["Privacy", "Terms", "Security", "Compliance"] },
            ].map((group) => (
              <div key={group.title}>
                <p className="text-xs font-semibold text-foreground uppercase tracking-wider mb-3">{group.title}</p>
                <ul className="space-y-2">
                  {group.links.map((link) => (
                    <li key={link}>
                      <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">{link}</button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="pt-8 border-t border-border/60 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-muted-foreground">&copy; 2026 KnowMate. All rights reserved.</p>
            <div className="flex items-center gap-6 text-xs text-muted-foreground">
              <button className="hover:text-foreground transition-colors">Privacy Policy</button>
              <button className="hover:text-foreground transition-colors">Terms of Service</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
