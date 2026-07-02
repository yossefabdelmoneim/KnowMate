import { Trash2 } from "lucide-react";
import { type Conversation } from "../types";

export function ConversationGroup({ label, items, activeId, onSelect, onDelete }: {
  label: string;
  items: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
}) {
  if (items.length === 0) return null;

  return (
    <div className="mb-4">
      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider px-3 mb-1.5">{label}</p>
      {items.map((c) => (
        <div
          key={c.id}
          onClick={() => onSelect(c.id)}
          className={`group flex items-center gap-1 w-full text-left px-3 py-2.5 rounded-xl transition-colors cursor-pointer ${activeId === c.id ? "bg-sidebar-accent text-sidebar-foreground" : "hover:bg-sidebar-accent/60 text-sidebar-foreground/80"}`}
        >
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium leading-tight truncate">{c.title}</p>
            <p className="text-xs text-muted-foreground mt-0.5 truncate">{c.preview}</p>
          </div>
          <button
            onClick={(e) => onDelete(c.id, e)}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-sidebar-accent text-muted-foreground hover:text-destructive transition-all flex-shrink-0"
            title="Delete conversation"
          >
            <Trash2 size={13} />
          </button>
        </div>
      ))}
    </div>
  );
}
