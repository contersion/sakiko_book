# TXT Reader

TXT Reader 是一个面向个人使用场景的 TXT 在线阅读器，支持上传本地 TXT 文件、自动解析章节、管理书架、同步阅读进度，以及按自己的文本格式定制章节识别规则。

当前仓库采用轻量前后端分离架构：

- 前端：Vue 3 + Vite + TypeScript + Vue Router + Pinia + Naive UI
- 后端：FastAPI + SQLAlchemy + SQLite
- 部署方式：Docker Compose

本 README 基于当前仓库真实结构编写，只保留源码目录和关键运行目录，不展开 `node_modules`、`dist`、`.venv` 之类的生成产物目录。

开发过程及思路[`development-process.md`](./development-process.md) 

## 使用方法

推荐使用流程如下：

1. 使用默认账号登录系统。
2. 在书架页上传 `.txt` 文件。
3. 如果默认章节规则识别不理想，到“目录规则”页测试或新建自定义规则。
4. 在书籍详情页查看目录、切换章节规则并重新解析。
5. 进入阅读页继续阅读，系统会按 `chapter_index + char_offset` 同步进度。
6. 根据需要调整字体大小、行高、主题，并使用书架分组整理书籍。

## 安装启动

本项目当前推荐且明确支持的启动方式是 `docker compose`。

### 运行前准备

- 已安装 Docker Desktop
- 已启用 Docker Compose

### 1. 准备环境变量

在项目根目录复制一份环境变量文件：

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

如需修改端口、默认账号或密钥，请编辑根目录 [`.env.example`](./.env.example) 对应生成的 `.env`。

最常用的几个变量：

- `BACKEND_PORT`：宿主机后端端口，默认 `8000`
- `FRONTEND_PORT`：宿主机前端端口，默认 `5173`
- `VITE_API_BASE_URL`：前端构建时使用的后端地址，默认 `http://localhost:8000`
- `CORS_ORIGINS`：允许访问后端的浏览器来源
- `SECRET_KEY`：后端 token 签名密钥
- `DEFAULT_ADMIN_USERNAME`：默认管理员用户名
- `DEFAULT_ADMIN_PASSWORD`：默认管理员密码

如果你修改了 `BACKEND_PORT` 或 `FRONTEND_PORT`，建议同时检查并更新：

- `VITE_API_BASE_URL`
- `CORS_ORIGINS`

这样可以避免前端仍然访问旧地址。

### 2. 启动服务

```bash
docker compose up --build -d
```

首次启动时，后端会自动完成以下初始化：

- 创建 `backend/data/` 数据目录
- 创建 `backend/uploads/` 上传目录
- 初始化 SQLite 数据库
- 创建所有数据表
- 写入内置章节规则
- 创建默认管理员账号
- 为已有用户补齐默认书架分组

### 3. 访问地址

- 前端：`http://localhost:5173`
- 后端接口：`http://localhost:8000`
- Swagger 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

### 4. 常用运维命令

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

停止服务：

```bash
docker compose down
```

## 默认账号

首次初始化时，系统会自动写入一个默认管理员：

- 用户名：`admin`
- 密码：`admin123`

如需修改，请在第一次启动前编辑项目根目录 `.env` 中的：

- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_PASSWORD`

注意：

- 这两个值只会在“默认管理员尚不存在”时生效。
- 如果数据库已经初始化过，单纯修改 `.env` 不会自动重置已有账号密码。
- 当前 SQLite 数据库默认保存在 `backend/data/app.db`。如果你是本地测试环境，且确认可以清空已有数据，可以删除该数据库后重新执行 `docker compose up --build -d` 让系统重新初始化。

## 目录结构

下面是当前仓库中与开发和运行直接相关的真实结构：

```text
.
├─ backend/
│  ├─ app/
│  │  ├─ core/             # 配置、数据库、依赖、鉴权、异常处理
│  │  ├─ models/           # SQLAlchemy 模型
│  │  ├─ routers/          # FastAPI 路由
│  │  ├─ schemas/          # Pydantic 数据结构
│  │  ├─ services/         # 业务逻辑
│  │  ├─ utils/            # 编码、正则、文件等工具
│  │  ├─ init_data.py      # 初始化建库与种子数据
│  │  └─ main.py           # 后端入口
│  ├─ tests/               # 后端测试
│  ├─ data/                # SQLite 数据目录（运行期）
│  ├─ uploads/             # TXT 原始文件与标准化文本（运行期）
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ README.md
├─ frontend/
│  ├─ src/
│  │  ├─ api/              # 前端 API 请求封装
│  │  ├─ components/       # 通用组件与弹窗
│  │  ├─ layouts/          # 应用布局
│  │  ├─ pages/            # 登录、书架、详情、阅读、规则管理页面
│  │  ├─ router/           # 路由与鉴权守卫
│  │  ├─ stores/           # Pinia 状态
│  │  ├─ styles/           # 全局样式
│  │  ├─ types/            # 前后端类型定义
│  │  ├─ utils/            # token、格式化等工具
│  │  └─ main.ts           # 前端入口
│  ├─ Dockerfile
│  ├─ nginx.conf
│  ├─ package.json
│  └─ README.md
├─ docs/
│  └─ IMPLEMENTATION_STEPS.md
├─ docker-compose.yml
├─ .env.example
└─ README.md
```

## 功能说明

### 1. 登录与认证

- 后端提供 `POST /api/auth/login` 和 `GET /api/auth/me`
- 前端登录态由 Pinia 管理，并把 token 保存在浏览器 `localStorage`
- 刷新页面后会自动恢复登录态
- 未登录状态下访问业务页会被路由守卫重定向到登录页

### 2. 书架

- 展示当前用户书籍列表
- 支持按书名搜索
- 支持上传 TXT
- 支持删除书籍
- 支持显示最近阅读时间和阅读百分比
- 支持继续阅读
- 支持为书籍分配分组

书架分组是当前仓库中的真实功能，不是占位设计：

- 可以创建、重命名、删除分组
- 系统会自动维护默认分组
- 书籍至少保留一个分组，避免出现“无分组书籍”

### 3. TXT 上传与章节解析

- 仅支持上传 `.txt` 文件
- 原始文件会保存到本地磁盘
- 后端会检测编码并尽量兼容：
  - `UTF-8`
  - `GBK`
  - `UTF-16`
- 标准化后的正文会按 UTF-8 保存
- 上传后会立即按当前规则解析章节并写入数据库

如果没有匹配到任何章节，系统不会报错中断，而是自动降级为“全文单章节模式”，保证书仍然可读。

### 4. 书籍详情与目录

- 查看书名、作者、文件信息、编码、总章节数、总字数
- 查看当前使用的章节规则
- 查看目录列表
- 从任意章节直接进入阅读页
- 在详情页切换规则并重新解析整本书

### 5. 目录规则管理

当前仓库已经实现完整的规则管理链路：

- 查看内置规则和自定义规则
- 新增、编辑、删除自定义规则
- 设置默认规则
- 测试规则是否能命中文本
- 直接把某条规则应用到某本书并触发重新解析

内置规则至少包含：

- 中文章节规则
- 英文章节规则
- 卷章混合规则
- 单章节全文模式

### 6. 阅读页

阅读页是目前前端里实现最完整的业务页面之一，支持：

- 按章节加载正文，而不是整本书一次性返回
- 上一章 / 下一章切换
- 目录抽屉
- 设置抽屉
- 沉浸式阅读布局
- PC 与移动端响应式适配

### 7. 阅读进度同步

进度同步的真实逻辑是：

- 以 `chapter_index + char_offset` 为主
- `percent` 主要用于展示
- 切换章节时立即保存
- 阅读过程中按节流策略自动同步
- 页面关闭前尝试再次保存

后端在进度冲突时会优先保留 `updated_at` 更新更晚的记录。

## 个性化调整

### 1. 自定义章节识别规则

这是项目最核心的个性化能力之一。

你可以：

- 自定义正则表达式
- 自定义 flags，例如 `MULTILINE`、`IGNORECASE`
- 在规则管理页直接测试真实匹配结果
- 将规则设为默认规则
- 将规则应用到某一本书并立即重解析

这意味着不同来源、不同排版风格的 TXT 小说，都可以根据自己的标题格式定制解析逻辑。

### 2. 阅读偏好

阅读页当前支持以下个性化设置：

- 字体大小
- 行高
- 浅色 / 深色主题

这些设置保存在浏览器 `localStorage` 中，属于设备本地偏好，不依赖后端数据库。

### 3. 书架整理方式

除了阅读设置，项目还支持按分组整理书架：

- 自定义分组名称
- 为同一本书分配多个分组
- 在书架页按分组筛选

这更偏向“书架组织方式”的个性化，而不是阅读器样式个性化。

## 常见问题

### 1. 启动后无法访问前端或后端

先检查容器是否正常运行：

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

默认访问地址是：

- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`

