import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import validate as v  # noqa: E402

DATA = ROOT / "data"


def load(items_path=None):
    paths = {n: DATA / f"{n}.csv" for n in v.SCHEMA}
    if items_path:
        paths["checklist_items"] = items_path
    return v.load_csvs(paths)


def checks(report, level=None):
    return {f.check for f in report.findings if level is None or f.level == level}


def test_bundled_dataset_passes():
    rep = v.validate(load(), as_of="2026-09-01")
    assert rep.ok
    assert rep.row_counts["rooms"] == 120


def test_dirty_sample_fails_with_expected_checks():
    rep = v.validate(load(DATA / "samples" / "checklist_items_dirty.csv"), as_of="2026-09-01")
    assert not rep.ok
    errs = checks(rep, "ERROR")
    for expected in ["missing_value", "duplicate_id", "invalid_value", "unparseable_date",
                     "orphan_room", "orphan_owner", "done_without_date", "created_after_due"]:
        assert expected in errs, expected
    warns = checks(rep, "WARNING")
    assert {"missing_optional_columns", "blocked_without_reason", "future_completion"} <= warns


def test_status_case_and_whitespace_are_normalised():
    raw = load()
    items = raw["checklist_items"].copy()
    items.loc[0, "status"] = "  in progress "
    items.loc[0, "completed_date"] = ""
    raw["checklist_items"] = items
    rep = v.validate(raw, as_of="2026-09-01")
    assert "invalid_value" not in checks(rep)
    assert rep.tables["checklist_items"].loc[0, "status"] == "In Progress"


def test_missing_required_column_is_an_error():
    raw = load()
    raw["rooms"] = raw["rooms"].drop(columns=["unit"])
    rep = v.validate(raw, as_of="2026-09-01")
    assert "missing_columns" in checks(rep, "ERROR")


def test_report_frame_has_sortable_counts():
    rep = v.validate(load(DATA / "samples" / "checklist_items_dirty.csv"), as_of="2026-09-01")
    df = rep.to_frame()
    assert str(df["rows_affected"].dtype) == "Int64"
    assert (df["level"] == "ERROR").sum() == len(rep.errors)
