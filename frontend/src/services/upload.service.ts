// Upload Service - Connects to FastAPI backend
// Backend: http://localhost:8000

import type { UploadState, UploadResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Cache the last successful upload so analysis can use the real image ID
let lastUploadResponse: UploadResponse | null = null;

export function getLastUploadResponse(): UploadResponse | null {
  return lastUploadResponse;
}

export async function uploadImage(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  const raw = await response.json();
  const result: UploadResponse = {
    id: raw.id ?? raw.image_id,
    requestId: raw.requestId ?? raw.request_id ?? "",
    filename: raw.filename ?? raw.original_filename ?? "",
    url: raw.url ?? raw.image_url ?? "",
    size: raw.size ?? raw.file_size ?? 0,
    mimeType: raw.mimeType ?? raw.mime_type ?? "",
    uploadedAt: raw.uploadedAt ?? raw.uploaded_at ?? new Date().toISOString(),
  };
  lastUploadResponse = result;
  return result;
}

export function getInitialState(): UploadState {
  return {
    status: "idle",
    progress: 0,
    file: null,
    previewUrl: null,
    errorMessage: null,
  };
}

// Simulate upload progress callback using XMLHttpRequest for progress tracking
export function simulateUploadProgress(
  file: File,
  onProgress: (progress: number) => void
): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE_URL}/api/upload`);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const progress = Math.round((event.loaded / event.total) * 100);
        onProgress(progress);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        const raw = JSON.parse(xhr.responseText);
        const result: UploadResponse = {
          id: raw.id ?? raw.image_id,
          requestId: raw.requestId ?? raw.request_id ?? "",
          filename: raw.filename ?? raw.original_filename ?? "",
          url: raw.url ?? raw.image_url ?? "",
          size: raw.size ?? raw.file_size ?? 0,
          mimeType: raw.mimeType ?? raw.mime_type ?? "",
          uploadedAt: raw.uploadedAt ?? raw.uploaded_at ?? new Date().toISOString(),
        };
        lastUploadResponse = result;
        resolve(result);
      } else {
        try {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.detail || "Upload failed"));
        } catch {
          reject(new Error("Upload failed"));
        }
      }
    };

    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(formData);
  });
}
