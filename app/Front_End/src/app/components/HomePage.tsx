import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Sparkles, BookOpen, FileText, Table, Zap, Shield,
  ChevronRight, Menu, X, Check, ArrowRight,
  BarChart2, Users, Lock, Globe, Layers, MessageSquare,
  Star, ChevronDown
} from "lucide-react";

interface HomePageProps {
  onNavigate: (page: "login" | "register") => void;
}

const features = [
  { icon: <BookOpen size={22} />, title: "Smart Document Analysis", desc: "Upload PDFs, Word, Excel, and more — AI extracts key insights instantly." },
  { icon: <MessageSquare size={22} />, title: "Conversational Q&A", desc: "Ask questions in plain English and get answers grounded in your documents." },
  { icon: <Table size={22} />, title: "Spreadsheet Intelligence", desc: "Analyze Excel and CSV data with natural language queries." },
  { icon: <Zap size={22} />, title: "Lightning Fast Processing", desc: "Enterprise-grade speed with local Ollama inference." },
  { icon: <Shield size={22} />, title: "Enterprise Security", desc: "Your data stays private. Self-hosted or cloud — you control access." },
  { icon: <Layers size={22} />, title: "Multi-Document Reasoning", desc: "Compare and cross-reference information across multiple files." },
];

const steps = [
  { num: "01", title: "Upload Documents", desc: "Drag and drop PDFs, Word files, spreadsheets, or images. We support all major formats." },
  { num: "02", title: "Ask Questions", desc: "Type any question about your documents in natural language. No complex queries needed." },
  { num: "03", title: "Get Answers", desc: "Receive AI-powered answers with source citations, so you always know where info comes from." },
];

const stats = [
  { label: "Documents Processed", value: "10K+", sub: "and counting" },
  { label: "Avg. Response Time", value: "< 2s", sub: "local inference" },
  { label: "Accuracy Rate", value: "94%", sub: "on enterprise docs" },
];

const pricing = [
  {
    name: "Starter",
    price: "Free",
    desc: "Perfect for trying out KnowMate",
    features: ["5 documents per month", "Basic Q&A", "Single user", "Community support"],
    cta: "Get Started",
    popular: false,
  },
  {
    name: "Pro",
    price: "$29",
    desc: "For professionals and small teams",
    features: ["500 documents per month", "Advanced analytics", "50 conversations", "Priority AI processing", "Email support"],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    desc: "For organizations with advanced needs",
    features: ["Unlimited documents", "Dedicated AI instance", "SSO & RBAC", "Custom integrations", "24/7 support", "SLA guarantee"],
    cta: "Contact Sales",
    popular: false,
  },
];

const faqs = [
  { q: "What file formats does KnowMate support?", a: "KnowMate supports PDF, DOCX, XLSX, PPTX, CSV, TXT, and common image formats (PNG, JPG, JPEG)." },
  { q: "Is my data secure?", a: "Absolutely. KnowMate can be deployed on your own infrastructure. All data is encrypted in transit and at rest. We never use your documents for model training." },
  { q: "How accurate are the answers?", a: "KnowMate achieves 94% accuracy on enterprise document QA tasks. Answers are always grounded in your uploaded documents with source citations." },
  { q: "Can I try it before committing?", a: "Yes! The Starter plan is completely free with no credit card required. You can start analyzing documents right away." },
];

