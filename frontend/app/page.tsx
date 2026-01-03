'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Trash2, Image as ImageIcon, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { formatDate } from '@/lib/utils';
import * as api from '@/lib/api';

interface Project {
  id: string;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
  has_room_photo: boolean;
  current_version: number | null;
  message_count: number;
}

export default function HomePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  // Load projects
  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await api.getProjects();
        setProjects(data);
      } catch (err) {
        console.error('Failed to load projects:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadProjects();
  }, []);

  // Create new project
  const handleCreateProject = useCallback(async () => {
    setIsCreating(true);
    try {
      const project = await api.createProject();
      router.push(`/design/${project.id}`);
    } catch (err) {
      console.error('Failed to create project:', err);
      setIsCreating(false);
    }
  }, [router]);

  // Delete project
  const handleDeleteProject = useCallback(
    async (e: React.MouseEvent, projectId: string) => {
      e.stopPropagation();
      if (!confirm('Are you sure you want to delete this project?')) return;

      try {
        await api.deleteProject(projectId);
        setProjects((prev) => prev.filter((p) => p.id !== projectId));
      } catch (err) {
        console.error('Failed to delete project:', err);
      }
    },
    []
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Interior Design AI
              </h1>
              <p className="text-gray-500 mt-1">
                Transform your room with AI-powered design
              </p>
            </div>
            <Button
              onClick={handleCreateProject}
              isLoading={isCreating}
              size="lg"
            >
              <Plus className="h-5 w-5 mr-2" />
              New Project
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Spinner size="lg" />
          </div>
        ) : projects.length === 0 ? (
          <EmptyState onCreateProject={handleCreateProject} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={() => router.push(`/design/${project.id}`)}
                onDelete={(e) => handleDeleteProject(e, project.id)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function EmptyState({ onCreateProject }: { onCreateProject: () => void }) {
  return (
    <div className="text-center py-16">
      <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-primary-50 flex items-center justify-center">
        <ImageIcon className="h-12 w-12 text-primary-500" />
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        No projects yet
      </h2>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">
        Create your first project to start redesigning your space with AI.
        Upload a room photo and chat to make changes.
      </p>
      <Button onClick={onCreateProject} size="lg">
        <Plus className="h-5 w-5 mr-2" />
        Create Your First Project
      </Button>
    </div>
  );
}

function ProjectCard({
  project,
  onClick,
  onDelete,
}: {
  project: Project;
  onClick: () => void;
  onDelete: (e: React.MouseEvent) => void;
}) {
  const statusColors = {
    in_progress: 'bg-yellow-100 text-yellow-800',
    finalized: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-800',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
    >
      {/* Thumbnail */}
      <div className="h-48 bg-gray-100 flex items-center justify-center">
        {project.has_room_photo ? (
          <div className="text-center text-gray-400">
            <ImageIcon className="h-12 w-12 mx-auto mb-2" />
            <span className="text-sm">
              {project.current_version
                ? `Version ${project.current_version}`
                : 'Original'}
            </span>
          </div>
        ) : (
          <div className="text-center text-gray-400">
            <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-30" />
            <span className="text-sm">No image</span>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-medium text-gray-900 truncate flex-1">
            {project.name}
          </h3>
          <button
            onClick={onDelete}
            className="p-1 hover:bg-gray-100 rounded ml-2 text-gray-400 hover:text-red-500 transition-colors"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
          <span className="flex items-center gap-1">
            <MessageSquare className="h-4 w-4" />
            {project.message_count}
          </span>
          <span
            className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              statusColors[project.status as keyof typeof statusColors]
            }`}
          >
            {project.status.replace('_', ' ')}
          </span>
        </div>

        <p className="text-xs text-gray-400">
          Updated {formatDate(project.updated_at)}
        </p>
      </div>
    </div>
  );
}
