"""
Multi-LLM Provider Demo for ITIL AI Agents

This demo showcases the new multi-LLM provider support integrated with the ITIL AI Agents framework.
Demonstrates how agents can use different LLM providers for various tasks.
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_agents.multi_llm_provider import (
        MultiLLMManager, LLMConfig, LLMProvider, ModelType, create_default_config_file
    )
    from ai_agents.itil_crewai_integration import ITILAgentCrew, AgentRole
    from integration.integration_manager import ITILIntegrationManager
    MULTI_LLM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    MULTI_LLM_AVAILABLE = False


class MultiLLMITILDemo:
    """Demonstration of multi-LLM support with ITIL AI agents"""
    
    def __init__(self):
        self.llm_manager = None
        self.agent_crew = None
        self.itil_manager = None
        self.demo_results = []
    
    async def initialize(self):
        """Initialize the demo environment"""
        print("🚀 Initializing Multi-LLM ITIL Demo")
        print("=" * 50)
        
        # Create default config file if needed
        config_file = "llm_config_demo.yaml"
        if not os.path.exists(config_file):
            create_default_config_file(config_file)
        
        # Initialize multi-LLM manager
        if MULTI_LLM_AVAILABLE:
            self.llm_manager = MultiLLMManager()
            
            # Add various providers for demonstration
            await self._setup_demo_providers()
            
            # Initialize ITIL integration manager (mock)
            self.itil_manager = ITILIntegrationManager()
            
            # Initialize agent crew with multi-LLM support
            self.agent_crew = ITILAgentCrew(
                itil_manager=self.itil_manager,
                llm_config_file=config_file
            )
            
            print("✅ Multi-LLM ITIL Demo initialized successfully")
        else:
            print("❌ Multi-LLM support not available")
    
    async def _setup_demo_providers(self):
        """Setup demo LLM providers"""
        print("\n🔧 Setting up LLM providers...")
        
        # Provider 1: OpenAI (will use mock if no API key)
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model=ModelType.GPT_4,
            api_key=os.getenv("OPENAI_API_KEY", "demo-key"),
            temperature=0.1,
            max_tokens=1000
        )
        self.llm_manager.add_provider("openai_gpt4", openai_config)
        
        # Provider 2: OpenAI GPT-3.5 for faster responses
        openai_35_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model=ModelType.GPT_3_5_TURBO,
            api_key=os.getenv("OPENAI_API_KEY", "demo-key"),
            temperature=0.1,
            max_tokens=800
        )
        self.llm_manager.add_provider("openai_gpt35", openai_35_config)
        
        # Provider 3: Ollama local models
        ollama_llama_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=ModelType.LLAMA_2_7B,
            api_base="http://localhost:11434",
            temperature=0.1,
            max_tokens=1000
        )
        self.llm_manager.add_provider("ollama_llama2", ollama_llama_config)
        
        # Provider 4: Ollama Mistral for code analysis
        ollama_mistral_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=ModelType.MISTRAL_7B,
            api_base="http://localhost:11434",
            temperature=0.1,
            max_tokens=1000
        )
        self.llm_manager.add_provider("ollama_mistral", ollama_mistral_config)
        
        # Provider 5: Anthropic Claude
        anthropic_config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model=ModelType.CLAUDE_3_SONNET,
            api_key=os.getenv("ANTHROPIC_API_KEY", "demo-key"),
            temperature=0.1,
            max_tokens=1000
        )
        self.llm_manager.add_provider("anthropic_claude", anthropic_config)
        
        # Provider 6: Google Gemini
        google_config = LLMConfig(
            provider=LLMProvider.GOOGLE,
            model=ModelType.GEMINI_PRO,
            api_key=os.getenv("GOOGLE_API_KEY", "demo-key"),
            temperature=0.1,
            max_tokens=1000
        )
        self.llm_manager.add_provider("google_gemini", google_config)
        
        # Provider 7: Mock provider for guaranteed availability
        mock_config = LLMConfig(
            provider=LLMProvider.MOCK,
            model=ModelType.CUSTOM,
            temperature=0.1,
            max_tokens=1000
        )
        self.llm_manager.add_provider("mock_reliable", mock_config)
        
        # Set primary and fallback providers
        self.llm_manager.set_primary_provider("openai_gpt4")
        self.llm_manager.add_fallback_provider("ollama_llama2")
        self.llm_manager.add_fallback_provider("anthropic_claude")
        self.llm_manager.add_fallback_provider("mock_reliable")
        
        providers = self.llm_manager.get_available_providers()
        print(f"✅ Configured {len(providers)} LLM providers: {', '.join(providers)}")
    
    async def demo_provider_comparison(self):
        """Demonstrate how different providers handle the same prompt"""
        print("\n🧪 Provider Comparison Demo")
        print("-" * 40)
        
        test_prompt = "Analyze this critical incident: Database server DB-PROD-01 is experiencing high CPU usage (95%) and memory consumption (88%). Connection timeouts are occurring, affecting 500+ users. Last known good state was 2 hours ago."
        
        system_prompt = "You are an expert ITIL incident analyst. Provide a structured analysis with priority assessment, immediate actions, and escalation recommendations."
        
        # Test each provider
        providers_to_test = ["openai_gpt4", "ollama_llama2", "anthropic_claude", "mock_reliable"]
        
        for provider_name in providers_to_test:
            if provider_name in self.llm_manager.get_available_providers():
                print(f"\n--- Testing {provider_name} ---")
                
                start_time = datetime.now()
                try:
                    response = await self.llm_manager.generate_response(
                        prompt=test_prompt,
                        system_prompt=system_prompt,
                        provider_name=provider_name
                    )
                    
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    
                    print(f"Provider: {response.provider.value}")
                    print(f"Model: {response.model.value}")
                    print(f"Response Time: {response_time:.2f}s")
                    print(f"Tokens: {response.usage_stats.get('total_tokens', 'N/A')}")
                    print(f"Response Preview: {response.content[:150]}...")
                    
                    # Store results
                    self.demo_results.append({
                        "provider": provider_name,
                        "response_time": response_time,
                        "tokens": response.usage_stats.get('total_tokens', 0),
                        "success": True
                    })
                    
                except Exception as e:
                    print(f"❌ {provider_name} failed: {e}")
                    self.demo_results.append({
                        "provider": provider_name,
                        "success": False,
                        "error": str(e)
                    })
    
    async def demo_specialized_provider_usage(self):
        """Demonstrate using specific providers for specialized tasks"""
        print("\n🎯 Specialized Provider Usage Demo")
        print("-" * 40)
        
        # Different tasks for different providers
        specialized_tasks = [
            {
                "task": "Incident Analysis",
                "provider": "openai_gpt4",
                "prompt": "Critical web application outage affecting customer portal",
                "reason": "GPT-4 for complex incident analysis"
            },
            {
                "task": "Code Review",
                "provider": "ollama_mistral",  
                "prompt": "Review this configuration change for security issues",
                "reason": "Mistral optimized for code analysis"
            },
            {
                "task": "Documentation",
                "provider": "anthropic_claude",
                "prompt": "Create user documentation for new incident reporting process",
                "reason": "Claude excels at structured documentation"
            },
            {
                "task": "Quick Triage",
                "provider": "openai_gpt35",
                "prompt": "Prioritize these 5 incidents based on business impact",
                "reason": "GPT-3.5 for fast, cost-effective triage"
            }
        ]
        
        for task_info in specialized_tasks:
            print(f"\n--- {task_info['task']} with {task_info['provider']} ---")
            print(f"Rationale: {task_info['reason']}")
            
            try:
                response = await self.llm_manager.generate_response(
                    prompt=task_info['prompt'],
                    system_prompt=f"You are an ITIL expert specialized in {task_info['task'].lower()}.",
                    provider_name=task_info['provider']
                )
                
                print(f"✅ Success: {response.content[:100]}...")
                
            except Exception as e:
                print(f"❌ Failed: {e}")
    
    async def demo_automatic_fallback(self):
        """Demonstrate automatic fallback when providers fail"""
        print("\n🔄 Automatic Fallback Demo")
        print("-" * 40)
        
        # Try to use a potentially unavailable provider
        print("Attempting to use primary provider (with potential fallback)...")
        
        try:
            response = await self.llm_manager.generate_response(
                prompt="Provide ITIL change management best practices for database upgrades",
                system_prompt="You are an ITIL change management expert."
            )
            
            print(f"✅ Response received from: {response.provider.value}")
            print(f"Model: {response.model.value}")
            print(f"Fallback chain worked successfully!")
            print(f"Response: {response.content[:200]}...")
            
        except Exception as e:
            print(f"❌ All providers failed: {e}")
    
    async def demo_agent_crew_integration(self):
        """Demonstrate agent crew using multi-LLM providers"""
        print("\n🤖 Agent Crew Multi-LLM Integration Demo")
        print("-" * 40)
        
        if not self.agent_crew:
            print("❌ Agent crew not initialized")
            return
        
        # Display LLM configuration
        llm_info = self.agent_crew.get_llm_provider_info()
        print(f"Multi-LLM Status: {'✅ Enabled' if llm_info['multi_llm_enabled'] else '❌ Disabled'}")
        print(f"Available Providers: {', '.join(llm_info['available_providers'])}")
        print(f"Primary Provider: {llm_info.get('primary_provider', 'None')}")
        
        # Test direct LLM calls from agent crew
        prompts_and_providers = [
            ("Analyze incident severity levels", "openai_gpt4"),
            ("Suggest problem management process improvements", "anthropic_claude"),
            ("Create change approval checklist", "ollama_llama2"),
            ("ITIL knowledge base search strategy", None)  # Use default
        ]
        
        for prompt, provider in prompts_and_providers:
            print(f"\n--- Testing: {prompt} ---")
            print(f"Provider: {provider or 'Default/Fallback'}")
            
            try:
                response = await self.agent_crew.get_llm_response(
                    prompt=prompt,
                    system_prompt="You are an ITIL expert providing concise, actionable advice.",
                    provider_name=provider
                )
                
                print(f"✅ Response: {response[:150]}...")
                
            except Exception as e:
                print(f"❌ Failed: {e}")
    
    async def demo_performance_monitoring(self):
        """Demonstrate performance monitoring across providers"""
        print("\n📊 Performance Monitoring Demo")
        print("-" * 40)
        
        # Test multiple quick requests to compare performance
        test_prompt = "What are the key ITIL 4 guiding principles?"
        providers = ["openai_gpt35", "ollama_llama2", "mock_reliable"]
        
        performance_data = []
        
        for provider in providers:
            if provider in self.llm_manager.get_available_providers():
                times = []
                successes = 0
                
                # Run 3 quick tests
                for i in range(3):
                    start_time = datetime.now()
                    try:
                        response = await self.llm_manager.generate_response(
                            prompt=f"{test_prompt} (Test {i+1})",
                            provider_name=provider
                        )
                        end_time = datetime.now()
                        response_time = (end_time - start_time).total_seconds()
                        times.append(response_time)
                        successes += 1
                        
                    except Exception:
                        times.append(30.0)  # Timeout penalty
                
                avg_time = sum(times) / len(times)
                success_rate = (successes / 3) * 100
                
                performance_data.append({
                    "provider": provider,
                    "avg_response_time": avg_time,
                    "success_rate": success_rate,
                    "min_time": min(times),
                    "max_time": max(times)
                })
        
        # Display performance results
        print("\nPerformance Results:")
        print("-" * 20)
        for data in sorted(performance_data, key=lambda x: x["avg_response_time"]):
            print(f"{data['provider']:<15} | "
                  f"Avg: {data['avg_response_time']:.2f}s | "
                  f"Range: {data['min_time']:.2f}-{data['max_time']:.2f}s | "
                  f"Success: {data['success_rate']:.0f}%")
    
    async def demo_configuration_management(self):
        """Demonstrate LLM provider configuration management"""
        print("\n⚙️  Configuration Management Demo")
        print("-" * 40)
        
        # Show current configuration
        print("Current Configuration:")
        providers = self.llm_manager.get_available_providers()
        for provider_name in providers:
            info = self.llm_manager.get_provider_info(provider_name)
            if info:
                print(f"  {provider_name}: {info['provider']} ({info['model']})")
        
        # Demonstrate changing primary provider
        print(f"\nCurrent primary: {self.llm_manager.primary_provider}")
        
        if "ollama_llama2" in providers:
            print("Switching primary provider to Ollama Llama2...")
            self.llm_manager.set_primary_provider("ollama_llama2")
            
            # Test with new primary
            response = await self.llm_manager.generate_response(
                "What is ITIL service management?",
                system_prompt="Provide a brief definition of ITIL."
            )
            print(f"✅ Response from new primary ({response.provider.value}): {response.content[:100]}...")
            
            # Switch back
            if "openai_gpt4" in providers:
                self.llm_manager.set_primary_provider("openai_gpt4")
                print("Switched back to OpenAI GPT-4")
    
    def generate_summary_report(self):
        """Generate a summary report of the demo"""
        print("\n📋 Multi-LLM Demo Summary Report")
        print("=" * 50)
        
        # Overall statistics
        total_tests = len(self.demo_results)
        successful_tests = len([r for r in self.demo_results if r.get('success', False)])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Provider performance
        if self.demo_results:
            print(f"\nProvider Performance:")
            successful_results = [r for r in self.demo_results if r.get('success', False)]
            if successful_results:
                avg_response_time = sum(r.get('response_time', 0) for r in successful_results) / len(successful_results)
                total_tokens = sum(r.get('tokens', 0) for r in successful_results)
                
                print(f"Average Response Time: {avg_response_time:.2f}s")
                print(f"Total Tokens Used: {total_tokens}")
        
        # Key features demonstrated
        print(f"\n✅ Key Features Demonstrated:")
        print(f"  • Multi-provider support (OpenAI, Ollama, Anthropic, Google)")
        print(f"  • Automatic fallback between providers")
        print(f"  • Provider-specific task optimization")
        print(f"  • Performance monitoring and comparison")
        print(f"  • Runtime configuration changes")
        print(f"  • Integration with ITIL AI agents")
        print(f"  • Local model support with Ollama")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        print(f"  • Configure actual API keys for full functionality")
        print(f"  • Install and run Ollama for local model support")
        print(f"  • Set up provider-specific configurations based on use case")
        print(f"  • Monitor usage costs across different providers")
        print(f"  • Use faster models (GPT-3.5) for simple tasks")
        print(f"  • Use more capable models (GPT-4, Claude) for complex analysis")


async def main():
    """Main demo execution"""
    print("🌟 Multi-LLM Provider Support for ITIL AI Agents")
    print("🎯 Demonstration of flexible LLM integration")
    print("=" * 60)
    
    if not MULTI_LLM_AVAILABLE:
        print("❌ Multi-LLM support not available. Please install required dependencies.")
        return
    
    # Initialize demo
    demo = MultiLLMITILDemo()
    await demo.initialize()
    
    try:
        # Run comprehensive demo
        print("\n🏃 Running Multi-LLM Demo Suite...")
        
        await demo.demo_provider_comparison()
        await demo.demo_specialized_provider_usage() 
        await demo.demo_automatic_fallback()
        await demo.demo_agent_crew_integration()
        await demo.demo_performance_monitoring()
        await demo.demo_configuration_management()
        
        # Generate final report
        demo.generate_summary_report()
        
        print(f"\n🎉 Multi-LLM Demo completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
    
    print(f"\n🔗 Next Steps:")
    print(f"  1. Configure actual API keys in environment variables")
    print(f"  2. Install Ollama and download local models")
    print(f"  3. Customize LLM configurations for your use case")
    print(f"  4. Integrate with your existing ITIL processes")
    print(f"  5. Monitor usage and optimize provider selection")


if __name__ == "__main__":
    asyncio.run(main())