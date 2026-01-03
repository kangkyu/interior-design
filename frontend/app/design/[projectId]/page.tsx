'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Settings } from 'lucide-react';
import Link from 'next/link';

import { ChatMessages } from '@/components/chat/ChatMessages';
import { ChatInput } from '@/components/chat/ChatInput';
import { DesignCanvas } from '@/components/design/DesignCanvas';
import { VersionHistory } from '@/components/design/VersionHistory';
import { ActionBar } from '@/components/design/ActionBar';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { useDesignStore } from '@/hooks/useDesignStore';
import { downloadBlob } from '@/lib/utils';
import * as api from '@/lib/api';
import type { Message, DesignVersion } from '@/types';

export default function DesignPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const {
    projectName,
    originalImageUrl,
    currentImageUrl,
    currentVersion,
    messages,
    isLoading,
    versions,
    compareMode,
    setProject,
    setOriginalImage,
    setCurrentImage,
    setRoomAnalysis,
    addMessage,
    setMessages,
    setLoading,
    setVersions,
    addVersion,
    toggleCompareMode,
    reset,
  } = useDesignStore();

  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load project data
  useEffect(() => {
    async function loadProject() {
      try {
        setIsInitializing(true);
        setError(null);

        // Get project details
        const project = await api.getProject(projectId);
        setProject(projectId, project.name);

        if (project.original_image_url) {
          setOriginalImage(project.original_image_url);
        }

        if (project.current_image_url) {
          setCurrentImage(
            project.current_image_url,
            project.current_version || 0
          );
        }

        if (project.room_analysis) {
          setRoomAnalysis(project.room_analysis as any);
        }

        // Get chat history
        const history = await api.getChatHistory(projectId);
        setMessages(history as Message[]);

        // Get versions
        const versionList = await api.getVersions(projectId);
        setVersions(versionList as DesignVersion[]);
      } catch (err) {
        console.error('Failed to load project:', err);
        setError('Failed to load project. Please try again.');
      } finally {
        setIsInitializing(false);
      }
    }

    loadProject();

    return () => {
      reset();
    };
  }, [projectId]);

  // Handle sending a chat message
  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message immediately
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      addMessage(userMessage);
      setLoading(true);

      try {
        const response = await api.sendChatMessage(projectId, content);

        // Add assistant response
        const assistantMessage: Message = {
          id: `response-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          image_url: response.image_url || undefined,
          version_number: response.version || undefined,
          created_at: new Date().toISOString(),
        };
        addMessage(assistantMessage);

        // Update current image if we got a new design
        if (response.image_url && response.version) {
          setCurrentImage(response.image_url, response.version);

          // Add to versions
          const newVersion: DesignVersion = {
            id: `version-${response.version}`,
            version_number: response.version,
            image_url: response.image_url,
            is_favorite: false,
            is_final: false,
            created_at: new Date().toISOString(),
          };
          addVersion(newVersion);
        }
      } catch (err) {
        console.error('Failed to send message:', err);
        // Add error message
        addMessage({
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          created_at: new Date().toISOString(),
        });
      } finally {
        setLoading(false);
      }
    },
    [projectId, isLoading]
  );

  // Handle image upload
  const handleImageUpload = useCallback(
    async (file: File) => {
      setLoading(true);

      try {
        const response = await api.uploadRoomPhoto(projectId, file);

        // Update images
        setOriginalImage(response.image_url);
        setCurrentImage(response.image_url, 0);

        if (response.analysis) {
          setRoomAnalysis(response.analysis as any);
        }

        // Add assistant message with analysis
        addMessage({
          id: `analysis-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          created_at: new Date().toISOString(),
        });
      } catch (err) {
        console.error('Failed to upload image:', err);
        addMessage({
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Failed to upload image. Please try again with a clear room photo.',
          created_at: new Date().toISOString(),
        });
      } finally {
        setLoading(false);
      }
    },
    [projectId]
  );

  // Handle version selection
  const handleSelectVersion = useCallback(
    async (versionNumber: number) => {
      try {
        const image = await api.getCurrentImage(projectId, versionNumber);
        setCurrentImage(image.image_url, versionNumber);
      } catch (err) {
        console.error('Failed to load version:', err);
      }
    },
    [projectId]
  );

  // Handle export
  const handleExport = useCallback(
    async (format: 'pdf' | 'shopping_list' | 'colors') => {
      try {
        if (format === 'pdf') {
          const blob = await api.exportDesign(projectId, format);
          downloadBlob(blob as Blob, `${projectName || 'design'}-specification.pdf`);
        } else {
          const data = await api.exportDesign(projectId, format);
          // For other formats, you might want to show a modal or download JSON
          console.log('Export data:', data);
          alert('Export data logged to console. PDF export downloads automatically.');
        }
      } catch (err) {
        console.error('Failed to export:', err);
        alert('Failed to export. Make sure you have finalized a design first.');
      }
    },
    [projectId, projectName]
  );

  // Handle finalize
  const handleFinalize = useCallback(async () => {
    if (currentVersion === 0) {
      alert('Please make some changes before finalizing.');
      return;
    }

    try {
      await api.finalizeVersion(projectId, currentVersion);
      alert(`Version ${currentVersion} has been finalized! You can now export the specifications.`);
      // Refresh versions
      const versionList = await api.getVersions(projectId);
      setVersions(versionList as DesignVersion[]);
    } catch (err) {
      console.error('Failed to finalize:', err);
      alert('Failed to finalize design. Please try again.');
    }
  }, [projectId, currentVersion]);

  if (isInitializing) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <Spinner size="lg" className="mx-auto mb-4" />
          <p className="text-gray-500">Loading project...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={() => router.push('/')}>Go Home</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </Link>
          <h1 className="font-semibold text-gray-900">
            {projectName || 'Untitled Project'}
          </h1>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <Settings className="h-5 w-5 text-gray-600" />
        </button>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Chat */}
        <div className="w-1/2 border-r flex flex-col bg-white">
          <ChatMessages
            messages={messages}
            isLoading={isLoading}
            onImageClick={(url) => setCurrentImage(url, currentVersion)}
          />
          <ChatInput
            onSend={handleSendMessage}
            onImageUpload={handleImageUpload}
            disabled={isLoading}
            placeholder={
              originalImageUrl
                ? "Describe what you'd like to change..."
                : 'Upload a room photo to get started'
            }
          />
        </div>

        {/* Right panel - Design */}
        <div className="w-1/2 flex flex-col bg-gray-50">
          <DesignCanvas
            currentImageUrl={currentImageUrl}
            originalImageUrl={originalImageUrl}
            compareMode={compareMode}
          />
          <VersionHistory
            versions={versions}
            currentVersion={currentVersion}
            originalImageUrl={originalImageUrl}
            onSelectVersion={handleSelectVersion}
          />
          <ActionBar
            canUndo={currentVersion > 1}
            canRedo={false}
            compareMode={compareMode}
            currentVersion={currentVersion}
            hasVersions={versions.length > 0}
            onUndo={() => handleSelectVersion(Math.max(0, currentVersion - 1))}
            onRedo={() => {}}
            onToggleCompare={toggleCompareMode}
            onFinalize={handleFinalize}
            onExport={handleExport}
          />
        </div>
      </div>
    </div>
  );
}
