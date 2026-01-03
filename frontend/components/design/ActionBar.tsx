'use client';

import { useState } from 'react';
import {
  Undo2,
  Redo2,
  GitCompare,
  CheckCircle,
  Download,
  FileText,
  ShoppingCart,
  Palette,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface ActionBarProps {
  canUndo: boolean;
  canRedo: boolean;
  compareMode: boolean;
  currentVersion: number;
  hasVersions: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onToggleCompare: () => void;
  onFinalize: () => void;
  onExport: (format: 'pdf' | 'shopping_list' | 'colors') => void;
}

export function ActionBar({
  canUndo,
  canRedo,
  compareMode,
  currentVersion,
  hasVersions,
  onUndo,
  onRedo,
  onToggleCompare,
  onFinalize,
  onExport,
}: ActionBarProps) {
  const [showExportMenu, setShowExportMenu] = useState(false);

  return (
    <div className="border-t bg-white px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onUndo}
            disabled={!canUndo}
            title="Undo"
          >
            <Undo2 className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={onRedo}
            disabled={!canRedo}
            title="Redo"
          >
            <Redo2 className="h-4 w-4" />
          </Button>

          <div className="w-px h-6 bg-gray-200 mx-2" />

          <Button
            variant={compareMode ? 'primary' : 'ghost'}
            size="sm"
            onClick={onToggleCompare}
            disabled={!hasVersions}
            title="Compare with original"
          >
            <GitCompare className="h-4 w-4 mr-1" />
            Compare
          </Button>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          {/* Export dropdown */}
          <div className="relative">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowExportMenu(!showExportMenu)}
              disabled={!hasVersions}
            >
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>

            {showExportMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowExportMenu(false)}
                />
                <div className="absolute right-0 bottom-full mb-2 w-48 bg-white rounded-lg shadow-lg border z-20">
                  <div className="p-1">
                    <button
                      onClick={() => {
                        onExport('pdf');
                        setShowExportMenu(false);
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                    >
                      <FileText className="h-4 w-4" />
                      PDF Report
                    </button>
                    <button
                      onClick={() => {
                        onExport('shopping_list');
                        setShowExportMenu(false);
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                    >
                      <ShoppingCart className="h-4 w-4" />
                      Shopping List
                    </button>
                    <button
                      onClick={() => {
                        onExport('colors');
                        setShowExportMenu(false);
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                    >
                      <Palette className="h-4 w-4" />
                      Color Palette
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={onFinalize}
            disabled={!hasVersions}
          >
            <CheckCircle className="h-4 w-4 mr-1" />
            Finalize
          </Button>
        </div>
      </div>

      {currentVersion > 0 && (
        <p className="text-xs text-gray-400 text-center mt-2">
          Current: Version {currentVersion}
        </p>
      )}
    </div>
  );
}
