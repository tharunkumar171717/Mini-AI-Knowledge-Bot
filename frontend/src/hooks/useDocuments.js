import { useCallback, useEffect, useState } from "react";
import { deleteDocument, getErrorMessage, listDocuments, uploadDocument } from "../api/client";

const POLL_MS = 2000;

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      setDocuments(await listDocuments());
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Uploads return at once with status "processing" and are indexed (and OCR'd) in the background,
  // so keep polling while any document is still processing.
  const processing = documents.some((d) => d.status === "processing");
  useEffect(() => {
    if (!processing) return;
    const timer = setInterval(refresh, POLL_MS);
    return () => clearInterval(timer);
  }, [processing, refresh]);

  const upload = useCallback(async (files) => {
    for (const file of files) {
      try {
        const doc = await uploadDocument(file);
        setDocuments((docs) => [doc, ...docs]);
        setError(null);
      } catch (err) {
        setError(`${file.name}: ${getErrorMessage(err)}`);
      }
    }
  }, []);

  const remove = useCallback(async (documentId) => {
    try {
      await deleteDocument(documentId);
      setDocuments((docs) => docs.filter((d) => d.id !== documentId));
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }, []);

  return { documents, loading, error, setError, upload, remove, clearError: () => setError(null) };
}
