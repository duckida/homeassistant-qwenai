@echo off
REM Quick GitHub Setup Script for OpenAI-Compatible AI Integration (Windows)

echo 🚀 Setting up GitHub repository for OpenAI-Compatible AI Integration
echo ==================================================================

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "manifest.json" (
    echo ❌ Please run this script from the qwenai integration directory
    echo    Should contain manifest.json file
    pause
    exit /b 1
)

echo 📁 Current directory: %CD%

REM Initialize git repository
if not exist ".git" (
    echo 📦 Initializing Git repository...
    git init
) else (
    echo ✅ Git repository already initialized
)

REM Add all files
echo 📝 Adding files to Git...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Initial release: OpenAI-Compatible AI Integration v1.0.0" -m "✨ Features:" -m "- Universal OpenAI-compatible API support (QwenAI, OpenAI, Azure OpenAI, OpenRouter, etc.)" -m "- Multi-language support (7 languages)" -m "- Enhanced security and performance" -m "- Comprehensive documentation" -m "- Production-ready code quality" -m "" -m "🛡️ Security:" -m "- Secure API key handling" -m "- URL validation and HTTPS enforcement" -m "- Rate limiting protection" -m "- No credential logging" -m "" -m "⚡ Performance:" -m "- Full async/await implementation" -m "- Connection pooling" -m "- Smart retry logic" -m "- Memory optimization" -m "" -m "🌍 Supported Languages:" -m "- English, 简体中文, 繁體中文, Français, Русский, Italiano, Español"

echo 🏷️ Creating version tag...
git tag -a v1.0.0 -m "Release v1.0.0: Universal OpenAI-Compatible Integration"

echo.
echo ✅ Local Git repository setup complete!
echo.
echo 🌐 Next steps to publish on GitHub:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Run: git remote add origin ^<your-repo-url^>
echo 4. Run: git branch -M main
echo 5. Run: git push -u origin main
echo 6. Run: git push origin v1.0.0
echo.
echo 📋 Repository structure created:
echo ├── custom_components/qwenai/ (integration files)
echo ├── .github/ (GitHub templates)
echo ├── README.md (documentation)
echo ├── CONTRIBUTING.md (contributor guide)
echo ├── SECURITY.md (security policy)
echo ├── LICENSE (MIT license)
echo └── .gitignore (ignore rules)
echo.
echo 🎉 Ready for GitHub sharing!
echo.
pause
