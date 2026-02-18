"""Nginx 运维工具 - Python Tool 实现"""
import asyncio
import re
import yaml
from pathlib import Path
from typing import Any

try:
    import aiohttp
except ImportError:
    aiohttp = None

from nanobot.agent.tools.base import Tool


class NginxStatusTool(Tool):
    """检查nginx运行状态"""
    
    name = "nginx_status"
    description = "检查nginx进程运行状态"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, **kwargs: Any) -> str:
        cmd = ["pgrep", "-f", "nginx: master"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        
        if stdout.strip():
            return "✓ Nginx 进程正在运行"
        return "✗ Nginx 进程未运行"


class NginxTestConfigTool(Tool):
    """测试nginx配置"""
    
    name = "nginx_test_config"
    description = "检查nginx配置文件语法"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, **kwargs: Any) -> str:
        nginx_bin = self.config.get("nginx", {}).get("binary", "nginx")
        cmd = [nginx_bin, "-t"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        output = stdout.decode() + stderr.decode()
        
        if proc.returncode == 0:
            return f"✓ 配置检查通过\n{output}"
        return f"✗ 配置错误\n{output}"


class NginxReloadTool(Tool):
    """平滑重载nginx配置"""
    
    name = "nginx_reload"
    description = "平滑重载nginx配置（不中断服务）"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, **kwargs: Any) -> str:
        nginx_bin = self.config.get("nginx", {}).get("binary", "nginx")
        cmd = [nginx_bin, "-s", "reload"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            return "✓ Nginx 配置已重载"
        return f"✗ 重载失败: {stderr.decode()}"


class NginxRestartTool(Tool):
    """重启nginx"""
    
    name = "nginx_restart"
    description = "重启nginx服务"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, **kwargs: Any) -> str:
        cmd = ["systemctl", "restart", "nginx"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            return "✓ Nginx 已重启"
        return f"✗ 重启失败: {stderr.decode()}"


class NginxErrorSummaryTool(Tool):
    """nginx错误日志统计"""
    
    name = "nginx_error_summary"
    description = "统计nginx错误日志"
    parameters = {
        "type": "object",
        "properties": {
            "lines": {
                "type": "integer",
                "description": "读取的行数",
                "default": 100,
            }
        },
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, lines: int = 100, **kwargs: Any) -> str:
        error_log = self.config.get("nginx", {}).get("error_log", "/var/log/nginx/error.log")
        
        try:
            cmd = ["tail", f"-n{lines}", error_log]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return f"✗ 无法读取错误日志: {stderr.decode()}"
            
            content = stdout.decode()
            if not content.strip():
                return "没有错误日志"
            
            error_counts: dict[str, int] = {}
            for line in content.split("\n"):
                match = re.search(r"(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.*)", line)
                if match:
                    error_type = match.group(3)[:50]
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            if not error_counts:
                return f"最近{lines}行没有错误"
            
            sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
            result = f"错误日志统计 (最近{lines}行):\n"
            for error, count in sorted_errors[:10]:
                result += f"  {count:4d}x  {error}\n"
            return result
            
        except FileNotFoundError:
            return f"✗ 错误日志文件不存在: {error_log}"


class NginxAccessStatsTool(Tool):
    """nginx访问日志统计"""
    
    name = "nginx_access_stats"
    description = "统计nginx访问日志"
    parameters = {
        "type": "object",
        "properties": {
            "lines": {
                "type": "integer",
                "description": "读取的行数",
                "default": 1000,
            }
        },
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, lines: int = 1000, **kwargs: Any) -> str:
        access_log = self.config.get("nginx", {}).get("access_log", "/var/log/nginx/access.log")
        
        try:
            cmd = ["tail", f"-n{lines}", access_log]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return f"✗ 无法读取访问日志: {stderr.decode()}"
            
            content = stdout.decode()
            if not content.strip():
                return "没有访问日志"
            
            ip_counts: dict[str, int] = {}
            url_counts: dict[str, int] = {}
            status_counts: dict[str, int] = {}
            
            for line in content.split("\n"):
                parts = line.split()
                if len(parts) >= 9:
                    ip = parts[0]
                    status = parts[8]
                    url = parts[6]
                    
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
                    url_counts[url] = url_counts.get(url, 0) + 1
                    if status.isdigit():
                        status_counts[status] = status_counts.get(status, 0) + 1
            
            result = f"访问日志统计 (最近{lines}行):\n\n"
            
            result += "TOP IP:\n"
            for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                result += f"  {count:5d}x  {ip}\n"
            
            result += "\nTOP URL:\n"
            for url, count in sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                result += f"  {count:5d}x  {url}\n"
            
            result += "\n状态码:\n"
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                result += f"  {count:5d}x  {status}\n"
            
            return result
            
        except FileNotFoundError:
            return f"✗ 访问日志文件不存在: {access_log}"


class NginxConnectionsTool(Tool):
    """nginx连接状态（需要stub_status）"""
    
    name = "nginx_connections"
    description = "查看nginx连接状态（需要配置stub_status）"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    async def execute(self, **kwargs: Any) -> str:
        status_url = self.config.get("nginx", {}).get("status_url", "http://127.0.0.1/nginx_status")
        
        if not aiohttp:
            return "✗ 需要安装 aiohttp: pip install aiohttp"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(status_url) as resp:
                    if resp.status != 200:
                        return f"✗ stub_status 返回 {resp.status}"
                    
                    text = await resp.text()
                    
                    result = "Nginx 连接状态:\n"
                    
                    for line in text.split("\n"):
                        if "Active connections" in line:
                            result += f"  {line.strip()}\n"
                        elif "server accepts" in line:
                            result += f"  {line.strip()}\n"
                        elif "Reading" in line:
                            result += f"  {line.strip()}\n"
                    
                    return result
                    
        except aiohttp.ClientError as e:
            return f"✗ 无法连接 stub_status: {e}"


def load_config() -> dict[str, Any]:
    """加载nginx插件配置"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def get_nginx_tools() -> list[Tool]:
    """获取所有nginx工具"""
    config = load_config()
    return [
        NginxStatusTool(config),
        NginxTestConfigTool(config),
        NginxReloadTool(config),
        NginxRestartTool(config),
        NginxErrorSummaryTool(config),
        NginxAccessStatsTool(config),
        NginxConnectionsTool(config),
    ]
