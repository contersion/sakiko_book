# Project Guidance

本项目是个人使用的 TXT 在线阅读器，支持书架、目录、阅读进度同步和用户自定义章节正则。

## Stack
- Frontend: Vue 3 + Vite + TypeScript + Vue Router + Pinia + Shadcn Vue + Tailwind CSS
- Backend: FastAPI + SQLAlchemy + SQLite

## Architecture Rules
- 使用轻量前后端分离
- 不要引入微服务、Redis、MQ、K8s
- 阅读正文必须按章节返回，不能整本返回
- 阅读进度以 chapter_index + char_offset 为主，percent 仅用于展示
- 章节解析支持内置规则和用户自定义 regex
- 没匹配到章节时必须降级为“全文”单章节模式

## Workflow
详细开发步骤见 `docs/IMPLEMENTATION_STEPS.md`。
进行较大功能开发、重构、验收前，先阅读该文件。

## Commands
- backend: `uvicorn app.main:app --reload`
- frontend: `npm run dev`
- docker: see README

## CORS / 跨域规则
- 后端已添加原生 ASGI `ReflectCORSMiddleware`（`backend/app/main.py`），反射任意 Origin。
- `ReflectCORSMiddleware` 必须先于标准 `CORSMiddleware` 注册（外层包裹），否则标准 CORS 会先拦截 OPTIONS 返回 400。
- ASGI scope 中获取 HTTP method 必须使用 `scope["method"]`，而非 `headers[":method"]`。
- 通过域名 / 反向代理访问时，若仍出现跨域问题，优先检查反向代理是否正确透传 `Origin` 头，而非盲目扩充 CORS 白名单。

## PWA / Service Worker 规则
- 前端已配置 PWA（`vite-plugin-pwa`），Service Worker 会自动缓存静态资源。
- 每次前端构建更新后，用户可能需要 Ctrl+F5 强制刷新并手动 Unregister SW，否则可能加载旧版。
- 新增或修改 PWA 相关配置（manifest、图标、主题色）时，需同步验证 `vite.config.ts` 和 `index.html`。

## Reading Page Refactor Rules
- 阅读页允许进行 UI 重构与前端交互重构，但不得修改后端接口、数据库结构、API 字段语义。
- 阅读正文仍必须按章节加载与返回，不能改为整本返回。
- 阅读进度定位仍以 `chapter_index + char_offset` 为主，`percent` 仅用于展示。
- 目录、阅读设置、主题、字体大小、行高、进度同步等现有能力应尽量复用，不要重写业务层。
- 阅读页需同时兼容 PC 与移动端，优先通过响应式布局、抽屉、浮动工具区实现。
- 允许将目录与设置从常驻面板改为抽屉式交互，但必须保持原有功能可用。