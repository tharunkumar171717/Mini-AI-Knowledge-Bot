import { useCallback, useState } from "react";
import { askQuestion, getErrorMessage } from "../api/client";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = useCallback(async (question) => {
    setMessages((msgs) => [...msgs, { role: "user", content: question }]);
    setLoading(true);
    try {
      const data = await askQuestion(question);
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: data.answer, sources: data.sources ?? [] },
      ]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: getErrorMessage(err), error: true },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, send };
}
