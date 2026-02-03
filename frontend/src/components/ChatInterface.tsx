import { useState, useRef, useEffect } from "react";
import { api } from "../services/api";

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ChatInterfaceProps {
  userId?: number;
}

export default function ChatInterface({ userId: propUserId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Interactive System Assistant initialized. Awaiting task commands.',
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await api.chat(inputValue, propUserId || 1);
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error(error);
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Neural processing failure. Please re-authenticate.",
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/40">
      {/* Dynamic Terminal Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[90%] relative ${message.sender === 'user' ? 'text-right' : 'text-left'}`}>
              <div className={`text-[9px] uppercase tracking-[0.3em] font-bold mb-3 ${message.sender === 'user' ? 'text-blue-400' : 'text-purple-400'}`}>
                {message.sender === 'user' ? 'Client Request' : 'System Intelligence'}
              </div>
              <div className={`p-5 rounded-2xl glass-morphism relative border ${message.sender === 'user'
                ? 'bg-blue-600/10 border-blue-500/20 rounded-tr-none'
                : 'bg-white/5 border-white/10 rounded-tl-none'
                }`}>
                <p className="text-sm leading-relaxed text-gray-200 font-light tracking-wide">{message.text}</p>
                <div className="mt-4 flex items-center gap-1.5 grayscale opacity-30">
                  <span className="text-[8px] font-mono">{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex gap-2">
              <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></div>
              <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
              <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce [animation-delay:0.4s]"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Futuristic Command Input */}
      <div className="p-8 border-t border-white/5 bg-black/60 relative">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-blue-500/20 to-transparent"></div>
        <form onSubmit={handleSendMessage} className="relative group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Execute protocol... (e.g., 'Add task to fix bug')"
            className="w-full pl-6 pr-14 py-4 bg-white/5 border border-white/10 rounded-2xl focus:outline-none text-sm text-white placeholder:text-gray-600 transition-all font-light caret-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-3 bg-blue-600 rounded-xl text-white hover:bg-blue-500 transition-all shadow-lg active:scale-90 disabled:opacity-20"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}