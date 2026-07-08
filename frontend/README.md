# BudgetTrip Frontend

Interfaz minimalista en modo oscuro para el planificador de viajes con agentes.

## Stack

- React + TypeScript + Vite
- Tailwind CSS v4
- Design tokens en `src/styles/design-tokens.css`

## Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Completá `.env`:

```env
VITE_API_KEY=tu_api_secret_key   # mismo valor que API_SECRET_KEY del backend
VITE_API_BASE_URL=               # vacío en dev (usa proxy de Vite)
```

## Desarrollo

Terminal 1 — backend:

```bash
cd ..
uvicorn budgettrip.interfaces.api.main:app --reload
```

Terminal 2 — frontend:

```bash
npm run dev
```

Abrí `http://localhost:5173`

## Rutas

| Ruta | Descripción |
|------|-------------|
| `/` | Landing page minimalista |
| `/chat` | Chat principal con el agente de requisitos |

## Paleta

| Token | Hex |
|-------|-----|
| Background | `#171010` |
| Surface | `#2B2B2B` |
| Elevated | `#362222` |
| Border | `#423F3E` |
| Text | `#F4EFEA` |

## Build

```bash
npm run build
npm run preview
```
