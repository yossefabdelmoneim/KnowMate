# KnowMate — Complete Enterprise AI Platform UI

## Context

The user wants a full, exhibition-quality frontend implementation of KnowMate: a multi-tenant enterprise AI knowledge assistant SaaS. Companies upload internal documents and chat with two AI agents (customer service or data analyst) powered by RAG. The platform serves admins, employees, support teams, and managers. The brief requests every major screen: landing page, auth, dashboard shell, AI chat, document management, user management, analytics, and settings — all responsive.

---

## Aesthetic Stance: Swiss/Precision

**Committed stance:** Swiss International — strict grid, information-dense, function declares the aesthetic. Not the overused SaaS-modern gray-rounded-card approach. Instead: cool slate canvas with a deep navy sidebar as structural anchor, electric-blue primary, and a subtle indigo AI accent.

**Typography:**
- `Plus Jakarta Sans` — display headings, sidebar labels, metric numbers
- `DM Sans` — body copy, chat messages, form inputs
- `JetBrains Mono` — status badges, doc IDs, timestamps, code snippets

**Color tokens to set in `theme.css`:**
```
--background: #F0F4F8          (cool blue-gray canvas)
--foreground: #0F172A          (slate 900)
--card: #FFFFFF
--card-foreground: #0F172A
--primary: #2563EB             (electric blue — AI signal)
--primary-foreground: #FFFFFF
--secondary: #EFF6FF           (blue-tinted surface)
--secondary-foreground: #1E3A5F
--muted: #E2E8F0
--muted-foreground: #64748B
--accent: #6366F1              (indigo — AI brand accent)
--accent-foreground: #FFFFFF
--border: rgba(15,23,42,0.08)
--ring: #2563EB
--radius: 0.5rem
--sidebar: #0F172A             (deep navy)
--sidebar-foreground: #E2E8F0
--sidebar-primary: #2563EB
--sidebar-primary-foreground: #FFFFFF
--sidebar-accent: #1E293B
--sidebar-accent-foreground: #CBD5E1
--sidebar-border: rgba(255,255,255,0.06)
```
Dark mode tokens: invert to dark slate (#0F172A) canvas, lighter cards (#1E293B).

**Font imports (`fonts.css`):**
```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
```
Apply: `body { font-family: 'DM Sans', sans-serif; }` and heading classes use `font-['Plus_Jakarta_Sans']`.

---

## Architecture: State-Driven SPA (No Router)

Since this is a Make sandbox (single `App.tsx`), navigation is driven by `useState` — `view` determines which top-level page renders, `subView` determines which dashboard panel is active.

```
type View = 'landing' | 'login' | 'register' | 'forgot-password' | 'dashboard'
type SubView = 'ai-assistant' | 'documents' | 'users' | 'analytics' | 'settings'
```

---

## Component Hierarchy (all colocated in App.tsx)

```
App
├── [view === 'landing']     → LandingPage
│   ├── Navbar (sticky, glass blur on scroll)
│   ├── HeroSection (split: left copy + right animated UI mockup)
│   ├── LogosSection (trusted by / company logos)
│   ├── FeaturesSection (3-col grid: RAG, multi-agent, multi-tenant)
│   ├── BenefitsSection (alternating image+copy rows)
│   ├── AgentsSection (2 agent cards: CS Agent + Data Analyst)
│   ├── TestimonialsSection
│   ├── CTASection (gradient panel)
│   └── Footer
│
├── [view === 'login']       → LoginPage (centered card, company logo)
├── [view === 'register']    → RegisterPage (2-col: form + feature list)
├── [view === 'forgot-password'] → ForgotPasswordPage
│
└── [view === 'dashboard']   → DashboardLayout
    ├── Sidebar (navy, collapsible)
    │   ├── Logo + workspace selector
    │   ├── NavItem list (icons + labels)
    │   ├── AgentSelector (CS Agent / Data Analyst toggle)
    │   └── UserAvatar + logout
    ├── TopBar (breadcrumb, search, notifications, avatar)
    └── Main content area
        ├── [subView === 'ai-assistant'] → AIAssistantPage
        │   ├── ChatHistoryPanel (left, scrollable)
        │   │   ├── NewChatButton
        │   │   └── ChatHistoryList (grouped by date)
        │   ├── ChatArea (center, main)
        │   │   ├── AgentBadge (active agent indicator)
        │   │   ├── MessageList (user + AI bubbles, citations inline)
        │   │   ├── SuggestedQuestionsBar
        │   │   └── MessageInputArea (textarea + send + attach + agent selector)
        │   └── SourceCitationsPanel (right, slide-in)
        │       ├── CitationCard (doc name, page, excerpt)
        │       └── RelevanceScore
        │
        ├── [subView === 'documents'] → DocumentsPage
        │   ├── PageHeader + UploadButton
        │   ├── DropZone (dashed border, drag active state)
        │   ├── SearchBar + FilterRow (type, status, date)
        │   └── DocumentTable
        │       ├── DocumentRow (icon, name, size, status badge, actions)
        │       └── ProcessingProgress (inline progress bar)
        │
        ├── [subView === 'users'] → UsersPage
        │   ├── InviteButton + Search
        │   └── UsersTable
        │       ├── UserRow (avatar, name, email, role badge, status, actions)
        │       └── RoleBadge (Admin/Manager/Employee/Support)
        │
        ├── [subView === 'analytics'] → AnalyticsPage
        │   ├── MetricsRow (4 KPI cards: queries/day, docs, active users, accuracy)
        │   ├── UsageChart (recharts AreaChart — daily query volume)
        │   ├── DocumentStatsChart (recharts BarChart — uploads by category)
        │   ├── AgentUsageDonut (recharts PieChart — CS vs Analyst split)
        │   ├── TopQueriesTable
        │   └── RecentActivityFeed
        │
        └── [subView === 'settings'] → SettingsPage
            ├── SettingsTabs (Profile | Security | AI Config | Branding | Billing)
            ├── CompanyProfileForm
            ├── SecurityPanel (2FA, SSO, session timeout, API keys)
            ├── AIConfigPanel (model selector, temperature, context window, agent personas)
            └── BrandingPanel (logo upload, primary color picker)
```

---

## Critical Implementation Details

### Landing Page
- Hero: Two-column. Left: headline "Your company's knowledge, intelligently connected." + sub + 2 CTAs. Right: browser-framed mockup of the chat UI (static but detailed).
- Use Unsplash for a background texture or team photo with overlay.
- Features grid: icon + title + 2-line description for 6 features.
- `LogosSection`: Horizontal marquee of company logos (use SVG placeholder rects with company-name text).

### AI Assistant Page
- Three-panel layout (`grid-cols-[260px_1fr_320px]` on desktop, collapsible panels on tablet/mobile).
- Chat messages: user messages right-aligned blue bubble; AI messages left-aligned with agent avatar and name badge.
- Inline `[1]` `[2]` citation markers that highlight the corresponding source card in the right panel.
- Suggested questions: pill buttons below the last AI message.
- Typing indicator: animated three-dot pulse during "AI is thinking" state.
- Agent selector in input bar: toggle between "CS Agent" and "Data Analyst".

### Document Management
- DropZone with `dragover` state (border turns blue, background tints).
- Status badges using `JetBrains Mono`: `PROCESSING` (amber), `READY` (green), `ERROR` (red), `QUEUED` (slate).
- Document list shows: file icon (color by type: PDF=red, DOCX=blue, XLSX=green), filename, upload date, pages, size, status, kebab menu (view, re-index, delete).
- Inline progress bar for documents currently processing.

### Analytics Page
- Use `recharts`: AreaChart with gradient fill for query volume, BarChart for doc uploads, PieChart for agent usage split.
- Real-seeming data: specific numbers, named employees, real document categories.

### Responsive Behavior
- `< 768px`: Sidebar becomes bottom nav or hamburger drawer; chat panels collapse to single view with tabs.
- `768px–1024px`: Sidebar collapses to icon-only rail; source citations panel hidden behind a toggle button.
- `> 1024px`: Full three-panel layout.

### Accessibility
- All interactive elements have `aria-label`.
- Focus ring uses `--ring` token (blue).
- Color is never the sole differentiator (status badges include text + icon).
- Sufficient contrast: all body text > 4.5:1 against background.

---

## Files to Write

| File | Action |
|------|--------|
| `src/styles/fonts.css` | Add Google Fonts import for Plus Jakarta Sans, DM Sans, JetBrains Mono |
| `src/styles/theme.css` | Update token values (preserve structure and `@theme inline` block) |
| `src/app/App.tsx` | Replace placeholder with full ~1400-line implementation |

---

## Sitemap (Reference)

```
/ (Landing)
/login
/register
/forgot-password
/dashboard
  /dashboard/ai-assistant      ← default view
  /dashboard/documents
  /dashboard/users
  /dashboard/analytics
  /dashboard/settings
```

---

## Verification

1. App renders landing page with hero, features, and CTA.
2. "Get Started" navigates to register, "Sign In" to login.
3. Login form submits and transitions to dashboard AI assistant view.
4. Sidebar navigation switches between all 5 sub-views without error.
5. AI chat: typing in input + send displays user bubble, then AI response with citation markers.
6. Documents: drag zone shows active state; document rows show status badges; search filters list.
7. Analytics: all 3 recharts charts render with real-looking data.
8. Settings: tabs switch between panels.
9. Mobile: sidebar collapses, layout reflows correctly at < 768px.
