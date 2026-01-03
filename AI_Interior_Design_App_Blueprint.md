# AI-Powered Interior Design App - Technical Blueprint

An AI-powered interior design application where users upload room photos, chat with AI to describe changes, and see their room transform visually in real-time.

---

## Core Feature: Chat & See

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE CORE LOOP                                   │
│                                                                         │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐  │
│    │  Upload  │      │   Chat   │      │    AI    │      │   See    │  │
│    │  Room    │─────▶│  Change  │─────▶│ Generates│─────▶│  Result  │  │
│    │  Photo   │      │  Request │      │  Design  │      │  Visual  │  │
│    └──────────┘      └──────────┘      └──────────┘      └──────────┘  │
│                            │                                   │        │
│                            └───────────── Repeat ◀─────────────┘        │
│                                                                         │
│    "Make walls blue"  ───▶  [AI Processing]  ───▶  [Updated Room Image] │
│    "Add wooden floor" ───▶  [AI Processing]  ───▶  [Updated Room Image] │
│    "More plants"      ───▶  [AI Processing]  ───▶  [Updated Room Image] │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### User Experience Flow

```
1. USER UPLOADS ROOM PHOTO
   └── "Here's my living room"

2. AI ANALYZES & RESPONDS
   └── "I see your living room with gray walls, a beige sofa,
        and hardwood floors. What would you like to change?"

3. USER CHATS THEIR REQUEST
   └── "Make the walls sage green"

4. AI GENERATES & SHOWS
   └── [New image with sage green walls]
   └── "Here's your room with sage green walls.
        What else would you like to adjust?"

5. USER CONTINUES CHATTING
   └── "Add a modern leather sofa"
   └── "Make it more bohemian"
   └── "I like it! Final."
```

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐  │
│  │      CHAT PANEL         │  │      VISUAL PANEL           │  │
│  │                         │  │                             │  │
│  │  [Upload Photo]         │  │  ┌─────────────────────┐   │  │
│  │                         │  │  │                     │   │  │
│  │  AI: I see your room... │  │  │   Current Design    │   │  │
│  │                         │  │  │      Image          │   │  │
│  │  You: Make walls blue   │  │  │                     │   │  │
│  │                         │  │  └─────────────────────┘   │  │
│  │  AI: Here's your room   │  │                             │  │
│  │      with blue walls... │  │  [Original] [v1] [v2] [v3]  │  │
│  │                         │  │                             │  │
│  │  [Type message...]  🎤  │  │  [Compare] [Undo] [Export]  │  │
│  └─────────────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                         │
│  Chat Interface + Image Display + Version History               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Chat Handler │  │ Image Upload │  │ Session Manager      │  │
│  │              │  │ & Analysis   │  │ (Design History)     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘  │
│         │                 │                                     │
│         ▼                 ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   AI ORCHESTRATOR                        │   │
│  │                                                          │   │
│  │  1. Understand chat message (Claude/GPT)                 │   │
│  │  2. Determine what to change                             │   │
│  │  3. Generate new design (Stable Diffusion/Flux)          │   │
│  │  4. Return image + conversational response               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Claude API   │  │ Replicate    │  │ Cloud Storage        │  │
│  │ (Chat + AI)  │  │ (Image Gen)  │  │ (S3/R2)              │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

# PHASE 1: Chat-Based 2D Design System

## 1.1 The Chat Experience

### Chat Message Types

| Type | From | Content |
|------|------|---------|
| **Image Upload** | User | Room photo |
| **Text Message** | User | Design request ("make walls blue") |
| **Voice Message** | User | Audio → transcribed to text |
| **Analysis Response** | AI | Description of current room |
| **Design Response** | AI | New image + explanation |
| **Clarification** | AI | Question when request is ambiguous |

### Example Conversation

