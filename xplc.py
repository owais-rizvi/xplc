#!/usr/bin/env python3
"""
xplc (XplainCrash) - AI-powered CLI error explainer
Usage: xplc <command>
"""

import sys
import subprocess
import json
from pathlib import Path
import argparse
import requests
from typing import Dict, Any, Optional, Tuple
from colorama import Fore, Style, init

init(autoreset=True)

class Config:
    """Handle configuration and API keys"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.xplc'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def set_api_key(self, provider: str, key: str):
        if 'api_keys' not in self._config:
            self._config['api_keys'] = {}
        self._config['api_keys'][provider] = key
        self.save_config()
        print(Fore.GREEN + f"✓ {provider} API key saved")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        return self._config.get('api_keys', {}).get(provider)
    
    def set_default_provider(self, provider: str):
        self._config['default_provider'] = provider
        self.save_config()
        print(Fore.GREEN + f"✓ Default provider set to {provider}")
    
    def get_default_provider(self) -> str:
        return self._config.get('default_provider', 'openai')

class AIProvider:
    """Base class for AI providers"""
    
    def explain_error(self, error_context: Dict[str, Any]) -> str:
        raise NotImplementedError

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def explain_error(self, error_context: Dict[str, Any]) -> str:
        prompt = self._build_prompt(error_context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Failed to get AI explanation: {str(e)}"
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""Explain this command error briefly and suggest a fix:

Command: {context['command']}
Error: {context['stderr']}
Exit code: {context['exit_code']}


Respond in this exact format:
- Error: [brief error description]
- Fix: [concise fix suggestion]
- [one-line explanation]"""

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def explain_error(self, error_context: Dict[str, Any]) -> str:
        prompt = self._build_prompt(error_context)
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()["content"][0]["text"].strip()
        except Exception as e:
            return f"Failed to get AI explanation: {str(e)}"
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""Explain this command error briefly and suggest a fix:

Command: {context['command']}
Error: {context['stderr']}
Exit code: {context['exit_code']}

Respond in this exact format:
- Error: [brief error description]
- Fix: [concise fix suggestion]
- [one-line explanation]"""

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    def explain_error(self, error_context: Dict[str, Any]) -> str:
        prompt = self._build_prompt(error_context)
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 150,
                "temperature": 0.3
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            return f"Failed to get AI explanation: {str(e)}"
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""Explain this command error briefly and suggest a fix:

Command: {context['command']}
Error: {context['stderr']}
Exit code: {context['exit_code']}

Respond in this exact format:
- Error: [brief error description]
- Fix: [concise fix suggestion]
- [one-line explanation]"""

class ErrorExplainer:
    """Main class that runs commands and explains errors"""
    
    def __init__(self):
        self.config = Config()
        self.providers = {
            'openai': OpenAIProvider,
            'claude': ClaudeProvider,
            'gemini': GeminiProvider
        }
    
    def run_command(self, command_args: list) -> Tuple[str, str, int]:
        """Run command and capture output"""
        try:
            result = subprocess.run(
                command_args,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out after 30 seconds", 1
        except Exception as e:
            return "", f"Failed to run command: {str(e)}", 1
    
    
    def get_provider(self, provider_name: str = None) -> Optional[AIProvider]:
        """Get AI provider instance"""
        if not provider_name:
            provider_name = self.config.get_default_provider()
        
        api_key = self.config.get_api_key(provider_name)
        if not api_key:
            print(Fore.RED + f"No API key found for {provider_name}")
            print(Fore.YELLOW + f"Set it with: xplc config --set-key {provider_name} YOUR_API_KEY")
            return None
        
        if provider_name not in self.providers:
            print(Fore.RED + f"Unknown provider: {provider_name}")
            print(Fore.YELLOW + f"Available: {', '.join(self.providers.keys())}")
            return None
        
        return self.providers[provider_name](api_key)
    
    def explain(self, command_args: list, provider_name: str = None):
        """Run command and explain any errors"""
        if not command_args:
            print("No command provided")
            return
        
        # Run the command
        stdout, stderr, exit_code = self.run_command(command_args)
        
        # If successful, just show output
        if exit_code == 0:
            if stdout:
                print(stdout)
            if stderr:  # Some tools output warnings to stderr even on success
                print(stderr)
            return
        
        # Command failed - show original error first
        print("Original command output:")
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        print()
        
        # Get AI explanation if error occurred
        if stderr or exit_code != 0:
            provider = self.get_provider(provider_name)
            if not provider:
                return
            
            error_context = {
                'command': ' '.join(command_args),
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': exit_code,
            }
            
            print(Fore.CYAN + "AI Explanation:")
            explanation = provider.explain_error(error_context)
            print(Fore.GREEN + explanation)

def main():
    explainer = ErrorExplainer()
    
    # Check if first argument is 'config'
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        # Handle config subcommand
        parser = argparse.ArgumentParser(description='Configure xplc')
        parser.add_argument('config', help='Configuration mode')
        parser.add_argument('--set-key', nargs=2, metavar=('PROVIDER', 'KEY'), 
                          help='Set API key for provider')
        parser.add_argument('--default', metavar='PROVIDER', 
                          help='Set default AI provider')
        parser.add_argument('--list', action='store_true', 
                          help='List current configuration')
        
        args = parser.parse_args()
        
        if args.set_key:
            provider, key = args.set_key
            explainer.config.set_api_key(provider, key)
        elif args.default:
            explainer.config.set_default_provider(args.default)
        elif args.list:
            config = explainer.config._config
            print("Current configuration:")
            print(f"Default provider: {config.get('default_provider', 'openai')}")
            print("API keys configured for:", ', '.join(config.get('api_keys', {}).keys()))
        else:
            print("Usage: xplc config [--set-key PROVIDER KEY] [--default PROVIDER] [--list]")
    else:
        # Handle normal command execution
        parser = argparse.ArgumentParser(description='xplc - AI-powered CLI error explainer')
        parser.add_argument('--provider', '-p', help='AI provider (openai, claude, gemini)')
        parser.add_argument('command', nargs='*', help='Command to run and explain')
        
        args = parser.parse_args()
        
        if args.command:
            explainer.explain(args.command, args.provider)
        else:
            print("Usage: xplc [--provider PROVIDER] <command>")
            print("       xplc config [--set-key PROVIDER KEY] [--default PROVIDER] [--list]")
            print("\nExamples:")
            print("  xplc python script.py")
            print("  xplc --provider gemini npm start") 
            print("  xplc config --set-key gemini YOUR_API_KEY")

if __name__ == '__main__':
    main()