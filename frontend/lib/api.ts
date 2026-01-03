/**
 * API client for the Interior Design backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new ApiError(error.detail || 'An error occurred', response.status);
  }
  return response.json();
}

// Projects
export async function createProject(name?: string) {
  const response = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name || 'Untitled Project' }),
  });
  return handleResponse<{ id: string; name: string }>(response);
}

export async function getProjects() {
  const response = await fetch(`${API_BASE}/projects`);
  return handleResponse<Array<{
    id: string;
    name: string;
    status: string;
    created_at: string;
    updated_at: string;
    has_room_photo: boolean;
    current_version: number | null;
    message_count: number;
  }>>(response);
}

export async function getProject(projectId: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}`);
  return handleResponse<{
    id: string;
    name: string;
    status: string;
    room_analysis: Record<string, unknown> | null;
    current_image_url: string | null;
    original_image_url: string | null;
    current_version: number | null;
  }>(response);
}

export async function deleteProject(projectId: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new ApiError('Failed to delete project', response.status);
  }
}

// Images
export async function uploadRoomPhoto(projectId: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/projects/${projectId}/upload`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse<{
    image_url: string;
    thumbnail_url: string | null;
    analysis: Record<string, unknown>;
    message: string;
  }>(response);
}

export async function getCurrentImage(projectId: string, version?: number) {
  const url = version
    ? `${API_BASE}/projects/${projectId}/image?version=${version}`
    : `${API_BASE}/projects/${projectId}/image`;
  const response = await fetch(url);
  return handleResponse<{
    image_url: string;
    thumbnail_url: string | null;
    version: number;
    is_original: boolean;
  }>(response);
}

// Chat
export async function sendChatMessage(projectId: string, content: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  return handleResponse<{
    type: string;
    message: string;
    image_url: string | null;
    version: number | null;
    changes: Array<Record<string, unknown>> | null;
  }>(response);
}

export async function getChatHistory(projectId: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/chat/history`);
  return handleResponse<Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    image_url: string | null;
    version_number: number | null;
    created_at: string;
  }>>(response);
}

// Versions
export async function getVersions(projectId: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/versions`);
  return handleResponse<Array<{
    id: string;
    version_number: number;
    image_url: string;
    thumbnail_url: string | null;
    is_favorite: boolean;
    is_final: boolean;
    created_at: string;
  }>>(response);
}

export async function toggleFavorite(projectId: string, versionNumber: number) {
  const response = await fetch(
    `${API_BASE}/projects/${projectId}/versions/${versionNumber}/favorite`,
    { method: 'POST' }
  );
  return handleResponse<{ is_favorite: boolean }>(response);
}

export async function finalizeVersion(projectId: string, versionNumber: number) {
  const response = await fetch(
    `${API_BASE}/projects/${projectId}/versions/${versionNumber}/finalize`,
    { method: 'POST' }
  );
  return handleResponse<{ message: string; version: number }>(response);
}

// Export
export async function exportDesign(projectId: string, format: 'pdf' | 'shopping_list' | 'colors' | 'json') {
  const response = await fetch(`${API_BASE}/projects/${projectId}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format }),
  });

  if (format === 'pdf') {
    if (!response.ok) {
      throw new ApiError('Failed to export PDF', response.status);
    }
    return response.blob();
  }

  return handleResponse<Record<string, unknown>>(response);
}

export async function getSpecification(projectId: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/specification`);
  return handleResponse<{
    project_name: string;
    summary_of_changes: string[];
    paint: Array<Record<string, unknown>>;
    furniture: Array<Record<string, unknown>>;
    budget: Array<{ category: string; low: number; high: number }>;
    total_budget_low: number;
    total_budget_high: number;
  }>(response);
}

// WebSocket helper
export function createWebSocket(projectId: string): WebSocket {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
  return new WebSocket(`${wsUrl}/api/projects/${projectId}/ws`);
}
