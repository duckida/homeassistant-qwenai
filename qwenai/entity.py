"""Base entity for QwenAI."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
import json
from typing import TYPE_CHECKING, Any, Literal

import openai
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.shared_params import FunctionDefinition, ResponseFormatJSONSchema
from openai.types.shared_params.response_format_json_schema import JSONSchema
import voluptuous as vol
from voluptuous_openapi import convert

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import CONF_MODEL
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, llm
from homeassistant.helpers.entity import Entity

from . import OpenRouterConfigEntry
from .const import DOMAIN, LOGGER

# Max number of back and forth with the LLM to generate a response
MAX_TOOL_ITERATIONS = 10


def _adjust_schema(schema: dict[str, Any]) -> None:
    """Adjust the schema to be compatible with OpenRouter API."""
    if schema["type"] == "object":
        if "properties" not in schema:
            return

        if "required" not in schema:
            schema["required"] = []

        # Process nested properties
        for prop, prop_info in schema["properties"].items():
            _adjust_schema(prop_info)

    elif schema["type"] == "array":
        if "items" not in schema:
            return

        _adjust_schema(schema["items"])


def _format_structured_output(
    name: str, schema: vol.Schema, llm_api: llm.APIInstance | None
) -> JSONSchema:
    """Format the schema to be compatible with OpenRouter API."""
    result: JSONSchema = {
        "name": name,
        "strict": True,
    }
    result_schema = convert(
        schema,
        custom_serializer=(
            llm_api.custom_serializer if llm_api else llm.selector_serializer
        ),
    )

    _adjust_schema(result_schema)

    result["schema"] = result_schema
    return result


def _format_tool(
    tool: llm.Tool,
    custom_serializer: Callable[[Any], Any] | None,
) -> ChatCompletionToolParam:
    """Format tool specification."""
    tool_spec = FunctionDefinition(
        name=tool.name,
        parameters=convert(tool.parameters, custom_serializer=custom_serializer),
    )
    if tool.description:
        tool_spec["description"] = tool.description
    return ChatCompletionToolParam(type="function", function=tool_spec)


def _convert_content_to_chat_message(
    content: conversation.Content,
) -> ChatCompletionMessageParam | None:
    """Convert any native chat message for this agent to the native format."""
    LOGGER.debug("_convert_content_to_chat_message=%s", content)
    if isinstance(content, conversation.ToolResultContent):
        return ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=content.tool_call_id,
            content=json.dumps(content.tool_result),
        )

    role: Literal["user", "assistant", "system"] = content.role
    if role == "system" and content.content:
        return ChatCompletionSystemMessageParam(role="system", content=content.content)

    if role == "user" and content.content:
        return ChatCompletionUserMessageParam(role="user", content=content.content)

    if role == "assistant":
        param = ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content.content,
        )
        if isinstance(content, conversation.AssistantContent) and content.tool_calls:
            param["tool_calls"] = [
                ChatCompletionMessageToolCallParam(
                    type="function",
                    id=tool_call.id,
                    function=Function(
                        arguments=json.dumps(tool_call.tool_args),
                        name=tool_call.tool_name,
                    ),
                )
                for tool_call in content.tool_calls
            ]
        return param
    LOGGER.warning("Could not convert message to Completions API: %s", content)
    return None


def _decode_tool_arguments(arguments: str) -> Any:
    """Decode tool call arguments."""
    try:
        if not arguments or arguments.strip() == "":
            return {}
        return json.loads(arguments)
    except json.JSONDecodeError as err:
        LOGGER.error("Failed to decode tool arguments: %s, raw arguments: %s", err, arguments)
        
        # Try to fix common JSON issues from QwenAI
        try:
            # Fix unquoted values like {"domain": scene} -> {"domain": "scene"}
            import re
            # Pattern to find unquoted values after colons
            fixed_args = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])', r': "\1"\2', arguments)
            LOGGER.debug("Attempting to fix JSON: %s -> %s", arguments, fixed_args)
            return json.loads(fixed_args)
        except json.JSONDecodeError:
            # If fix fails, return empty dict to prevent crash
            LOGGER.warning("Could not fix malformed JSON arguments, using empty dict: %s", arguments)
            return {}
        except Exception as fix_err:
            LOGGER.error("Error while trying to fix JSON: %s", fix_err)
            return {}


async def _transform_response(
    message: ChatCompletionMessage,
) -> AsyncGenerator[conversation.AssistantContentDeltaDict]:
    """Transform the OpenRouter message to a ChatLog format."""
    data: conversation.AssistantContentDeltaDict = {
        "role": message.role,
        "content": message.content,
    }
    if message.tool_calls:
        data["tool_calls"] = [
            llm.ToolInput(
                id=tool_call.id,
                tool_name=tool_call.function.name,
                tool_args=_decode_tool_arguments(tool_call.function.arguments),
            )
            for tool_call in message.tool_calls
        ]
    yield data


class OpenRouterEntity(Entity):
    """Base entity for QwenAI."""

    _attr_has_entity_name = True

    def __init__(self, entry: OpenRouterConfigEntry, subentry: ConfigSubentry) -> None:
        """Initialize the entity."""
        self.entry = entry
        self.subentry = subentry
        self.model = subentry.data[CONF_MODEL]
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    async def _async_handle_chat_log(
        self,
        chat_log: conversation.ChatLog,
        structure_name: str | None = None,
        structure: vol.Schema | None = None,
    ) -> None:
        """Generate an answer for the chat log."""

        model_args = {
            "model": self.model,
            "user": chat_log.conversation_id,
            "extra_headers": {
                "X-Title": "Home Assistant",
                "HTTP-Referer": "https://www.home-assistant.io/integrations/qwenai",
            },
            "extra_body": {
                "enable_thinking": False,  # Required for QwenAI non-streaming calls
            },
        }

        tools: list[ChatCompletionToolParam] | None = None
        if chat_log.llm_api:
            tools = [
                _format_tool(tool, chat_log.llm_api.custom_serializer)
                for tool in chat_log.llm_api.tools
            ]

        if tools:
            model_args["tools"] = tools

        model_args["messages"] = [
            m
            for content in chat_log.content
            if (m := _convert_content_to_chat_message(content))
        ]

        if structure:
            if TYPE_CHECKING:
                assert structure_name is not None
            model_args["response_format"] = ResponseFormatJSONSchema(
                type="json_schema",
                json_schema=_format_structured_output(
                    structure_name, structure, chat_log.llm_api
                ),
            )
            
            # QwenAI requires the word "json" to be mentioned in messages when using structured output
            json_mentioned = False
            for message in model_args["messages"]:
                if message.get("role") in ["system", "user"] and message.get("content"):
                    content = message.get("content", "").lower()
                    if "json" in content:
                        json_mentioned = True
                        break
            
            if not json_mentioned:
                # Add JSON instruction to the last user message or create a system message
                if model_args["messages"] and model_args["messages"][-1].get("role") == "user":
                    current_content = model_args["messages"][-1].get("content", "")
                    model_args["messages"][-1]["content"] = f"{current_content}\n\nPlease respond in JSON format as specified."
                else:
                    # Insert a system message at the beginning
                    system_msg = ChatCompletionSystemMessageParam(
                        role="system", 
                        content="You must respond in JSON format as requested."
                    )
                    model_args["messages"].insert(0, system_msg)

        client = self.entry.runtime_data

        for _iteration in range(MAX_TOOL_ITERATIONS):
            try:
                result = await client.chat.completions.create(**model_args)
            except openai.AuthenticationError as err:
                LOGGER.error("Authentication failed with QwenAI API: %s", err)
                raise HomeAssistantError("Invalid API key or authentication failed") from err
            except openai.RateLimitError as err:
                LOGGER.error("Rate limit exceeded on QwenAI API: %s", err)
                raise HomeAssistantError("API rate limit exceeded, please try again later") from err
            except openai.InternalServerError as err:
                LOGGER.error("QwenAI API internal server error: %s", err)
                raise HomeAssistantError("QwenAI API is experiencing issues, please try again later") from err
            except openai.BadRequestError as err:
                LOGGER.error("Bad request to QwenAI API: %s", err)
                raise HomeAssistantError(f"Invalid request parameters: {err}") from err
            except openai.APIConnectionError as err:
                LOGGER.error("Failed to connect to QwenAI API: %s", err)
                raise HomeAssistantError("Unable to connect to QwenAI API") from err
            except openai.APITimeoutError as err:
                LOGGER.error("QwenAI API request timed out: %s", err)
                raise HomeAssistantError("API request timed out") from err
            except openai.OpenAIError as err:
                LOGGER.error("Unexpected QwenAI API error: %s", err)
                raise HomeAssistantError(f"Unexpected API error: {err}") from err

            result_message = result.choices[0].message

            model_args["messages"].extend(
                [
                    msg
                    async for content in chat_log.async_add_delta_content_stream(
                        self.entity_id, _transform_response(result_message)
                    )
                    if (msg := _convert_content_to_chat_message(content))
                ]
            )
            if not chat_log.unresponded_tool_results:
                break
