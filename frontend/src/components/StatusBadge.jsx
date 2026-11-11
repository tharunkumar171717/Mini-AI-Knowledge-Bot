const STYLES = {
  processing: "text-amber-700 bg-amber-50",
  completed: "text-green-700 bg-green-50",
  failed: "text-red-700 bg-red-50",
};

const LABELS = { processing: "Processing", completed: "Completed", failed: "Failed" };

export default function StatusBadge({ status }) {
  return (
    <span className={`rounded px-1.5 py-0.5 text-[11px] ${STYLES[status] ?? "bg-gray-100 text-gray-600"}`}>
      {LABELS[status] ?? status}
    </span>
  );
}
