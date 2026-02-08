import { useState } from "react";
import { Task } from "../types/task";
import { api } from "../services/api";

interface TaskItemProps {
  task: Task;
  userId: number;
  onTaskUpdate: () => void;
  onTaskDelete: () => void;
}

export default function TaskItem({ task, userId, onTaskUpdate, onTaskDelete }: TaskItemProps) {
  const [loading, setLoading] = useState(false);

  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await api.toggleTaskComplete(userId, task.id, !task.completed);
      onTaskUpdate();
    } catch (err) {
      console.error("Failed to toggle task:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) return;

    setLoading(true);
    try {
      await api.deleteTask(userId, task.id);
      onTaskDelete();
    } catch (err) {
      console.error("Failed to delete task:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 ${task.completed ? "bg-gray-50 opacity-80" : "bg-white"}`}>
      <div className="flex items-start gap-4">
        <button
          onClick={handleToggleComplete}
          disabled={loading}
          className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center mt-1 transition-all duration-200 ${
            task.completed
              ? "bg-gradient-to-r from-green-400 to-green-500 border-green-500"
              : "border-gray-300 hover:border-blue-500"
          } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          title={task.completed ? "Mark as incomplete" : "Mark as complete"}
        >
          {task.completed && (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-base truncate ${task.completed ? "line-through text-gray-500" : "text-gray-800"}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`text-sm mt-1.5 ${task.completed ? "text-gray-400" : "text-gray-600"} break-words`}>
              {task.description}
            </p>
          )}
          <div className="flex items-center mt-3 text-xs text-gray-400">
            <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
            {task.completed && (
              <span className="ml-3 inline-flex items-center px-2 py-0.5 rounded-full bg-green-100 text-green-800">
                <svg className="mr-1.5 h-3 w-3" fill="currentColor" viewBox="0 0 8 8">
                  <circle cx="4" cy="4" r="3" />
                </svg>
                Completed
              </span>
            )}
          </div>
        </div>

        <button
          onClick={handleDelete}
          disabled={loading}
          className="p-2 text-gray-400 hover:text-red-500 rounded-full hover:bg-red-50 transition-colors disabled:opacity-50"
          title="Delete task"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  );
}