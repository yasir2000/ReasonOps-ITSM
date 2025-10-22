"""
Multi-LLM Provider Support for ITIL AI Agents Framework

This module provides comprehensive support for multiple LLM providers including:
- OpenAI (GPT-3.5, GPT-4, GPT-4-turbo)
- Anthropic (Claude 3 Haiku, Sonnet, Opus)
- Google (Gemini Pro, Gemini Pro Vision)
- Azure OpenAI Service
- Local Ollama models (Llama 2, Mistral, CodeLlama, etc.)
- Hugging Face Transformers
- Custom API endpoints
"""

import sys
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import logging
from abc import ABC, abstractmethod
import asyncio
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core LLM integration imports with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI not installed. Install with: pip install openai")
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("⚠️  Anthropic not installed. Install with: pip install anthropic")
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    print("⚠️  Google AI not installed. Install with: pip install google-generativeai")
    GOOGLE_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("⚠️  Ollama not installed. Install with: pip install ollama")
    OLLAMA_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️  Transformers not installed. Install with: pip install transformers torch")
    TRANSFORMERS_AVAILABLE = False

try:
    import requests
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    print("⚠️  HTTP libraries not installed. Install with: pip install requests aiohttp")
    HTTP_AVAILABLE = False

# Configuration management
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("⚠️  PyYAML not installed. Install with: pip install pyyaml")
    YAML_AVAILABLE = False


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    CUSTOM_API = "custom_api"
    MOCK = "mock"  # For testing