export default function HomePage({ onNavigate }: HomePageProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const scrollTo = (id: string) => {
    setMobileMenuOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ── Nav ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center">
              <Sparkles size={16} className="text-white" />
            </div>
            <span className="text-lg font-bold" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            {["Features", "How it works", "Pricing", "FAQ"].map((item) => (
              <button
                key={item}
                onClick={() => scrollTo(item.toLowerCase().replace(/\s+/g, "-"))}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {item}
              </button>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={() => onNavigate("login")}
              className="text-sm font-medium text-foreground hover:text-primary transition-colors px-4 py-2"
            >
              Sign In
            </button>
            <button
              onClick={() => onNavigate("register")}
              className="text-sm font-semibold bg-primary text-primary-foreground px-5 py-2.5 rounded-xl hover:bg-primary/90 transition-all"
            >
              Get Started
            </button>
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-xl hover:bg-muted transition-colors"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-border bg-background overflow-hidden"
            >
              <div className="px-6 py-4 space-y-3">
                {["Features", "How it works", "Pricing", "FAQ"].map((item) => (
                  <button
                    key={item}
                    onClick={() => scrollTo(item.toLowerCase().replace(/\s+/g, "-"))}
                    className="block w-full text-left text-sm text-muted-foreground hover:text-foreground py-2 transition-colors"
                  >
                    {item}
                  </button>
                ))}
                <div className="pt-3 border-t border-border space-y-2">
                  <button onClick={() => onNavigate("login")} className="w-full text-sm font-medium text-center py-2.5 rounded-xl border border-border hover:bg-muted transition-colors">
                    Sign In
                  </button>
                  <button onClick={() => onNavigate("register")} className="w-full text-sm font-semibold text-center py-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
                    Get Started
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ── Hero ── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 border border-primary/20 rounded-full text-xs font-medium text-primary mb-6">
              <Sparkles size={12} />
              AI-Powered Document Intelligence
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold leading-tight mb-5" style={{ fontFamily: "'Instrument Sans', sans-serif", letterSpacing: "-0.02em" }}>
              Turn your documents into{" "}
              <span className="bg-gradient-to-r from-primary to-emerald-300 bg-clip-text text-transparent">answers</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
              Upload PDFs, spreadsheets, and reports — then ask anything. KnowMate analyzes your documents
              and delivers accurate answers with sources, powered by local AI.
            </p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => onNavigate("register")}
                className="flex items-center gap-2 text-sm font-semibold bg-primary text-primary-foreground px-6 py-3 rounded-xl hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
              >
                Get Started Free
                <ArrowRight size={15} />
              </button>
              <button
                onClick={() => scrollTo("features")}
                className="flex items-center gap-2 text-sm font-medium text-foreground px-6 py-3 rounded-xl border border-border hover:bg-muted transition-colors"
              >
                Learn More
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-3 gap-4 p-6 bg-card border border-border rounded-2xl">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-2xl sm:text-3xl font-bold text-foreground" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>{s.value}</p>
                <p className="text-xs font-medium text-foreground mt-1">{s.label}</p>
                <p className="text-xs text-muted-foreground">{s.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold mb-3" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
              Everything you need to understand your documents
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              From simple PDFs to complex spreadsheets — KnowMate handles it all.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="p-5 bg-card border border-border rounded-xl hover:border-primary/30 hover:shadow-sm transition-all"
              >
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-3">
                  {f.icon}
                </div>
                <h3 className="text-sm font-semibold mb-1.5">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="py-20 px-6 bg-card/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold mb-3" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
              How it works
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Three simple steps to unlock insights from your documents.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {steps.map((step, i) => (
              <motion.div
                key={step.num}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.12, duration: 0.4 }}
                className="relative text-center p-6"
              >
                <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <span className="text-lg font-bold text-primary">{step.num}</span>
                </div>
                <h3 className="text-base font-semibold mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pricing ── */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold mb-3" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
              Simple, transparent pricing
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Start for free. Scale as you grow.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {pricing.map((plan) => (
              <div
                key={plan.name}
                className={`relative p-6 rounded-2xl border transition-all ${
                  plan.popular
                    ? "border-primary/40 bg-card shadow-lg shadow-primary/5"
                    : "border-border bg-card"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary text-primary-foreground text-xs font-semibold rounded-full">
                    Most Popular
                  </div>
                )}
                <h3 className="text-sm font-semibold mb-1">{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-3xl font-bold" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>{plan.price}</span>
                  {plan.price !== "Custom" && plan.price !== "Free" && <span className="text-sm text-muted-foreground">/mo</span>}
                </div>
                <p className="text-xs text-muted-foreground mb-5">{plan.desc}</p>
                <ul className="space-y-2.5 mb-6">
                  {plan.features.map((feat) => (
                    <li key={feat} className="flex items-start gap-2 text-sm text-foreground/80">
                      <Check size={14} className="text-primary flex-shrink-0 mt-0.5" />
                      {feat}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => onNavigate("register")}
                  className={`w-full text-sm font-semibold py-2.5 rounded-xl transition-all ${
                    plan.popular
                      ? "bg-primary text-primary-foreground hover:bg-primary/90"
                      : "border border-border text-foreground hover:bg-muted"
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section id="faq" className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-3" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
              Frequently asked questions
            </h2>
          </div>
          <div className="space-y-2">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-border rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between px-5 py-4 text-left text-sm font-medium hover:bg-muted/50 transition-colors"
                >
                  {faq.q}
                  <ChevronDown size={15} className={`text-muted-foreground transition-transform ${openFaq === i ? "rotate-180" : ""}`} />
                </button>
                <AnimatePresence>
                  {openFaq === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-4 text-sm text-muted-foreground leading-relaxed">{faq.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-10 rounded-2xl bg-gradient-to-br from-primary/10 via-card to-card border border-primary/20"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-3" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>
              Ready to transform your document workflow?
            </h2>
            <p className="text-muted-foreground mb-8 max-w-lg mx-auto">
              Join thousands of professionals using KnowMate to extract insights from their documents in seconds.
            </p>
            <button
              onClick={() => onNavigate("register")}
              className="inline-flex items-center gap-2 text-sm font-semibold bg-primary text-primary-foreground px-8 py-3.5 rounded-xl hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
            >
              Get Started Free
              <ArrowRight size={15} />
            </button>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-lg bg-primary flex items-center justify-center">
              <Sparkles size={12} className="text-white" />
            </div>
            <span className="text-sm font-bold" style={{ fontFamily: "'Instrument Sans', sans-serif" }}>KnowMate</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-muted-foreground">
            <span>&copy; 2026 KnowMate. All rights reserved.</span>
            <button className="hover:text-foreground transition-colors">Privacy</button>
            <button className="hover:text-foreground transition-colors">Terms</button>
          </div>
        </div>
      </footer>
    </div>
  );
}