```
┌─────────────────────────────────────────────────────────────────┐
│ USER                                                            │
│ ┌─────────────────────────────────────┐                        │
│ │ [📷 living_room.jpg]                │                        │
│ │ Here's my living room. I want to    │                        │
│ │ modernize it.                       │                        │
│ └─────────────────────────────────────┘                        │
│                                                                 │
│                               AI                                │
│               ┌─────────────────────────────────────┐          │
│               │ I can see your living room! It has: │          │
│               │ • Beige walls                       │          │
│               │ • Brown leather sofa                │          │
│               │ • Traditional wooden furniture      │          │
│               │ • Warm lighting                     │          │
│               │                                     │          │
│               │ For a modern look, I can help with: │          │
│               │ • Neutral/cool wall colors          │          │
│               │ • Minimalist furniture              │          │
│               │ • Clean lines                       │          │
│               │                                     │          │
│               │ What would you like to change first?│          │
│               └─────────────────────────────────────┘          │
│                                                                 │
│ USER                                                            │
│ ┌─────────────────────────────────────┐                        │
│ │ Change the walls to white and add   │                        │
│ │ a gray sectional sofa               │                        │
│ └─────────────────────────────────────┘                        │
│                                                                 │
│                               AI                                │
│               ┌─────────────────────────────────────┐          │
│               │ [🖼️ Generated Design Image]         │          │
│               │                                     │          │
│               │ Here's your room with:              │          │
│               │ ✓ Crisp white walls                 │          │
│               │ ✓ Modern gray sectional sofa        │          │
│               │                                     │          │
│               │ The white walls really open up the  │          │
│               │ space! Would you like to:           │          │
│               │ • Change the flooring?              │          │
│               │ • Add some accent pieces?           │          │
│               │ • Adjust the lighting?              │          │
│               └─────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1.2 Image Upload & Room Understanding

### Upload Flow

```
User uploads photo
       │
       ▼
┌──────────────────┐
│ Validate Image   │ ── Invalid ──▶ "Please upload a clear room photo"
│ (is it a room?)  │
└────────┬─────────┘
         │ Valid
         ▼
┌──────────────────┐
│ Analyze Room     │
│ (Claude Vision)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Generate Maps    │
│ • Depth map      │
│ • Segmentation   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Store & Respond  │ ──▶ "I see your [room_type] with..."
└──────────────────┘
```

### Room Analysis Prompt (Claude Vision)

```python
ROOM_ANALYSIS_PROMPT = """
Analyze this room photo and provide:

1. Room type (living room, bedroom, kitchen, etc.)
2. Current furniture and decor items
3. Wall colors
4. Floor type and color
5. Lighting conditions
6. Current style (modern, traditional, minimalist, etc.)
7. Notable features (windows, doors, fireplace, etc.)

Respond conversationally, as if you're an interior designer
meeting a client for the first time.
"""
```

### Analysis Response Structure

```json
{
  "room_type": "living_room",
  "analysis": {
    "furniture": ["beige sofa", "wooden coffee table", "bookshelf"],
    "walls": {"color": "cream", "hex": "#F5F5DC"},
    "floor": {"type": "hardwood", "color": "medium brown"},
    "lighting": "natural light from large window",
    "style": "traditional",
    "features": ["large window on left", "fireplace"]
  },
  "conversation_response": "I can see your cozy living room! You have cream-colored walls, a comfortable beige sofa, and beautiful hardwood floors. The natural light from that large window is lovely. What changes are you thinking about?"
}
```

---

## 1.3 Chat-to-Design Pipeline

### How Chat Becomes an Image

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CHAT-TO-DESIGN PIPELINE                             │
│                                                                         │
│  USER MESSAGE                                                           │
│  "Make the walls sage green and add a modern rug"                       │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ STEP 1: UNDERSTAND (Claude/GPT)                                  │   │
│  │                                                                  │   │
│  │ Input:                                                           │   │
│  │ - User message                                                   │   │
│  │ - Room analysis (from upload)                                    │   │
│  │ - Current design state                                           │   │
│  │ - Conversation history                                           │   │
│  │                                                                  │   │
│  │ Output:                                                          │   │
│  │ {                                                                │   │
│  │   "changes": [                                                   │   │
│  │     {"element": "walls", "action": "change_color",               │   │
│  │      "value": "sage green"},                                     │   │
│  │     {"element": "rug", "action": "add",                          │   │
│  │      "style": "modern", "location": "center"}                    │   │
│  │   ],                                                             │   │
│  │   "generation_prompt": "living room with sage green walls,       │   │
│  │                         modern geometric rug in center..."       │   │
│  │ }                                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ STEP 2: GENERATE (Stable Diffusion / Flux)                       │   │
│  │                                                                  │   │
│  │ Inputs:                                                          │   │
│  │ - Current room image (original or last generated)                │   │
│  │ - Depth map (to preserve room structure)                         │   │
│  │ - Generated prompt from Step 1                                   │   │
│  │                                                                  │   │
│  │ Process:                                                         │   │
│  │ - Use ControlNet to maintain room layout                         │   │
│  │ - Use img2img or inpainting based on change scope                │   │
│  │                                                                  │   │
│  │ Output:                                                          │   │
│  │ - New design image                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ STEP 3: RESPOND (Claude/GPT)                                     │   │
│  │                                                                  │   │
│  │ Generate conversational response:                                │   │
│  │ "Here's your room with sage green walls - such a calming         │   │
│  │  color choice! I've added a modern geometric rug that            │   │
│  │  complements the new wall color. What do you think?"             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  DISPLAY TO USER                                                        │
│  [New Image] + [AI Message]                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### The AI Orchestrator (Core Logic)

```python
# app/services/orchestrator.py

