"""
Susrutha Health Partner - rule-based health triage engine
=========================================================

This module is the "brain" of the prototype and it deliberately contains NO
machine-learning diagnosis. Everything is transparent, deterministic and
auditable:

1. The knowledge base lives in plain JSON under ``data/`` and is summarised from
   WHO / CDC / NHS / MedlinePlus public health information.
2. A symptom pattern is scored against each condition's published symptom
   description using a weighted match (classic features weigh more).
3. A separate triage gate looks at RED FLAG symptoms and personal risk factors
   and decides the urgency of care - independent of which condition matched.
4. The output is always framed as "pattern alignment + urgency guidance",
   never as a diagnosis.

Author: Team Susrutha - Healthcare & Medical Innovation track.
"""

from __future__ import annotations

import json
import math
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ordering of care levels, from least to most urgent.
CARE_ORDER: List[str] = ["selfcare", "routine", "urgent", "emergency"]

CARE_META: Dict[str, Dict[str, str]] = {
    "selfcare": {
        "label": "Self-care at home",
        "headline": "Home care is usually enough",
        "tone": "low",
        "guidance": (
            "Your pattern fits a mild, usually self-limiting illness. Rest, fluids and simple "
            "home care are normally enough. See a doctor if it has not improved in 2-3 days, "
            "or sooner if it gets worse."
        ),
    },
    "routine": {
        "label": "Routine appointment",
        "headline": "Book a doctor's appointment soon",
        "tone": "medium",
        "guidance": (
            "This is not an emergency, but it does need a clinician's assessment and usually a "
            "test. Book an appointment in the next day or two and keep a note of your symptoms."
        ),
    },
    "urgent": {
        "label": "Urgent - see a doctor today",
        "headline": "Get a same-day medical assessment",
        "tone": "high",
        "guidance": (
            "Please see a doctor TODAY - go to a hospital OPD, a fever clinic or an urgent care "
            "centre. Do not wait several days, and go to an emergency department immediately if "
            "any red-flag symptom appears."
        ),
    },
    "emergency": {
        "label": "Emergency - act now",
        "headline": "Seek emergency care immediately",
        "tone": "critical",
        "guidance": (
            "Call 108 for an ambulance or 112, or go to the nearest emergency department now. "
            "Do not drive yourself if you feel very unwell. Do not wait for test results."
        ),
    },
}

DISCLAIMER = (
    "This tool provides general health information from public sources (WHO, CDC, NHS, "
    "MedlinePlus) to help you decide what to do next. It is NOT a diagnosis and it cannot "
    "rule out serious illness. Always consult a qualified doctor about your own health."
)

# Generic words that appear in many symptom descriptions. Matching on them alone would
# produce false positives ("where can I get a blood test" is not "blood in vomit"), so the
# chatbot ignores them when scanning a sentence for symptoms.
GENERIC_SYMPTOM_WORDS = {
    "blood", "pain", "severe", "feeling", "high", "very", "body", "more", "over", "than",
    "with", "cannot", "little", "less", "other", "sensation", "sound", "light", "wound",
    "hands", "feet", "face", "eyes", "skin", "white", "cold", "days", "times", "again",
    "slow", "hard", "awake", "loss", "sore", "mild", "yellow", "above", "around", "spots",
    "red", "pink", "burning", "frequent", "cloudy", "watery", "itchy", "blocked", "runny",
    "dry", "stiff", "sudden", "sticky", "passing", "night", "sweaty", "swelling", "and",
    "motions", "tract", "while", "when", "have", "since", "keeps", "down", "keep", "urine",
}

# Words the chatbot treats as an immediate emergency trigger.
EMERGENCY_PHRASES = [
    "chest pain", "chest pressure", "heart attack", "cannot breathe", "can't breathe",
    "difficulty breathing", "breathing difficulty", "unconscious", "passed out", "fainted",
    "bleeding heavily", "heavy bleeding", "severe bleeding", "stroke", "paralysis",
    "slurred speech", "fits", "seizure", "convulsion", "not breathing", "collapsed",
    "blue lips", "emergency", "ambulance", "108", "suicide", "overdose",
    # precise red-flag phrases so a mild sentence cannot trip the alarm
    "blood in vomit", "vomiting blood", "blood in stool", "bloody stool", "black stool",
    "blood in urine", "stiff neck", "one sided weakness", "cannot keep fluids",
    "no urine", "not passing urine", "severe abdominal pain", "cannot drink",
]


