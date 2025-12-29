"""Mock LLM Client - Simulation Only

LLM calls are intentionally mocked to isolate execution control
from model behavior and ensure full reproducibility.

No real API calls are made. This allows:
- Deterministic results
- No API keys required
- Fast execution
- Focus on control logic, not LLM outputs
"""

import time
from typing import Dict, Any


def call_llm(prompt: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock LLM call - simulates API behavior without network calls.

    Returns:
        Simulated response with timing and metadata
    """
    start_time = time.perf_counter()

    # Simulate API latency (10ms)
    time.sleep(0.01)

    return {
        "response": f"SIMULATED_RESPONSE: {prompt[:50]}...",
        "metadata": metadata,
        "model": "mock-llm",
        "latency_ms": (time.perf_counter() - start_time) * 1000,
        "timestamp": time.time(),
    }