class DesignOrchestrator:
    """
    The brain of the app - takes chat input, produces design output
    """

    def __init__(self):
        self.claude = anthropic.Anthropic()
        self.image_generator = ImageGenerator()

    async def process_message(
        self,
        user_message: str,
        session: DesignSession
    ) -> DesignResponse:
        """
        Main entry point - process user's chat message
        """

        # Step 1: Understand what user wants
        understanding = await self.understand_request(
            message=user_message,
            room_analysis=session.room_analysis,
            current_design=session.current_design,
            history=session.conversation_history
        )

        # Step 2: Check if we need clarification
        if understanding.needs_clarification:
            return DesignResponse(
                type="clarification",
                message=understanding.clarification_question,
                image=None
            )

        # Step 3: Generate new design
        new_image = await self.image_generator.generate(
            base_image=session.current_image,
            depth_map=session.depth_map,
            prompt=understanding.generation_prompt,
            change_type=understanding.change_type
        )

        # Step 4: Save new state
        session.add_design_state(new_image, understanding)

        # Step 5: Generate response message
        response_message = await self.generate_response(
            changes_made=understanding.changes,
            new_image=new_image
        )

        return DesignResponse(
            type="design",
            message=response_message,
            image=new_image.url,
            version=session.current_version
        )

    async def understand_request(
        self,
        message: str,
        room_analysis: dict,
        current_design: dict,
        history: list
    ) -> Understanding:
        """
        Use Claude to understand what the user wants
        """

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=UNDERSTANDING_SYSTEM_PROMPT,
            messages=[
                *history,
                {
                    "role": "user",
                    "content": f"""
                    Room context: {json.dumps(room_analysis)}
                    Current design state: {json.dumps(current_design)}

                    User says: "{message}"

                    What changes should we make? Respond in JSON.
                    """
                }
            ]
        )

        return Understanding.parse(response.content[0].text)
```

### Understanding System Prompt

```python
UNDERSTANDING_SYSTEM_PROMPT = """
You are an AI interior design assistant. Your job is to understand
what design changes the user wants and translate them into actionable
instructions for image generation.

Given the user's message, determine:

1. CHANGES: What specific elements to modify
   - walls, floor, ceiling, furniture, lighting, decor, style

2. CHANGE_TYPE: How significant is the change?
   - "minor": Color/material change only (use low denoising)
   - "moderate": Adding/removing items (use medium denoising)
   - "major": Complete style overhaul (use high denoising)

3. GENERATION_PROMPT: A detailed prompt for image generation
   - Include all visible elements
   - Describe the requested changes specifically
   - Maintain elements that should stay the same

4. NEEDS_CLARIFICATION: Is the request ambiguous?
   - If yes, provide a natural question to ask

Respond ONLY in this JSON format:
{
  "changes": [
    {"element": "walls", "action": "change_color", "value": "sage green"}
  ],
  "change_type": "minor",
  "generation_prompt": "Interior photo of living room, sage green walls...",
  "needs_clarification": false,
  "clarification_question": null
}
"""
```

---

## 1.4 Image Generation

### Generation Modes

| Mode | When to Use | Denoising | ControlNet Weight |
|------|-------------|-----------|-------------------|
| **Minor Edit** | Color/material changes | 0.3-0.4 | 0.9 |
| **Moderate Edit** | Add/remove furniture | 0.5-0.6 | 0.8 |
| **Major Edit** | Style overhaul | 0.7-0.8 | 0.7 |
| **Inpainting** | Change specific item | 0.8-0.9 | N/A |

### Image Generator Service

```python
# app/services/image_generator.py

import replicate

class ImageGenerator:

    async def generate(
        self,
        base_image: str,      # URL or bytes
        depth_map: str,       # URL or bytes
        prompt: str,
        change_type: str      # minor, moderate, major
    ) -> GeneratedImage:

        # Select parameters based on change type
        params = self.get_params(change_type)

        # Generate using Replicate (Stable Diffusion XL + ControlNet)
        output = replicate.run(
            "stability-ai/sdxl:latest",
            input={
                "image": base_image,
                "prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "strength": params["denoising"],
                "controlnet_conditioning_scale": params["controlnet_weight"],
                "control_image": depth_map,
            }
        )

        return GeneratedImage(
            url=output[0],
            prompt=prompt,
            params=params
        )

    def get_params(self, change_type: str) -> dict:
        return {
            "minor": {"denoising": 0.35, "controlnet_weight": 0.9},
            "moderate": {"denoising": 0.55, "controlnet_weight": 0.8},
            "major": {"denoising": 0.75, "controlnet_weight": 0.7},
        }[change_type]


