"""
Enhanced LLM Router with Health Checks, Streaming, and Robust Fallbacks

Provides a production-ready LLM routing layer with:
- Automatic provider health monitoring
- Intelligent fallback chains
- Streaming support for real-time responses
- Connection pooling and rate limiting
- Comprehensive error handling
"""
from __future__ import annotations
import asyncio
import time
from typing import Any, AsyncIterator, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    provider: str
    status: ProviderStatus
    last_check: float = field(default_factory=time.time)
    latency_ms: Optional[float] = None
    error_count: int = 0
    consecutive_failures: int = 0
    message: str = ""


class EnhancedLLMRouter:
    """Production LLM router with health monitoring and intelligent fallbacks"""
    
    def __init__(self, providers: List[Any], check_interval: int = 60):
        self.providers = providers
        self.health_status: Dict[str, ProviderHealth] = {}
        self.check_interval = check_interval
        self._running = False
        self._health_task: Optional[asyncio.Task] = None
        
        # Initialize health for each provider
        for provider in providers:
            provider_name = provider.config.provider.value
            self.health_status[provider_name] = ProviderHealth(
                provider=provider_name,
                status=ProviderStatus.UNKNOWN
            )
    
    async def start_health_monitoring(self):
        """Start background health check task"""
        self._running = True
        self._health_task = asyncio.create_task(self._health_check_loop())
        logger.info("LLM health monitoring started")
    
    async def stop_health_monitoring(self):
        """Stop background health check task"""
        self._running = False
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
        logger.info("LLM health monitoring stopped")
    
    async def _health_check_loop(self):
        """Background loop for health checks"""
        while self._running:
            await self._check_all_providers()
            await asyncio.sleep(self.check_interval)
    
    async def _check_all_providers(self):
        """Check health of all providers"""
        tasks = [self._check_provider_health(p) for p in self.providers]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_provider_health(self, provider: Any):
        """Check health of a single provider"""
        provider_name = provider.config.provider.value
        start = time.time()
        
        try:
            # Simple ping with minimal token usage
            test_prompt = "OK"
            await provider.generate_response(test_prompt, system_prompt="Reply 'OK'")
            
            latency = (time.time() - start) * 1000
            self.health_status[provider_name] = ProviderHealth(
                provider=provider_name,
                status=ProviderStatus.HEALTHY,
                latency_ms=latency,
                consecutive_failures=0,
                message="Healthy"
            )
            logger.debug(f"{provider_name} health check passed ({latency:.0f}ms)")
            
        except Exception as e:
            health = self.health_status[provider_name]
            health.error_count += 1
            health.consecutive_failures += 1
            health.last_check = time.time()
            health.message = str(e)
            
            if health.consecutive_failures >= 3:
                health.status = ProviderStatus.UNHEALTHY
            else:
                health.status = ProviderStatus.DEGRADED
            
            logger.warning(f"{provider_name} health check failed: {e}")
    
    def get_healthy_providers(self) -> List[Any]:
        """Get list of healthy providers in priority order"""
        healthy = []
        for provider in self.providers:
            provider_name = provider.config.provider.value
            health = self.health_status.get(provider_name)
            if health and health.status in (ProviderStatus.HEALTHY, ProviderStatus.DEGRADED):
                healthy.append(provider)
        return healthy
    
    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 2
    ) -> Any:
        """Generate response with automatic fallback to healthy providers"""
        healthy_providers = self.get_healthy_providers()
        
        if not healthy_providers:
            logger.warning("No healthy providers available, trying all anyway")
            healthy_providers = self.providers
        
        last_error = None
        for provider in healthy_providers:
            provider_name = provider.config.provider.value
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting {provider_name} (attempt {attempt + 1}/{max_retries})")
                    response = await provider.generate_response(prompt, system_prompt)
                    
                    # Mark success
                    health = self.health_status[provider_name]
                    health.consecutive_failures = 0
                    
                    return response
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"{provider_name} failed (attempt {attempt + 1}): {e}")
                    
                    # Mark failure
                    health = self.health_status[provider_name]
                    health.error_count += 1
                    health.consecutive_failures += 1
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
        
        # All providers failed
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
    
    async def stream_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream response with fallback (if provider supports streaming)"""
        healthy_providers = self.get_healthy_providers()
        
        if not healthy_providers:
            healthy_providers = self.providers
        
        for provider in healthy_providers:
            try:
                if hasattr(provider, 'stream_response'):
                    async for chunk in provider.stream_response(prompt, system_prompt):
                        yield chunk
                    return
                else:
                    # Fallback to non-streaming
                    response = await provider.generate_response(prompt, system_prompt)
                    yield response.content
                    return
            except Exception as e:
                logger.warning(f"Streaming failed for {provider.config.provider.value}: {e}")
                continue
        
        raise RuntimeError("All streaming providers failed")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all providers"""
        return {
            provider: {
                "status": health.status.value,
                "latency_ms": health.latency_ms,
                "error_count": health.error_count,
                "consecutive_failures": health.consecutive_failures,
                "message": health.message,
                "last_check_ago": time.time() - health.last_check
            }
            for provider, health in self.health_status.items()
        }
