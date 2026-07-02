import { useState } from "react";
import { motion } from "motion/react";
import { FileText, Copy, ThumbsUp, ThumbsDown, Check, Sparkles } from "lucide-react";
import { type Message } from "../types";

export function ChatMessage({ msg, onFeedback }: { msg: Message; onFeedback: (id: string, v: "up" | "down") => void }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(msg.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderContent = (content: string) => {
    const lines = content.split("\n");
    return lines.map((line, i) => {
      if (line.startsWith("## ")) return <h2 key={i} className="text-lg font-semibold mt-4 mb-2 text-foreground">{line.slice(3)}</h2>;
      if (line.startsWith("### ")) return <h3 key={i} className="text-base font-semibold mt-3 mb-1.5 text-foreground">{line.slice(4)}</h3>;
      if (line.startsWith("```")) return null;
      if (line.startsWith("> ")) return (
        <blockquote key={i} className="border-l-2 border-primary/50 pl-3 my-2 text-muted-foreground italic text-[15px]">
          {line.slice(2)}
        </blockquote>
      );
      if (line.startsWith("- ")) return (
        <li key={i} className="ml-4 text-[15px] text-foreground/90 my-0.5 list-disc">{line.slice(2).replace(/\*\*(.*?)\*\*/g, "$1")}</li>
      );
      if (/^\d+\./.test(line)) return (
        <li key={i} className="ml-4 text-[15px] text-foreground/90 my-0.5 list-decimal">{line.replace(/^\d+\.\s*/, "").replace(/\*\*(.*?)\*\*/g, "$1")}</li>
      );
      if (line.startsWith("*Source:") || line.startsWith("*")) return (
        <p key={i} className="text-sm text-muted-foreground mt-3 italic">{line.replace(/\*/g, "")}</p>
      );
      if (line.trim() === "") return <br key={i} />;

      const boldProcessed = line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      return <p key={i} className="text-[15px] text-foreground/90 my-1" dangerouslySetInnerHTML={{ __html: boldProcessed }} />;
    });
  };

  if (msg.role === "user") {
    return (
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex justify-end mb-6">
        <div className="max-w-full sm:max-w-[75%]">
          {msg.files && msg.files.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-2 justify-end">
              {msg.files.map((f, i) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary text-sm rounded-lg font-medium">
                  <FileText size={13} /> {f}
                </span>
              ))}
            </div>
          )}
          <div className="bg-primary text-primary-foreground rounded-2xl rounded-br-md px-4 py-3 shadow-sm">
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.15 } }} className="flex justify-start mb-6">
      <div className="max-w-full sm:max-w-[85%]">
        <div className="flex items-start gap-3">
          <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-1">
            <Sparkles size={13} className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[15px] leading-relaxed text-foreground/90 prose max-w-none">
              {renderContent(msg.content)}
            </div>

            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-border">
                <p className="text-sm font-semibold text-muted-foreground mb-2">Sources</p>
                <div className="flex flex-wrap gap-1.5">
                  {msg.citations.map((c) => (
                    <span key={c.id} className="text-sm px-2 py-0.5 bg-muted rounded-md text-muted-foreground">
                      [{c.id}] {c.source}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center gap-1 mt-2">
              <button onClick={handleCopy} className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" title="Copy response">
                {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
              </button>
              <button onClick={() => onFeedback(msg.id, "up")} className={`p-1.5 rounded-lg hover:bg-muted transition-colors ${msg.feedback === "up" ? "text-emerald-500" : "text-muted-foreground hover:text-foreground"}`} title="Helpful">
                <ThumbsUp size={12} />
              </button>
              <button onClick={() => onFeedback(msg.id, "down")} className={`p-1.5 rounded-lg hover:bg-muted transition-colors ${msg.feedback === "down" ? "text-destructive" : "text-muted-foreground hover:text-foreground"}`} title="Not helpful">
                <ThumbsDown size={12} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