NEGATIVE_PROMPT = """
blurry, distorted, low quality, cartoon, painting,
unrealistic proportions, watermark, text, bad lighting,
oversaturated, undersaturated
"""
```

---

## 1.5 Frontend Implementation

### Tech Stack

```
Next.js 14 (App Router)
├── Tailwind CSS (styling)
├── Zustand (state management)
├── Socket.io (real-time updates)
└── react-media-recorder (optional voice input)
```

### Main Page Layout

```typescript
// app/design/[projectId]/page.tsx

export default function DesignPage({ params }) {
  return (
    <div className="flex h-screen">
      {/* Left Panel - Chat */}
      <div className="w-1/2 border-r flex flex-col">
        <ChatHeader />
        <ChatMessages />
        <ChatInput />
      </div>

      {/* Right Panel - Visual */}
      <div className="w-1/2 flex flex-col">
        <DesignCanvas />
        <VersionHistory />
        <ActionBar />
      </div>
    </div>
  );
}
```

### Chat Component

```typescript
// components/ChatMessages.tsx

export function ChatMessages() {
  const { messages, isGenerating } = useDesignStore();

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg) => (
        <ChatBubble key={msg.id} message={msg} />
      ))}

      {isGenerating && (
        <div className="flex items-center gap-2 text-gray-500">
          <Spinner />
          <span>Designing your changes...</span>
        </div>
      )}
    </div>
  );
}

function ChatBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg p-3 ${
          isUser
            ? "bg-blue-500 text-white"
            : "bg-gray-100 text-gray-900"
        }`}
      >
        {/* If message has an image */}
        {message.image && (
          <img
            src={message.image}
            alt="Design"
            className="rounded mb-2 cursor-pointer"
            onClick={() => showFullImage(message.image)}
          />
        )}

        {/* Message text */}
        <p>{message.content}</p>
      </div>
    </div>
  );
}
```

### Chat Input with Voice Option

```typescript
// components/ChatInput.tsx

export function ChatInput() {
  const [input, setInput] = useState("");
  const { sendMessage, uploadImage } = useDesignStore();

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="border-t p-4">
      <div className="flex items-center gap-2">
        {/* Image upload */}
        <button onClick={uploadImage} className="p-2 hover:bg-gray-100 rounded">
          <ImageIcon />
        </button>

        {/* Text input */}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Describe what you'd like to change..."
          className="flex-1 border rounded-lg px-4 py-2"
        />

        {/* Voice input (optional) */}
        <VoiceButton />

        {/* Send */}
        <button
          onClick={handleSend}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg"
        >
          Send
        </button>
      </div>
    </div>
  );
}
```

### Design Canvas (Right Panel)

```typescript
// components/DesignCanvas.tsx

export function DesignCanvas() {
  const { currentImage, originalImage, compareMode } = useDesignStore();

  if (compareMode) {
    return (
      <ReactCompareSlider
        itemOne={<img src={originalImage} alt="Original" />}
        itemTwo={<img src={currentImage} alt="Current" />}
      />
    );
  }

  return (
    <div className="flex-1 flex items-center justify-center bg-gray-50 p-4">
      {currentImage ? (
        <img
          src={currentImage}
          alt="Current Design"
          className="max-h-full max-w-full object-contain rounded-lg shadow-lg"
        />
      ) : (
        <UploadPrompt />
      )}
    </div>
  );
}
```

### Version History

```typescript
// components/VersionHistory.tsx

export function VersionHistory() {
  const { versions, currentVersion, setVersion } = useDesignStore();

  return (
    <div className="border-t p-4">
      <h3 className="text-sm font-medium mb-2">Design History</h3>
      <div className="flex gap-2 overflow-x-auto">
        {versions.map((v, i) => (
          <button
            key={v.id}
            onClick={() => setVersion(i)}
            className={`flex-shrink-0 w-16 h-16 rounded border-2
              ${i === currentVersion ? "border-blue-500" : "border-gray-200"}`}
          >
            <img
              src={v.thumbnail}
              alt={`Version ${i}`}
              className="w-full h-full object-cover rounded"
            />
          </button>
        ))}
      </div>
    </div>
  );
}
```

---

