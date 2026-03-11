import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export interface TranscodeSettings {
  codec: string;
  resolution: string;
  video_bitrate?: string;
  audio_bitrate?: string;
}

export interface VideoFile {
  id: string;
  name: string;
  original_path: string;
  output_path?: string;
  size: number;
  status: string;
  progress: number;
  error?: string;
}

export interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  total_files: number;
  completed_files: number;
  failed_files: number;
  current_file?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  videos: VideoFile[];
  settings: TranscodeSettings;
}

export const api = {
  async createTask(
    files: File[],
    settings: TranscodeSettings,
    name?: string
  ): Promise<Task> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('codec', settings.codec);
    formData.append('resolution', settings.resolution);
    formData.append('video_bitrate', settings.video_bitrate || '2000k');
    formData.append('audio_bitrate', settings.audio_bitrate || '128k');
    if (name) formData.append('name', name);

    const response = await axios.post(`${API_BASE}/tasks`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async listTasks(): Promise<Task[]> {
    const response = await axios.get(`${API_BASE}/tasks`);
    return response.data;
  },

  async getTask(taskId: string): Promise<Task> {
    const response = await axios.get(`${API_BASE}/tasks/${taskId}`);
    return response.data;
  },

  async startTask(taskId: string): Promise<void> {
    await axios.post(`${API_BASE}/tasks/${taskId}/start`);
  },

  async cancelTask(taskId: string): Promise<void> {
    await axios.post(`${API_BASE}/tasks/${taskId}/cancel`);
  },

  async deleteTask(taskId: string): Promise<void> {
    await axios.delete(`${API_BASE}/tasks/${taskId}`);
  },

  async listUploads(): Promise<{ name: string; size: number; path: string }[]> {
    const response = await axios.get(`${API_BASE}/uploads`);
    return response.data;
  },

  async listOutputs(): Promise<{ name: string; size: number; path: string }[]> {
    const response = await axios.get(`${API_BASE}/outputs`);
    return response.data;
  },
};
