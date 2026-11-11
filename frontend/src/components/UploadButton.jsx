import { useRef, useState } from "react";
import { Upload } from "lucide-react";

// Keep in line with the backend MAX_UPLOAD_MB (4 on Vercel, which caps request bodies at 4.5 MB).
const MAX_MB = Number(import.meta.env.VITE_MAX_UPLOAD_MB ?? 20);
const ALLOWED = /\.(pdf|png|jpe?g|txt|md)$/i;

export default function UploadButton({ onUpload, onError }) {
  const inputRef = useRef(null);
  const [busy, setBusy] = useState(false);

  const handleChange = async (event) => {
    const files = [...(event.target.files ?? [])];
    event.target.value = "";
    if (!files.length) return;

    const bad = files.find((f) => !ALLOWED.test(f.name));
    if (bad) return onError(`${bad.name}: only PDF, PNG, JPEG and TXT files are allowed.`);
    const big = files.find((f) => f.size > MAX_MB * 1024 * 1024);
    if (big) return onError(`${big.name}: file is larger than ${MAX_MB} MB.`);

    setBusy(true);
    await onUpload(files);
    setBusy(false);
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.png,.jpg,.jpeg,.txt,.md,application/pdf,image/png,image/jpeg,text/plain"
        hidden
        onChange={handleChange}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={busy}
        className="flex w-full items-center justify-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Upload size={16} />
        {busy ? "Uploading…" : "Upload documents"}
      </button>
      <p className="text-center text-[11px] text-gray-400">PDF, PNG, JPEG or TXT · scanned pages are OCR'd</p>
    </>
  );
}
