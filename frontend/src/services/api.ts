/**
 * API Client for Phase V with advanced task features.
 * 
 * Features:
 * - Advanced task CRUD with Phase V fields
 * - Search, filter, and sort capabilities
 * - Event subscriptions
 * - Reminder management
 */

import {
  Task,
  TaskListResponse,
  User,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskCompleteResponse,
  TaskFilters,
  EventListResponse,
  EventStats,
} from "../types/task";

// Determine API URL based on environment
const API_URL =
  typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Add a helper function to check if we're in the browser
const isBrowser = typeof window !== "undefined";

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

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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
      if (error instanceof TypeError && error.message.includes("fetch")) {
        // Network error
        throw new Error(
          "Network error: Unable to connect to the server. Please check your internet connection and try again."
        );
      }
      throw error;
    }
  }

  // ============================================================================
  // Authentication endpoints
  // ============================================================================

  async registerUser(
    email: string,
    name: string
  ): Promise<{ access_token: string; token_type: string; user: User }> {
    return this.request(`/api/auth/register`, {
      method: "POST",
      body: JSON.stringify({ email, name }),
    });
  }

  async getCurrentUser(token: string): Promise<User> {
    try {
      const originalToken = this.token;
      this.token = token;

      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      this.token = originalToken;

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get user information");
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  async validateTokenAndGetUser(token: string): Promise<{ isValid: boolean; user?: User }> {
    try {
      const response = await fetch(`${API_URL}/health`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        return { isValid: true };
      } else {
        return { isValid: false };
      }
    } catch (error) {
      return { isValid: false };
    }
  }

  // ============================================================================
  // Task endpoints (Phase V Enhanced)
  // ============================================================================

  /**
   * Get tasks with advanced filtering and sorting.
   * 
   * @param userId - User ID
   * @param filters - Optional filters (status, priority, tags, keyword, dates, sorting)
   */
  async getTasks(userId: number, filters?: TaskFilters): Promise<TaskListResponse> {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.status && filters.status !== "all") {
        params.append("status", filters.status);
      }
      if (filters.priority) {
        params.append("priority", filters.priority);
      }
      if (filters.tags && filters.tags.length > 0) {
        params.append("tags", filters.tags.join(","));
      }
      if (filters.keyword) {
        params.append("keyword", filters.keyword);
      }
      if (filters.due_date_from) {
        params.append("due_date_from", filters.due_date_from);
      }
      if (filters.due_date_to) {
        params.append("due_date_to", filters.due_date_to);
      }
      if (filters.sort_by) {
        params.append("sort_by", filters.sort_by);
      }
      if (filters.sort_order) {
        params.append("sort_order", filters.sort_order);
      }
    }

    const queryString = params.toString();
    const endpoint = `/api/${userId}/tasks${queryString ? `?${queryString}` : ""}`;

    return this.request<TaskListResponse>(endpoint);
  }

  async getTask(userId: number, taskId: number): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`);
  }

  /**
   * Create a new task with Phase V advanced properties.
   */
  async createTask(userId: number, data: CreateTaskRequest): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  /**
   * Update an existing task with Phase V advanced properties.
   */
  async updateTask(userId: number, taskId: number, data: UpdateTaskRequest): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTask(userId: number, taskId: number): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    });
  }

  /**
   * Toggle task completion. For recurring tasks, returns the next occurrence.
   */
  async toggleTaskComplete(
    userId: number,
    taskId: number,
    completed: boolean
  ): Promise<TaskCompleteResponse> {
    return this.request<TaskCompleteResponse>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    });
  }

  // ============================================================================
  // Event endpoints (Phase V)
  // ============================================================================

  /**
   * Get event history (audit log) with filtering.
   */
  async getEvents(
    userId: number,
    options?: {
      event_type?: string;
      task_id?: number;
      from_date?: string;
      to_date?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<EventListResponse> {
    const params = new URLSearchParams();

    if (options) {
      if (options.event_type) params.append("event_type", options.event_type);
      if (options.task_id) params.append("task_id", options.task_id.toString());
      if (options.from_date) params.append("from_date", options.from_date);
      if (options.to_date) params.append("to_date", options.to_date);
      if (options.limit) params.append("limit", options.limit.toString());
      if (options.offset) params.append("offset", options.offset.toString());
    }

    const queryString = params.toString();
    const endpoint = `/api/${userId}/events${queryString ? `?${queryString}` : ""}`;

    return this.request<EventListResponse>(endpoint);
  }

  /**
   * Get event statistics for a time period.
   */
  async getEventStats(userId: number, days: number = 7): Promise<EventStats> {
    return this.request<EventStats>(`/api/${userId}/events/stats?days=${days}`);
  }

  /**
   * Create a WebSocket connection for real-time event streaming.
   */
  createEventStream(userId: number): WebSocket | null {
    if (!isBrowser) return null;

    const wsUrl = API_URL.replace(/^http/, "ws");
    const ws = new WebSocket(`${wsUrl}/api/${userId}/events/stream`);

    return ws;
  }

  // ============================================================================
  // Chat endpoints
  // ============================================================================

  async chat(
    message: string,
    userId: number
  ): Promise<{ response: string; action_performed?: string; task_result?: any }> {
    const headers = this.getHeaders();

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
        body: JSON.stringify({
          messages: [{ role: "user", content: message }],
          user_id: userId,
        }),
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          "Network error: Unable to connect to the server. Please check your internet connection and try again."
        );
      }
      throw error;
    }
  }
}

export const api = new ApiClient();
export { API_URL };
