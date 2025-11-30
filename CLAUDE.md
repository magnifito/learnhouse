# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LearnHouse is an open-source educational platform (beta) that enables anyone to provide world-class educational content. It's built as a monorepo using Turbo with two main applications:

- **Frontend (apps/web)**: Next.js 16 application with App Directory
- **Backend (apps/api)**: FastAPI Python application

## Tech Stack

**Frontend:**
- Next.js 16 with App Directory
- React 19
- TailwindCSS 4 (with @tailwindcss/postcss)
- Radix UI for accessible components
- Tiptap (ProseMirror wrapper) for rich text editing
- YJS for collaborative editing
- NextAuth for authentication
- SWR for data fetching

**Backend:**
- FastAPI with async/await
- SQLModel + SQLAlchemy for PostgreSQL ORM
- Alembic for migrations
- Pydantic v1 for validation (note: v1, not v2)
- Redis for caching
- Uvicorn ASGI server
- Pytest for testing
- Ruff for linting (ignores E501, E712)

**Infrastructure:**
- PostgreSQL database
- Redis for caching
- pnpm as package manager (v9.0.6)
- Turbo for monorepo management
- Python 3.12.3 (required)

## Development Commands

**Root Level (uses Turbo):**
```bash
pnpm dev          # Start all apps in development mode
pnpm build        # Build all apps
pnpm start        # Start all apps in production mode
pnpm lint         # Lint all apps
pnpm format       # Format code with Prettier
```

**Frontend (apps/web):**
```bash
pnpm dev          # Start Next.js dev server with Turbopack
pnpm dev-https    # Start with HTTPS on port 443
pnpm build        # Build for production
pnpm start        # Start production server
pnpm lint         # Run ESLint (|| true, won't fail)
pnpm lint:fix     # Auto-fix ESLint issues
```

**Backend (apps/api):**
```bash
# Run the API server
python app.py

# Run with uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port <port>

# Database migrations
alembic upgrade head              # Apply migrations
alembic revision --autogenerate -m "description"  # Generate migration

# CLI setup tool
python cli.py install             # Interactive setup
python cli.py install --short     # Quick setup with defaults

# Testing
pytest                            # Run all tests
pytest src/tests/                 # Run specific test directory
pytest -v                         # Verbose output
pytest --cov                      # With coverage
```

## Architecture

### Backend Structure (apps/api/src/)

- **routers/**: API route handlers organized by domain
  - `courses/`: Course, chapter, assignment, certification endpoints
  - `courses/activities/`: Activity and block endpoints
  - `ai/`: AI copilot features
  - `ee/`: Enterprise edition (payments, cloud_internal)
  - `auth.py`, `users.py`, `orgs.py`, `roles.py`, etc.
- **services/**: Business logic layer
- **db/**: Database models and schemas (SQLModel)
- **security/**: Authentication and authorization
- **core/**: Core application functionality (events, config)
- **tests/**: Pytest test suites

API versioning: All routes prefixed with `/api/v1`

### Frontend Structure (apps/web/)

- **app/**: Next.js App Directory routes
  - `api/`: API route handlers
  - `auth/`: Authentication pages
  - `orgs/`: Organization-specific routes
  - `home/`: Landing pages
  - `editor/`: Course content editor
  - `payments/`: Payment flows
- **components/**: React components
  - `Contexts/`: React Context providers
  - `Dashboard/`: Dashboard UI components
  - `Objects/`: Reusable object components
  - `Pages/`: Page-level components
  - `ui/`: Radix UI component wrappers
  - `Hooks/`: Custom React hooks
- **services/**: Frontend service layer (API calls)
  - Organized by domain: `courses/`, `auth/`, `organizations/`, `blocks/`, etc.

### Key Patterns

**Backend:**
- FastAPI routers are registered in `src/router.py` and included in `app.py`
- Database models use SQLModel (combines SQLAlchemy + Pydantic)
- Async/await throughout for performance
- JWT authentication via fastapi-jwt-auth
- Config loaded from `config/config.py` (LearnHouseConfig)
- Logfire instrumentation available (opt-in via config)
- Development mode enables `/docs` and `/redoc` endpoints

**Frontend:**
- NextAuth for authentication (session management)
- Services in `services/` make API calls to backend
- Tiptap editor for rich content (blocks-based, Notion-like)
- YJS for multiplayer/collaborative editing
- SWR for client-side data fetching and caching

### Database

- PostgreSQL is the primary database
- Migrations managed by Alembic (see `apps/api/migrations/`)
- SQLModel provides ORM with Pydantic validation
- Connection string configured in LearnHouseConfig

### Initial Setup

Run the CLI install command to set up the first organization and admin user:

```bash
cd apps/api
python cli.py install --short
```

Requires environment variables:
- `LEARNHOUSE_INITIAL_ADMIN_PASSWORD` (required)
- `LEARNHOUSE_INITIAL_ADMIN_EMAIL` (optional, defaults to admin@school.dev)

## Important Notes

- **Python Version**: Requires Python >=3.12.3, <3.13.0
- **Package Manager**: Must use pnpm (v9.0.6)
- **Pydantic Version**: Backend uses Pydantic v1, not v2
- **Environment Files**: Required for both apps (refer to docs.learnhouse.app)
- **Beta Status**: Project is in beta, expect breaking changes
- **Dev Mode**: Backend development mode enables Swagger docs at `/docs`
- **Pytest Config**: Async tests auto-detected, warnings filtered in pyproject.toml

## Additional Resources

- [Official Docs](https://docs.learnhouse.app)
- [Dev Environment Setup Guide](https://docs.learnhouse.app/setup-dev-environment)
- [Roadmap](https://www.learnhouse.app/roadmap)
- [GitHub Issues](https://github.com/learnhouse/learnhouse/issues)