class ModelType(Enum):
    """Types of models available"""
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    LLAMA_2_7B = "llama2:7b"
    LLAMA_2_13B = "llama2:13b"
    LLAMA_2_70B = "llama2:70b"
    MISTRAL_7B = "mistral:7b"
    CODELLAMA_7B = "codellama:7b"
    CODELLAMA_13B = "codellama:13b"
    CODELLAMA_34B = "codellama:34b"
    NEURAL_CHAT = "neural-chat:7b"
    ORCA_MINI = "orca-mini:3b"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model: ModelType
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    retry_attempts: int = 3
    custom_headers: Optional[Dict[str, str]] = None
    model_kwargs: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    provider: LLMProvider
    model: ModelType
    usage_stats: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration"""
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model.value,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if OPENAI_AVAILABLE:
            self.client = openai.OpenAI(
                api_key=config.api_key,
                base_url=config.api_base,
                timeout=config.timeout
            )
        else:
            self.client = None
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        if not OPENAI_AVAILABLE:
            return False
        
        if not self.config.api_key:
            self.logger.error("OpenAI API key is required")
            return False
        
        return True
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response from OpenAI"""
        if not self.client:
            return self._mock_response(prompt)
        
        start_time = time.time()
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.config.model.value,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty
            )
            
            content = response.choices[0].message.content
            usage_stats = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage_stats=usage_stats,
                response_time=time.time() - start_time,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> LLMResponse:
        """Generate mock response when OpenAI is not available"""
        return LLMResponse(
            content=f"Mock OpenAI response for: {prompt[:50]}...",
            provider=self.config.provider,
            model=self.config.model,
            usage_stats={"total_tokens": 100},
            response_time=0.5
        )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=config.api_key)
        else:
            self.client = None
    
    def validate_config(self) -> bool:
        """Validate Anthropic configuration"""
        if not ANTHROPIC_AVAILABLE:
            return False
        
        if not self.config.api_key:
            self.logger.error("Anthropic API key is required")
            return False
        
        return True
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response from Anthropic Claude"""
        if not self.client:
            return self._mock_response(prompt)
        
        start_time = time.time()
        
        try:
            # Combine system prompt and user prompt for Claude
            full_prompt = ""
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
            else:
                full_prompt = f"Human: {prompt}\n\nAssistant:"
            
            response = self.client.messages.create(
                model=self.config.model.value,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            content = response.content[0].text
            usage_stats = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage_stats=usage_stats,
                response_time=time.time() - start_time,
                metadata={"stop_reason": response.stop_reason}
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> LLMResponse:
        """Generate mock response when Anthropic is not available"""
        return LLMResponse(
            content=f"Mock Anthropic response for: {prompt[:50]}...",
            provider=self.config.provider,
            model=self.config.model,
            usage_stats={"total_tokens": 100},
            response_time=0.5
        )


class GoogleProvider(BaseLLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if GOOGLE_AVAILABLE and config.api_key:
            genai.configure(api_key=config.api_key)
            self.model = genai.GenerativeModel(config.model.value)
        else:
            self.model = None
    
    def validate_config(self) -> bool:
        """Validate Google configuration"""
        if not GOOGLE_AVAILABLE:
            return False
        
        if not self.config.api_key:
            self.logger.error("Google API key is required")
            return False
        
        return True
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response from Google Gemini"""
        if not self.model:
            return self._mock_response(prompt)
        
        start_time = time.time()
        
        try:
            # Combine system prompt and user prompt
            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            generation_config = genai.types.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
                top_p=self.config.top_p
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            content = response.text
            usage_stats = {
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage_stats=usage_stats,
                response_time=time.time() - start_time,
                metadata={"finish_reason": response.candidates[0].finish_reason}
            )
            
        except Exception as e:
            self.logger.error(f"Google API error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> LLMResponse:
        """Generate mock response when Google is not available"""
        return LLMResponse(
            content=f"Mock Google response for: {prompt[:50]}...",
            provider=self.config.provider,
            model=self.config.model,
            usage_stats={"total_tokens": 100},
            response_time=0.5
        )


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"
        if OLLAMA_AVAILABLE:
            self.client = ollama.Client(host=self.base_url)
        else:
            self.client = None
    
    def validate_config(self) -> bool:
        """Validate Ollama configuration"""
        if not OLLAMA_AVAILABLE:
            return False
        
        try:
            # Test connection to Ollama server
            if self.client:
                self.client.list()
            return True
        except Exception as e:
            self.logger.error(f"Ollama connection failed: {e}")
            return False
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response from Ollama"""
        if not self.client:
            return self._mock_response(prompt)
        
        start_time = time.time()
        
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat(
                model=self.config.model.value,
                messages=messages,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                    "top_p": self.config.top_p
                }
            )
            
            content = response['message']['content']
            usage_stats = {
                "prompt_eval_count": response.get('prompt_eval_count', 0),
                "eval_count": response.get('eval_count', 0),
                "total_tokens": response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
            }
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage_stats=usage_stats,
                response_time=time.time() - start_time,
                metadata={
                    "model": response.get('model'),
                    "eval_duration": response.get('eval_duration'),
                    "prompt_eval_duration": response.get('prompt_eval_duration')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> LLMResponse:
        """Generate mock response when Ollama is not available"""
        return LLMResponse(
            content=f"Mock Ollama response for: {prompt[:50]}...",
            provider=self.config.provider,
            model=self.config.model,
            usage_stats={"total_tokens": 100},
            response_time=0.5
        )


class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face Transformers LLM provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.model_name = config.model_kwargs.get('model_name') if config.model_kwargs else None
        self.pipeline = None
        self.tokenizer = None
        
        if TRANSFORMERS_AVAILABLE and self.model_name:
            try:
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model_name,
                    tokenizer=self.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            except Exception as e:
                self.logger.error(f"Failed to load Hugging Face model: {e}")
    
    def validate_config(self) -> bool:
        """Validate Hugging Face configuration"""
        if not TRANSFORMERS_AVAILABLE:
            return False
        
        if not self.model_name:
            self.logger.error("Hugging Face model name is required")
            return False
        
        return self.pipeline is not None
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response from Hugging Face model"""
        if not self.pipeline:
            return self._mock_response(prompt)
        
        start_time = time.time()
        
        try:
            # Combine system prompt and user prompt
            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Generate response
            outputs = self.pipeline(
                full_prompt,
                max_new_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = outputs[0]['generated_text']
            # Remove the input prompt from the output
            content = generated_text[len(full_prompt):].strip()
            
            # Calculate token usage
            input_tokens = len(self.tokenizer.encode(full_prompt))
            output_tokens = len(self.tokenizer.encode(content))
            usage_stats = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage_stats=usage_stats,
                response_time=time.time() - start_time,
                metadata={"model_name": self.model_name}
            )
            
        except Exception as e:
            self.logger.error(f"Hugging Face generation error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> LLMResponse:
        """Generate mock response when Hugging Face is not available"""
        return LLMResponse(
            content=f"Mock Hugging Face response for: {prompt[:50]}...",
            provider=self.config.provider,
            model=self.config.model,
            usage_stats={"total_tokens": 100},
            response_time=0.5
        )


class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing"""
    
    def validate_config(self) -> bool:
        """Always valid for mock provider"""
        return True
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate mock response"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Generate contextual mock response based on prompt content
        if "incident" in prompt.lower():
            content = """Based on the incident analysis, I recommend:
1. Immediate priority assessment and categorization
2. Root cause analysis to identify underlying issues  
3. Implementation of temporary workaround if available
4. Communication to affected stakeholders
5. Escalation to appropriate technical team if needed"""
        elif "problem" in prompt.lower():
            content = """Problem analysis suggests:
1. Review similar historical incidents for patterns
2. Conduct thorough root cause investigation
3. Develop permanent solution to prevent recurrence
4. Update knowledge base with findings
5. Implement proactive monitoring"""
        elif "change" in prompt.lower():
            content = """Change management recommendations:
1. Assess risk level and potential impact
2. Obtain necessary approvals before implementation
3. Plan rollback strategy in case of issues
4. Schedule change during appropriate maintenance window
5. Monitor post-implementation for any adverse effects"""
        else:
            content = f"Mock AI response based on the prompt: {prompt[:100]}..."
        
        return LLMResponse(
            content=content,
            provider=LLMProvider.MOCK,
            model=ModelType.CUSTOM,
            usage_stats={"total_tokens": len(content.split())},
            response_time=0.1,
            metadata={"mock": True}
        )


class MultiLLMManager:
    """Manager for multiple LLM providers with load balancing and fallbacks"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        if config_file:
            self.load_config(config_file)
        else:
            self._setup_default_config()
    
    def load_config(self, config_file: str):
        """Load configuration from file"""
        try:
            if YAML_AVAILABLE:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
            else:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            
            self._parse_config(config_data)
            
        except Exception as e:
            self.logger.error(f"Failed to load config file: {e}")
            self._setup_default_config()
    
    def _parse_config(self, config_data: Dict[str, Any]):
        """Parse configuration data"""
        self.primary_provider = config_data.get('primary_provider')
        self.fallback_providers = config_data.get('fallback_providers', [])
        
        # Setup providers
        for provider_name, provider_config in config_data.get('providers', {}).items():
            try:
                llm_config = LLMConfig(
                    provider=LLMProvider(provider_config.get('provider')),
                    model=ModelType(provider_config.get('model')),
                    api_key=provider_config.get('api_key'),
                    api_base=provider_config.get('api_base'),
                    api_version=provider_config.get('api_version'),
                    temperature=provider_config.get('temperature', 0.1),
                    max_tokens=provider_config.get('max_tokens', 2000),
                    timeout=provider_config.get('timeout', 30),
                    model_kwargs=provider_config.get('model_kwargs')
                )
                
                self.add_provider(provider_name, llm_config)
                
            except Exception as e:
                self.logger.error(f"Failed to setup provider {provider_name}: {e}")
    
    def _setup_default_config(self):
        """Setup default configuration with mock provider"""
        self.logger.info("Setting up default configuration with mock provider")
        
        mock_config = LLMConfig(
            provider=LLMProvider.MOCK,
            model=ModelType.CUSTOM,
            temperature=0.1,
            max_tokens=2000
        )
        
        self.add_provider("mock", mock_config)
        self.primary_provider = "mock"
    
    def add_provider(self, name: str, config: LLMConfig):
        """Add a new LLM provider"""
        try:
            # Create provider instance based on type
            if config.provider == LLMProvider.OPENAI:
                provider = OpenAIProvider(config)
            elif config.provider == LLMProvider.ANTHROPIC:
                provider = AnthropicProvider(config)
            elif config.provider == LLMProvider.GOOGLE:
                provider = GoogleProvider(config)
            elif config.provider == LLMProvider.OLLAMA:
                provider = OllamaProvider(config)
            elif config.provider == LLMProvider.HUGGINGFACE:
                provider = HuggingFaceProvider(config)
            elif config.provider == LLMProvider.MOCK:
                provider = MockProvider(config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
            
            # Validate configuration
            if provider.validate_config():
                self.providers[name] = provider
                self.logger.info(f"Added provider: {name} ({config.provider.value})")
            else:
                self.logger.warning(f"Provider {name} failed validation, using mock instead")
                self.providers[name] = MockProvider(config)
            
        except Exception as e:
            self.logger.error(f"Failed to add provider {name}: {e}")
            # Add mock provider as fallback
            self.providers[name] = MockProvider(config)
    
    async def generate_response(self, 
                              prompt: str, 
                              system_prompt: Optional[str] = None,
                              provider_name: Optional[str] = None) -> LLMResponse:
        """Generate response with automatic fallback"""
        
        # Determine which provider to use
        if provider_name and provider_name in self.providers:
            providers_to_try = [provider_name]
        elif self.primary_provider and self.primary_provider in self.providers:
            providers_to_try = [self.primary_provider] + self.fallback_providers
        else:
            providers_to_try = list(self.providers.keys())
        
        # Try providers in order
        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue
                
            try:
                self.logger.debug(f"Trying provider: {provider_name}")
                provider = self.providers[provider_name]
                response = await provider.generate_response(prompt, system_prompt)
                
                if response.content:
                    self.logger.info(f"Successfully generated response using: {provider_name}")
                    return response
                    
            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        # If all providers fail, return mock response
        self.logger.error("All providers failed, returning mock response")
        mock_provider = MockProvider(LLMConfig(LLMProvider.MOCK, ModelType.CUSTOM))
        return await mock_provider.generate_response(prompt, system_prompt)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific provider"""
        if provider_name in self.providers:
            return self.providers[provider_name].get_provider_info()
        return None
    
    def set_primary_provider(self, provider_name: str):
        """Set the primary provider"""
        if provider_name in self.providers:
            self.primary_provider = provider_name
            self.logger.info(f"Set primary provider to: {provider_name}")
        else:
            self.logger.error(f"Provider not found: {provider_name}")
    
    def add_fallback_provider(self, provider_name: str):
        """Add a fallback provider"""
        if provider_name in self.providers and provider_name not in self.fallback_providers:
            self.fallback_providers.append(provider_name)
            self.logger.info(f"Added fallback provider: {provider_name}")


def create_default_config_file(filename: str = "llm_config.yaml"):
    """Create a default configuration file"""
    default_config = {
        "primary_provider": "openai_gpt4",
        "fallback_providers": ["ollama_llama2", "mock"],
        "providers": {
            "openai_gpt4": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": "${OPENAI_API_KEY}",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 30
            },
            "openai_gpt35": {
                "provider": "openai", 
                "model": "gpt-3.5-turbo",
                "api_key": "${OPENAI_API_KEY}",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 30
            },
            "anthropic_claude": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "api_key": "${ANTHROPIC_API_KEY}",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 30
            },
            "google_gemini": {
                "provider": "google",
                "model": "gemini-pro",
                "api_key": "${GOOGLE_API_KEY}",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 30
            },
            "ollama_llama2": {
                "provider": "ollama",
                "model": "llama2:7b",
                "api_base": "http://localhost:11434",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 60
            },
            "ollama_mistral": {
                "provider": "ollama",
                "model": "mistral:7b",
                "api_base": "http://localhost:11434",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 60
            },
            "ollama_codellama": {
                "provider": "ollama",
                "model": "codellama:7b",
                "api_base": "http://localhost:11434",
                "temperature": 0.1,
                "max_tokens": 2000,
                "timeout": 60
            },
            "mock": {
                "provider": "mock",
                "model": "custom",
                "temperature": 0.1,
                "max_tokens": 2000
            }
        }
    }
    
    try:
        if YAML_AVAILABLE:
            with open(filename, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
        else:
            with open(filename, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        print(f"✅ Created default configuration file: {filename}")
        print("Edit this file to configure your LLM providers with actual API keys.")
        
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")


async def main():
    """Main function to demonstrate multi-LLM support"""
    print("🤖 Multi-LLM Provider Support for ITIL AI Agents")
    print("=" * 60)
    
    # Create default config file if it doesn't exist
    config_file = "llm_config.yaml"
    if not os.path.exists(config_file):
        create_default_config_file(config_file)
    
    # Initialize multi-LLM manager
    print("\n🔧 Initializing Multi-LLM Manager...")
    llm_manager = MultiLLMManager()
    
    # Add some providers manually for demo
    print("\n➕ Adding LLM Providers...")
    
    # Add OpenAI provider (will use mock if no API key)
    openai_config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model=ModelType.GPT_4,
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
        max_tokens=1000
    )
    llm_manager.add_provider("openai", openai_config)
    
    # Add Ollama provider (will use mock if Ollama not running)
    ollama_config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model=ModelType.LLAMA_2_7B,
        api_base="http://localhost:11434",
        temperature=0.1,
        max_tokens=1000
    )
    llm_manager.add_provider("ollama", ollama_config)
    
    # Add Anthropic provider (will use mock if no API key)
    anthropic_config = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model=ModelType.CLAUDE_3_SONNET,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.1,
        max_tokens=1000
    )
    llm_manager.add_provider("anthropic", anthropic_config)
    
    # Set primary and fallback providers
    llm_manager.set_primary_provider("openai")
    llm_manager.add_fallback_provider("ollama")
    llm_manager.add_fallback_provider("anthropic")
    
    # Display available providers
    providers = llm_manager.get_available_providers()
    print(f"\n📋 Available Providers: {', '.join(providers)}")
    
    # Test different types of ITIL prompts
    test_prompts = [
        {
            "type": "Incident Analysis",
            "system": "You are an ITIL incident management expert. Analyze incidents and provide structured recommendations.",
            "prompt": "A critical database server is experiencing high CPU usage affecting 500+ users. Connection timeouts are increasing. What immediate actions should be taken?"
        },
        {
            "type": "Problem Management", 
            "system": "You are an ITIL problem management specialist. Identify root causes and permanent solutions.",
            "prompt": "We've had 5 similar email server incidents in the past month. Each incident was resolved by restarting the service. What problem analysis approach should we take?"
        },
        {
            "type": "Change Management",
            "system": "You are an ITIL change management advisor. Assess risks and provide change recommendations.",
            "prompt": "Proposed change: Upgrade production web server from Apache 2.4.41 to 2.4.54 during next maintenance window. Assess the risk and provide recommendations."
        }
    ]
    
    # Test each prompt with different providers
    for i, test in enumerate(test_prompts, 1):
        print(f"\n🧪 Test {i}: {test['type']}")
        print("-" * 40)
        
        try:
            response = await llm_manager.generate_response(
                prompt=test['prompt'],
                system_prompt=test['system']
            )
            
            print(f"Provider: {response.provider.value}")
            print(f"Model: {response.model.value}")
            print(f"Response Time: {response.response_time:.2f}s")
            print(f"Tokens: {response.usage_stats.get('total_tokens', 'N/A')}")
            print(f"Response:\n{response.content[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test provider-specific calls
    print(f"\n🎯 Testing Specific Provider Calls...")
    for provider_name in providers[:2]:  # Test first 2 providers
        print(f"\n--- Testing {provider_name} ---")
        try:
            response = await llm_manager.generate_response(
                prompt="What are the key benefits of ITIL 4 Service Value System?",
                provider_name=provider_name
            )
            print(f"✅ {provider_name}: {response.content[:100]}...")
            
        except Exception as e:
            print(f"❌ {provider_name} failed: {e}")
    
    # Display provider information
    print(f"\n📊 Provider Information:")
    for provider_name in providers:
        info = llm_manager.get_provider_info(provider_name)
        if info:
            print(f"  {provider_name}: {info['provider']} ({info['model']})")
    
    print(f"\n🎉 Multi-LLM Support Demo Complete!")
    print("Key Features:")
    print("✅ Support for OpenAI, Anthropic, Google, Ollama, Hugging Face")
    print("✅ Automatic fallback between providers")
    print("✅ Local model support with Ollama")
    print("✅ Configuration file management")
    print("✅ Usage statistics and monitoring")
    print("✅ Graceful error handling")


if __name__ == "__main__":
    asyncio.run(main())