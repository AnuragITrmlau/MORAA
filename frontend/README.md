# 💎 MORAA GemVision — Frontend

Next.js 16 + React 19 web application for the MORAA GemVision jewellery analysis platform.

## ✨ Features

- Modern dashboard with real-time metrics
- AI-powered jewellery image analysis
- Interactive charts and visualisations (Framer Motion)
- Upload & preview jewellery images
- Professional PDF report viewer
- History tracking with pagination
- Dark/light theme support
- Responsive design (Tailwind CSS v4)

---

## 🚀 How to Run the Frontend

### Prerequisites

- **Node.js** >= 18 (recommended: 20 LTS)
- The **backend** server should be running on port 8000 for full functionality (see setup below)

### Step-by-Step Setup

#### 1. Clone & navigate to the frontend

```bash
cd frontend
```

#### 2. Install dependencies

```bash
npm install
```

This installs all packages listed in `package.json` (Next.js, React, Framer Motion, Zustand, etc.).

#### 3. Start the development server

```bash
npm run dev
```

You should see output like:

```
▲ Next.js 16.2.10
- Local: http://localhost:3000
```

#### 4. Open in your browser

Visit **http://localhost:3000** to see the app.

---

## 🔁 Running with the Backend

The frontend communicates with the FastAPI backend at `http://localhost:8000`. For full functionality (analysis, history, reports), both servers need to run simultaneously.

**Open two terminal windows:**

| Terminal 1 — Frontend (this one) | Terminal 2 — Backend |
|---|---|
| ```bash<br>cd frontend<br>npm run dev<br>``` | ```bash<br>cd backend<br>source venv/bin/activate<br>uvicorn app.main:app --reload --port 8000<br>``` |
| Starts on **http://localhost:3000** | Starts on **http://localhost:8000** |

**On Windows (PowerShell):**

| Terminal 1 — Frontend | Terminal 2 — Backend |
|---|---|
| ```powershell<br>cd frontend<br>npm run dev<br>``` | ```powershell<br>cd backend<br>.\venv\Scripts\activate<br>uvicorn app.main:app --reload --port 8000<br>``` |

> See the [Backend README](../backend/README.md) for complete backend setup instructions.

---

## 📜 Available Commands

| Command | Description |
|---|---|
| `npm run dev` | Development server with hot reload |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | Run ESLint |

---

## 🧩 Tech Stack

| Library | Purpose |
|---|---|
| Next.js 16 | React framework (App Router) |
| React 19 | UI library |
| TypeScript | Type safety |
| Tailwind CSS v4 | Utility-first CSS |
| Framer Motion | Animations |
| Zustand | State management |
| React Hook Form | Form handling |
| Lucide React | Icons |
| class-variance-authority | Component variants |
| tailwind-merge | Class merging |

---

## 📂 Project Structure

```
frontend/src/
├── app/              # Next.js App Router pages & layout
│   ├── globals.css   # Global styles & Tailwind imports
│   ├── layout.tsx    # Root layout
│   └── page.tsx      # Landing page
├── components/       # Reusable UI components
│   ├── pages/        # Page-level components (Dashboard, History, etc.)
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   ├── ChartCard.tsx
│   ├── MetricCard.tsx
│   ├── SummaryCard.tsx
│   ├── PreviewCard.tsx
│   ├── UploadCard.tsx
│   ├── RiskAssessment.tsx
│   ├── TrendAlert.tsx
│   ├── CompetitorTable.tsx
│   ├── AssistantPanel.tsx
│   └── FooterBar.tsx
├── contexts/         # React contexts (ThemeContext)
├── lib/              # Utility functions
├── services/         # API service layer
│   ├── analysis.service.ts
│   ├── assistant.service.ts
│   ├── history.service.ts
│   ├── market.service.ts
│   ├── report.service.ts
│   └── upload.service.ts
├── stores/           # Zustand state stores
├── types/            # TypeScript type definitions
├── hooks/            # Custom React hooks
├── features/         # Feature-based modules
└── styles/           # Additional styles
```

---

## 🔌 API Configuration

The frontend expects the backend API at `http://localhost:8000`. If your backend runs on a different host or port, update the base URL in the service files under `src/services/`.

---

## 🌐 Pages

| Route | Description |
|---|---|
| `/` | Landing / overview |
| `/dashboard` | Main dashboard with metrics |
| `/analysis/new` | Upload & analyse a new image |
| `/history` | View past analyses |
| `/reports` | Browse generated PDF reports |
| `/profile` | User profile settings |
| `/settings` | Application settings |
