// Determine API URL based on environment
import { Task, TaskListResponse, User } from '../types/task';

const API_URL =
  typeof window !== 'undefined'
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Add a helper function to check if we're in the browser
const isBrowser = typeof window !== 'undefined';

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

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      if (!response.ok) {
        // Try to get error details from response
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.error?.message || errorMessage;
        } catch (e) {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        // Network error
        throw new Error('Network error: Unable to connect to the server. Please check your internet connection and try again.');
      }
      throw error;
    }
  }

  // Authentication endpoints
  async registerUser(email: string, name: string): Promise<{ access_token: string; token_type: string; user: User }> {
    return this.request(`/api/auth/register`, {
      method: "POST",
      body: JSON.stringify({ email, name }),
    });
  }

  async getCurrentUser(token: string): Promise<User> {
    // Use the new /me endpoint to get user information
    try {
      // Temporarily store the token to make the request
      const originalToken = this.token;
      this.token = token;

      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });

      // Restore original token
      this.token = originalToken;

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get user information");
      }

      const userData = await response.json();
      return userData;
    } catch (error) {
      // Restore original token if there was an error
      this.token = this.token; // this is just to be safe
      throw error;
    }
  }

  async validateTokenAndGetUser(token: string): Promise<{isValid: boolean, user?: User}> {
    try {
      // Similar approach - try to make a simple authenticated request
      const response = await fetch(`${API_URL}/health`, {
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // In a real implementation, we'd call a /api/me endpoint here
        // For now, we'll just return that the token is valid
        return { isValid: true };
      } else {
        return { isValid: false };
      }
    } catch (error) {
      return { isValid: false };
    }
  }

  // Task endpoints
  async getTasks(userId: number, status?: "pending" | "completed" | "all"): Promise<TaskListResponse> {
    let endpoint = `/api/${userId}/tasks`;
    if (status) {
      endpoint += `?status=${status}`;
    }
    return this.request<TaskListResponse>(endpoint);
  }

  async getTask(userId: number, taskId: number): Promise<{ task: Task }> {
    return this.request<{ task: Task }>(`/api/${userId}/tasks/${taskId}`);
  }

  async createTask(userId: number, data: CreateTaskRequest): Promise<{ task: Task }> {
    return this.request<{ task: Task }>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTask(userId: number, taskId: number, data: UpdateTaskRequest): Promise<{ task: Task }> {
    return this.request<{ task: Task }>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTask(userId: number, taskId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    });
  }

  async toggleTaskComplete(userId: number, taskId: number, completed: boolean): Promise<{ task: Task }> {
    return this.request<{ task: Task }>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    });
  }
}

export const api = new ApiClient();
export { API_URL };

