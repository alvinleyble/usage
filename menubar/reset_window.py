# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 lollapalooza <https://github.com/aqua5230>
#
# Part of "usage". Free software licensed under the GNU Affero General Public
# License v3.0 only; see the LICENSE file for full terms and the warranty disclaimer.

"""Formatting for provider-reported quota-window time remaining."""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP


def format_remaining_percentage(
    reset_at: float | None,
    window_seconds: float | None,
    now: float,
) -> str | None:
    """Return time remaining in a provider-reported window, or ``None`` if unsure.

    A duration is deliberately required: a reset time alone does not establish
    how much of a provider's rolling window has elapsed.
    """
    if not all(_is_finite(value) for value in (reset_at, window_seconds, now)):
        return None
    assert reset_at is not None and window_seconds is not None
    if window_seconds <= 0 or reset_at < now:
        return None
    percent = max(0.0, min(100.0, (reset_at - now) / window_seconds * 100.0))
    rounded = Decimal(str(percent)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = format(rounded, "f").rstrip("0").rstrip(".")
    return f"{text}%"


def _is_finite(value: float | None) -> bool:
    return (
        value is not None
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )
