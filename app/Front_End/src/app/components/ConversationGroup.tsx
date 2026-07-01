import { type Conversation } from "../types";

export function ConversationGroup({ label, items, activeId, onSelect }: {
  label: string;
  items: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
}) {
  if (items.length === 0) return null;

  return (
    <div className="mb-4">
      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider px-3 mb-1.5">{label}</p>
      {items.map((c) => (
        <button
          key={c.id}
          onClick={() => onSelect(c.id)}
          className={`w-full text-left px-3 py-2.5 rounded-xl transition-colors group ${activeId === c.id ? "bg-sidebar-accent text-sidebar-foreground" : "hover:bg-sidebar-accent/60 text-sidebar-foreground/80"}`}
        >
          <p className="text-sm font-medium leading-tight truncate">{c.title}</p>
          <p className="text-xs text-muted-foreground mt-0.5 truncate">{c.preview}</p>
        </button>
      ))}
    </div>
  );
}
