import { useEffect, useState } from "react";
import { Task, TaskFilter } from "../types/task";
import { api } from "../services/api";
import TaskItem from "./TaskItem";

interface TaskListProps {
  userId: number;
}

export default function TaskList({ userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<TaskFilter>("all");

  const fetchTasks = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await api.getTasks(userId, filter === "all" ? undefined : filter);
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch tasks");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [userId, filter]);

  const filteredTasks = tasks;

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Your Tasks</h2>

        <div className="flex gap-2">
          {(["all", "pending", "completed"] as TaskFilter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-md text-sm ${
                filter === f
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading tasks...</div>
      ) : filteredTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
          {filter === "all"
            ? "No tasks yet. Add your first task above!"
            : filter === "pending"
            ? "No pending tasks"
            : "No completed tasks"}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              userId={userId}
              onTaskUpdate={fetchTasks}
              onTaskDelete={fetchTasks}
            />
          ))}
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        {filteredTasks.length} task{filteredTasks.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}
