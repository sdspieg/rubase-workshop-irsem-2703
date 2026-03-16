# CLI-Based LLM Setup Guide for the RuBase Workshop

## Don't Let the Terminal Intimidate You!

If you're a researcher who primarily uses graphical interfaces, don't worry! Using CLI tools for LLMs is just like having a conversation with ChatGPT, Claude, or Gemini in your browser - except you're typing in a terminal window instead.

**The key insight**: You'll interact with these AI assistants using the same natural language you already use. The LLMs do all the heavy lifting. You just need to:
1. Open a terminal (think of it as a text-based window)
2. Type your question or request in plain English
3. Press Enter

That's it! The AI responds just like it would in a browser. No programming required.

### Example Conversation
Instead of typing in a browser text box:
> "Summarize the main themes in this research paper"

You type in a terminal:
```bash
claude "Summarize the main themes in this research paper"
```

The only difference is where you're typing - the conversation itself is identical.

## Why CLI Instead of Browser?

We'll be using command-line interface (CLI) versions of LLMs for several important research advantages:

### Advantages of CLI LLMs

1. **Automation & Scripting**: CLI tools can be integrated into research pipelines and automated workflows
2. **Batch Processing**: Process multiple files or queries without manual copy-pasting
3. **Data Privacy**: Keep your research data local without uploading to web services
4. **Reproducibility**: Script your analysis for consistent, repeatable results
5. **Integration**: Seamlessly combine with other command-line research tools
6. **Performance**: No browser overhead, faster processing for large datasets
7. **Version Control**: Track your prompts and workflows in Git alongside your research

## Installation Guide

### For Windows Users

Windows users need to install WSL (Windows Subsystem for Linux) first, as most CLI LLM tools are designed for Unix-like environments.

#### Step 1: Install WSL (One Command!)

WSL installation has been dramatically simplified. You only need one command:

1. **Open PowerShell as Administrator**
   - Right-click the Start button
   - Select "Windows Terminal (Admin)" or "PowerShell (Admin)"

2. **Install WSL with a single command**
   ```powershell
   wsl --install
   ```
   This automatically:
   - Enables required Windows features
   - Installs WSL2
   - Downloads and installs Ubuntu (default distribution)
   - Sets up GPU support for AI workloads

3. **Restart your computer** when prompted

4. **Set up your Linux environment**
   - After restart, Ubuntu will open automatically
   - Create a username and password (remember these!)
   - That's it! You're ready to go

#### Alternative: Choose a Different Linux Distribution

To see available distributions:
```powershell
wsl --list --online
```

To install a specific distribution:
```powershell
wsl --install -d Debian
```

### For macOS Users

macOS is Unix-based, so you don't need WSL. Your Terminal app already provides the command-line environment we need.

#### No Additional Setup Required!

Unlike Windows, macOS comes ready to go. You can install the LLM tools directly using the installation commands in the next section.

**Optional**: Homebrew can make some installations easier, but it's NOT required. All the LLM tools can be installed without it using npm or direct downloads.

## Installing CLI LLM Tools

### Option 1: Claude Code (Anthropic)

Claude Code is Anthropic's official CLI tool - an agentic coding assistant that runs in your terminal.

**Official Documentation:**
- Main Docs: https://docs.anthropic.com/en/docs/claude-code
- GitHub: https://github.com/anthropics/claude-code
- Advanced Setup: https://code.claude.com/docs/en/setup

**Simplest Installation - No Dependencies:**
```bash
# One-command installation (works on Linux, macOS, WSL)
curl -fsSL https://claude.ai/install.sh | bash

# Open a new terminal window for PATH to update
```

**Alternative methods (if you already have these tools):**
```bash
# Via npm (if you already have Node.js)
npm install -g @anthropic-ai/claude-code

# Via Homebrew (if you already have it)
brew install claude-code
```

**Getting Started:**
```bash
# Start Claude Code
claude

# The first time you run it, you'll be prompted to authenticate
# Note: Requires Claude Pro subscription ($20/month)
```

### Option 2: OpenAI Codex CLI

OpenAI's official coding agent that runs locally in your terminal.

**Official Documentation:**
- Main Docs: https://developers.openai.com/codex/cli/
- GitHub: https://github.com/openai/codex
- Getting Started: https://help.openai.com/en/articles/11096431-openai-codex-cli-getting-started

**Simplest Installation:**
```bash
# Download the binary directly from GitHub (no dependencies!)
# Go to: https://github.com/openai/codex/releases
# Download the file for your system and run it

# Alternative methods (if you already have these tools):
# Via npm (if you have Node.js)
npm install -g @openai/codex

# Via Homebrew (if you have it)
brew install --cask codex
```

**Getting Started:**
```bash
# Start Codex
codex

# Authenticate with your OpenAI account or API key on first run
# Works with ChatGPT Plus, Pro, or API subscriptions
```

