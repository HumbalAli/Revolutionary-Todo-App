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
    <div className={`p-4 border rounded-lg mb-2 ${task.completed ? "bg-gray-50" : "bg-white"}`}>
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggleComplete}
          disabled={loading}
          className="mt-1 h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
        />

        <div className="flex-1">
          <h3 className={`font-medium ${task.completed ? "line-through text-gray-500" : "text-gray-900"}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`text-sm mt-1 ${task.completed ? "text-gray-400" : "text-gray-600"}`}>
              {task.description}
            </p>
          )}
          <p className="text-xs text-gray-400 mt-2">
            Created: {new Date(task.created_at).toLocaleDateString()}
          </p>
        </div>

        <button
          onClick={handleDelete}
          disabled={loading}
          className="text-red-600 hover:text-red-800 disabled:opacity-50"
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
