"""Static checks: requirements, Python syntax, and earlier repository fixes."""
import ast
import re
import sys

import pytest

from conftest import PROJECT_ROOT

REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
LOCAL_PACKAGES = {"config", "main", "scripts", "tests", "conftest"}

# import name -> distribution name in requirements.txt
IMPORT_TO_DIST = {
    "pandas": "pandas",
    "sqlalchemy": "sqlalchemy",
    "dotenv": "python-dotenv",
}
# Libraries loaded by name at runtime rather than by an import statement:
#   openpyxl -> pd.read_excel(engine="openpyxl") in main/extract.py
#   psycopg2 -> "postgresql+psycopg2://" connection string in main/load.py
RUNTIME_DISTS = {"openpyxl", "psycopg2-binary"}

PROJECT_PY_FILES = sorted(
    p for p in PROJECT_ROOT.rglob("*.py")
    if not any(part in {"venv", ".venv", "env", "__pycache__"} for part in p.parts)
)


def pinned_requirements():
    raw = REQUIREMENTS.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "requirements.txt has a UTF-8 BOM"
    assert not raw.startswith((b"\xff\xfe", b"\xfe\xff")), "requirements.txt is UTF-16"
    lines = [l.strip() for l in raw.decode("utf-8").splitlines() if l.strip()]
    pins = {}
    for line in lines:
        match = re.fullmatch(r"([A-Za-z0-9_.\-]+)==([A-Za-z0-9_.\-]+)", line)
        assert match, f"malformed requirement line: {line!r}"
        name = match.group(1).lower().replace("_", "-")
        assert name not in pins, f"duplicate requirement: {name}"
        pins[name] = match.group(2)
    return pins


# ── requirements.txt ────────────────────────────────────────

def test_requirements_is_valid_utf8_with_pinned_versions():
    assert len(pinned_requirements()) > 0


def test_every_third_party_import_is_in_requirements():
    pins = pinned_requirements()
    stdlib = set(sys.stdlib_module_names)
    missing = []
    for path in PROJECT_PY_FILES:
        if "tests" in path.relative_to(PROJECT_ROOT).parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top in stdlib or top in LOCAL_PACKAGES:
                    continue
                dist = IMPORT_TO_DIST.get(top)
                if dist is None or dist not in pins:
                    missing.append(f"{path.name}: {top}")
    assert not missing, f"imports without a requirement: {missing}"


@pytest.mark.parametrize("dist", sorted(RUNTIME_DISTS))
def test_runtime_libraries_are_in_requirements(dist):
    assert dist in pinned_requirements()


def test_pyodbc_removed_and_unused():
    assert "pyodbc" not in pinned_requirements()
    for path in PROJECT_PY_FILES:
        if path.name == "test_project_files.py":
            continue
        assert "pyodbc" not in path.read_text(encoding="utf-8"), path


# ── Python syntax ───────────────────────────────────────────

@pytest.mark.parametrize("path", PROJECT_PY_FILES, ids=lambda p: str(p.relative_to(PROJECT_ROOT)))
def test_python_syntax(path):
    compile(path.read_text(encoding="utf-8"), str(path), "exec")


# ── earlier fixes still in place ────────────────────────────

def test_run_pipeline_bat_uses_project_relative_paths():
    bat = (PROJECT_ROOT / "run_pipeline.bat").read_text(encoding="ascii")
    assert 'cd /d "%~dp0"' in bat
    assert "python scripts\\pipeline.py" in bat
    assert "exit /b %EXIT_CODE%" in bat
    assert not re.search(r"[A-Za-z]:\\Users", bat, re.IGNORECASE)


def test_gitattributes_keeps_bat_files_crlf():
    attrs = (PROJECT_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert re.search(r"^\*\.bat\s+text\s+eol=crlf", attrs, re.MULTILINE)


def test_gitignore_covers_secrets_logs_and_caches():
    ignored = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for entry in (".env", "logs/", "*.log", "__pycache__/", "venv/", ".venv/"):
        assert entry in ignored, entry


def test_readme_has_real_links_and_no_placeholders():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "https://github.com/HassanElhussieny/Sales_ETL_Project.git" in readme
    assert "https://www.linkedin.com/in/hassan-elhussieny-023291273/" in readme
    for placeholder in ("yourusername", "yourprofile", "Data_Analytics_project"):
        assert placeholder not in readme, placeholder


def test_no_hardcoded_personal_paths_in_project_files():
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_dir() or ".git" in path.parts or path.suffix in {".xlsx", ".pyc"}:
            continue
        if path.name == "test_project_files.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "LENOVO" not in text, path
