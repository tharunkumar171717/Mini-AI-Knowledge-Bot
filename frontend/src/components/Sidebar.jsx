import { Bot, X } from "lucide-react";
import DocumentItem from "./DocumentItem";
import UploadButton from "./UploadButton";

export default function Sidebar({ documents, loading, error, onUpload, onDelete, onError, onClearError }) {
  return (
    <aside className="flex max-h-64 shrink-0 flex-col border-b border-gray-200 bg-gray-50/60 md:max-h-none md:w-72 md:border-r md:border-b-0">
      <div className="space-y-3 border-b border-gray-200 p-3">
        <div className="flex items-center gap-2">
          <Bot size={18} className="text-indigo-600" />
          <h1 className="text-sm font-semibold">Knowledge Bot</h1>
        </div>
        <UploadButton onUpload={onUpload} onError={onError} />
        {error && (
          <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-2 text-xs text-red-700">
            <span className="flex-1">{error}</span>
            <button type="button" onClick={onClearError} aria-label="Dismiss">
              <X size={12} />
            </button>
          </div>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        <h2 className="px-2 pb-1 text-xs font-medium tracking-wide text-gray-500 uppercase">Documents</h2>
        {loading ? (
          <p className="px-2 py-2 text-sm text-gray-400">Loading…</p>
        ) : documents.length === 0 ? (
          <p className="px-2 py-2 text-sm text-gray-400">No documents yet.</p>
        ) : (
          <ul className="space-y-0.5">
            {documents.map((doc) => (
              <DocumentItem key={doc.id} document={doc} onDelete={onDelete} />
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
