"""Configuration and hermes-agent repo discovery."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EvolutionConfig:
    """Configuration for a self-evolution optimization run."""

    # hermes-agent repo path
    hermes_agent_path: Path = field(default_factory=lambda: get_hermes_agent_path())

    # Optimization parameters
    iterations: int = 10
    population_size: int = 5

    # LLM configuration
    optimizer_model: str = "openai/gpt-4.1"  # Model for GEPA reflections
    eval_model: str = "openai/gpt-4.1-mini"  # Model for LLM-as-judge scoring
    judge_model: str = "openai/gpt-4.1"  # Model for dataset generation

    # PR #5: Configurable cost cap
    # Previously hardcoded at $10. Now configurable per-deployment.
    # For multi-group setups, the cap scales with group count but has a max.
    max_cost_per_run_usd: float = 10.00
    cost_per_1k_tokens: dict = field(default_factory=lambda: {
        "gpt-4.1": 0.005,
        "openai/gpt-4.1": 0.005,
        "gpt-4.1-mini": 0.0006,
        "openai/gpt-4.1-mini": 0.0006,
        "gpt-4o": 0.005,
        "openai/gpt-4o": 0.005,
        "gpt-4o-mini": 0.0006,
        "openai/gpt-4o-mini": 0.0006,
        "gpt-3.5-turbo": 0.002,
        "openai/gpt-3.5-turbo": 0.002,
    })

    # Constraints
    max_skill_size: int = 15_000  # 15KB default
    max_tool_desc_size: int = 500  # chars
    max_param_desc_size: int = 200  # chars
    max_prompt_growth: float = 0.2  # 20% max growth over baseline

    # Eval dataset
    eval_dataset_size: int = 20  # Total examples to generate
    train_ratio: float = 0.5
    val_ratio: float = 0.25
    holdout_ratio: float = 0.25

    # PR #4: Multi-group session filtering
    # Only mine sessions from these groups. Empty = all groups.
    # Format: list of chat_ids (e.g., ["-1001234567890", "-1009998887777"])
    target_groups: list = field(default_factory=list)
    
    # Exclude specific groups from mining (privacy / isolation)
    # Baked in BLR equivalent for any deployment
    excluded_groups: list = field(default_factory=list)

    # Benchmark gating
    run_pytest: bool = True
    run_tblite: bool = False  # Expensive — opt-in
    tblite_regression_threshold: float = 0.02  # Max 2% regression allowed

    # Output
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    create_pr: bool = True


def get_hermes_agent_path() -> Path:
    """Discover the hermes-agent repo path.

    Priority:
    1. HERMES_AGENT_REPO env var
    2. ~/.hermes/hermes-agent (standard install location)
    3. ../hermes-agent (sibling directory)
    """
    env_path = os.getenv("HERMES_AGENT_REPO")
    if env_path:
        p = Path(env_path).expanduser()
        if p.exists():
            return p

    home_path = Path.home() / ".hermes" / "hermes-agent"
    if home_path.exists():
        return home_path

    sibling_path = Path(__file__).parent.parent.parent / "hermes-agent"
    if sibling_path.exists():
        return sibling_path

    raise FileNotFoundError(
        "Cannot find hermes-agent repo. Set HERMES_AGENT_REPO env var "
        "or ensure it exists at ~/.hermes/hermes-agent"
    )
