# Contributing to OpenAI-Compatible AI Integration

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Home Assistant development environment
- Git

### Development Setup
```bash
# Clone the repository
git clone https://github.com/custom-components/qwenai.git
cd qwenai

# Install development dependencies
pip install -r requirements_dev.txt

# Set up pre-commit hooks
pre-commit install
```

## 🔧 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Write comprehensive docstrings
- Maintain async/await patterns throughout

### Security Requirements
- **Never log API keys or sensitive data**
- Validate all user inputs
- Use HTTPS for all external connections
- Implement proper error handling

### Performance Standards
- Use async/await for all I/O operations
- Implement proper connection pooling
- Add timeout protection for network calls
- Cache expensive operations when appropriate

## 🌍 Translation Contributions

We welcome translations for additional languages! 

### Adding a New Language
1. Create a new file in `translations/` directory
2. Follow the naming convention: `{language_code}.json`
3. Copy the structure from `translations/en.json`
4. Translate all strings while preserving JSON structure

### Current Languages
- `en.json` - English
- `zh.json` - 简体中文 (Simplified Chinese)
- `zh-Hant.json` - 繁體中文 (Traditional Chinese)
- `fr.json` - Français (French)
- `ru.json` - Русский (Russian)
- `it.json` - Italiano (Italian)
- `es.json` - Español (Spanish)

### Language Priority List
We're looking for contributions in:
- `de.json` - Deutsch (German)
- `ja.json` - 日本語 (Japanese)
- `ko.json` - 한국어 (Korean)
- `pt.json` - Português (Portuguese)
- `nl.json` - Nederlands (Dutch)
- `pl.json` - Polski (Polish)

## 🤖 AI Provider Support

### Adding New Provider Support
When adding support for a new OpenAI-compatible provider:

1. **Update constants** in `const.py`:
   ```python
   KNOWN_ENDPOINTS["new_provider"] = "https://api.example.com/v1"
   ```

2. **Test compatibility**:
   - API authentication
   - Model listing
   - Chat completions
   - Structured outputs (if supported)
   - Tool calling (if supported)

3. **Update documentation**:
   - Add provider to README.md
   - Include setup instructions
   - Document any provider-specific features

### Provider-Specific Considerations
- **Authentication**: Different API key formats
- **Rate Limits**: Provider-specific limits
- **Model Names**: Different naming conventions
- **Features**: Not all providers support all OpenAI features

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_init.py

# Run with coverage
pytest --cov=custom_components.qwenai
```

### Test Coverage Requirements
- Minimum 80% code coverage
- Test both success and failure scenarios
- Mock external API calls
- Test security validations

### Manual Testing Checklist
- [ ] Integration setup flow
- [ ] API key validation
- [ ] Multiple provider support
- [ ] Conversation functionality
- [ ] AI task functionality
- [ ] Error handling
- [ ] Multi-language UI

## 📝 Documentation

### Code Documentation
- Add docstrings to all public functions
- Include parameter and return type information
- Document security considerations
- Explain performance optimizations

### User Documentation
- Update README.md for new features
- Add usage examples
- Document configuration options
- Include troubleshooting guides

## 🐛 Bug Reports

### Before Submitting
1. Check existing issues
2. Reproduce the bug
3. Test with latest version
4. Check Home Assistant logs

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Home Assistant version:
- Integration version:
- AI Provider:
- Python version:

**Logs**
Include relevant log entries (remove sensitive data)
```

## 🎯 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this work?

**Alternative Solutions**
Other ways this could be implemented

**Additional Context**
Any other relevant information
```

## 🔒 Security Policy

### Reporting Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email security concerns to: [security@example.com]
- Include detailed information about the vulnerability
- We will respond within 48 hours

### Security Best Practices
- No hardcoded credentials
- Validate all inputs
- Use secure communication channels
- Implement proper authentication
- Follow OWASP guidelines

## 📋 Pull Request Process

### Before Submitting
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Run the test suite
7. Ensure code style compliance

### PR Template
```markdown
**Description**
Brief description of changes

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new security issues
```

### Review Process
1. Automated checks must pass
2. Code review by maintainers
3. Testing in development environment
4. Approval and merge

## 🏷️ Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Test with Home Assistant
- [ ] Create GitHub release
- [ ] Update documentation

## 🤝 Community

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on technical discussions

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community chat
- **Discord**: Real-time community support

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the OpenAI-Compatible AI Integration for Home Assistant! 🎉
