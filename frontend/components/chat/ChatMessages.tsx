'use client';

import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/Spinner';
import type { Message } from '@/types';

interface ChatMessagesProps {
  messages: Message[];
  isLoading?: boolean;
  onImageClick?: (imageUrl: string) => void;
}

export function ChatMessages({ messages, isLoading, onImageClick }: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && !isLoading && (
        <div className="text-center text-gray-500 py-8">
          <p>Upload a room photo to get started!</p>
        </div>
      )}

      {messages.map((message) => (
        <ChatBubble
          key={message.id}
          message={message}
          onImageClick={onImageClick}
        />
      ))}

      {isLoading && (
        <div className="flex items-center gap-2 text-gray-500">
          <Spinner size="sm" />
          <span>Designing your changes...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

interface ChatBubbleProps {
  message: Message;
  onImageClick?: (imageUrl: string) => void;
}

function ChatBubble({ message, onImageClick }: ChatBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[85%] rounded-2xl px-4 py-3',
          isUser
            ? 'bg-primary-600 text-white rounded-br-md'
            : 'bg-gray-100 text-gray-900 rounded-bl-md'
        )}
      >
        {/* Uploaded image (user) */}
        {message.uploaded_image_url && (
          <img
            src={message.uploaded_image_url}
            alt="Uploaded room"
            className="rounded-lg mb-2 max-w-full cursor-pointer hover:opacity-90 transition-opacity"
            onClick={() => onImageClick?.(message.uploaded_image_url!)}
          />
        )}

        {/* Generated image (assistant) */}
        {message.image_url && (
          <div className="mb-2">
            <img
              src={message.image_url}
              alt="Generated design"
              className="rounded-lg max-w-full cursor-pointer hover:opacity-90 transition-opacity"
              onClick={() => onImageClick?.(message.image_url!)}
            />
            {message.version_number && (
              <span className="text-xs opacity-70 mt-1 inline-block">
                Version {message.version_number}
              </span>
            )}
          </div>
        )}

        {/* Message text */}
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
