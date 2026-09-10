# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 lollapalooza <https://github.com/aqua5230>

from __future__ import annotations

import pytest

from loaders.agy_quota_probe import AgyQuotaWindow
from loaders.grok_quota_probe import GrokQuotaResult
from menubar import agy as menubar_agy
from menubar import grok as menubar_grok
from menubar import state as menubar_state
from menubar.reset_window import format_remaining_percentage


@pytest.mark.parametrize(
    ("reset_at", "window_seconds", "expected"),
    [
        (150.0, 100.0, "50%"),
        (149.5, 100.0, "49.5%"),
        (149.555, 100.0, "49.56%"),
        (250.0, 100.0, "100%"),
        (100.0, 100.0, "0%"),
    ],
)
def test_format_remaining_percentage_formats_rounds_and_clamps(
    reset_at: float, window_seconds: float, expected: str
) -> None:
    assert format_remaining_percentage(reset_at, window_seconds, 100.0) == expected


@pytest.mark.parametrize(
    ("reset_at", "window_seconds"),
    [
        (None, 100.0),
        (150.0, None),
        (150.0, 0.0),
        (150.0, -1.0),
        (99.0, 100.0),
        (float("nan"), 100.0),
    ],
)
def test_format_remaining_percentage_rejects_insufficient_or_invalid_data(
    reset_at: float | None, window_seconds: float | None
) -> None:
    assert format_remaining_percentage(reset_at, window_seconds, 100.0) is None


def test_quota_row_keeps_countdown_when_provider_did_not_report_window_duration() -> None:
    row = menubar_state._quota_row(
        "Session", 50.0, 160.0, 100.0, menubar_state.CODEX_COLOR, language="en"
    )

    assert row.reset_text == "Resets in 1m"


def test_quota_row_uses_percentage_only_when_provider_reports_duration() -> None:
    row = menubar_state._quota_row(
        "Session",
        50.0,
        149.555,
        100.0,
        menubar_state.CODEX_COLOR,
        language="en",
        window_seconds=100.0,
    )

    assert row.reset_text == "49.56%"


def test_antigravity_row_uses_its_reported_reset_boundary_and_window() -> None:
    row = menubar_agy._window_row(
        "Session",
        AgyQuotaWindow(50.0, "1m", 1, resets_at=150.0, window_seconds=100.0),
        "en",
        100.0,
    )

    assert row.reset_text == "50%"


def test_grok_row_keeps_countdown_without_period_start() -> None:
    quota = GrokQuotaResult(
        used_percent=18.0,
        period_end="1970-01-01T00:02:40+00:00",
        fetched_at="1970-01-01T00:00:00+00:00",
        subscription_tier=None,
    )

    projection = menubar_grok.project_quota(quota, "en", now=100.0)

    assert projection is not None
    assert projection.weekly.reset_text == "Resets in 1m"


def test_grok_row_uses_reported_period_start_for_percentage() -> None:
    quota = GrokQuotaResult(
        used_percent=18.0,
        period_end="1970-01-01T00:03:20+00:00",
        fetched_at="1970-01-01T00:00:00+00:00",
        subscription_tier=None,
        period_start="1970-01-01T00:00:00+00:00",
    )

    projection = menubar_grok.project_quota(quota, "en", now=100.0)

    assert projection is not None
    assert projection.weekly.reset_text == "50%"
