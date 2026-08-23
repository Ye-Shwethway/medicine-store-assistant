from __future__ import annotations

from app.multi_agent_review import router as multi_agent_review_router
from app.native_agent_runtime import router as native_agent_runtime_router

# main.py already mounts the native runtime router. Keep this registration bounded
# to the native AI runtime surface so D4.8 does not add another transport layer.
native_agent_runtime_router.include_router(multi_agent_review_router)
