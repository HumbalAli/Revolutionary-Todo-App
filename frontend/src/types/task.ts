/**
 * Task and User type definitions for Phase V.
 * 
 * Phase V additions:
 * - Priority levels (HIGH/MEDIUM/LOW)
 * - Tags for categorization
 * - Due dates and reminders
 * - Recurrence patterns
 * - Advanced filtering and sorting
 */

// ============================================================================
// Enums and Constants
// ============================================================================

export type Priority = "HIGH" | "MEDIUM" | "LOW";
export type TaskStatus = "pending" | "in_progress" | "completed";
export type SortField = "due_date" | "priority" | "created_at" | "title";
export type SortOrder = "asc" | "desc";

export const PRIORITY_LABELS: Record<Priority, string> = {
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
};

export const PRIORITY_COLORS: Record<Priority, string> = {
  HIGH: "#ef4444",    // red-500
  MEDIUM: "#f59e0b",  // amber-500
  LOW: "#22c55e",     // green-500
};

// Common tag presets
export const TAG_PRESETS = ["work", "home", "urgent", "personal", "health", "finance"];

// Recurrence presets
export const RECURRENCE_PRESETS: Record<string, { label: string; rrule: string }> = {
  daily: { label: "Daily", rrule: "FREQ=DAILY" },
  weekdays: { label: "Weekdays", rrule: "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR" },
  weekly: { label: "Weekly", rrule: "FREQ=WEEKLY" },
  biweekly: { label: "Every 2 weeks", rrule: "FREQ=WEEKLY;INTERVAL=2" },
  monthly: { label: "Monthly", rrule: "FREQ=MONTHLY" },
  quarterly: { label: "Quarterly", rrule: "FREQ=MONTHLY;INTERVAL=3" },
  yearly: { label: "Yearly", rrule: "FREQ=YEARLY" },
};

// ============================================================================
// Task Types
// ============================================================================

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
  // Phase V advanced properties
  due_date?: string | null;
  priority?: Priority | null;
  tags?: string[];
  recurrence_rule?: string | null;
  recurrence_parent_id?: number | null;
  is_recurring?: boolean;
  reminder_offset_minutes?: number | null;
  recurrence_count?: number | null;
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
  // Phase V advanced properties
  due_date?: string;
  priority?: Priority;
  tags?: string[];
  recurrence_rule?: string;
  reminder_offset_minutes?: number;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  // Phase V advanced properties
  due_date?: string;
  priority?: Priority;
  tags?: string[];
  recurrence_rule?: string;
  reminder_offset_minutes?: number;
}

export interface ToggleCompleteRequest {
  completed: boolean;
}

export interface TaskCompleteResponse {
  completed_task: Task;
  next_occurrence?: Task | null;
}

// ============================================================================
// Filter Types (Phase V)
// ============================================================================

export interface TaskFilters {
  status?: TaskStatus | "all";
  priority?: Priority | null;
  tags?: string[];
  keyword?: string;
  due_date_from?: string;
  due_date_to?: string;
  sort_by?: SortField;
  sort_order?: SortOrder;
}

export type TaskFilter = "all" | "pending" | "completed";

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  default_priority?: Priority | null;
  default_reminder_offset_minutes: number;
  default_tags: string[];
  timezone: string;
  notification_preferences: Record<string, unknown>;
}

// ============================================================================
// Auth Types
// ============================================================================

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

// ============================================================================
// Event Types (Phase V)
// ============================================================================

export interface TaskEvent {
  id: string;
  event_type: string;
  schema_version: string;
  timestamp: string;
  user_id: string;
  task_id: string;
  data: Record<string, unknown>;
}

export interface EventListResponse {
  events: TaskEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface EventStats {
  period_days: number;
  from_date: string;
  to_date: string;
  event_counts: Record<string, number>;
  total_events: number;
}
