from pathlib import Path

folders = [
    "data/raw", "data/processed", "data/labels",
    "notebooks", "src", "app", "models", "reports", "docs", "tests",
]
files = [
    "src/__init__.py", "src/config.py", "src/flood_mapping.py",
    "src/features.py", "src/risk_model.py", "src/impact.py", "src/alerts.py",
    "app/dashboard.py", "tests/test_setup.py",
    "README.md", "requirements.txt", ".env", ".gitignore",
]

for f in folders:
    Path(f).mkdir(parents=True, exist_ok=True)
    (Path(f) / ".gitkeep").touch()
for f in files:
    Path(f).touch()

print("Structure created.")