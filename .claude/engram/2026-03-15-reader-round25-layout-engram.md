# Reader Round 25 Layout Engram

## Basic Info
- Date: 2026-03-15
- Project: local_txt_reader
- Scope: Frontend reader page + Docker verification
- Topic: Round 25 reader implementation, side panel anchoring, overflow fix
- Status: Completed
- Draft Note: Auto-generated from the current conversation and may still need user补充

## User Goal
Implement the frontend coding phase for Round 25 after an analysis-first step, while keeping the backend and API contract unchanged.

The concrete goals that emerged during the discussion were:
- Analyze the existing reader page before changing code
- Keep the reader business logic intact
- Build the Round 25 immersive reading experience in the frontend only
- Deploy the new frontend to Docker and verify it is actually running
- In a follow-up refinement, do not redesign the whole reader again
- Fix only the desktop left tool panel and right progress panel layout issues
- Make both side panels anchor around the centered reading column instead of the browser edges
- Ensure the left tool panel contents never overflow outside their container
- Preserve the mobile hide/collapse behavior

## Constraints
- Do not modify backend reader APIs
- Do not change database structure or API field semantics
- Keep chapter-by-chapter loading
- Keep reading progress based on `chapter_index + char_offset`
- Keep catalog drawer, settings drawer, chapter switching, scroll reading, and progress sync working
- Desktop can use fixed positioning around the reading column
- Mobile should keep the existing hidden or collapsed interaction model

## Environment Notes
- Attempted to use `engram-server` MCP first, but no writable Engram MCP tools were exposed in the current session
- MCP resource listing returned empty, so the fallback Engram store was the project-level `./.claude/engram`
- Implementation and deployment were performed in the Windows workspace with Docker Desktop

## Analysis Findings
### Reader page structure before modification
- `frontend/src/pages/ReaderPage.vue` already contained the main reader data flow, including chapter loading, progress restoration, scroll tracking, and preference persistence
- The business logic for `loadReader`, `openChapter`, `flushProgress`, and `restoreScrollForCharOffset` was reusable and should not be rewritten
- The page was large and UI-heavy, so regressions were most likely to come from layout changes rather than API work

### Why the original desktop side panels did not satisfy the follow-up requirement
- The left tool area and right progress area were still placed in the outer page grid and only used `sticky`
- That made them visually anchor to the page layout rather than to the centered reading column
- The left tool column was too narrow for its internal cards, causing content to visually push outside the outer module boundary

## Fixes Applied
### 1. Round 25 reader implementation
- Reworked the reader page into an immersive frontend layout while preserving the existing reader logic
- Hid the global app chrome for the reader route through layout and router metadata updates
- Kept the chapter drawer, settings drawer, scroll reading mode, progress display, chapter navigation, and sync behavior intact

### 2. Focused desktop side panel positioning fix
- Updated `frontend/src/pages/ReaderPage.vue` so the desktop side panels use `fixed` positioning instead of relying on the outer page flow
- Introduced shared width variables for the reading column and side panels
- Positioned the left rail with the reading-column-based formula:
  - `50% - column width / 2 - side width - gap`
- Positioned the right rail with the mirrored formula:
  - `50% + column width / 2 + gap`
- Kept both panels vertically centered in the viewport with `top: 50%` and `translateY(-50%)`

### 3. Left tool panel overflow fix
- Gave the left tool container an explicit safe desktop width
- Converted the inner panel structure to stable vertical flex layout
- Ensured all internal tool cards stay inside the parent container using:
  - `width: 100%`
  - `max-width: 100%`
  - `min-width: 0`
  - `box-sizing: border-box`
  - `overflow-wrap` for text
- Preserved the hover and visual styling without allowing internal blocks to escape the container

### 4. Docker deployment and version verification
- Built and deployed the updated frontend and backend containers
- Verified basic backend health and frontend availability
- Later confirmed that Docker was still serving the old frontend asset hashes after a local rebuild
- Rebuilt only the frontend container with `docker compose up -d --build frontend`
- Confirmed the container began serving the latest asset hashes from the newest local build

## Files Changed During This Discussion
- `frontend/src/pages/ReaderPage.vue`
- `frontend/src/layouts/AppLayout.vue`
- `frontend/src/router/index.ts`
- `frontend/src/router/meta.d.ts`

## Verification Performed
### Frontend checks
- Ran `npm.cmd run typecheck`
- Ran `npm.cmd run build`
- The frontend build passed successfully
- The only remaining warning was the existing large-chunk warning from Vite

### Docker smoke checks
- Ran `docker compose up -d --build`
- Verified `txt-reader-backend` and `txt-reader-frontend` were running
- Verified `GET http://127.0.0.1:8000/health` returned healthy service metadata
- Verified login and auth endpoints during the earlier smoke test
- Verified `GET http://127.0.0.1:5173` and `GET http://127.0.0.1:5173/reader/1` returned `200`

### Docker version verification
- Compared local `frontend/dist/index.html` asset hashes with the assets returned by the running Docker frontend
- Detected that Docker initially served an older frontend build
- Rebuilt the frontend container
- Confirmed Docker then served the new asset files:
  - `index-YPadGSk8.js`
  - `index-Bm-PbBC-.css`

## Reusable Lessons
### Anchoring floating side panels around centered content
- If the reading content is centered with a max width, side panels should share the same width variables and anchor calculations
- `sticky` inside an outer page grid is not enough when the UX requirement is to orbit the reading column rather than the browser edges
- A shared `--reader-column-width` variable makes the reading surface and both side rails stay visually aligned

### Preventing rail-card overflow in narrow support panels
- Support rails should have an explicit width before card layout tuning starts
- Inner card stacks should use normal flex or grid flow instead of fragile positional tricks
- `min-width: 0` and `box-sizing: border-box` are essential when compact cards contain multi-line text

### Verifying container freshness
- A successful local frontend build does not prove Docker is serving the new version
- Comparing the built asset hashes with the assets currently returned by the running container is a reliable way to detect stale frontend deployments

## Recommended Future Guardrails
- When adjusting the reader shell again, keep layout-only changes inside `ReaderPage.vue` unless route-level chrome behavior also changes
- Keep the side rails and reading column on shared CSS variables to avoid drift during future visual tweaks
- When a user asks for a narrow UI correction, avoid reopening the broader layout unless the requested fix truly requires it
- After Docker redeploys, confirm the served asset hashes before claiming the container is on the latest frontend build