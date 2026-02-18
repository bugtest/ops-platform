"""插件管理API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from nanobot.core.plugins import get_plugin_manager

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


class PluginConfigRequest(BaseModel):
    config: dict[str, Any]


@router.get("")
async def list_plugins():
    """列出所有插件"""
    pm = get_plugin_manager()
    return {"plugins": pm.list_plugins()}


@router.get("/{name}")
async def get_plugin(name: str):
    """获取插件详情"""
    pm = get_plugin_manager()
    plugin = pm.get_plugin(name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin.to_dict()


@router.post("/{name}/enable")
async def enable_plugin(name: str):
    """启用插件"""
    pm = get_plugin_manager()
    if not pm.get_plugin(name):
        raise HTTPException(status_code=404, detail="Plugin not found")
    pm.enable_plugin(name)
    return {"status": "ok", "enabled": True}


@router.post("/{name}/disable")
async def disable_plugin(name: str):
    """禁用插件"""
    pm = get_plugin_manager()
    if not pm.get_plugin(name):
        raise HTTPException(status_code=404, detail="Plugin not found")
    pm.disable_plugin(name)
    return {"status": "ok", "enabled": False}


@router.get("/{name}/config")
async def get_plugin_config(name: str):
    """获取插件配置"""
    pm = get_plugin_manager()
    plugin = pm.get_plugin(name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"config": plugin.config}


@router.put("/{name}/config")
async def update_plugin_config(name: str, request: PluginConfigRequest):
    """更新插件配置"""
    pm = get_plugin_manager()
    if not pm.get_plugin(name):
        raise HTTPException(status_code=404, detail="Plugin not found")
    pm.update_config(name, request.config)
    return {"status": "ok"}
