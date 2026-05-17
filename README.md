# Online Judge

一个面向王道数据结构代码题的前后端分离 OJ 系统原型。

## 功能

- 在线编写 C++ 代码，编辑器支持语法高亮
- 编辑器额外高亮 `cin / cout / cerr / clog / endl`
- 提交后自动编译、运行并返回判题结果
- 支持先运行公开样例，查看期望输出、实际输出和差异
- 只上传原始题面，由 DeepSeek 自动生成题目结构、公开样例、隐藏测试点和参考解
- Django REST 后端、React + TypeScript 前端、PostgreSQL 数据库

## 技术栈

- 后端：Django、Django REST Framework
- 前端：React、TypeScript、Vite、Monaco Editor
- 数据库：PostgreSQL
- 判题：本地 `g++` 编译 + 进程执行

## 快速开始

1. 启动 PostgreSQL：

```bash
docker compose up -d
```

2. 配置后端环境：

```bash
cd backend
copy .env.example .env
```

3. 使用 `uv` 安装后端依赖并运行：

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

4. 安装前端依赖并运行：

```bash
cd frontend
npm install
npm run dev
```

## 运行要求

- Python 3.11+
- uv
- Node.js 20+
- PostgreSQL 16+
- C++ 编译器，默认读取 `CPP_COMPILER=g++`
- 当前支持 `C++11 / C++14 / C++17`，默认使用 `C++14`

## WSL 开发方式

如果在 Windows 上使用 WSL2 开发，推荐把 PostgreSQL、`g++` 和 Django 后端都放在 Ubuntu 中运行：

```bash
# 仅首次配置
bash /mnt/d/Projects/OnlineJudge/scripts/setup_wsl.sh
bash /mnt/d/Projects/OnlineJudge/scripts/setup_backend_wsl.sh

# 启动后端
bash /mnt/d/Projects/OnlineJudge/scripts/run_backend_wsl.sh
```

当前默认配置位于 `backend/.env.example`，本地开发时可复制为 `backend/.env` 后按需调整。

## DeepSeek 配置

在 `backend/.env` 中填写：

```env
DEEPSEEK_API_KEY=your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

上传题目接口依赖 DeepSeek，未配置密钥时会返回错误。

## 文档

- [需求文档](docs/requirements.md)
- [技术文档](docs/technical-design.md)

## GitHub

- 个人主页：[yCyperSpace](https://github.com/yCyperSpace)

## License

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE)。
