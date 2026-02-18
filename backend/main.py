"""运维平台后端服务"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from nanobot.core import init_agent, close_agent, init_plugins
from nanobot.api import chat, plugins

app = FastAPI(
    title="智能运维平台 API",
    description="基于nanobot的智能运维平台",
    version="0.1.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(plugins.router)


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    # 获取工作目录
    workspace = Path.home() / ".nanobot"
    plugins_dir = Path(__file__).parent.parent / "plugins"
    
    # 初始化插件
    init_plugins(plugins_dir)
    
    # 初始化Agent（可选，简化版不需要）
    await init_agent(workspace, plugins_dir)
    
    print(f"运维平台启动完成")
    print(f"  Workspace: {workspace}")
    print(f"  Plugins: {plugins_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    await close_agent()


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智能运维平台 API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
