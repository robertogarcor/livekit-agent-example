import sys
import types
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


if "livekit.agents" not in sys.modules:
    livekit_module = types.ModuleType("livekit")
    agents_module = types.ModuleType("livekit.agents")

    def _function_tool(*args, **kwargs):
        return lambda func: func

    class _RunContext:
        pass

    setattr(agents_module, "function_tool", _function_tool)
    setattr(agents_module, "RunContext", _RunContext)

    setattr(livekit_module, "agents", agents_module)
    sys.modules["livekit"] = livekit_module
    sys.modules["livekit.agents"] = agents_module
