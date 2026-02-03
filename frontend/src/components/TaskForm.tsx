import { useState } from "react";
import { api } from "../services/api";

interface TaskFormProps {
  userId: number;
  onTaskCreated: () => void;
}

export default function TaskForm({ userId, onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || loading) return;

    setLoading(true);
    try {
      await api.createTask(userId, { title, description });
      setTitle("");
      setDescription("");
      onTaskCreated();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 bg-transparent">
      <form onSubmit={handleSubmit} className="flex flex-col space-y-8">
        <div className="space-y-4">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Initialize new task protocol..."
            className="w-full bg-transparent border-none focus:ring-0 focus:outline-none text-2xl font-bold text-white placeholder:text-[#1a1a1d] transition-all tracking-tight caret-blue-500"
            disabled={loading}
          />

          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detailed metadata (Optional)"
            className="w-full bg-transparent border-none focus:ring-0 focus:outline-none text-sm text-gray-400 placeholder:text-[#1a1a1d] font-light resize-none h-12 caret-blue-500"
            disabled={loading}
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-gray-600">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full border border-white/5 bg-white/5">
              <div className="w-1 h-1 bg-blue-400 rounded-full"></div>
              <span className="text-[10px] font-bold uppercase tracking-widest">Normal Priority</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full border border-white/5 bg-white/5">
              <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
              <span className="text-[10px] font-bold uppercase tracking-widest">Single User</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={!title.trim() || loading}
            className="group flex items-center gap-3 py-3 px-8 bg-white text-black font-bold rounded-2xl hover:bg-blue-600 hover:text-white transition-all shadow-xl active:scale-95 disabled:opacity-20 disabled:grayscale"
          >
            {loading ? (
              <span className="text-xs uppercase tracking-widest">Initiating...</span>
            ) : (
              <>
                <span className="text-xs uppercase tracking-widest">Add Protocol</span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
