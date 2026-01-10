export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  limit: number;
  offset: number;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
}

export interface ToggleCompleteRequest {
  completed: boolean;
}

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  success: boolean;
  data?: {
    user?: User;
    token?: string;
  };
  error?: {
    code: string;
    message: string;
  };
  message?: string;
}

export interface ApiError {
  code: string;
  message: string;
}

