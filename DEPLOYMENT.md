# 部署文档

## 部署到 Railway + Vercel

### 第一步：准备工作

1. 注册 GitHub 账号：https://github.com
2. 注册 Railway 账号：https://railway.app
3. 注册 Vercel 账号：https://vercel.com

### 第二步：上传到 GitHub

```bash
# 进入项目目录
cd web_proxy_manager

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Web Video Transcode Manager"

# 在 GitHub 创建新仓库后，添加远程仓库
git remote add origin https://github.com/你的用户名/web-proxy-manager.git

# 推送到 GitHub
git push -u origin main
```

### 第三步：部署后端到 Railway

1. 访问 https://railway.app
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 选择 `web-proxy-manager` 仓库
5. 选择 `backend` 目录作为 Root Directory
6. 添加环境变量：
   - `PORT`: `8000`
7. 点击 **"Deploy"**
8. 等待部署完成，复制生成的 URL（如 `https://xxx.railway.app`）

### 第四步：部署前端到 Vercel

1. 访问 https://vercel.com
2. 点击 **"Add New..."** → **"Project"**
3. 选择 `web-proxy-manager` 仓库
4. 配置构建设置：
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. 添加环境变量：
   - `VITE_API_URL`: `https://你的 railway-app.railway.app`
6. 点击 **"Deploy"**
7. 等待部署完成

### 第五步：访问你的应用

- **前端地址**: `https://你的应用.vercel.app`
- **后端 API**: `https://你的应用.railway.app`

---

## 部署到 Render

### 后端部署

1. 访问 https://render.com
2. 创建 **Web Service**
3. 连接 GitHub 仓库
4. 配置：
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `PORT`: `8000`
5. 部署

### 前端部署

同 Vercel 部署步骤。

---

## 部署到 Fly.io

### 安装 Fly CLI

```bash
# Windows
winget install fly.flyctl

# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

### 部署后端

```bash
cd backend

# 登录
fly auth login

# 创建应用
fly apps create your-app-name

# 设置环境变量
fly secrets set PORT=8000

# 部署
fly deploy
```

---

## 本地生产部署

### 使用 Docker

#### 1. 创建 Dockerfile (backend/Dockerfile)

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 构建并运行

```bash
cd backend
docker build -t web-proxy-manager-backend .
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/outputs:/app/outputs web-proxy-manager-backend
```

#### 3. 构建前端

```bash
cd frontend
npm run build
```

#### 4. 使用 Nginx 托管

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/web-proxy-manager/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 故障排查

### 前端无法连接后端

1. 检查 `VITE_API_URL` 环境变量是否正确
2. 确认后端服务正在运行
3. 检查 CORS 设置

### 转码失败

1. 确认 FFmpeg 已安装
2. 检查文件权限
3. 查看后端日志

### 部署后文件上传失败

1. 检查存储空间
2. 确认上传目录有写权限
3. 检查文件大小限制

---

## 成本估算

| 服务 | 免费额度 | 付费价格 | 适用场景 |
|------|----------|----------|----------|
| Railway | $5/月 | $5/月起 | 小型项目 |
| Vercel | 100GB/月 | $20/月 | 静态网站 |
| Render | 750 小时/月 | $7/月 | Web 服务 |
| Fly.io | 3 个容器 | $5/月 | 容器化应用 |

**建议**: 个人使用选择 Railway + Vercel 组合，性价比最高。
