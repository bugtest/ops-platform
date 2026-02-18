# 智能运维平台 (ops-platform)

基于 [nanobot](https://github.com/HKUDS/nanobot) 开发的智能运维平台，支持通过自然语言管理运维对象。

## 特性

- 🤖 **AI 对话界面** - 用自然语言管理运维对象
- 🔌 **插件系统** - 插件式架构，轻松扩展
- 🌐 **nginx 插件** - 示例：状态检查、配置测试、日志分析

## 技术栈

- **后端**: FastAPI + Python
- **前端**: Vue3 + Vite + TailwindCSS
- **核心**: nanobot Agent

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/bugtest/ops-platform.git
cd ops-platform
```

### 2. 安装后端依赖

```bash
cd backend
pip install fastapi uvicorn pydantic pyyaml aiohttp
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动服务

```bash
# 终端1: 启动后端
cd backend
python main.py

# 终端2: 启动前端
cd frontend
npm run dev
```

### 5. 访问

- 前端: http://localhost:5173
- API文档: http://localhost:8000/docs

## 使用示例

```
用户: nginx状态怎么样？
Agent: ✓ Nginx 进程正在运行

用户: 检查下配置
Agent: ✓ 配置检查通过

用户: 查看最近错误日志
Agent: 错误日志统计:
  15x upstream timed out
  8x connection reset
```

## 项目结构

```
ops-platform/
├── backend/           # FastAPI 后端
│   ├── main.py
│   ├── api/          # API 路由
│   └── core/         # 核心模块
├── frontend/         # Vue3 前端
│   └── src/
│       ├── views/    # 页面
│       └── components/
├── plugins/          # 运维插件
│   └── nginx/       # nginx 插件示例
└── README.md
```

## License

MIT
