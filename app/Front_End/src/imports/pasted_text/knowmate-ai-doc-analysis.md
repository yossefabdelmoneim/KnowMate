# KnowMate — Premium AI Document Analysis SaaS UI/UX Design Prompt

Design a modern, premium AI web application called **KnowMate**. The platform acts as an intelligent document analysis assistant where users can upload PDF, Word, Excel, PowerPoint, CSV, text files, and images, then chat with an AI that understands, analyzes, and answers questions about the uploaded documents.

The design should be inspired by **ChatGPT**, **Claude**, and **Notion AI**, while maintaining its own distinctive identity. The interface should feel polished, premium, highly intuitive, and production-ready with a clean SaaS aesthetic.

## Overall Design Style

* Modern AI SaaS interface.
* Minimal, clean, and distraction-free.
* Premium typography.
* Excellent whitespace and spacing.
* 8px spacing system.
* Rounded corners (12–16px).
* Soft shadows.
* Smooth micro-interactions and animations.
* Professional iconography.
* Fully responsive (desktop-first with mobile adaptation).

### Color Palette

Use a color palette heavily inspired by the **ChatGPT web interface**, featuring elegant neutral tones rather than bright gradients.

Primary colors should include:

* Soft off-white backgrounds
* Light gray surfaces
* Neutral borders
* Dark charcoal text
* Muted green accents inspired by ChatGPT
* Subtle blue and purple highlights only where appropriate

Avoid overly saturated colors. The interface should feel calm, premium, modern, and productivity-focused, closely resembling ChatGPT's visual language while still establishing **KnowMate** as its own recognizable brand.

Provide both:

* Light Mode
* Elegant Dark Mode matching ChatGPT's dark theme aesthetics

---

# Layout

## Left Sidebar (Collapsible)

Include:

* KnowMate logo
* New Chat button
* Search conversations
* Chat history grouped by:

  * Today
  * Yesterday
  * Last 7 Days
  * Older
* User profile section at bottom containing:

  * Avatar
  * Name
  * Email
  * Settings
  * Logout

---

# Main Workspace

When no conversation exists:

Display:

* Large welcome illustration or AI hero section
* Personalized greeting
* Suggested prompt cards
* Recently uploaded documents
* Quick Actions

After conversation starts:

Display:

* User messages
* AI responses
* Markdown rendering
* Code blocks
* Syntax highlighting
* Tables
* Citations
* Expandable references
* Copy response
* Regenerate response
* Like/Dislike feedback
* Typing indicator with animated dots
* Streaming AI responses

---

# Chat Input

Create a large rounded floating input area fixed to the bottom.

Include:

* Multi-line text input
* Upload button
* Drag-and-drop upload
* Voice input button (UI only)
* Send button
* Attachment preview
* Character count
* Keyboard shortcut hints

Allow uploading multiple documents within a single conversation.

---

# Document Experience

After upload, display document cards above the conversation.

Each card should contain:

* File icon
* Filename
* File size
* Upload progress
* Upload status
* Remove button
* Preview button
* Processing indicator
* Analysis completed indicator

Supported files:

* PDF
* DOCX
* XLSX
* PPTX
* CSV
* TXT
* Images

---

# AI Features

Design interfaces for:

* Document summarization
* Question answering
* Key insights extraction
* Table analysis
* Spreadsheet analysis
* OCR for scanned documents
* Citation references
* Multi-document comparison
* Follow-up questions
* Suggested next questions
* Source highlighting
* Confidence indicators

---

# Dashboard Pages

Design complete UI screens for:

* Login
* Register
* Forgot Password
* User Dashboard
* User Profile
* Account Settings
* Subscription & Billing
* API Keys (Optional)
* Notifications
* Help Center
* Privacy Settings
* Security (2FA & Sessions)

---

# Components

Create reusable components including:

* Primary buttons
* Secondary buttons
* Ghost buttons
* Icon buttons
* Cards
* Chat bubbles
* Message actions
* Inputs
* Textareas
* Search bars
* Dropdown menus
* Tabs
* Modals
* Tooltips
* Toast notifications
* File upload cards
* Progress bars
* Loading skeletons
* Empty states
* Error states
* Confirmation dialogs
* Pagination
* Breadcrumbs
* Avatars
* Status badges
* Chips
* Toggle switches

---

# Design System

Create a comprehensive design system including:

## Typography

* Display
* Heading 1–6
* Body Large
* Body Medium
* Caption
* Labels

## Color Tokens

* Primary
* Secondary
* Accent
* Surface
* Background
* Border
* Success
* Warning
* Error
* Info

## Spacing

Use an 8px grid system.

## Elevation

Multiple shadow levels for cards, modals, and floating elements.

## Border Radius

Consistent radius scale:

* 8px
* 12px
* 16px
* 24px

## Icons

Use a clean outline icon set similar to Lucide or Heroicons.

---

# Interactions

Design interactive prototypes showing:

* Sidebar collapse
* Hover states
* Button animations
* File upload
* Drag-and-drop interaction
* AI typing animation
* Loading states
* Chat streaming
* Modal transitions
* Success notifications

Animations should be smooth, subtle, and premium.

---

# Deliverables

Provide a complete production-ready UI/UX design including:

* High-fidelity desktop screens
* Responsive tablet layouts
* Responsive mobile layouts
* Auto Layout
* Reusable components
* Component variants
* Design Tokens
* Variables
* Constraints
* Interactive prototypes
* Complete Design System
* Developer handoff specifications
* Pixel-perfect spacing
* Accessibility considerations (WCAG AA)
* Clean, consistent, scalable design suitable for implementation in React, Next.js, Tailwind CSS, or similar modern frontend frameworks.