## 1.6 Backend Implementation

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment config
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── projects.py     # Project CRUD
│   │   │   ├── chat.py         # Chat endpoint
│   │   │   └── images.py       # Image upload/export
│   │   └── websocket.py        # Real-time updates
│   │
│   ├── services/
│   │   ├── orchestrator.py     # Main AI logic
│   │   ├── room_analyzer.py    # Vision AI analysis
│   │   ├── image_generator.py  # SD/Flux generation
│   │   └── storage.py          # S3/R2 storage
│   │
│   └── models/
│       ├── database.py         # SQLAlchemy models
│       └── schemas.py          # Pydantic schemas
│
├── requirements.txt
└── Dockerfile
```

### Chat API Endpoint

```python
# app/api/routes/chat.py

from fastapi import APIRouter, WebSocket
from app.services.orchestrator import DesignOrchestrator

router = APIRouter()
orchestrator = DesignOrchestrator()

@router.post("/projects/{project_id}/chat")
async def send_message(
    project_id: str,
    message: ChatMessage,
    session: DesignSession = Depends(get_session)
):
    """
    Process a chat message and return design response
    """
    response = await orchestrator.process_message(
        user_message=message.content,
        session=session
    )

    return {
        "type": response.type,
        "message": response.message,
        "image_url": response.image,
        "version": response.version
    }


@router.websocket("/projects/{project_id}/ws")
async def websocket_chat(websocket: WebSocket, project_id: str):
    """
    WebSocket for real-time chat and generation progress
    """
    await websocket.accept()
    session = await get_or_create_session(project_id)

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                # Send "thinking" status
                await websocket.send_json({
                    "type": "status",
                    "status": "understanding"
                })

                # Process message
                response = await orchestrator.process_message(
                    user_message=data["content"],
                    session=session
                )

                # Send response
                await websocket.send_json({
                    "type": "response",
                    "message": response.message,
                    "image_url": response.image,
                    "version": response.version
                })

    except WebSocketDisconnect:
        pass
```

### Database Schema

```sql
-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Room photos (original uploads)
CREATE TABLE room_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    image_url TEXT NOT NULL,
    analysis JSONB,           -- Room analysis from Vision AI
    depth_map_url TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Chat messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    role VARCHAR(20),         -- 'user' or 'assistant'
    content TEXT,
    image_url TEXT,           -- For generated designs
    version_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Design versions
CREATE TABLE design_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    version_number INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,
    prompt_used TEXT,
    changes JSONB,            -- What was changed
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 1.7 API Endpoints Summary

```yaml
# Projects
POST   /api/projects              # Create new project
GET    /api/projects              # List projects
GET    /api/projects/{id}         # Get project with history

# Images
POST   /api/projects/{id}/upload  # Upload room photo
GET    /api/projects/{id}/image   # Get current design

# Chat
POST   /api/projects/{id}/chat    # Send message, get response
GET    /api/projects/{id}/history # Get chat history

# Versions
GET    /api/projects/{id}/versions         # Get all versions
POST   /api/projects/{id}/versions/{n}/set # Go to specific version

# Export
POST   /api/projects/{id}/export  # Export final design
```

---

## 1.8 Export for Contractors & Designers

The final deliverable isn't just a pretty picture - it's an **actionable specification** that users can hand to contractors, painters, furniture stores, and interior designers.

