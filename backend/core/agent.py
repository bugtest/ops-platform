"""运维平台核心模块 - 封装nanobot agent"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator


class AgentManager:
    """nanobot Agent封装管理器 - 简化版"""
    
    def __init__(self, workspace: Path, plugins_dir: Path):
        self.workspace = workspace
        self.plugins_dir = plugins_dir
        self._process: asyncio.subprocess.Process | None = None
    
    async def start(self):
        """启动agent（暂不需要）"""
        pass
    
    async def stop(self):
        """停止agent"""
        if self._process:
            self._process.terminate()
            self._process = None
    
    async def chat(self, message: str, session_id: str = "web:default") -> str:
        """
        对话（同步返回完整响应）
        使用nanobot agent命令
        """
        cmd = [
            "nanobot", "agent",
            "-m", message,
            "-s", session_id,
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace),
            )
            stdout, stderr = await proc.communicate()
            
            if stderr:
                print(f"nanobot stderr: {stderr.decode()}")
            
            return stdout.decode()
        except FileNotFoundError:
            return "Error: nanobot command not found. Please install nanobot first."
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def chat_stream(self, message: str, session_id: str = "web:default") -> AsyncGenerator[str, None]:
        """
        流式对话（逐字返回）
        使用nanobot agent命令
        """
        cmd = [
            "nanobot", "agent",
            "-m", message,
            "-s", session_id,
            "--no-markdown",
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace),
            )
            
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                yield line.decode()
            
            await proc.wait()
            
        except FileNotFoundError:
            yield "Error: nanobot command not found."
        except Exception as e:
            yield f"Error: {str(e)}"


_agent_manager: AgentManager | None = None


def get_agent_manager() -> AgentManager:
    """获取全局AgentManager实例"""
    global _agent_manager
    if _agent_manager is None:
        raise RuntimeError("AgentManager not initialized")
    return _agent_manager


async def init_agent(workspace: Path, plugins_dir: Path):
    """初始化AgentManager"""
    global _agent_manager
    _agent_manager = AgentManager(workspace, plugins_dir)
    await _agent_manager.start()


async def close_agent():
    """关闭AgentManager"""
    global _agent_manager
    if _agent_manager:
        await _agent_manager.stop()
        _agent_manager = None
