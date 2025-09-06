# xplc - AI-Powered CLI Error Explainer


**xplc** (XplainCrash) is a command-line tool that captures errors from failed commands and uses AI to provide clear explanations and fix suggestions. Never struggle with cryptic error messages again!

## ✨ Features

- 🤖 **AI-Powered Explanations**: Uses OpenAI, Claude, or Gemini to explain errors
- 🚀 **Zero Learning Curve**: Just prefix any command with `xplc`
- 🎨 **Beautiful Output**: Color-coded responses for better readability
- 🔧 **Multi-Provider Support**: Choose between OpenAI, Anthropic Claude, or Google Gemini
- ⚡ **Fast & Efficient**: Optimized prompts for quick, cost-effective responses

## 🎬 Demo

```bash
$ xplc python broken_script.py
Original command output:
  File "broken_script.py", line 5
    def my_function(
                   ^
SyntaxError: expected ':'

AI Explanation:
- Error: Missing colon at the end of function definition
- Fix: Add ':' after the function parameters: def my_function():
- Python function definitions require a colon to separate the header from the body
```

## 📦 Installation

### Install from Source
```bash
git clone https://github.com/owais-rizvi/xplc.git
cd xplc
pip install -e .
```

## 🔑 Setup

### 1. Get an API Key
Choose one of these AI providers:

| Provider | Free Tier | Cost | Setup Link |
|----------|-----------|------|------------|
| **Gemini** ⭐ | Very generous | Free | [Get API Key](https://makersuite.google.com/app/apikey) |
| **OpenAI** | $5 credit (expires) | Paid | [Get API Key](https://platform.openai.com/api-keys) |
| **Claude** | None | Paid | [Get API Key](https://console.anthropic.com/) |

> **Recommendation**: Start with Gemini for the best free experience!

### 2. Configure xplc
```bash
# Set your API key (replace with your actual key)
xplc config --set-key gemini YOUR_GEMINI_API_KEY

# Set as default provider (optional)
xplc config --default gemini

# Verify setup
xplc config --list
```

## 🚀 Usage

### Basic Usage
Simply prefix any command with `xplc`:

```bash
# Python errors
xplc python my_script.py

# JavaScript/Node.js errors
xplc node server.js
xplc npm start

# Java compilation errors
xplc javac MyClass.java

# Build system errors
xplc make
xplc cargo build

# Any command that might fail!
xplc your-command --with --arguments
```

### Advanced Usage
```bash
# Use a specific AI provider
xplc --provider openai python script.py

# Configuration management
xplc config --set-key openai your-openai-key
xplc config --set-key claude your-claude-key
xplc config --default claude
xplc config --list
```

## 🎯 Examples

### Python Syntax Error
```bash
$ xplc python broken.py
AI Explanation:
- Error: Missing colon at the end of the function definition
- Fix: Add a colon (:) after (a, b)
- The function definition in Python requires a colon to indicate the start of the function body
```

### Java Runtime Error
```bash
$ xplc java MyProgram
AI Explanation:
- Error: ArrayIndexOutOfBoundsException when accessing array element
- Fix: Check array bounds before accessing elements or verify your loop conditions
- The program tried to access index 5 in an array that only has 3 elements (indices 0-2)
```

### Node.js Module Error
```bash
$ xplc node server.js
AI Explanation:
- Error: Cannot find module 'express'
- Fix: Install the missing dependency with: npm install express
- The required module is not installed in your project's node_modules directory
```

## ⚙️ Configuration

xplc stores configuration in `~/.xplc/config.json`:

```json
{
  "default_provider": "gemini",
  "api_keys": {
    "gemini": "your-gemini-key",
    "openai": "your-openai-key"
  }
}
```

### Supported Providers

| Provider | Models Used | Notes |
|----------|-------------|-------|
| **Gemini** | gemini-1.5-flash-latest | Fast, generous free tier |
| **OpenAI** | gpt-3.5-turbo | Reliable, requires billing setup |
| **Claude** | claude-3-haiku-20240307 | High quality, pay-per-use only |

## 📊 Cost Optimization

xplc is designed to be cost-efficient:

- ✅ Sends only essential error context (stderr + exit code)
- ✅ Uses shorter, optimized prompts
- ✅ Limits response tokens (150 max)
- ✅ Supports free tier providers (Gemini)

**Typical costs per error explanation:**
- **Gemini**: Free ⭐
- **OpenAI**: ~$0.0005 
- **Claude**: ~$0.001