如果你修改了端口，请确认 `.env` 中的：

- `BACKEND_PORT`
- `FRONTEND_PORT`
- `VITE_API_BASE_URL`
- `CORS_ORIGINS`

是一致的。

### 2. 为什么修改了默认账号密码，登录还是旧账号？

因为默认账号只在“数据库里还没有这个用户”时写入一次。

如果 `backend/data/app.db` 已经存在并且管理员已创建，修改 `.env` 不会自动覆盖旧账号。

### 3. 上传 TXT 后没有识别出目录怎么办？

这是预期内可恢复的情况。

系统会自动降级为“全文”单章节模式，保证可以继续阅读。之后你可以：

- 到“目录规则”页测试现有规则
- 新建自定义规则
- 回到书籍详情页重新解析目录

### 4. 为什么某些 TXT 会提示编码不支持？

当前真实实现主要支持：

- UTF-8
- GBK
- UTF-16

如果文件使用了其他编码，后端会直接返回友好错误，而不会错误入库。

### 5. 为什么分组删不掉？

如果某个分组下有书籍只属于这一个分组，后端会阻止删除，避免书籍变成“完全没有分组”的状态。

### 6. 阅读设置会不会跨设备同步？

不会。

当前仓库里：

- 阅读进度会同步到后端
- 阅读样式偏好保存在浏览器本地 `localStorage`

所以换设备后，阅读位置可以恢复，但字体大小、行高、主题等设置不会自动带过去。

## 后续扩展建议

结合当前真实仓库结构，比较自然的下一步扩展方向有：

### 1. 增加前端自动化测试

目前后端测试已经比较完整，前端更偏真实页面实现和手动联调。可以考虑补充：

- 关键页面的组件测试
- 登录、上传、阅读链路的端到端测试
- Docker 部署后的 smoke test

### 2. 增强书籍元数据管理

当前书籍上传后，标题主要来自文件名，作者和描述默认较弱。可以继续补：

- 编辑作者
- 编辑简介
- 自定义封面
- 最近阅读排序 / 分组排序

### 3. 增强阅读器能力

当前阅读器已具备核心能力，但还可以继续扩展：

- 更多主题方案
- 段落间距和页边距设置
- 目录搜索
- 阅读统计
- 书签 / 批注

### 4. 增加数据备份与迁移能力

项目当前使用 SQLite 和本地上传目录，很适合做个人数据备份。后续可以考虑：

- 导出数据库与上传文件
- 导入备份
- 迁移到新机器

### 5. 明确依赖版本与交付边界

当前仓库已有 Docker 化部署能力，但还可以进一步增强可维护性：

- 增加更严格的依赖锁定策略
- 增加发布说明
- 增加升级与数据兼容说明

## 补充说明

- 后端还有单独的快速说明文档：[`backend/README.md`](./backend/README.md)
- 前端还有单独的说明文档：[`frontend/README.md`](./frontend/README.md)
- 开发过程文档在：[`docs/IMPLEMENTATION_STEPS.md`](./docs/IMPLEMENTATION_STEPS.md)

如果你接下来要继续整理交付文档，最值得优先补的是：

- Docker 部署后的数据备份说明
- 规则编写示例库
- 常见 TXT 格式对应的正则模板
