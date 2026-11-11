import { useState } from "react";
import { SendHorizontal } from "lucide-react";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");

  const submit = (event) => {
    event.preventDefault();
    const question = value.trim();
    if (!question || disabled) return;
    onSend(question);
    setValue("");
  };

  // Enter sends, Shift+Enter adds a new line.
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) submit(event);
  };

  return (
    <form onSubmit={submit} className="border-t border-gray-200 p-3">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-lg border border-gray-300 px-3 py-2 focus-within:border-gray-400">
        <textarea
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents…"
          className="max-h-40 flex-1 resize-none text-sm outline-none"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          aria-label="Send"
          className="rounded-md bg-indigo-600 p-1.5 text-white disabled:opacity-30"
        >
          <SendHorizontal size={16} />
        </button>
      </div>
    </form>
  );
}