### What Gets Exported

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DESIGN SPECIFICATION REPORT                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  BEFORE / AFTER IMAGES                                          │   │
│  │  [Original Photo]              [Final Design]                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  PAINT & WALL FINISHES                                          │   │
│  │                                                                  │   │
│  │  • Walls: Sage Green                                            │   │
│  │    - Hex: #9DC183                                               │   │
│  │    - Benjamin Moore: Kittery Point Green HC-119                 │   │
│  │    - Sherwin Williams: Nurture Green SW 6451                    │   │
│  │    - Finish: Eggshell                                           │   │
│  │    - Estimated coverage: 450 sq ft                              │   │
│  │                                                                  │   │
│  │  • Accent Wall: Deep Forest                                     │   │
│  │    - Hex: #228B22                                               │   │
│  │    - Benjamin Moore: Forest Green 2047-10                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  FLOORING                                                        │   │
│  │                                                                  │   │
│  │  • Type: Engineered Hardwood                                    │   │
│  │  • Color: Medium Oak                                            │   │
│  │  • Similar Products:                                            │   │
│  │    - Home Depot: Malibu Wide Plank French Oak                   │   │
│  │    - Lumber Liquidators: Bellawood Matte Oak                    │   │
│  │  • Estimated area: 320 sq ft                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  FURNITURE & DECOR (Shopping List)                              │   │
│  │                                                                  │   │
│  │  1. Sectional Sofa - Gray, L-shaped, Modern                     │   │
│  │     • Style: Mid-century modern                                 │   │
│  │     • Dimensions: ~110" x 85"                                   │   │
│  │     • Similar: West Elm Andes, IKEA Söderhamn, Article Sven    │   │
│  │     • Price range: $1,500 - $3,500                              │   │
│  │                                                                  │   │
│  │  2. Coffee Table - Walnut, Rectangular                          │   │
│  │     • Dimensions: ~48" x 24"                                    │   │
│  │     • Similar: CB2 Frame, Target Threshold, Wayfair             │   │
│  │     • Price range: $200 - $800                                  │   │
│  │                                                                  │   │
│  │  3. Indoor Plant - Fiddle Leaf Fig                              │   │
│  │     • Size: Large (5-6 ft)                                      │   │
│  │     • Planter: White ceramic, modern                            │   │
│  │     • Price range: $80 - $200                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  LIGHTING                                                        │   │
│  │                                                                  │   │
│  │  • Main: Warm white (2700K-3000K)                               │   │
│  │  • Pendant lights over dining: Brass, globe style               │   │
│  │  • Floor lamp: Arc lamp, brushed nickel                         │   │
│  │  • Recommendations: Philips Hue for smart control               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ESTIMATED BUDGET                                                │   │
│  │                                                                  │   │
│  │  Paint & Materials:        $300 - $500                          │   │
│  │  Flooring:                 $2,500 - $4,000                      │   │
│  │  Furniture:                $3,000 - $7,000                      │   │
│  │  Lighting:                 $400 - $800                          │   │
│  │  Decor & Plants:           $300 - $600                          │   │
│  │  Labor (if applicable):    $1,000 - $3,000                      │   │
│  │  ─────────────────────────────────────────                      │   │
│  │  TOTAL ESTIMATE:           $7,500 - $15,900                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Export Formats

| Format | Use Case | Contents |
|--------|----------|----------|
| **PDF Report** | Hand to contractor/designer | Full spec with images, colors, shopping list |
| **Shopping List** | Furniture shopping | Items with links, dimensions, price ranges |
| **Color Palette** | Paint store | Paint codes for all major brands |
| **Mood Board** | Share vision | Images + color swatches + style notes |
| **JSON Data** | Integration | Machine-readable specifications |

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPECIFICATION GENERATION                             │
│                                                                         │
│  Final Design Image                                                     │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ANALYZE FINAL DESIGN (Claude Vision)                            │   │
│  │                                                                  │   │
│  │ Extract from image:                                              │   │
│  │ • Dominant colors → Match to paint brand codes                   │   │
│  │ • Furniture items → Identify style, suggest similar products    │   │
│  │ • Materials → Flooring type, fabric types                       │   │
│  │ • Lighting → Color temperature, fixture styles                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ENRICH WITH PRODUCT DATA                                        │   │
│  │                                                                  │   │
│  │ • Match colors to Benjamin Moore, Sherwin Williams, Behr        │   │
│  │ • Search furniture catalogs for similar items                   │   │
│  │ • Get current prices from affiliate APIs                        │   │
│  │ • Calculate material quantities based on room size              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ GENERATE REPORT                                                  │   │
│  │                                                                  │   │
│  │ • Create PDF with professional layout                           │   │
│  │ • Include before/after comparison                               │   │
│  │ • List all specifications with actionable details               │   │
│  │ • Add shopping links and budget estimates                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  User downloads and shares with contractor                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Specification Generator Service

```python
# app/services/spec_generator.py

class SpecificationGenerator:
    """
    Generates actionable specifications from final design
    """

    def __init__(self):
        self.claude = anthropic.Anthropic()
        self.color_matcher = ColorMatcher()
        self.product_search = ProductSearch()

    async def generate_spec(
        self,
        final_image: str,
        original_image: str,
        conversation_history: list,
        room_analysis: dict
    ) -> DesignSpecification:

        # Step 1: Analyze final design
        design_analysis = await self.analyze_design(final_image)

        # Step 2: Match colors to paint brands
        paint_specs = await self.color_matcher.match_paints(
            design_analysis.colors
        )

        # Step 3: Find similar products
        furniture_specs = await self.product_search.find_similar(
            design_analysis.furniture
        )

        # Step 4: Calculate quantities
        quantities = self.calculate_quantities(
            room_analysis.dimensions,
            design_analysis
        )

        # Step 5: Estimate budget
        budget = self.estimate_budget(furniture_specs, quantities)

        return DesignSpecification(
            images={
                "before": original_image,
                "after": final_image
            },
            paint=paint_specs,
            flooring=design_analysis.flooring,
            furniture=furniture_specs,
            lighting=design_analysis.lighting,
            quantities=quantities,
            budget=budget
        )

    async def analyze_design(self, image: str) -> DesignAnalysis:
        """Use Claude Vision to extract design details"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "url", "url": image}
                    },
                    {
                        "type": "text",
                        "text": DESIGN_ANALYSIS_PROMPT
                    }
                ]
            }]
        )

        return DesignAnalysis.parse(response.content[0].text)


DESIGN_ANALYSIS_PROMPT = """
Analyze this interior design image and extract detailed specifications
that a contractor or designer could use to recreate this room.

For each element, provide:

1. COLORS (extract hex codes from the image):
   - Wall colors (primary and accent)
   - Ceiling color
   - Trim/molding color

2. FLOORING:
   - Type (hardwood, tile, carpet, etc.)
   - Color/finish
   - Pattern if any

3. FURNITURE (list each item):
   - Type (sofa, table, chair, etc.)
   - Style (modern, traditional, mid-century, etc.)
   - Color/material
   - Approximate dimensions
   - Similar products that match this style

4. LIGHTING:
   - Type of fixtures
   - Color temperature (warm/cool)
   - Style

5. DECOR:
   - Plants
   - Art
   - Textiles (rugs, curtains, pillows)
   - Accessories

Respond in JSON format.
"""
```