def _load(name: str) -> Dict[str, Any]:
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in kilometres between two coordinates."""
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", (text or "").lower()).strip()


class KnowledgeBase:
    """Loads the JSON knowledge base and exposes the service layer."""

    def __init__(self, data_dir: str = DATA_DIR) -> None:
        global DATA_DIR
        DATA_DIR = data_dir
        self.symptoms_doc = _load("symptoms.json")
        self.conditions_doc = _load("conditions.json")
        self.facilities_doc = _load("facilities.json")
        self.localities_doc = _load("localities.json")
        self.chat_doc = _load("chatbot.json")

        self.conditions: List[Dict[str, Any]] = self.conditions_doc["conditions"]
        self.by_id: Dict[str, Dict[str, Any]] = {c["id"]: c for c in self.conditions}
        self.facilities: List[Dict[str, Any]] = self.facilities_doc["facilities"]
        self.localities: List[Dict[str, Any]] = self.localities_doc["localities"]

        # Flat symptom lookup: id -> {label, keywords, emergency, group}
        self.symptoms: Dict[str, Dict[str, Any]] = {}
        for group in self.symptoms_doc["groups"]:
            for sym in group["symptoms"]:
                self.symptoms[sym["id"]] = {
                    **sym,
                    "group": group["name"],
                    "group_id": group["id"],
                }

        # Reverse index used by the chatbot: English text -> symptom ids.
        # Two levels of precision on purpose, so the assistant does not "find" a symptom
        # inside an ordinary sentence:
        #   * symptom_phrases - whole multi-word keywords ("blood in vomit") matched as
        #     substrings. High precision, so these are trusted.
        #   * symptom_words   - single distinctive words from the labels/keywords, with a
        #     generic-word stop-list removed ("blood", "pain", "severe" ... ) so that
        #     "where can I get a blood test" is not read as "blood in vomit".
        self.symptom_phrases: Dict[str, List[str]] = {}
        self.symptom_words: Dict[str, List[str]] = {}
        for sym_id, sym in self.symptoms.items():
            for keyword in sym.get("keywords", []):
                clean = _norm(keyword)
                if " " in clean and clean:
                    self.symptom_phrases.setdefault(clean, []).append(sym_id)

            keyword_tokens = {word for kw in sym.get("keywords", []) for word in _norm(kw).split()}
            label_tokens = set(_norm(sym["label"]).split())
            tokens = keyword_tokens | label_tokens | {sym_id.replace("_", " ")}
            for word in tokens:
                if len(word) > 3 and word not in GENERIC_SYMPTOM_WORDS and " " not in word:
                    # Rank so that an explicit keyword outranks a word that merely appears in a
                    # label. When several symptoms share a word, "fever" should resolve to the
                    # plain fever symptom rather than both fever and high fever.
                    rank = 0 if word in keyword_tokens else 1
                    self.symptom_words.setdefault(word, []).append((rank, sym_id))

        # Keep only the best candidate per word, so one word never reports two symptoms.
        self.symptom_words = {
            word: [sym_id for _, sym_id in sorted(candidates)[:1]]
            for word, candidates in self.symptom_words.items()
        }

    # ------------------------------------------------------------------ #
    # Catalogue helpers
    # ------------------------------------------------------------------ #
    def symptom_groups(self) -> List[Dict[str, Any]]:
        return self.symptoms_doc["groups"]

    def symptom_label(self, sym_id: str) -> str:
        sym = self.symptoms.get(sym_id)
        return sym["label"] if sym else sym_id.replace("_", " ").title()

    def emergency_ids(self) -> List[str]:
        return [sid for sid, s in self.symptoms.items() if s.get("emergency")]

    def library(self) -> List[Dict[str, Any]]:
        """Compact condition list for the Health Library UI."""
        out = []
        for cond in self.conditions:
            out.append(
                {
                    "id": cond["id"],
                    "name": cond["name"],
                    "aka": cond.get("aka", ""),
                    "category": cond["category"],
                    "care_level": cond["care_level"],
                    "care_label": CARE_META[cond["care_level"]]["label"],
                    "overview": cond["overview"],
                    "symptom_count": len(cond["symptoms"]),
                    "symptoms": [
                        self.symptom_label(s)
                        for s in sorted(
                            cond["symptoms"], key=lambda k: -cond["symptoms"][k]
                        )[:6]
                    ],
                    "red_flag_count": len(cond["red_flags"]),
                }
            )
        return sorted(out, key=lambda c: c["name"])

    def condition_detail(self, cond_id: str) -> Optional[Dict[str, Any]]:
        cond = self.by_id.get(cond_id)
        if not cond:
            return None
        detail = dict(cond)
        detail["symptom_labels"] = [
            {"id": sid, "label": self.symptom_label(sid), "weight": weight}
            for sid, weight in sorted(cond["symptoms"].items(), key=lambda kv: -kv[1])
        ]
        detail["care_label"] = CARE_META[cond["care_level"]]["label"]
        return detail

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Free-text search across the condition library."""
        q = _norm(query)
        if not q:
            return self.library()
        tokens = [t for t in q.split() if len(t) > 2]
        scored: List[tuple] = []
        for cond in self.conditions:
            haystack = " ".join(
                [
                    cond["name"],
                    cond.get("aka", ""),
                    cond["category"],
                    cond["overview"],
                    " ".join(self.symptom_label(s) for s in cond["symptoms"]),
                    " ".join(cond["precautions"]),
                ]
            ).lower()
            score = 0
            for token in tokens:
                if token in cond["name"].lower():
                    score += 5
                score += haystack.count(token)
            if score:
                scored.append((score, cond["id"]))
        scored.sort(reverse=True)
        order = [cid for _, cid in scored]
        lib = {c["id"]: c for c in self.library()}
        return [lib[cid] for cid in order]

    # ------------------------------------------------------------------ #
    # Core feature 1 - Symptom check + risk awareness
    # ------------------------------------------------------------------ #
    def assess(
        self,
        selected: Sequence[str],
        profile: Optional[Dict[str, Any]] = None,
        top_n: int = 4,
    ) -> Dict[str, Any]:
        """Score a symptom pattern against the knowledge base and triage it."""
        profile = profile or {}
        selected = [s for s in dict.fromkeys(selected) if s in self.symptoms]

        red_flags_hit = [s for s in selected if self.symptoms[s].get("emergency")]
        risk_factors = self._risk_factors(profile, selected)
        duration = profile.get("duration_days")

        results: List[Dict[str, Any]] = []
        for cond in self.conditions:
            weights: Dict[str, int] = cond["symptoms"]
            matched = [s for s in selected if s in weights]
            matched_weight = sum(weights[s] for s in matched)
            total_weight = sum(weights.values())
            if not selected:
                continue
            coverage = matched_weight / total_weight
            specificity = len(matched) / len(selected)
            # Weighted blend: how much of the condition picture is present, and
            # how much of what the user reported the condition explains.
            raw = 0.65 * coverage + 0.35 * specificity
            if not matched:
                raw = 0.0
            results.append(
                {
                    "id": cond["id"],
                    "name": cond["name"],
                    "category": cond["category"],
                    "care_level": cond["care_level"],
                    "care_label": CARE_META[cond["care_level"]]["label"],
                    "raw": raw,
                    "matched": matched,
                    "matched_labels": [self.symptom_label(s) for s in matched],
                    "missing_key": self._missing_key_symptoms(cond, matched),
                    "overview": cond["overview"],
                }
            )

        results.sort(key=lambda r: (-r["raw"], -len(r["matched"])))
        top = results[: max(1, top_n)]
        best = top[0]["raw"] if top else 0.0
        for item in top:
            item["match_percent"] = round((item["raw"] / best) * 100) if best else 0
            item["absolute"] = round(item["raw"], 3)
            item["band"] = self._band(item["raw"])

        # ---- Triage gate (independent of the condition scoring) ---- #
        level = self._base_level(top, selected, profile)
        if red_flags_hit:
            level = "emergency"
        else:
            level = self._escalate(level, risk_factors, len(red_flags_hit) == 0)

        primary = self.by_id.get(top[0]["id"]) if top else None
        ambiguity = (
            len(top) > 1
            and best > 0
            and (top[1]["raw"] / best) >= 0.80
            and top[1]["raw"] > 0
        )

        return {
            "disclaimer": DISCLAIMER,
            "care": {
                "level": level,
                "label": CARE_META[level]["label"],
                "headline": CARE_META[level]["headline"],
                "tone": CARE_META[level]["tone"],
                "guidance": CARE_META[level]["guidance"],
            },
            "emergency_symptoms": [
                {"id": s, "label": self.symptom_label(s)} for s in red_flags_hit
            ],
            "risk_factors": risk_factors,
            "risk_note": self._risk_note(risk_factors, duration),
            "matches": top,
            "ambiguity_warning": ambiguity,
            "insufficient_data": len(selected) < 2,
            "selected": [
                {"id": s, "label": self.symptom_label(s)} for s in selected
            ],
            "next_steps": self._next_steps(level, primary, red_flags_hit),
            "red_flags": (primary or {}).get("red_flags", [])[:5],
            "precautions": (primary or {}).get("precautions", [])[:6],
            "self_care": (primary or {}).get("self_care", [])[:5],
            "tests": (primary or {}).get("tests", []),
            "specialties": (primary or {}).get("specialties", []),
            "sources": (primary or {}).get("sources", []),
            "primary_id": (primary or {}).get("id"),
            "emergency_numbers": self.facilities_doc.get("emergency_numbers", []),
        }

    @staticmethod
    def _band(raw: float) -> str:
        if raw >= 0.45:
            return "Strong"
        if raw >= 0.30:
            return "Moderate"
        if raw >= 0.18:
            return "Fair"
        return "Weak"

    def _missing_key_symptoms(
        self, cond: Dict[str, Any], matched: Iterable[str], limit: int = 3
    ) -> List[str]:
        matched = set(matched)
        key = [
            (w, s) for s, w in cond["symptoms"].items() if w >= 3 and s not in matched
        ]
        key.sort(reverse=True)
        return [self.symptom_label(s) for _, s in key[:limit]]

    def _risk_factors(
        self, profile: Dict[str, Any], selected: Sequence[str]
    ) -> List[str]:
        factors: List[str] = []
        try:
            age = int(profile.get("age")) if profile.get("age") not in (None, "") else None
        except (TypeError, ValueError):
            age = None
        if age is not None:
            if age < 1:
                factors.append("infant under 1 year")
            elif age < 5:
                factors.append("child under 5 years")
            elif age >= 60:
                factors.append("age 60 years or above")
        if profile.get("pregnant"):
            factors.append("pregnancy")
        for item in profile.get("chronic") or []:
            if item:
                factors.append(str(item))
        if profile.get("severity") == "severe":
            factors.append("symptoms described as severe")
        if any(self.symptoms[s].get("emergency") for s in selected):
            factors.append("a red-flag symptom reported")
        return factors

    @staticmethod
    def _risk_note(factors: Sequence[str], duration: Any) -> str:
        notes: List[str] = []
        if factors:
            notes.append(
                "Your answers include "
                + ", ".join(factors)
                + ". These make complications more likely, so we have raised the urgency level."
            )
        try:
            days = int(duration) if duration not in (None, "") else None
        except (TypeError, ValueError):
            days = None
        if days is not None and days >= 7:
            notes.append(
                f"You have had these symptoms for about {days} days. Symptoms lasting more than "
                "a week always need a clinician's review."
            )
        elif days is not None and days <= 1:
            notes.append(
                "Symptoms started very recently - watch closely for the next 24-48 hours."
            )
        return " ".join(notes)

    def _base_level(
        self,
        top: Sequence[Dict[str, Any]],
        selected: Sequence[str],
        profile: Dict[str, Any],
    ) -> str:
        if not top:
            return "routine"
        if len(selected) < 2:
            # A single symptom is not enough to justify a low-urgency label.
            return max(top[0]["care_level"], "routine", key=CARE_ORDER.index)
        return top[0]["care_level"]

    @staticmethod
    def _escalate(level: str, factors: Sequence[str], hard_escalate: bool = True) -> str:
        if not factors or not hard_escalate:
            return level
        idx = CARE_ORDER.index(level)
        return CARE_ORDER[min(idx + 1, len(CARE_ORDER) - 1)]

    @staticmethod
    def _next_steps(
        level: str, primary: Optional[Dict[str, Any]], red_flags: Sequence[str]
    ) -> List[str]:
        steps: List[str] = []
        if level == "emergency":
            steps.append("Call 108 for an ambulance or 112, or reach the nearest emergency department now.")
            steps.append("Do not drive yourself if you feel faint, breathless or confused.")
        elif level == "urgent":
            steps.append("Visit a hospital OPD, fever clinic or urgent care centre today.")
        elif level == "routine":
            steps.append("Book an appointment with a general physician within the next day or two.")
        else:
            steps.append("Rest, keep drinking fluids and monitor your symptoms at home.")
        if primary and primary.get("tests"):
            steps.append(
                "Ask your doctor about these tests: " + ", ".join(primary["tests"][:3]) + "."
            )
        if red_flags:
            steps.append("Go straight to an emergency department if this happens: " + red_flags[0] + ".")
        steps.append("Use the Find Care tab to locate a suitable hospital or laboratory in Hyderabad.")
        return steps

    # ------------------------------------------------------------------ #
    # Core feature 2 - Facility discovery (Hyderabad)
    # ------------------------------------------------------------------ #
    def _specialty_weights(self) -> Dict[str, float]:
        """Inverse-frequency weight per specialty.

        A department offered by only a few hospitals ("Fever / Tropical Diseases") is far more
        informative than one offered by nearly all of them ("General Medicine"). Weighting by
        rarity stops "Dengue" from simply matching every hospital in the city, and it is easy
        to explain: the rarer the service, the more it counts.
        """
        total = max(1, len(self.facilities))
        counts: Dict[str, int] = {}
        for fac in self.facilities:
            for spec in set(fac["specialties"]):
                counts[spec] = counts.get(spec, 0) + 1
        return {s: math.log((total + 1) / (c + 1)) + 1.0 for s, c in counts.items()}

    def find_facilities(
        self,
        condition_id: Optional[str] = None,
        specialty: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        sector: str = "all",
        limit: int = 12,
        order: str = "auto",
    ) -> Dict[str, Any]:
        cond = self.by_id.get(condition_id or "")
        wanted: List[str] = []
        if cond:
            wanted = list(cond["specialties"])
        if specialty and specialty != "All":
            wanted = [specialty]
        weights = self._specialty_weights()
        wanted_weight = sum(weights.get(s, 1.0) for s in wanted) or 1.0

        origin_lat = float(lat) if lat is not None else None
        origin_lng = float(lng) if lng is not None else None

        rows: List[Dict[str, Any]] = []
        for fac in self.facilities:
            if sector in ("Government", "Private", "Diagnostic Lab") and fac["type"] != sector:
                continue
            overlap = [s for s in wanted if s in fac["specialties"]]
            if wanted and not overlap:
                continue
            distance = None
            if origin_lat is not None and origin_lng is not None:
                distance = haversine_km(origin_lat, origin_lng, fac["lat"], fac["lng"])
            relevance = sum(weights.get(s, 1.0) for s in overlap) / wanted_weight if wanted else 1.0
            row = dict(fac)
            row["matched_specialties"] = overlap
            row["distance_km"] = round(distance, 1) if distance is not None else None
            row["relevance"] = round(relevance, 3)
            if wanted:
                row["tier"] = (
                    "Best match" if relevance >= 0.7
                    else "Good match" if relevance >= 0.45
                    else "General care"
                )
            else:
                row["tier"] = ""
            # Ranking rule (documented so it is easy to defend):
            #   * with a location  -> nearest first, then best specialty match, then Government
            #   * without a location -> best specialty match, then Government, then private
            type_order = 0 if fac["type"] == "Government" else 1
            by_relevance = order == "relevance" or (order == "auto" and distance is None)
            if by_relevance:
                row["_rank"] = (-relevance, distance if distance is not None else 999, type_order, fac["id"])
            else:
                row["_rank"] = (distance if distance is not None else 999, -relevance, type_order, fac["id"])
            row["sort"] = "relevance" if by_relevance else "distance"
            rows.append(row)

        rows.sort(key=lambda r: r["_rank"])
        for row in rows:
            row.pop("_rank", None)
            row["maps_url"] = (
                "https://www.google.com/maps/dir/?api=1&destination="
                f"{row['lat']},{row['lng']}"
            )
        return {
            "condition": cond["name"] if cond else None,
            "condition_id": cond["id"] if cond else None,
            "specialties": wanted,
            "results": rows[:limit],
            "total": len(rows),
            "sorted_by": "relevance" if (order == "relevance" or (order == "auto" and origin_lat is None)) else "distance",
            "emergency_numbers": self.facilities_doc.get("emergency_numbers", []),
            "note": self.facilities_doc.get("note", ""),
            "localities": self.localities,
        }

    def facilities_for_specialty_list(self, specialties: Sequence[str], **kwargs: Any):
        """Used by the chatbot to suggest where to go for a set of specialties."""
        pool: List[Dict[str, Any]] = []
        for fac in self.facilities:
            if any(s in fac["specialties"] for s in specialties):
                pool.append(fac)
        if kwargs.get("sector") in ("Government", "Private", "Diagnostic Lab"):
            pool = [f for f in pool if f["type"] == kwargs["sector"]]
        pool.sort(key=lambda f: 0 if f["type"] == "Government" else 1)
        return pool[:5]

    # ------------------------------------------------------------------ #
    # Core feature 3 - Chat assistant (rule based, transparent)
    # ------------------------------------------------------------------ #
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        text = _norm(message)
        if not text:
            return {
                "reply": self.chat_doc["greeting"],
                "intent": "greeting",
                "urgent": False,
                "suggestions": self.default_suggestions(),
            }

        # 1. Emergency always wins.
        for phrase in EMERGENCY_PHRASES:
            if phrase in text:
                intent = self._intent("emergency")
                return self._reply(intent, urgent=True)

        # 2. A named condition -> answer from the curated knowledge base.
        cond, detail_kind = self._detect_condition(text)
        if cond:
            return self._condition_reply(cond, detail_kind)

        # 3. A self-reported symptom pattern -> acknowledge it, triage-lite, then send the
        #    user to the full checker for the age/duration questions.
        hits = self._symptom_words_in(text)
        self_report = bool(
            re.search(r"\b(i have|i am|i ve|having|suffering|feeling|experiencing|since|my)\b", text)
        )
        if hits and (self_report or len(hits) >= 2):
            labels = ", ".join(self.symptom_label(h) for h in hits[:4])
            detail = ""
            if len(hits) >= 2:
                quick = self.assess(hits, {})
                ranking = " and ".join(f"**{m['name']}**" for m in quick["matches"][:2])
                detail = (
                    "\n\nUsing only what you just told me, the closest patterns in my knowledge "
                    f"base are {ranking}, and the guidance would be **{quick['care']['label']}**. "
                    "That is a similarity match, **not a diagnosis**."
                )
            return {
                "intent": "symptom_hint",
                "reply": (
                    f"You mentioned: **{labels}**.\n\n"
                    "⚠️ Symptoms on their own cannot identify a condition - several illnesses share "
                    "exactly the same ones."
                    + detail
                    + "\n\nOpen the **Symptom Checker** tab, tick everything that applies and add "
                    "your age and how long you have had it. You will get the full ranked breakdown, "
                    "the red flags to watch for and where to go in Hyderabad."
                ),
                "urgent": False,
                "actions": [{"type": "tab", "target": "checker", "label": "Open Symptom Checker"}],
                "suggestions": ["Is it an emergency?", "How do I prevent dengue?", "Where can I test for typhoid?"],
            }

        # 4. Other intents by keyword score.
        best, best_score = None, 0
        for intent in self.chat_doc["intents"]:
            if intent["id"] in ("emergency", "greeting"):
                continue
            score = 0
            for kw in intent["keywords"]:
                if kw in text:
                    score += 1 + (2 if " " in kw else 0)
            if score:
                score = score * 10 + intent.get("priority", 0) / 100
                if score > best_score:
                    best, best_score = intent, score
        if best:
            return self._reply(best, suggestions=self.suggestions_for(best["id"]))

        # 5. Bare symptom words without a self-report -> still guide to the checker.
        if hits:
            labels = ", ".join(self.symptom_label(h) for h in hits[:4])
            return {
                "intent": "symptom_hint",
                "reply": (
                    f"You mentioned: **{labels}**. Symptoms on their own cannot identify a "
                    "condition - several illnesses share the same ones.\n\n"
                    "Use the **Symptom Checker** tab and tick everything that applies (plus your "
                    "age and how long you have had them). It will show how your pattern lines up "
                    "with common conditions, how urgent it looks and what to do next.\n\n"
                    "⚠️ Call **108** immediately if there is chest pain, difficulty breathing, "
                    "confusion, a seizure or heavy bleeding."
                ),
                "urgent": False,
                "actions": [{"type": "tab", "target": "checker", "label": "Open Symptom Checker"}],
                "suggestions": ["Is it an emergency?", "How do I prevent dengue?", "Where can I test for typhoid?"],
            }

        # 5. Greeting as a soft fallback.
        if re.search(r"\b(hi|hey|hello|namaste)\b", text):
            intent = self._intent("greeting")
            return self._reply(intent)

        return {
            "intent": "fallback",
            "reply": self.chat_doc["fallback"],
            "urgent": False,
            "suggestions": self.default_suggestions(),
        }

    def _intent(self, intent_id: str) -> Dict[str, Any]:
        for intent in self.chat_doc["intents"]:
            if intent["id"] == intent_id:
                return intent
        return {"id": intent_id, "response": self.chat_doc["fallback"], "actions": []}

    def _reply(self, intent: Dict[str, Any], urgent: bool = False, suggestions=None) -> Dict[str, Any]:
        return {
            "intent": intent["id"],
            "reply": intent["response"],
            "urgent": urgent or intent["id"] == "emergency",
            "actions": intent.get("actions", []),
            "suggestions": suggestions or self.suggestions_for(intent["id"]),
        }

    def _detect_condition(self, text: str):
        """Return (condition_id, detail_kind) if the message names a condition."""
        detail = "overview"
        if re.search(r"\b(prevent|prevention|precaution|avoid|protect)\w*", text):
            detail = "precautions"
        elif re.search(r"\b(test|tests|testing|diagnos|blood work|scan)\w*", text):
            detail = "tests"
        elif re.search(r"\b(symptom|symptoms|signs|feel like)\w*", text):
            detail = "symptoms"
        elif re.search(r"\b(treat|treatment|cure|home care|home remedy|manage|remedies)\w*", text):
            detail = "self_care"

        # Only CONDITION names and their common spoken aliases belong here. Symptom words are
        # deliberately excluded: "I have fever with chills and headache" must go to the symptom
        # pathway, not be answered as a lecture about migraine.
        alias = {
            "dengue": "dengue", "break bone": "dengue",
            "malaria": "malaria",
            "chikungunya": "chikungunya",
            "typhoid": "typhoid", "enteric fever": "typhoid",
            "common cold": "common_cold", "cold": "common_cold",
            "flu": "influenza", "influenza": "influenza",
            "covid": "covid19", "corona": "covid19",
            "gastro": "gastroenteritis", "gastroenteritis": "gastroenteritis",
            "diarrhoea": "gastroenteritis", "diarrhea": "gastroenteritis",
            "food poisoning": "food_poisoning", "food poison": "food_poisoning",
            "uti": "uti", "urine infection": "uti", "urinary tract": "uti",
            "anaemia": "iron_deficiency_anaemia", "anemia": "iron_deficiency_anaemia",
            "iron deficiency": "iron_deficiency_anaemia", "low haemoglobin": "iron_deficiency_anaemia",
            "migraine": "migraine",
            "allergy": "allergic_rhinitis", "allergic rhinitis": "allergic_rhinitis", "hay fever": "allergic_rhinitis",
            "conjunctivitis": "conjunctivitis", "pink eye": "conjunctivitis", "madras eye": "conjunctivitis",
            "diabetes": "type2_diabetes", "blood sugar": "type2_diabetes",
        }
        for needle, cond_id in alias.items():
            if needle in text:
                return cond_id, detail
        return None, detail

    def _condition_reply(self, cond_id: str, detail: str) -> Dict[str, Any]:
        cond = self.by_id[cond_id]
        meta = CARE_META[cond["care_level"]]
        top_symptoms = [
            self.symptom_label(s)
            for s in sorted(cond["symptoms"], key=lambda k: -cond["symptoms"][k])[:7]
        ]
        parts: List[str] = [f"### {cond['name']}"]

        if detail == "precautions":
            parts.append("**How to protect yourself / others**")
            parts += [f"• {p}" for p in cond["precautions"][:5]]
        elif detail == "tests":
            parts.append("**Tests a clinician may advise**")
            parts += [f"• {t}" for t in cond["tests"]]
            parts.append(
                "\nTesting is decided by a doctor based on your timeline. Open **Find Care** to see "
                "hospitals and laboratories in Hyderabad that run these tests."
            )
        elif detail == "symptoms":
            parts.append("**Typical symptoms**")
            parts += [f"• {s}" for s in top_symptoms]
            parts.append("\nIf these sound like you, run them through the **Symptom Checker** tab.")
        elif detail == "self_care" and cond.get("self_care"):
            parts.append("**Home care steps**")
            parts += [f"• {s}" for s in cond["self_care"]]
        elif detail == "self_care":
            parts.append(
                "This condition should not be self-managed - it needs a clinician's assessment "
                "and usually prescription treatment."
            )
            parts.append(f"**Recommended urgency:** {meta['label']} - {meta['guidance']}")
        else:
            parts.append(cond["overview"])
            parts.append("**Commonly reported symptoms:** " + ", ".join(top_symptoms) + ".")
            hours = {"emergency": "immediately (call 108)", "urgent": "the same day", "routine": "within a day or two", "selfcare": "at home, with review if it worsens"}
            parts.append(f"**Usual urgency:** {meta['label']} - seek care {hours[cond['care_level']]}.")

        parts.append("**Watch out for these red flags:** " + "; ".join(cond["red_flags"][:3]) + ".")
        parts.append(f"**Where to go in Hyderabad:** " + ", ".join(cond["specialties"][:3]) + ".")
        parts.append(
            f"_Source: {cond['sources'][0]['label']}. This is general information, not a diagnosis._"
        )
        return {
            "intent": f"condition_{detail}",
            "reply": "\n\n".join(parts),
            "urgent": cond["care_level"] == "emergency",
            "actions": [
                {"type": "tab", "target": "checker", "label": "Check my symptoms"},
                {"type": "facilities", "target": cond["id"], "label": f"Find care for {cond['name']}"},
            ],
            "suggestions": [
                f"Can {cond['name']} be treated at home?",
                f"What tests are used for {cond['name']}?",
                "Is it an emergency?",
            ],
        }

    def _symptom_words_in(self, text: str) -> List[str]:
        hits: List[str] = []
        for phrase, ids in self.symptom_phrases.items():
            if phrase in text:
                for sym_id in ids:
                    if sym_id not in hits:
                        hits.append(sym_id)
        for word in text.split():
            for sym_id in self.symptom_words.get(word, []):
                if sym_id not in hits:
                    hits.append(sym_id)
        return hits[:6]

    def suggestions_for(self, intent_id: str) -> List[str]:
        mapping = {
            "emergency": ["Where is the nearest hospital?", "What are the emergency numbers?"],
            "greeting": ["What is dengue?", "How to prevent malaria?", "Where can I test for typhoid?", "I have fever and body pain"],
            "identity_limit": ["Is it an emergency?", "What is dengue?", "How do I make ORS?"],
            "find_facility": ["Where can I test for dengue?", "Government hospitals in Hyderabad", "Is it an emergency?"],
            "symptom_check": ["I have fever with chills", "I have burning while urinating", "Is it an emergency?"],
            "when_to_see_doctor": ["What is dengue?", "How do I make ORS?", "Where is the fever hospital?"],
            "ors": ["I have loose motions", "When should I see a doctor?"],
            "privacy": ["Is it an emergency?", "What can you do?"],
        }
        return mapping.get(intent_id, self.default_suggestions())

    def default_suggestions(self) -> List[str]:
        return [
            "What is dengue?",
            "How do I prevent malaria?",
            "Where can I get tested in Hyderabad?",
            "I have fever and body pain",
            "When should I see a doctor?",
        ]

    def emergency_info(self) -> Dict[str, Any]:
        return {
            "numbers": self.facilities_doc.get("emergency_numbers", []),
            "nearest_emergency": self.facilities_for_specialty_list(["Emergency"]),
        }
