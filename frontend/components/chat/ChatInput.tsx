'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { ImagePlus, Send, Mic, MicOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  onImageUpload: (file: File) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  onImageUpload,
  disabled,
  placeholder = "Describe what you'd like to change...",
}: ChatInputProps) {
  const [input, setInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageUpload(file);
      e.target.value = '';
    }
  };

  return (
    <div className="border-t bg-white p-4">
      <div className="flex items-end gap-2">
        {/* Image upload button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className={cn(
            'p-2 rounded-lg transition-colors',
            disabled
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
          )}
          title="Upload image"
        >
          <ImagePlus className="h-5 w-5" />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Text input */}
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={cn(
              'w-full resize-none rounded-xl border border-gray-200 px-4 py-3 pr-12',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
              'disabled:bg-gray-50 disabled:text-gray-400',
              'max-h-32'
            )}
            style={{
              minHeight: '48px',
              height: 'auto',
            }}
          />
        </div>

        {/* Send button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className={cn(
            'p-3 rounded-xl transition-colors',
            disabled || !input.trim()
              ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          )}
        >
          <Send className="h-5 w-5" />
        </button>
      </div>

      <p className="text-xs text-gray-400 mt-2 text-center">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