### Option 3: Google Gemini CLI

Google's terminal-based AI agent with built-in Google Search and other tools.

**Official Documentation:**
- Main Docs: https://geminicli.com/docs/
- GitHub: https://github.com/google-gemini/gemini-cli
- Getting Started: https://geminicli.com/docs/get-started/
- Google Cloud Docs: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli

**Simplest - No Installation Needed!**
```bash
# Run directly without installing anything
npx @google/gemini-cli

# Or if you want to install it:
# Via npm (if you have Node.js)
npm install -g @google/gemini-cli

# Via Homebrew (if you have it)
brew install gemini-cli
```

**Setup:**
```bash
# Set your Google API key
export GOOGLE_API_KEY="your-api-key-here"

# Start Gemini CLI
gemini
```

### Option 4: Universal LLM Tool (llm)

Simon Willison's `llm` provides a unified interface for multiple LLM providers - great for comparing models.

**Installation:**
```bash
# Install via pip
pip install llm

# Install plugins for different providers
llm install llm-claude-3
llm install llm-openai
llm install llm-gemini
```

**Setup:**
```bash
# Configure API keys
llm keys set claude
llm keys set openai
llm keys set gemini
```

**Usage:**
```bash
# Query different models
llm "Your prompt" -m claude-3-sonnet
llm "Your prompt" -m gpt-4-turbo
llm "Your prompt" -m gemini-pro

# Save conversation threads
llm "Analyze this" --continue research_thread

# Export results
llm logs --json > results.json
```

## Quick Test Commands

After installation, test your setup:

```bash
# Test Claude Code
claude --version

# Test OpenAI Codex
codex --version

# Test Gemini CLI
gemini --version

# Test llm tool
llm --version
```

## Troubleshooting

### Common Issues on Windows/WSL

1. **"Command not found"**:
   - Make sure you're running commands in WSL (Ubuntu), not PowerShell
   - Open a new terminal window after installation for PATH updates

2. **WSL Installation Issues**:
   - If `wsl --install` fails, ensure Windows is updated
   - Check that virtualization is enabled in BIOS

3. **Node.js/npm Not Found in WSL**:
   ```bash
   # Install Node.js in WSL
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

### Common Issues on macOS

1. **"Command not found"** after npm install:
   ```bash
   # Add npm global bin to PATH
   echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Permission errors with npm**:
   ```bash
   # Configure npm to use a different directory
   mkdir ~/.npm-global
   npm config set prefix '~/.npm-global'
   ```

## Workshop Preparation Checklist

### Windows Users
- [ ] WSL installed (`wsl --install` in PowerShell Admin)
- [ ] Restarted computer after WSL installation
- [ ] Created WSL username and password
- [ ] Can open Ubuntu/WSL terminal

### All Users
- [ ] At least one CLI LLM tool installed
- [ ] Have API key(s) ready for your chosen tool(s)
- [ ] Successfully ran a test command

## Pricing & Access Levels

### What You Can Do For Free

**Google Gemini CLI - FREE**
- ✅ 60 requests per minute
- ✅ 1,000 requests per day
- ✅ Access to powerful Gemini models
- ✅ 1M token context window
- ✅ Built-in web search and file operations
- Get your free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

### Paid Options

**Claude Code - $20/month (Claude Pro)**
- Full access to Claude's most capable models
- Unlimited* conversations in the CLI (*subject to fair use)
- Same subscription works for both web and CLI
- Sign up at [claude.ai](https://claude.ai)

**OpenAI Codex - Multiple Options**
- **ChatGPT Go** ($8/month): Basic enhanced features, limited CLI access
- **ChatGPT Plus** ($20/month): Full CLI access included
- **ChatGPT Pro Lite** ($100/month - coming soon): 3-5x Plus capacity, priority access
- **ChatGPT Pro** ($200/month): Unlimited access, highest priority
- **Pay-as-you-go API**: Use API credits instead of subscription
- Sign up at [platform.openai.com](https://platform.openai.com)

### For the Workshop

- **Best for trying it out**: Start with **Gemini CLI (FREE)**
- **If you already subscribe**: Use whichever service you're already paying for
- **For research projects**: Consider the $20/month tiers for unlimited usage
- **Minimum requirement**: One working CLI tool (free Gemini is perfect!)

## Quick Start Examples

Once installed, here are some research-focused examples:

```bash
# Literature review help
claude "Summarize the main themes in social media sentiment analysis research"

# Method extraction
codex "Extract the methodology from this paper" < paper.txt

# Data analysis
gemini "Identify patterns in this dataset" < data.csv

# Comparative analysis with llm tool
echo "What are the limitations of transformer models?" | llm -m gemini-pro
```

## Important Notes

- Keep API keys secure - never share or commit to Git
- Most tools cache responses to save on API calls
- Use `--help` flag with any tool for detailed options
- Check rate limits for your subscription tier