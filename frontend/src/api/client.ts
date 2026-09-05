import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const runWorkflow = async (userQuery: string, file: File | null) => {
  const formData = new FormData();
  formData.append('user_query', userQuery);
  if (file) {
    formData.append('image', file);
  }

  const { data } = await apiClient.post('/execute', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const startWorkflowRun = async (userQuery: string, file: File | null) => {
  const formData = new FormData();
  formData.append('user_query', userQuery);
  if (file) {
    formData.append('image', file);
  }

  const { data } = await apiClient.post('/workflow/run', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data.run_id;
};

export const subscribeToWorkflow = (runId: string, onMessage: (msg: any) => void, onError: (err: any) => void) => {
  const eventSource = new EventSource(`${API_BASE_URL}/workflow/stream/${runId}`);
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error("Failed to parse SSE data", e);
    }
  };

  eventSource.onerror = (err) => {
    eventSource.close();
    onError(err);
  };

  return () => {
    eventSource.close();
  };
};

export const fetchVramStatus = async () => {
  const { data } = await apiClient.get('/vram');
  return data;
};

// Keep existing methods from previous step so other pages don't break
export const getSystemStatus = async () => {
  const { data } = await apiClient.get('/system/status');
  return data;
};

export const getHealth = async () => {
  const { data } = await apiClient.get('/health');
  return data;
};
