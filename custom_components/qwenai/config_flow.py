"""Config flow for QwenAI integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from openai import AsyncOpenAI, AuthenticationError, OpenAIError, RateLimitError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_API_KEY, CONF_LLM_HASS_API, CONF_MODEL
from homeassistant.core import callback
from homeassistant.helpers import llm
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TemplateSelector,
)

from .const import (
    BACKOFF_FACTOR,
    CONF_BASE_URL,
    CONF_PROMPT,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    MAX_RETRIES,
    OPENROUTER_HEADERS,
    RECOMMENDED_CONVERSATION_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_api_key(api_key: str, base_url: str, hass) -> tuple[bool, str | None]:
    """Validate API key with retry logic."""
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=get_async_client(hass),
        default_headers=OPENROUTER_HEADERS,
        timeout=DEFAULT_TIMEOUT,
    )
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Test connection by listing models
            async for _ in client.with_options(timeout=10.0).models.list():
                break
            return True, None
        except AuthenticationError:
            return False, "invalid_auth"
        except RateLimitError as err:
            if attempt < MAX_RETRIES:
                wait_time = BACKOFF_FACTOR * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
            return False, f"rate_limit_exceeded: {err}"
        except OpenAIError as err:
            if attempt < MAX_RETRIES:
                wait_time = BACKOFF_FACTOR * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
            return False, f"api_error: {err}"
        except Exception as err:
            return False, f"unknown_error: {err}"
    
    return False, "max_retries_exceeded"


async def _fetch_models(api_key: str, base_url: str, hass) -> list[dict[str, Any]]:
    """Fetch available models from the API."""
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=get_async_client(hass),
        default_headers=OPENROUTER_HEADERS,
        timeout=DEFAULT_TIMEOUT,
    )
    
    models = []
    try:
        async for model in client.models.list():
            models.append({
                "id": model.id,
                "name": getattr(model, "name", model.id),
                "description": getattr(model, "description", ""),
            })
    except Exception as err:
        _LOGGER.warning("Could not fetch models: %s", err)
    
    return models


class OpenRouterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for QwenAI."""

    VERSION = 1

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this handler."""
        return {
            "conversation": ConversationFlowHandler,
            "ai_task_data": AITaskDataFlowHandler,
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self._async_abort_entries_match({CONF_API_KEY: user_input[CONF_API_KEY]})
            
            base_url = user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL)
            
            try:
                is_valid, error_msg = await _validate_api_key(
                    user_input[CONF_API_KEY], base_url, self.hass
                )
                if not is_valid:
                    if "invalid_auth" in str(error_msg):
                        errors["base"] = "invalid_auth"
                    elif "rate_limit" in str(error_msg):
                        errors["base"] = "rate_limit"
                    else:
                        errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title="QwenAI",
                        data=user_input,
                    )
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
                
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                }
            ),
            errors=errors,
        )


class OpenRouterSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for QwenAI."""

    def __init__(self) -> None:
        """Initialize the subentry flow."""
        self.models: dict[str, dict[str, Any]] = {}

    async def _get_models(self) -> None:
        """Fetch models from QwenAI."""
        entry = self._get_entry()
        # Respect user-updated options first, then original config data, then default
        base_url = entry.options.get(CONF_BASE_URL, entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL))
        
        models = await _fetch_models(
            entry.data[CONF_API_KEY], 
            base_url,
            self.hass
        )
        self.models = {model["id"]: model for model in models}


class ConversationFlowHandler(OpenRouterSubentryFlowHandler):
    """Handle subentry flow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to create a conversation subentry."""
        if user_input is not None:
            if not user_input.get(CONF_LLM_HASS_API):
                user_input.pop(CONF_LLM_HASS_API, None)
            model_name = self.models.get(user_input[CONF_MODEL], {}).get("name", user_input[CONF_MODEL])
            return self.async_create_entry(
                title=model_name, data=user_input
            )
            
        try:
            await self._get_models()
        except Exception:
            _LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="cannot_connect")
            
        options = [
            SelectOptionDict(value=model_id, label=model_data.get("name", model_id))
            for model_id, model_data in self.models.items()
        ]

        hass_apis: list[SelectOptionDict] = [
            SelectOptionDict(
                label=api.name,
                value=api.id,
            )
            for api in llm.async_get_apis(self.hass)
        ]

        schema = {
            vol.Required(CONF_MODEL): SelectSelector(
                SelectSelectorConfig(
                    options=options,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_PROMPT,
                description={
                    "suggested_value": RECOMMENDED_CONVERSATION_OPTIONS.get(
                        CONF_PROMPT, llm.DEFAULT_INSTRUCTIONS_PROMPT
                    )
                },
            ): TemplateSelector(),
            vol.Optional(CONF_LLM_HASS_API): SelectSelector(
                SelectSelectorConfig(options=hass_apis, multiple=True)
            ),
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema),
        )


class AITaskDataFlowHandler(OpenRouterSubentryFlowHandler):
    """Handle subentry flow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to create an AI task subentry."""
        if user_input is not None:
            model_name = self.models.get(user_input[CONF_MODEL], {}).get("name", user_input[CONF_MODEL])
            return self.async_create_entry(
                title=model_name, data=user_input
            )
            
        try:
            await self._get_models()
        except Exception:
            _LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="cannot_connect")

        # Filter models that support structured outputs (if available)
        available_models = []
        for model_id, model_data in self.models.items():
            # For now, assume all models support AI tasks
            # In the future, we could filter based on model capabilities
            available_models.append(
                SelectOptionDict(value=model_id, label=model_data.get("name", model_id))
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODEL): SelectSelector(
                        SelectSelectorConfig(
                            options=available_models,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow to allow changing base_url (and future options)."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            # Save updated options; subentry flows will use this option when fetching models.
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_BASE_URL, self.config_entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_BASE_URL, default=current): str,
                }
            ),
        )


async def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowHandler:
    """Return the options flow handler for this config entry."""
    return OptionsFlowHandler(config_entry)
