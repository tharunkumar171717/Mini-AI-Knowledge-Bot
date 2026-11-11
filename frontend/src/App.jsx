import ChatWindow from "./components/ChatWindow";
import Sidebar from "./components/Sidebar";
import { useChat } from "./hooks/useChat";
import { useDocuments } from "./hooks/useDocuments";

export default function App() {
  const docs = useDocuments();
  const chat = useChat();
  const hasCompleted = docs.documents.some((d) => d.status === "completed");

  return (
    <div className="flex h-full flex-col md:flex-row">
      <Sidebar
        documents={docs.documents}
        loading={docs.loading}
        error={docs.error}
        onUpload={docs.upload}
        onDelete={docs.remove}
        onError={docs.setError}
        onClearError={docs.clearError}
      />
      <ChatWindow
        messages={chat.messages}
        loading={chat.loading}
        onSend={chat.send}
        hasDocuments={hasCompleted}
      />
    </div>
  );
}
