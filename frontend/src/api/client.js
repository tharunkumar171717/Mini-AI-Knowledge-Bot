import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001",
  timeout: 120_000,
});

// FastAPI puts the reason in `detail`: a string for HTTPException, a list for validation errors.
export function getErrorMessage(error) {
  if (!error.response) {
    return error.code === "ECONNABORTED"
      ? "The request timed out."
      : "Cannot reach the server. Is the backend running?";
  }
  const detail = error.response.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  return `Request failed (${error.response.status}).`;
}

export async function listDocuments() {
  const { data } = await api.get("/api/documents");
  return data;
}

// Opens in a new tab; `page` jumps to that page in the browser's PDF viewer.
export function documentFileUrl(documentId, page) {
  const url = `${api.defaults.baseURL}/api/documents/${documentId}/file`;
  return page ? `${url}#page=${page}` : url;
}

export async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/api/documents/upload", form);
  return data;
}

export async function deleteDocument(documentId) {
  await api.delete(`/api/documents/${documentId}`);
}

export async function askQuestion(question) {
  const { data } = await api.post("/api/chat", { question });
  return data;
}
