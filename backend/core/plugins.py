"""插件管理器"""
import json
import yaml
from pathlib import Path
from typing import Any


class Plugin:
    """运维插件"""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.enabled = False
        
        # 加载配置
        config_file = path / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}
        
        # 加载 Skill
        skill_file = path / "SKILL.md"
        if skill_file.exists():
            with open(skill_file, 'r') as f:
                self.skill_content = f.read()
        else:
            self.skill_content = ""
    
    def enable(self):
        """启用插件"""
        self.enabled = True
    
    def disable(self):
        """禁用插件"""
        self.enabled = False
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "config": self.config,
            "has_skill": bool(self.skill_content),
        }


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self._plugins: dict[str, Plugin] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """加载所有插件"""
        if not self.plugins_dir.exists():
            return
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                plugin = Plugin(item)
                self._plugins[plugin.name] = plugin
    
    def list_plugins(self) -> list[dict[str, Any]]:
        """列出所有插件"""
        return [p.to_dict() for p in self._plugins.values()]
    
    def get_plugin(self, name: str) -> Plugin | None:
        """获取插件"""
        return self._plugins.get(name)
    
    def enable_plugin(self, name: str) -> bool:
        """启用插件"""
        plugin = self._plugins.get(name)
        if plugin:
            plugin.enable()
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """禁用插件"""
        plugin = self._plugins.get(name)
        if plugin:
            plugin.disable()
            return True
        return False
    
    def update_config(self, name: str, config: dict[str, Any]) -> bool:
        """更新插件配置"""
        plugin = self._plugins.get(name)
        if plugin:
            plugin.config = config
            # 保存到文件
            config_file = plugin.path / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        return False
    
    def get_enabled_plugins(self) -> list[str]:
        """获取已启用的插件名"""
        return [p.name for p in self._plugins.values() if p.enabled]


_plugin_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """获取全局PluginManager实例"""
    global _plugin_manager
    if _plugin_manager is None:
        raise RuntimeError("PluginManager not initialized")
    return _plugin_manager


def init_plugins(plugins_dir: Path):
    """初始化PluginManager"""
    global _plugin_manager
    _plugin_manager = PluginManager(plugins_dir)
