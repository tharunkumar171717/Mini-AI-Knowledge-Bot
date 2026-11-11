import Sources from "./Sources";

export default function MessageBubble({ message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-lg bg-gray-100 px-3 py-2 text-sm whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[85%]">
      <div className={`text-sm leading-relaxed whitespace-pre-wrap ${message.error ? "text-red-600" : ""}`}>
        {message.content}
      </div>
      <Sources sources={message.sources} />
    </div>
  );
}
