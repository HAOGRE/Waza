"""Shipped auditors must not drift on mechanical definitions.

skills/check/scripts/audit_signals.py and
skills/health/scripts/check_maintainability.py stay self-contained by policy
(no shared module across shipped skills), so their common definitions are
copies. This test enforces "align the copies in place": the sets and regexes
that decide WHICH files and markers count must be identical. Thresholds and
status semantics are per-product calibration and intentionally not compared.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load_module("waza_audit_signals", "skills/check/scripts/audit_signals.py")
maint = load_module(
    "waza_check_maintainability", "skills/health/scripts/check_maintainability.py"
)


def test_excluded_dirs_aligned():
    assert audit.EXCLUDED_DIRS == maint.EXCLUDED_DIRS


def test_source_exts_aligned():
    assert audit.SOURCE_EXTS == maint.SOURCE_EXTS


def test_source_exts_preserve_existing_coverage():
    assert {".md", ".yaml", ".yml"} <= audit.SOURCE_EXTS


def test_audit_consumers_normalize_extension_case(tmp_path, capsys):
    source = tmp_path / "UPPER.PY"
    source.write_text("# todo\n")
    audit.block_drift_markers([source], tmp_path)
    assert "total=1" in capsys.readouterr().out


def test_marker_regex_aligned():
    assert audit.MARKER_RE.pattern == maint.MARKER_RE.pattern
    assert audit.MARKER_RE.flags == maint.MARKER_RE.flags


def test_marker_regex_preserves_lowercase_detection():
    for marker in ("todo", "fixme", "hack", "xxx"):
        assert audit.MARKER_RE.search(marker)


def test_minified_filter_aligned():
    assert audit.MINIFIED_RE.pattern == maint.MINIFIED_RE.pattern
    assert audit.MINIFIED_RE.flags == maint.MINIFIED_RE.flags
