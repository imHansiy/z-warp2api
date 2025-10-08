#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration settings for Warp API server

Contains environment variables, paths, and constants.
"""
import os
import pathlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Path configurations
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
PROTO_DIR = SCRIPT_DIR / "proto"
LOGS_DIR = SCRIPT_DIR / "logs"

# API configuration
WARP_URL = os.getenv("WARP_URL", "https://app.warp.dev/ai/multi-agent")

# Environment variables with defaults
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8002"))
WARP_JWT = os.getenv("WARP_JWT")

# Client headers configuration
CLIENT_VERSION = os.getenv("CLIENT_VERSION", "v0.2025.08.06.08.12.stable_02")
OS_CATEGORY = os.getenv("OS_CATEGORY", "Windows")
OS_NAME = os.getenv("OS_NAME", "Windows")
OS_VERSION = os.getenv("OS_VERSION", "11 (26100)")

# Protobuf field names for text detection
TEXT_FIELD_NAMES = ("text", "prompt", "query", "content", "message", "input")
PATH_HINT_BONUS = ("conversation", "query", "input", "user", "request", "delta")

# Response parsing configuration
SYSTEM_STR = {"agent_output.text", "server_message_data", "USER_INITIATED", "agent_output", "text"}

# JWT refresh configuration
REFRESH_TOKEN_B64 = os.getenv("REFRESH_TOKEN_B64")
REFRESH_URL = os.getenv("REFRESH_URL")