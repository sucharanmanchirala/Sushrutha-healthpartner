"""
Susrutha Health Partner - Daily Health Activity helper
======================================================

Owns the three pieces of logic the Daily Health Activity feature needs, so the rules
live in one tested, auditable place instead of in the browser:

1. ``activity_for`` - deterministic, date-based selection of the featured activity.
   ``date.toordinal() % number_of_activities`` is stable: the same activity is shown
   for the whole day, in every language, on every page load, without any storage.

2. ``localise`` - returns the requested language's title/steps/duration/messages for
   that activity (English fallback), keeping activity *ids* untouched.

3. ``complete`` - idempotent completion bookkeeping. The browser keeps the log in
   ``localStorage`` (no database, no account, no personal data), and sends it back
   with each request; the server applies the rules and returns the updated log plus
   the weekly summary. Marking the same day twice never increases the count.

Safety: the content itself lives in ``data/activities.json`` and carries the
wellbeing-only framing - general suggestions, no medical claims, an easier
alternative for every activity, and a reminder that the Symptom Checker / 108
stay in charge when something feels like a medical problem.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from i18n import DEFAULT_LANG, SUPPORTED, normalise

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

SUMMARY_WINDOW_DAYS = 7
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _load_doc() -> Dict[str, Any]:
    with open(os.path.join(DATA_DIR, "activities.json"), "r", encoding="utf-8") as handle:
        return json.load(handle)


DOC: Dict[str, Any] = _load_doc()
ACTIVITIES: List[Dict[str, Any]] = DOC.get("activities", [])


def activity_ids() -> List[str]:
    return [a["id"] for a in ACTIVITIES]


def normalise_lang(lang: Any) -> str:
    """Return a supported language code (en / te / hi), falling back to English."""
    return normalise(lang)


def _pick(field: Any, lang: str) -> Any:
    """Pick the localized value from a per-language mapping, with English fallback."""
    if isinstance(field, dict):
        return field.get(lang) or field.get(DEFAULT_LANG) or ""
    return field


def activity_for(date: Optional[dt.date] = None) -> Dict[str, Any]:
    """The featured activity for a given date (defaults to today, server local time).

    Selection is purely a function of the date, so refreshing the page never changes
    today's activity and no storage is required.
    """
    if not ACTIVITIES:
        raise RuntimeError("data/activities.json contains no activities")
    day = date or dt.date.today()
    return ACTIVITIES[day.toordinal() % len(ACTIVITIES)]


def localise(activity: Dict[str, Any], lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """Return the activity with human-readable text in ``lang``.

    Ids and icons are machine-readable and are never translated.
    """
    code = normalise_lang(lang)
    return {
        "id": activity["id"],
        "icon": activity.get("icon", "🌿"),
        "category": _pick(activity.get("category"), code),
        "title": _pick(activity.get("title"), code),
        "why": _pick(activity.get("why"), code),
        "steps": list(_pick(activity.get("steps"), code) or []),
        "duration": _pick(activity.get("duration"), code),
        "done": _pick(activity.get("done"), code),
        "alt": _pick(activity.get("alt"), code),
        "lang": code,
        "available_in": sorted(
            [k for k, v in activity.get("title", {}).items() if v]
        ),
    }


def payload(lang: str = DEFAULT_LANG, date: Optional[dt.date] = None) -> Dict[str, Any]:
    """Everything the browser needs to render today's featured activity."""
    day = date or dt.date.today()
    return {
        "date": day.isoformat(),
        "lang": normalise_lang(lang),
        "activity": localise(activity_for(day), lang),
        "total_activities": len(ACTIVITIES),
        "safety": _pick(DOC.get("safety"), normalise_lang(lang)),
        "summary_labels": {
            "label": _pick(DOC.get("summary", {}).get("label"), normalise_lang(lang)),
            "empty": _pick(DOC.get("summary", {}).get("empty"), normalise_lang(lang)),
            "storage": _pick(DOC.get("summary", {}).get("storage"), normalise_lang(lang)),
        },
        "content_languages": sorted(DOC.get("activities", [{}])[0].get("title", {}).keys())
        if ACTIVITIES else ["en"],
    }


# --------------------------------------------------------------------------- #
# Completion log
# --------------------------------------------------------------------------- #
def parse_log(raw: Any) -> Dict[str, str]:
    """Coerce whatever the browser sent into a clean ``{date: activity_id}`` log.

    Accepts a dict, a JSON string, or nothing. Unknown keys are dropped and only
    well-formed ``YYYY-MM-DD`` dates with a known activity id survive, so a tampered
    payload can never break the summary.
    """
    if not raw:
        return {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return {}
    if not isinstance(raw, dict):
        return {}
    known = set(activity_ids())
    log: Dict[str, str] = {}
    for key, value in raw.items():
        key = str(key)
        if _DATE_RE.match(key) and isinstance(value, str) and value in known:
            log[key] = value
    return log


def complete(
    log: Dict[str, str], date: str, activity_id: str
) -> Tuple[Dict[str, str], bool]:
    """Mark ``date`` complete for ``activity_id``.

    Idempotent: if the date is already recorded the log is returned untouched and
    ``already`` is True, so repeated clicks cannot increase the completion count.
    Returns ``(new_log, already_done)``.
    """
    if not _DATE_RE.match(str(date)):
        raise ValueError("date must be formatted YYYY-MM-DD")
    if activity_id not in set(activity_ids()):
        raise ValueError("unknown activity id")
    updated = dict(log)
    if date in updated:
        return updated, True
    updated[date] = activity_id
    return updated, False


def weekly_summary(log: Dict[str, str], today: Optional[dt.date] = None) -> Dict[str, Any]:
    """Completion counts for the window ending on ``today`` (default: server today)."""
    end = today or dt.date.today()
    days = [end - dt.timedelta(days=i) for i in range(SUMMARY_WINDOW_DAYS - 1, -1, -1)]
    done_dates = [d.isoformat() for d in days if d.isoformat() in log]
    return {
        "done": len(done_dates),
        "total": SUMMARY_WINDOW_DAYS,
        "completed_dates": done_dates,
        "day_keys": [d.isoformat() for d in days],
        "activity_by_date": {d.isoformat(): log[d.isoformat()] for d in days if d.isoformat() in log},
    }
