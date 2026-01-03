'use client';

import { useState } from 'react';
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DesignCanvasProps {
  currentImageUrl: string | null;
  originalImageUrl: string | null;
  compareMode?: boolean;
}

export function DesignCanvas({
  currentImageUrl,
  originalImageUrl,
  compareMode = false,
}: DesignCanvasProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!currentImageUrl) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-400">
          <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
            <svg
              className="w-12 h-12"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
          <p className="text-lg font-medium">No design yet</p>
          <p className="text-sm">Upload a room photo to get started</p>
        </div>
      </div>
    );
  }

  if (compareMode && originalImageUrl) {
    return (
      <div className="flex-1 relative bg-gray-900">
        <ReactCompareSlider
          itemOne={
            <ReactCompareSliderImage
              src={originalImageUrl}
              alt="Original"
              style={{ objectFit: 'contain' }}
            />
          }
          itemTwo={
            <ReactCompareSliderImage
              src={currentImageUrl}
              alt="Current Design"
              style={{ objectFit: 'contain' }}
            />
          }
          className="h-full"
        />
        <div className="absolute bottom-4 left-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
          Original
        </div>
        <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
          Current
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 relative bg-gray-50 flex items-center justify-center p-4">
      <img
        src={currentImageUrl}
        alt="Current Design"
        className={cn(
          'max-h-full max-w-full object-contain rounded-lg shadow-lg',
          'transition-transform duration-200'
        )}
      />

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={() => setIsFullscreen(true)}
          className="p-2 bg-white/90 rounded-lg shadow hover:bg-white transition-colors"
          title="Fullscreen"
        >
          <Maximize2 className="h-5 w-5 text-gray-700" />
        </button>
      </div>

      {/* Fullscreen modal */}
      {isFullscreen && (
        <div
          className="fixed inset-0 z-50 bg-black flex items-center justify-center"
          onClick={() => setIsFullscreen(false)}
        >
          <img
            src={currentImageUrl}
            alt="Current Design"
            className="max-h-screen max-w-screen object-contain"
          />
          <button
            onClick={() => setIsFullscreen(false)}
            className="absolute top-4 right-4 p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
          >
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
