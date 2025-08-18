# OpenAI-Compatible AI Integration for Home Assistant

[![GitHub Release](https://img.shields.io/github/release/custom-components/qwenai.svg?style=flat-square)](https://github.com/custom-components/qwenai/releases)
[![License](https://img.shields.io/github/license/custom-components/qwenai.svg?style=flat-square)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/custom-components/qwenai)

A powerful Home Assistant custom integration that provides conversation and AI task capabilities using **multiple OpenAI-compatible AI providers**. Originally designed for QwenAI (Alibaba Cloud), this integration is **universal** and works with any OpenAI-compatible API.

## 🎯 Supported AI Providers

| Provider | Base URL | Notes |
|----------|----------|-------|
| **QwenAI/Alibaba Cloud** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | Default, excellent Chinese support |
| **OpenAI** | `https://api.openai.com/v1` | GPT-3.5, GPT-4, GPT-4o models |
| **Azure OpenAI** | `https://your-resource.openai.azure.com/` | Enterprise OpenAI deployment |
| **OpenRouter** | `https://openrouter.ai/api/v1` | Access to 100+ models |
| **Anthropic** | Via compatibility layers | Claude models |
| **Local APIs** | `http://localhost:port/v1` | Ollama, LM Studio, etc. |

## ✨ Key Features

### 🛡️ Security & Privacy
- **Secure API Key Handling**: No logging of credentials, format validation
- **URL Validation**: HTTPS enforcement, private network protection
- **Rate Limiting**: Exponential backoff to prevent abuse
- **Timeout Protection**: All network operations have timeouts

### ⚡ Performance Optimizations
- **Async/Await Throughout**: Non-blocking operations
- **Connection Pooling**: Shared HTTP client with HA
- **Smart Retries**: Automatic retry with backoff
- **Memory Efficient**: Streaming model lists, proper resource cleanup

### 🌍 Multi-Language Support
- **8 Languages**: English, 简体中文, 繁體中文, Français, Русский, Italiano, Español
- **Localized UI**: Complete translation of setup flows
- **Unicode Support**: Full support for non-Latin characters

### 🤖 AI Capabilities
- **Conversation Agent**: Voice and text interactions with Home Assistant
- **AI Task Support**: Structured data generation with JSON schemas
- **Tool Calling**: Direct Home Assistant entity control
- **Custom Prompts**: Configurable system instructions

## 🚀 Installation

### HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations" → "Custom Repositories"
3. Add `https://github.com/custom-components/qwenai` as an integration
4. Install "OpenAI-Compatible AI Integration"
5. Restart Home Assistant

### Manual Installation
1. Download the latest release
2. Copy `custom_components/qwenai` to your HA `custom_components` folder
3. Restart Home Assistant

## ⚙️ Configuration

### 1. Get Your API Key

#### For QwenAI (Recommended for Chinese users):
1. Visit [DashScope Console](https://dashscope.console.aliyun.com/)
2. Create account and get API key
3. Models available: `qwen-turbo`, `qwen-plus`, `qwen-max`

#### For OpenAI:
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create API key
3. Models available: `gpt-3.5-turbo`, `gpt-4`, `gpt-4o`

#### For Azure OpenAI:
1. Set up Azure OpenAI resource
2. Get endpoint URL and API key
3. Use your deployment names as model IDs

### 2. Add Integration
1. Go to **Settings** → **Integrations**
2. Click **"Add Integration"**
3. Search for **"QwenAI"** or **"OpenAI-Compatible AI"**
4. Enter your API key
5. (Optional) Custom base URL for other providers

### 3. Configure Agents

#### Conversation Agent
- **Model**: Choose your AI model
- **System Prompt**: How the AI should behave
- **Home Assistant API**: Enable for device control
- **Max Tokens**: Response length (100-4000)
- **Temperature**: Creativity level (0.0-1.0)

#### AI Task Agent
- **Model**: Choose your AI model
- Used for structured data generation in automations

## 📖 Usage Examples

### Voice Control
```yaml
# Use in voice assistants
"Turn off all living room lights"
"Set bedroom temperature to 22 degrees"
"What's the weather like today?"
```

### Automation with AI Tasks
```yaml
automation:
  - alias: "AI Weekly Summary"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: ai_task.generate_data
        data:
          agent_id: qwenai.your_agent
          prompt: "Generate a weekly home summary"
          response_format:
            type: json_schema
            json_schema:
              name: weekly_summary
              schema:
                type: object
                properties:
                  energy_usage: {type: number}
                  security_events: {type: integer}
                  suggestions: {type: array}
```

### Conversation Service
```yaml
service: conversation.process
data:
  agent_id: conversation.qwen_agent
  text: "Turn on the kitchen lights and start coffee maker"
```

## 🔧 Advanced Configuration

### Custom Base URLs
Change the base URL in integration options to use different providers:

```
OpenAI: https://api.openai.com/v1
Azure: https://your-resource.openai.azure.com/
OpenRouter: https://openrouter.ai/api/v1
Local: http://localhost:1234/v1
```

### Performance Tuning
- **Connection Pool**: Automatically optimized
- **Timeouts**: 30s default, configurable
- **Retries**: 3 attempts with exponential backoff
- **Rate Limits**: Built-in protection

### Security Best Practices
- Use HTTPS endpoints only
- Rotate API keys regularly
- Monitor usage in provider dashboards
- Use least-privilege API keys when available

## 🛠️ Development

### Setting Up Development Environment
```bash
git clone https://github.com/custom-components/qwenai
cd qwenai
pip install -r requirements_dev.txt
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
- **Type Hints**: Full typing support
- **Security**: No credential logging
- **Performance**: Async throughout
- **Maintainability**: Clear documentation

## 🐛 Troubleshooting

### Common Issues

#### "Cannot connect to AI service"
- Verify API key is correct
- Check base URL format
- Test network connectivity
- Review Home Assistant logs

#### "Rate limit exceeded"
- Wait before retrying
- Check provider usage limits
- Consider upgrading API plan

#### "Invalid response format"
- Update to latest integration version
- Check model compatibility
- Verify JSON schema format

### Debug Logging
Add to `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.qwenai: debug
```

## 📋 Supported Models

### QwenAI Models
- `qwen-turbo`: Fast, cost-effective
- `qwen-plus`: Balanced performance
- `qwen-max`: Most capable
- `qwen-vl-plus`: Vision capabilities

### OpenAI Models
- `gpt-3.5-turbo`: Fast and efficient
- `gpt-4`: Advanced reasoning
- `gpt-4o`: Multimodal capabilities
- `gpt-4-turbo`: Latest improvements

### Azure OpenAI
- Use your deployment names
- Same model capabilities as OpenAI
- Enterprise security and compliance

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- Additional language translations
- Model-specific optimizations
- Documentation improvements
- Bug fixes and features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Home Assistant team for the excellent platform
- OpenAI for the API standard
- Alibaba Cloud for QwenAI models
- Community contributors and testers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/custom-components/qwenai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/custom-components/qwenai/discussions)
- **Documentation**: [Wiki](https://github.com/custom-components/qwenai/wiki)

---

**Made with ❤️ for the Home Assistant community**
    custom_components.qwenai: debug
```

## Advanced Configuration

### Custom Prompts
You can customize the system prompt for conversation agents to change the assistant's behavior, personality, or focus areas.

### Home Assistant API Integration
Enable specific Home Assistant APIs to allow the AI to:
- Control devices and entities
- Access sensor data
- Trigger automations
- Manage scenes and scripts

## Support

For issues and feature requests, please check:
1. Home Assistant logs for error details
2. DashScope service status
3. Your API key quota and permissions

## License

This integration is based on the Home Assistant OpenRouter integration and adapted for Qwen AI compatibility.
