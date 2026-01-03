'use client';

import { Star, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DesignVersion } from '@/types';

interface VersionHistoryProps {
  versions: DesignVersion[];
  currentVersion: number;
  originalImageUrl: string | null;
  onSelectVersion: (version: number) => void;
  onToggleFavorite?: (version: number) => void;
}

export function VersionHistory({
  versions,
  currentVersion,
  originalImageUrl,
  onSelectVersion,
  onToggleFavorite,
}: VersionHistoryProps) {
  const allVersions = [
    // Original as version 0
    ...(originalImageUrl
      ? [
          {
            version_number: 0,
            image_url: originalImageUrl,
            thumbnail_url: originalImageUrl,
            is_original: true,
            is_favorite: false,
            is_final: false,
          },
        ]
      : []),
    ...versions.map((v) => ({
      ...v,
      is_original: false,
    })),
  ];

  if (allVersions.length === 0) {
    return null;
  }

  return (
    <div className="border-t bg-white p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">Design History</h3>
        <span className="text-xs text-gray-500">
          {versions.length} version{versions.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
        {allVersions.map((v) => (
          <button
            key={v.version_number}
            onClick={() => onSelectVersion(v.version_number)}
            className={cn(
              'relative flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden',
              'border-2 transition-all duration-200',
              'hover:border-primary-400',
              v.version_number === currentVersion
                ? 'border-primary-500 ring-2 ring-primary-200'
                : 'border-gray-200'
            )}
          >
            <img
              src={v.thumbnail_url || v.image_url}
              alt={v.is_original ? 'Original' : `Version ${v.version_number}`}
              className="w-full h-full object-cover"
            />

            {/* Version label */}
            <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs py-0.5 text-center">
              {v.is_original ? 'Original' : `v${v.version_number}`}
            </div>

            {/* Favorite star */}
            {!v.is_original && v.is_favorite && (
              <div className="absolute top-1 right-1">
                <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
              </div>
            )}

            {/* Final checkmark */}
            {!v.is_original && v.is_final && (
              <div className="absolute top-1 left-1 bg-green-500 rounded-full p-0.5">
                <Check className="h-3 w-3 text-white" />
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
