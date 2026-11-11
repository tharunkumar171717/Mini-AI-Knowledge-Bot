import { FileText } from "lucide-react";
import { documentFileUrl } from "../api/client";

export default function Sources({ sources }) {
  if (!sources?.length) return null;

  // Several chunks can come from the same page; show each file + page once, with its best score.
  const best = new Map();
  for (const s of sources) {
    const key = `${s.filename}#${s.page}`;
    if (!best.has(key) || best.get(key).score < s.score) best.set(key, s);
  }

  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {[...best.entries()].map(([key, s]) => (
        <a
          key={key}
          href={documentFileUrl(s.document_id, s.filename.toLowerCase().endsWith(".pdf") ? s.page : undefined)}
          target="_blank"
          rel="noopener noreferrer"
          title={s.content}
          className="inline-flex items-center gap-1 rounded border border-gray-200 px-1.5 py-0.5 text-xs text-gray-500 hover:border-blue-300 hover:text-blue-600"
        >
          <FileText size={12} />
          {s.filename} · p. {s.page}
          <span className="text-gray-400">{Math.round(s.score * 100)}%</span>
        </a>
      ))}
    </div>
  );
}
