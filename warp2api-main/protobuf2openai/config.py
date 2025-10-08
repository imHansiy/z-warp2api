from __future__ import annotations

import os

bridge_host = os.getenv("WARP_BRIDGE_HOST", "127.0.0.1")
bridge_port = os.getenv("WARP_BRIDGE_PORT", "8000")
BRIDGE_BASE_URL = os.getenv("WARP_BRIDGE_URL", f"http://{bridge_host}:{bridge_port}")
FALLBACK_BRIDGE_URLS = [
    BRIDGE_BASE_URL,
    f"http://{bridge_host}:{bridge_port}",
]

WARMUP_INIT_RETRIES = int(os.getenv("WARP_COMPAT_INIT_RETRIES", "10"))
WARMUP_INIT_DELAY_S = float(os.getenv("WARP_COMPAT_INIT_DELAY", "0.5"))
WARMUP_REQUEST_RETRIES = int(os.getenv("WARP_COMPAT_WARMUP_RETRIES", "3"))
WARMUP_REQUEST_DELAY_S = float(os.getenv("WARP_COMPAT_WARMUP_DELAY", "1.5")) 