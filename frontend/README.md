# Interior Design AI - Frontend

Next.js frontend for the AI-powered interior design application.

## Features

- **Chat-based interface**: Natural conversation to modify designs
- **Real-time updates**: See design changes instantly
- **Version history**: Browse and compare all design iterations
- **Before/After comparison**: Slide to compare original vs current
- **Export**: Download PDF specifications for contractors

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **State**: Zustand
- **UI Components**: Custom + Lucide icons

## Quick Start

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure environment

```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local
```

### 3. Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Make sure backend is running

```bash
cd ../backend
docker-compose up -d
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page (project list)
│   ├── globals.css          # Global styles
│   └── design/
│       └── [projectId]/
│           └── page.tsx     # Design workspace
│
├── components/
│   ├── chat/
│   │   ├── ChatMessages.tsx # Chat message list
│   │   └── ChatInput.tsx    # Chat input with upload
│   ├── design/
│   │   ├── DesignCanvas.tsx # Image display + compare
│   │   ├── VersionHistory.tsx # Version thumbnails
│   │   └── ActionBar.tsx    # Undo/redo/export actions
│   └── ui/
│       ├── Button.tsx
│       └── Spinner.tsx
│
├── hooks/
│   └── useDesignStore.ts    # Zustand state store
│
├── lib/
│   ├── api.ts              # API client functions
│   └── utils.ts            # Utility functions
│
├── types/
│   └── index.ts            # TypeScript types
│
└── package.json
```

## Key Pages

### Home (`/`)
- List of all projects
- Create new project button
- Delete projects

### Design Workspace (`/design/[projectId]`)
- Split view: Chat (left) + Design (right)
- Upload room photo
- Chat to make changes
- Version history at bottom
- Export/finalize actions

## State Management

Using Zustand for simple, efficient state:

```typescript
const store = useDesignStore();

// Access state
store.currentImageUrl
store.messages
store.versions

// Actions
store.addMessage(message)
store.setCurrentImage(url, version)
store.toggleCompareMode()
```

## API Integration

All API calls go through `/lib/api.ts`:

```typescript
import * as api from '@/lib/api';

// Create project
const project = await api.createProject('My Room');

// Upload photo
const result = await api.uploadRoomPhoto(projectId, file);

// Send chat message
const response = await api.sendChatMessage(projectId, 'Make walls blue');

// Export PDF
const blob = await api.exportDesign(projectId, 'pdf');
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `/api` (proxied) |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |

## Development

### Code style
```bash
npm run lint
```

### Build for production
```bash
npm run build
npm start
```

### Deploy to Vercel
```bash
vercel
```

## License

MIT
