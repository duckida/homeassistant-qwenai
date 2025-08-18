#!/bin/bash
# Quick GitHub Setup Script for OpenAI-Compatible AI Integration

echo "🚀 Setting up GitHub repository for OpenAI-Compatible AI Integration"
echo "=================================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "❌ Please run this script from the qwenai integration directory"
    echo "   Should contain manifest.json file"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Initialize git repository
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📝 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial release: OpenAI-Compatible AI Integration v1.0.0

✨ Features:
- Universal OpenAI-compatible API support (QwenAI, OpenAI, Azure OpenAI, OpenRouter, etc.)
- Multi-language support (7 languages)
- Enhanced security and performance
- Comprehensive documentation
- Production-ready code quality

🛡️ Security:
- Secure API key handling
- URL validation and HTTPS enforcement
- Rate limiting protection
- No credential logging

⚡ Performance:
- Full async/await implementation
- Connection pooling
- Smart retry logic
- Memory optimization

🌍 Supported Languages:
- English, 简体中文, 繁體中文, Français, Русский, Italiano, Español"

echo "🏷️ Creating version tag..."
git tag -a v1.0.0 -m "Release v1.0.0: Universal OpenAI-Compatible Integration"

echo ""
echo "✅ Local Git repository setup complete!"
echo ""
echo "🌐 Next steps to publish on GitHub:"
echo "1. Create a new repository on GitHub.com"
echo "2. Copy the repository URL"
echo "3. Run: git remote add origin <your-repo-url>"
echo "4. Run: git branch -M main"
echo "5. Run: git push -u origin main"
echo "6. Run: git push origin v1.0.0"
echo ""
echo "📋 Repository structure created:"
echo "├── custom_components/qwenai/ (integration files)"
echo "├── .github/ (GitHub templates)"
echo "├── README.md (documentation)"
echo "├── CONTRIBUTING.md (contributor guide)"
echo "├── SECURITY.md (security policy)"
echo "├── LICENSE (MIT license)"
echo "└── .gitignore (ignore rules)"
echo ""
echo "🎉 Ready for GitHub sharing!"
