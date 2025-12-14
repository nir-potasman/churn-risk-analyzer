import { User, Bot } from 'lucide-react';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  plan?: string[];
  steps?: string[];
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-2`}>
        <div className={`p-2 rounded-full ${isUser ? 'bg-blue-500' : 'bg-green-500'} text-white`}>
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>
        <div className={`p-3 rounded-lg ${isUser ? 'bg-blue-100' : 'bg-gray-100'}`}>
          <p className="whitespace-pre-wrap">{message.content}</p>
          
          {/* Display Plan if available (for debugging/transparency) */}
          {message.plan && message.plan.length > 0 && (
            <div className="mt-2 text-sm text-gray-600 border-t pt-2 border-gray-300">
              <p className="font-semibold text-xs uppercase tracking-wide mb-1">Agent Plan:</p>
              <ul className="list-decimal pl-4 space-y-1">
                {message.plan.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Display Execution Steps */}
          {message.steps && message.steps.length > 0 && (
            <div className="mt-2 text-sm text-gray-600 border-t pt-2 border-gray-300">
              <p className="font-semibold text-xs uppercase tracking-wide mb-1">Execution Log:</p>
              <ul className="list-disc pl-4 space-y-1">
                {message.steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

