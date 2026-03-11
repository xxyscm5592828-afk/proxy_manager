@echo off
chcp 65001 >nul
echo ========================================
echo Web 视频转码管理器 - GitHub 上传工具
echo ========================================
echo.
echo 此脚本将帮助你把项目上传到 GitHub
echo.

REM 检查 Git 是否安装
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误：未检测到 Git，请先安装 Git
    echo 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git 已安装 ✓
echo.

REM 获取用户名
set /p GITHUB_USERNAME="请输入你的 GitHub 用户名："
if "%GITHUB_USERNAME%"=="" (
    echo 错误：用户名不能为空
    pause
    exit /b 1
)

echo.
echo 请在 GitHub 上创建新仓库:
echo 1. 访问 https://github.com/new
echo 2. 仓库名称：web-proxy-manager
echo 3. 可见性：Public 或 Private（根据你的需求）
echo 4. 不要勾选 "Initialize this repository with a README"
echo 5. 点击 "Create repository"
echo.
pause

echo.
echo 创建完成后，请输入仓库 URL:
set /p REPO_URL="仓库 URL (如：https://github.com/你的用户名/web-proxy-manager.git): "

if "%REPO_URL%"=="" (
    set REPO_URL=https://github.com/%GITHUB_USERNAME%/web-proxy-manager.git
)

echo.
echo 正在添加远程仓库...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

if %ERRORLEVEL% NEQ 0 (
    echo 错误：添加远程仓库失败，请检查 URL 是否正确
    pause
    exit /b 1
)

echo 远程仓库添加成功 ✓
echo.
echo 正在推送到 GitHub...
git branch -M main
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 推送失败！可能的原因:
    echo 1. 网络连接问题
    echo 2. 认证失败（需要输入 GitHub 用户名和密码）
    echo 3. 仓库不存在
    echo.
    echo 如果是认证问题，请使用 Personal Access Token 代替密码
    echo 生成 Token: https://github.com/settings/tokens
    pause
    exit /b 1
)

echo.
echo ========================================
echo 上传成功！✓
echo ========================================
echo.
echo 你的项目已上传到：%REPO_URL%
echo.
echo 下一步:
echo 1. 访问 https://railway.app 部署后端
echo 2. 访问 https://vercel.com 部署前端
echo 3. 详细部署步骤请查看 DEPLOYMENT.md
echo.
pause
