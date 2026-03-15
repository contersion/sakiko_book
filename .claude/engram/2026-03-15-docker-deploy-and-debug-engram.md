# Docker Deploy And Debug Engram

## Basic Info
- Date: 2026-03-15
- Project: local_txt_reader
- Scope: Frontend + Backend integration
- Topic: Docker deployment, upload interaction bug, encoding recovery
- Status: Completed

## User Goal
Deploy the current project on Docker and make the real browser workflow usable.

The concrete expectations that emerged during the discussion were:
- `docker-compose` should bring the project up successfully
- backend root access should not look broken during deployment checks
- the bookshelf upload button should actually trigger a request
- Chinese UI copy should render correctly after the upload fix

## Environment Notes
- Attempted to use `engram-server` MCP first, but it was not mounted in the current session
- Fell back to the project-level `./.claude/engram` directory as the local Engram store
- Deployment and fixes were executed in the Windows workspace with Docker Desktop

## Problems Encountered
### 1. Backend root path returned 404 after deployment
- `http://localhost:8000/` returned a structured 404 error
- Health endpoint `/health` was already healthy, so this was not a container startup failure
- Root cause: the FastAPI app only registered the API router and `/health`, but no `/` route

### 2. Clicking "Upload TXT" produced no network traffic
- The bookshelf page showed no request in DevTools when trying to upload a TXT file
- Root cause: `n-upload` used `custom-request` together with `default-upload=false`, but there was no manual `submit()` call
- Because the file list was hidden, the UI looked like it did nothing at all

### 3. Chinese text turned into mojibake after the upload fix
- Upload started working, but bookshelf Chinese copy rendered as garbled characters
- Root cause: `frontend/src/pages/BookshelfPage.vue` had been written back with the wrong encoding during a Windows PowerShell fallback edit
- Evidence showed the file bytes decoded correctly as GBK, but failed as UTF-8 and introduced replacement characters in the browser build

## Fixes Applied
### Backend deployment usability fix
- Added `GET /` in `backend/app/routers/health.py`
- Reused the same response payload as `/health`
- Result: visiting `http://localhost:8000/` now returns service metadata instead of 404

### Frontend upload trigger fix
- Updated `frontend/src/pages/BookshelfPage.vue`
- Removed `:default-upload="false"` from the `n-upload` component
- Kept the existing `custom-request="handleUpload"`
- Result: selecting a file now automatically enters the existing upload request flow

### Frontend encoding recovery fix
- Recovered `frontend/src/pages/BookshelfPage.vue` by decoding the file content as GBK and rewriting it as UTF-8
- Rebuilt and redeployed the frontend image afterward
- Result: Chinese copy became readable again while preserving the upload behavior fix

## Files Changed During This Discussion
- `backend/app/routers/health.py`
- `frontend/src/pages/BookshelfPage.vue`

## Verification Performed
### Docker deployment
- Ran `docker compose up -d --build`
- Verified `txt-reader-backend` and `txt-reader-frontend` were both `Up`

### Backend availability
- Verified `GET /health` returned `200`
- Verified `GET /` returned `200` after the root route fix

### Frontend build
- Ran `npm.cmd run build` in `frontend/`
- Build passed after both the upload fix and the encoding recovery

### Upload smoke test
- Logged in with the default admin account
- Uploaded a temporary TXT file through the real backend upload endpoint
- Confirmed a book record was created successfully
- Deleted the temporary uploaded book to avoid polluting user data

## Reusable Lessons
### Naive UI upload behavior
- In Naive UI, `custom-request` does not mean the request is always automatic
- If `default-upload=false` is also set, the component will not auto-submit the selected file
- If the file list is hidden and no explicit `submit()` exists, the UI can appear completely unresponsive

### Windows encoding safety
- When forced to fall back from `apply_patch` on Windows, direct file writes are risky for UTF-8 Vue source files
- PowerShell fallback writes must explicitly preserve UTF-8
- Safer approach: write with `[System.IO.File]::WriteAllText(..., new UTF8Encoding($false))`
- Do not assume `Set-Content` will preserve the original encoding of frontend source files

## Recommended Future Guardrails
- If `n-upload` uses `custom-request`, avoid `default-upload=false` unless the page also provides an explicit `submit()` path
- When patch tooling is unavailable on Windows, always set encoding explicitly before writing `.vue`, `.ts`, `.css`, or `.md` files containing Chinese copy
- Keep a small smoke-check for upload interaction and UTF-8 validation whenever the bookshelf page is edited