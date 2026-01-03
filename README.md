# Interior Design AI

An AI-powered interior design application where users upload room photos, chat with AI to describe changes, and see their room transform visually in real-time.

![Interior Design AI](https://via.placeholder.com/800x400?text=Interior+Design+AI)

## Features

- **Chat-based design**: Describe changes in natural language
- **AI-powered generation**: Uses Claude for understanding + Stable Diffusion for images
- **Real-time visual feedback**: See design changes instantly
- **Version history**: Track all design iterations
- **Before/After comparison**: Slide to compare designs
- **Export for contractors**: PDF specifications with paint codes, furniture lists, and budget estimates

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14, Tailwind CSS, Zustand |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| AI | Anthropic Claude, Replicate (Stable Diffusion) |
| Storage | S3-compatible (AWS S3, Cloudflare R2) |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- API Keys:
  - [Anthropic API key](https://console.anthropic.com/)
  - [Replicate API token](https://replicate.com/)

### 1. Clone and setup

```bash
cd interior-design
```

### 2. Start the backend

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys

docker-compose up -d
```

Backend runs at: http://localhost:8000

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         THE CORE LOOP                           │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │  Upload  │    │   Chat   │    │    AI    │    │   See    │ │
│  │   Room   │───▶│  Change  │───▶│ Generates│───▶│  Result  │ │
│  │  Photo   │    │ Request  │    │  Design  │    │  Visual  │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                        │                               │       │
│                        └──────── Repeat ◀──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Example Conversation

1. **Upload**: User uploads a living room photo
2. **AI Responds**: "I see your living room with beige walls and a leather sofa. What would you like to change?"
3. **User**: "Make the walls sage green and add a modern rug"
4. **AI Generates**: New design image with sage green walls and modern rug
5. **User**: "Perfect! Add some plants"
6. **AI Generates**: Updated design with plants
7. **User**: "Finalize this"
8. **Export**: Download PDF specification for contractors

## Project Structure

```
interior-design/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/routes/     # API endpoints
│   │   ├── models/         # Database models
│   │   └── services/       # AI services
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── frontend/               # Next.js frontend
│   ├── app/               # Pages
│   ├── components/        # React components
│   ├── hooks/             # Custom hooks
│   └── lib/               # Utilities
│
└── AI_Interior_Design_App_Blueprint.md  # Full technical spec
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects` | POST | Create project |
| `/api/projects/{id}/upload` | POST | Upload room photo |
| `/api/projects/{id}/chat` | POST | Send chat message |
| `/api/projects/{id}/export` | POST | Export specifications |

## Export for Contractors

The app generates professional specifications including:

- **Paint codes**: Benjamin Moore, Sherwin Williams, Behr
- **Furniture list**: Dimensions, style, where to buy
- **Budget estimate**: Low-high range by category
- **Before/After images**: Visual comparison

## Configuration

### Backend (.env)

```env
ANTHROPIC_API_KEY=sk-ant-...
REPLICATE_API_TOKEN=r8_...
DATABASE_URL=postgresql+asyncpg://...
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Cost Estimates

| Service | Per Session |
|---------|-------------|
| Claude API | ~$0.02 |
| Image Generation | ~$0.40 |
| **Total** | **~$0.42** |

## Roadmap

- [x] Phase 1: Chat-based 2D design
- [ ] Phase 2: 3D visualization
- [ ] Phase 3: AR preview
- [ ] Furniture catalog integration
- [ ] Multi-room support

## License

MIT

## Contributing

Contributions welcome! Please read the contributing guidelines first.
