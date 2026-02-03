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
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await api.deleteTask(userId, task.id);
      onTaskDelete();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-6 glass-morphism rounded-3xl rev-card group relative overflow-hidden ${task.completed ? 'opacity-50 grayscale-[0.8]' : ''}`}>
      {/* Background Glow */}
      <div className={`absolute top-0 left-0 w-1 h-full transition-all duration-300 ${task.completed ? 'bg-zinc-700' : 'bg-blue-600 group-hover:h-full group-hover:w-full group-hover:opacity-[0.03]'}`}></div>

      <div className="flex items-center justify-between gap-6 relative z-10">
        <div className="flex items-center gap-6 min-w-0">
          <button
            onClick={handleToggleComplete}
            disabled={loading}
            className={`flex-shrink-0 w-8 h-8 rounded-xl border-2 flex items-center justify-center transition-all ${task.completed
                ? 'bg-emerald-500 border-emerald-500 shadow-lg shadow-emerald-500/20'
                : 'border-white/10 hover:border-blue-500 group-hover:scale-110 bg-white/5'
              }`}
          >
            {task.completed && (
              <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={4} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>

          <div className="min-w-0">
            <h3 className={`text-lg font-bold tracking-tight transition-all ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>
              {task.title}
            </h3>
            {task.description && (
              <p className="text-sm text-gray-400 mt-1 font-light italic opacity-80 group-hover:opacity-100 transition-opacity">
                {task.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all transform translate-x-4 group-hover:translate-x-0">
          <button
            onClick={handleDelete}
            className="p-3 bg-red-500/10 hover:bg-red-500 hover:text-white text-red-400 rounded-xl transition-all"
            title="Terminate Protocol"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
