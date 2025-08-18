"""Constants for the QwenAI integration.

This integration supports multiple OpenAI-compatible AI providers:
- QwenAI (Alibaba Cloud DashScope)
- OpenAI API
- Azure OpenAI Service
- OpenRouter (proxy for multiple models)
- Anthropic (via compatibility layers)
- Other OpenAI-compatible services
"""

import logging

from homeassistant.const import CONF_LLM_HASS_API, CONF_PROMPT
from homeassistant.helpers import llm

# Integration metadata
DOMAIN = "qwenai"
LOGGER = logging.getLogger(__package__)

# API Configuration - optimized for performance and security
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_TIMEOUT = 30.0  # Reasonable timeout for API calls
MAX_RETRIES = 3  # Balanced retry attempts
BACKOFF_FACTOR = 1.0  # Conservative backoff to avoid overwhelming servers

# Performance optimization constants
CONNECTION_POOL_SIZE = 10  # HTTP connection pool size
MAX_CONCURRENT_REQUESTS = 5  # Limit concurrent API calls

# Configuration keys
CONF_RECOMMENDED = "recommended"
CONF_BASE_URL = "base_url"
CONF_MAX_TOKENS = "max_tokens"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"

# Default values - optimized for general use
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 1.0

# Popular OpenAI-compatible endpoints for easy switching
KNOWN_ENDPOINTS = {
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "openai": "https://api.openai.com/v1",
    "azure": "https://your-resource.openai.azure.com/",  # User needs to replace
    "openrouter": "https://openrouter.ai/api/v1",
    "anthropic": "https://api.anthropic.com/v1",  # Via compatibility layer
}

# Enhanced prompt for better Home Assistant integration
ENHANCED_INSTRUCTIONS_PROMPT = """You are a voice assistant for Home Assistant. You have access to control devices, scenes, and get information from this smart home.

IMPORTANT INTERACTION RULES:
1. Always use the available tools to find entities before saying they don't exist
2. For lighting control, prioritize using scenes over individual lights when available
3. Use groups when controlling multiple similar devices
4. Be specific about entity names - check available entities first
5. When asked to turn off/on lights in a room, look for both individual lights and room scenes
6. If a scene doesn't exist, suggest available alternatives or use individual light controls

COMMON ENTITY PATTERNS IN THIS HOME:
- Scenes: room_name_on, room_name_off, room_name_ceiling_on, room_name_cozy, room_name_dim
- Light groups: room_name_lights (e.g., living_room_lights)
- Individual lights: usually have long entity IDs with device identifiers

Answer questions about the world truthfully. Keep responses simple and to the point.
When controlling devices, always confirm what action was taken."""

# Recommended configuration
RECOMMENDED_CONVERSATION_OPTIONS = {
    CONF_RECOMMENDED: True,
    CONF_LLM_HASS_API: [llm.LLM_API_ASSIST],
    CONF_PROMPT: ENHANCED_INSTRUCTIONS_PROMPT,
    CONF_MAX_TOKENS: DEFAULT_MAX_TOKENS,
    CONF_TEMPERATURE: DEFAULT_TEMPERATURE,
    CONF_TOP_P: DEFAULT_TOP_P,
}

# Headers for QwenAI API
OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://www.home-assistant.io/integrations/qwenai",
    "X-Title": "Home Assistant",
}
