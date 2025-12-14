import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Loader2 } from 'lucide-react';
import { ChatMessage, Message } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // In production, use env var for URL. For local dev, localhost:8000 is fine.
      const response = await axios.post('http://localhost:8000/api/v1/chat', {
        message: userMessage
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        plan: response.data.plan,
        steps: response.data.steps
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-full max-w-4xl mx-auto p-4 flex flex-col h-full">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Stampli Churn Analyzer</h1>
            <p className="text-sm text-gray-500">Powered by Redshift & Bedrock Agents</p>
          </div>
        </header>

        <div className="flex-1 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col border border-gray-100">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-20">
                <p>Start by asking a question about customer churn.</p>
                <p className="text-sm mt-2">Example: "Who are the top 3 customers by revenue?"</p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}
            
            {isLoading && (
              <div className="flex justify-start animate-pulse">
                <div className="flex items-center gap-2 text-gray-500 bg-gray-50 p-3 rounded-lg">
                  <Loader2 className="animate-spin" size={18} />
                  <span className="text-sm">Analyzing data...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <ChatInput 
            input={input} 
            setInput={setInput} 
            isLoading={isLoading} 
            onSubmit={handleSubmit} 
          />
        </div>
      </div>
    </div>
  );
}

export default App;