### Color Matching Service

```python
# app/services/color_matcher.py

class ColorMatcher:
    """
    Matches hex colors to real paint brand codes
    """

    # Paint brand color databases (simplified)
    PAINT_DATABASES = {
        "benjamin_moore": "path/to/bm_colors.json",
        "sherwin_williams": "path/to/sw_colors.json",
        "behr": "path/to/behr_colors.json"
    }

    def match_paints(self, colors: list[ColorSpec]) -> list[PaintSpec]:
        results = []

        for color in colors:
            hex_code = color.hex

            # Find closest matches in each brand
            matches = {
                "hex": hex_code,
                "element": color.element,
                "matches": {
                    "benjamin_moore": self.find_closest("benjamin_moore", hex_code),
                    "sherwin_williams": self.find_closest("sherwin_williams", hex_code),
                    "behr": self.find_closest("behr", hex_code)
                }
            }

            results.append(matches)

        return results

    def find_closest(self, brand: str, hex_code: str) -> PaintMatch:
        """Find closest color in brand's catalog using color distance"""
        # Uses Delta-E color difference algorithm
        # Returns closest matching paint with name and code
        pass
```

### PDF Report Generator

```python
# app/services/pdf_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFReportGenerator:

    def generate(self, spec: DesignSpecification) -> bytes:
        """Generate professional PDF report"""

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Page 1: Before/After + Summary
        self.add_cover_page(c, spec)

        # Page 2: Paint Specifications
        self.add_paint_page(c, spec.paint)

        # Page 3: Flooring Specifications
        self.add_flooring_page(c, spec.flooring)

        # Page 4-5: Furniture Shopping List
        self.add_furniture_pages(c, spec.furniture)

        # Page 6: Lighting & Decor
        self.add_lighting_page(c, spec.lighting)

        # Page 7: Budget Summary
        self.add_budget_page(c, spec.budget)

        c.save()
        return buffer.getvalue()
```

### Export API Endpoints

```python
# app/api/routes/export.py

@router.post("/projects/{project_id}/export")
async def export_design(
    project_id: str,
    format: ExportFormat,  # pdf, shopping_list, colors, json
    session: DesignSession = Depends(get_session)
):
    """Generate and download design specifications"""

    # Generate full specification
    spec = await spec_generator.generate_spec(
        final_image=session.current_image,
        original_image=session.original_image,
        conversation_history=session.messages,
        room_analysis=session.room_analysis
    )

    if format == "pdf":
        pdf_bytes = pdf_generator.generate(spec)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=design-spec.pdf"}
        )

    elif format == "shopping_list":
        return {
            "furniture": spec.furniture,
            "decor": spec.decor,
            "estimated_total": spec.budget.total
        }

    elif format == "colors":
        return {
            "paint_codes": spec.paint,
            "color_palette": [c.hex for c in spec.colors]
        }

    elif format == "json":
        return spec.dict()
```

