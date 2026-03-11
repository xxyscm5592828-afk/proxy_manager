# Web 视频转码管理器

基于 FastAPI + React 的 Web 版视频转码任务管理系统，支持批量转码视频为代理文件（低分辨率版本）。

##🌟 功能特性

-✅ 批量上传视频文件
-✅ 支持多种编码格式（H.264/H.265/VP9/ProRes）
-✅ 多种分辨率选择（1080p/720p/480p/360p）
-✅ 实时转码进度显示
-✅ 任务管理（启动/暂停/删除）
-✅ 支持文件拖拽上传
-✅ 响应式 UI 设计

<img width="2400" height="1656" alt="a62e488647fd105441d28cacb603c43e" src="https://github.com/user-attachments/assets/feecfcf8-a385-4f7f-b2cd-c0fde8879251" />
<img width="1600" height="1496" alt="3b110ab3d1c10c6a54133b1cdd304b61" src="https://github.com/user-attachments/assets/0669ff14-2e25-4252-8a15-9ee9ed90803c" />
<img width="2400" height="1656" alt="93d547ed58931b05c53b17de49f2f384" src="https://github.com/user-attachments/assets/4cec2524-0b2d-43d8-90f0-d3174a5e647d" />



## 📦 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **FFmpeg** - 视频转码核心
- **Uvicorn** - ASGI 服务器
- **WebSockets** - 实时进度推送

### 前端
- **React 18** - UI 框架
- ** TypeScript** - 类型安全
- **Ant Design** - UI 组件库
- **Vite** - 构建工具
- **Axios** - HTTP 客户端

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- FFmpeg

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/web-proxy-manager.git
cd 网络代理管理器
```

### 2. 安装后端依赖

```bash
cd 后端
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd ../frontend
npm 安装
```

### 4. 启动后端服务

```bash
cd 后端
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端开发服务器

```bash
cd 前端
npm 运行开发
```

### 6. 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📁 项目结构

```
网页代理管理器/
│── backend/                    # 后端服务
│   ├── main.py                 # 应用入口
│   ├── api/
│   │   ├── routes.py           # API 路由
│   │   └── websocket.py        # WebSocket 连接
│   ├── core/
│   │   ├── transcode.py        # FFmpeg 转码引擎
│   │   └── task_manager.py     # 任务管理器
│   ├── models/
│   │   └── schemas.py          # 数据模型
│   ├── uploads/                # 上传的视频文件
│   └── outputs/                # 转码后的文件
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   └── TaskList.tsx    # 任务列表组件
│   │   ├── services/
│   │   │   ├── api.ts          # API 调用
│   │   │   └── websocket.ts    # WebSocket 服务
│   │   └── main.tsx            # 应用入口
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔧 配置说明

### 环境变量

创建 `frontend/.env` 文件：

```env
VITE_API_URL=http://localhost:8000
```

### 转码参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| codec | 编码格式 | libx264 |
| resolution | 分辨率 | 1280x720 |
| video_bitrate | 视频码率 | 2000k |
| audio_bitrate | 音频码率 | 128k |

## 🌐 部署

### 本地部署

参考 [快速开始](#-快速开始) 章节。

### 云端部署

#### Railway（后端）

1. 在 Railway 创建新项目
2. 连接 GitHub 仓库
3. 设置环境变量 `PORT=8000`
4. 部署

#### Vercel（前端）

1. 在 Vercel 导入项目
2. 设置环境变量 `VITE_API_URL=你的 Railway 地址`
3. 部署

详细部署指南请参考 [部署文档](./DEPLOYMENT.md)

## 📝 API 文档

启动后端后访问：http://localhost:8000/docs

### 主要接口

- `POST /api/tasks` - 创建转码任务
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/{id}` - 获取任务详情
- `POST /api/tasks/{id}/start` - 启动任务
- `POST /api/tasks/{id}/cancel` - 取消任务
- `DELETE /api/tasks/{id}` - 删除任务
- `GET /api/outputs/{filename}` - 下载转码文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 联系方式

- GitHub: [@你的用户名](https://github.com/你的用户名)
- Email: your@email.com

---

**注意**: 本项目需要安装 FFmpeg 才能正常使用转码功能。
