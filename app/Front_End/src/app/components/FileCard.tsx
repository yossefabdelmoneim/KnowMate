import { motion } from "motion/react";
import { X, Check, Loader2, FileText, FileSpreadsheet, FileImage, File, AlertCircle } from "lucide-react";
import { type UploadedFile } from "../types";

const fileColorMap: Record<string, string> = {
  pdf: "bg-red-500/10 text-red-600 dark:text-red-400",
  docx: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  xlsx: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
  pptx: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
  csv: "bg-green-500/10 text-green-600 dark:text-green-400",
  txt: "bg-gray-500/10 text-gray-600 dark:text-gray-400",
  img: "bg-purple-500/10 text-purple-600 dark:text-purple-400",
};

function fileTypeIcon(type: string) {
  if (type === "xlsx" || type === "csv") return <FileSpreadsheet size={16} />;
  if (type === "img") return <FileImage size={16} />;
  if (type === "pdf" || type === "docx" || type === "pptx" || type === "txt") return <FileText size={16} />;
  return <File size={16} />;
}

export function FileCard({ file, onRemove }: { file: UploadedFile; onRemove: (id: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 6 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="flex items-center gap-3 bg-card border border-border rounded-xl p-3 min-w-0 sm:min-w-[200px] sm:max-w-[260px] group shadow-sm w-full sm:w-auto"
    >
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold ${fileColorMap[file.icon]}`}>
        {fileTypeIcon(file.icon)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate leading-tight">{file.name}</p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="text-xs text-muted-foreground">{file.size}</span>
          {file.status === "uploading" && (
            <div className="flex items-center gap-1 text-xs text-amber-500">
              <Loader2 size={10} className="animate-spin" />
              <span>{file.progress}%</span>
            </div>
          )}
          {file.status === "processing" && (
            <div className="flex items-center gap-1 text-xs text-blue-500">
              <Loader2 size={10} className="animate-spin" />
              <span>Analyzing</span>
            </div>
          )}
          {file.status === "ready" && (
            <div className="flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
              <Check size={10} />
              <span>Ready</span>
            </div>
          )}
          {file.status === "error" && (
            <div className="flex items-center gap-1 text-xs text-destructive" title={file.errorMessage}>
              <AlertCircle size={10} />
              <span>Failed</span>
            </div>
          )}
        </div>
        {file.status === "uploading" && (
          <div className="mt-1.5 h-1 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${file.progress}%` }}
              transition={{ duration: 0.4 }}
            />
          </div>
        )}
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={() => onRemove(file.id)}
          className="p-1 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
        >
          <X size={13} />
        </button>
      </div>
    </motion.div>
  );
}