### Sample PDF Output

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              INTERIOR DESIGN SPECIFICATION                      │
│                    Living Room Redesign                         │
│                                                                 │
│  Generated: January 2, 2025                                     │
│  Project ID: LR-2025-001                                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [BEFORE IMAGE]                    [AFTER IMAGE]                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SUMMARY OF CHANGES                                             │
│  ──────────────────                                             │
│  • Walls repainted from beige to sage green                     │
│  • Replaced leather sofa with modern gray sectional             │
│  • Added geometric area rug                                     │
│  • Updated lighting to warm white                               │
│  • Added indoor plants for freshness                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PAINT SPECIFICATIONS                                           │
│  ────────────────────                                           │
│                                                                 │
│  MAIN WALLS                                                     │
│  Color: Sage Green                                              │
│  ┌────────┐                                                     │
│  │████████│  Hex: #9DC183                                       │
│  └────────┘                                                     │
│                                                                 │
│  Paint Matches:                                                 │
│  • Benjamin Moore: Kittery Point Green (HC-119)                 │
│  • Sherwin Williams: Nurture Green (SW 6451)                    │
│  • Behr: Fresh Artichoke (M370-5)                               │
│                                                                 │
│  Recommended Finish: Eggshell                                   │
│  Estimated Coverage: 450 sq ft (2 coats)                        │
│  Paint Needed: ~2 gallons                                       │
│                                                                 │
│  [Continue for each color...]                                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FURNITURE SHOPPING LIST                                        │
│  ───────────────────────                                        │
│                                                                 │
│  1. SECTIONAL SOFA                                              │
│     Style: Modern, L-shaped                                     │
│     Color: Charcoal Gray                                        │
│     Material: Performance fabric                                │
│     Dimensions: 110"W x 85"D x 34"H                             │
│                                                                 │
│     Where to Buy:                                               │
│     • West Elm - Andes Sectional ($2,999)                       │
│     • Article - Sven Sectional ($2,399)                         │
│     • IKEA - Söderhamn ($1,299)                                │
│     • Wayfair - Similar styles ($800-2,000)                     │
│                                                                 │
│  [Continue for each item...]                                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BUDGET ESTIMATE                                                │
│  ───────────────                                                │
│                                                                 │
│  Category              Low         High                         │
│  ─────────────────────────────────────────                      │
│  Paint & Supplies      $250        $400                         │
│  Furniture             $3,500      $7,000                       │
│  Lighting              $300        $600                         │
│  Decor & Plants        $200        $500                         │
│  Labor (optional)      $500        $1,500                       │
│  ─────────────────────────────────────────                      │
│  TOTAL                 $4,750      $10,000                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Affiliate Integration (Revenue Opportunity)

```python
# Partner with furniture/home improvement retailers

AFFILIATE_PARTNERS = {
    "amazon": {"commission": "4%", "api": True},
    "wayfair": {"commission": "7%", "api": True},
    "west_elm": {"commission": "5%", "api": False},
    "home_depot": {"commission": "3%", "api": True},
    "lowes": {"commission": "2%", "api": True}
}

# When generating shopping lists, include affiliate links
# User buys products → You earn commission
```

---

## 1.9 Deployment

### Recommended Stack

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | Vercel | Free tier available |
| Backend | Railway / Render | ~$5-20/mo |
| Database | Supabase | Free tier available |
| Image Storage | Cloudflare R2 | ~$0.015/GB |
| AI (Chat) | Claude API | ~$0.003/1K tokens |
| AI (Images) | Replicate | ~$0.02-0.05/image |

### Cost Per Design Session

| Service | Usage | Cost |
|---------|-------|------|
| Claude (understanding + responses) | ~5 calls | $0.02 |
| Image Generation | ~10 images | $0.40 |
| Storage | ~30MB | $0.001 |
| **Total per session** | | **~$0.42** |

---

## 1.9 Implementation Checklist

### MVP (4-6 weeks)

- [ ] **Week 1-2: Core Setup**
  - [ ] Next.js frontend with chat UI
  - [ ] FastAPI backend
  - [ ] Database setup (Supabase)
  - [ ] Image storage (R2)

- [ ] **Week 3-4: AI Integration**
  - [ ] Room photo upload + analysis (Claude Vision)
  - [ ] Chat message processing (Claude)
  - [ ] Image generation (Replicate/SD)
  - [ ] Depth map generation

- [ ] **Week 5-6: Export & Polish**
  - [ ] Version history UI
  - [ ] Before/after comparison
  - [ ] Export specification generator
  - [ ] PDF report generation
  - [ ] Color matching to paint brands
  - [ ] Shopping list with product suggestions
  - [ ] Error handling & testing

### Post-MVP
- [ ] Voice input option
- [ ] Multiple room support
- [ ] Style presets
- [ ] Furniture catalog integration
- [ ] Phase 2: 3D visualization

---

## Phase 2: 3D Design System

*(To be detailed after Phase 1)*

- 3D room reconstruction from 2D designs
- Interactive 3D walkthrough
- Furniture placement in 3D
- AR preview on mobile
- Export to 3D formats

---

*Document Version: 3.0*
*Last Updated: January 2025*
