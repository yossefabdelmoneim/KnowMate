export type Mode = "home" | "welcome" | "chat" | "login" | "register" | "forgot-password" | "reset-password" | "settings" | "profile";

export interface UploadedFile {
  id: string;
  name: string;
  size: string;
  type: string;
  status: "uploading" | "processing" | "ready" | "error";
  progress: number;
  icon: "pdf" | "docx" | "xlsx" | "pptx" | "csv" | "txt" | "img";
  errorMessage?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  files?: string[];
  timestamp: Date;
  feedback?: "up" | "down";
  citations?: { id: number; source: string }[];
}

export interface Conversation {
  id: string;
  title: string;
  preview: string;
  date: Date;
}

export interface Session {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}
