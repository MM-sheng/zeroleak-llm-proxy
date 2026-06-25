from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_governance_files_exist() -> None:
    required = [
        "AGENTS.md",
        "PROJECT_SPEC.md",
        "TASKS.md",
        "DECISIONS.md",
        "CONTEXT.md",
        "README.md",
        "requirements.txt",
        ".env.example",
    ]

    missing = [name for name in required if not (ROOT / name).exists()]

    assert missing == []


def test_tasks_has_exactly_one_next() -> None:
    task_text = (ROOT / "TASKS.md").read_text(encoding="utf-8")

    assert task_text.count("Status: NEXT") == 1


def test_env_example_defaults_to_no_live_trading() -> None:
    env_text = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "LIVE_TRADING=false" in env_text
    assert "POLYMARKET_PRIVATE_KEY=" in env_text

