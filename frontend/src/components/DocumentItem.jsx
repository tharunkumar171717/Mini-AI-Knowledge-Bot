import { FileImage, FileText, ScanText, Trash2 } from "lucide-react";
import StatusBadge from "./StatusBadge";

export default function DocumentItem({ document, onDelete }) {
  const Icon = document.mime_type?.startsWith("image/") ? FileImage : FileText;

  const handleDelete = () => {
    if (window.confirm(`Delete "${document.filename}"?`)) onDelete(document.id);
  };

  return (
    <li className="group flex items-start gap-2 rounded-md px-2 py-2 hover:bg-white">
      <Icon size={16} className="mt-0.5 shrink-0 text-gray-400" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm" title={document.filename}>
          {document.filename}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-1.5 text-[11px] text-gray-500">
          <StatusBadge status={document.status} />
          {document.page_count != null && (
            <span>
              {document.page_count} {document.page_count === 1 ? "page" : "pages"}
            </span>
          )}
          {document.ocr_pages > 0 && (
            <span className="inline-flex items-center gap-0.5" title="Pages read with OCR">
              <ScanText size={11} /> OCR {document.ocr_pages}
            </span>
          )}
        </div>
        {document.status === "failed" && document.error && (
          <p className="mt-1 line-clamp-3 text-[11px] text-red-600" title={document.error}>
            {document.error}
          </p>
        )}
      </div>
      <button
        type="button"
        onClick={handleDelete}
        aria-label={`Delete ${document.filename}`}
        className="shrink-0 rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-red-600"
      >
        <Trash2 size={14} />
      </button>
    </li>
  );
}
