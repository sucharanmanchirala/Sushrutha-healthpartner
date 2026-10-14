"""
Susrutha Health Partner - Flask application
===========================================

A single-file Flask service that exposes the rule-based health engine over a
small REST API and serves the front-end.

Run it with:
    python app.py
then open http://127.0.0.1:5000

Design notes for the jury
-------------------------
* No user accounts, no database, no analytics: the assessment is computed in
  memory and the result is returned to the browser. Nothing is persisted.
* Every medical answer is traceable to the JSON knowledge base, which names its
  source (WHO / CDC / NHS / MedlinePlus) per condition.
* The engine never returns the word "diagnosis" as a conclusion - it returns a
  symptom-pattern alignment and an urgency category.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from health_engine import DISCLAIMER, KnowledgeBase

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
kb = KnowledgeBase()


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "conditions": len(kb.conditions), "facilities": len(kb.facilities)})


@app.get("/api/meta")
def meta():
    return jsonify(
        {
            "app_name": "Susrutha Health Partner",
            "tagline": "Understand your symptoms. Find the right care. In minutes.",
            "disclaimer": DISCLAIMER,
            "emergency_numbers": kb.facilities_doc.get("emergency_numbers", []),
            "stats": {
                "conditions": len(kb.conditions),
                "symptoms": len(kb.symptoms),
                "facilities": len(kb.facilities),
                "sources": sorted(
                    {
                        s["label"].split(" - ")[0]
                        for c in kb.conditions
                        for s in c["sources"]
                    }
                ),
            },
            "data_note": kb.conditions_doc.get("note", ""),
        }
    )


# --------------------------------------------------------------------------- #
# Catalogue
# --------------------------------------------------------------------------- #
@app.get("/api/symptoms")
def symptoms():
    return jsonify({"groups": kb.symptom_groups()})


@app.get("/api/library")
def library():
    query = request.args.get("q", "").strip()
    items = kb.search(query) if query else kb.library()
    return jsonify({"query": query, "count": len(items), "items": items})


@app.get("/api/conditions/<cond_id>")
def condition(cond_id: str):
    detail = kb.condition_detail(cond_id)
    if not detail:
        return jsonify({"error": "unknown condition", "id": cond_id}), 404
    return jsonify(detail)


# --------------------------------------------------------------------------- #
# Core feature: symptom assessment + risk awareness
# --------------------------------------------------------------------------- #
@app.post("/api/assess")
def assess():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    selected: List[str] = payload.get("symptoms") or []
    profile: Dict[str, Any] = payload.get("profile") or {}
    if not isinstance(selected, list):
        return jsonify({"error": "symptoms must be a list of symptom ids"}), 400
    return jsonify(kb.assess(selected, profile))


# --------------------------------------------------------------------------- #
# Core feature: facility discovery around Hyderabad
# --------------------------------------------------------------------------- #
@app.get("/api/facilities")
def facilities():
    def _float(name: str):
        raw = request.args.get(name)
        try:
            return float(raw) if raw not in (None, "") else None
        except ValueError:
            return None

    data = kb.find_facilities(
        condition_id=request.args.get("condition") or None,
        specialty=request.args.get("specialty") or None,
        lat=_float("lat"),
        lng=_float("lng"),
        sector=request.args.get("sector", "all"),
        limit=int(request.args.get("limit", 12)),
        order=request.args.get("order", "auto"),
    )
    return jsonify(data)


@app.get("/api/specialties")
def specialties():
    found = sorted({s for c in kb.conditions for s in c["specialties"]})
    return jsonify({"specialties": found})


# --------------------------------------------------------------------------- #
# Core feature: chat assistant
# --------------------------------------------------------------------------- #
@app.post("/api/chat")
def chat():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    message = str(payload.get("message", ""))
    return jsonify(kb.chat(message, payload.get("context") or {}))


@app.get("/api/emergency")
def emergency():
    data = kb.emergency_info()
    return jsonify(
        {
            "numbers": data["numbers"],
            "hospitals": [
                {
                    "name": f["name"],
                    "area": f["area"],
                    "type": f["type"],
                    "lat": f["lat"],
                    "lng": f["lng"],
                }
                for f in data["nearest_emergency"]
            ],
        }
    )


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "not found", "path": request.path}), 404
    return render_template("index.html"), 200


def _port() -> int:
    """Use $PORT when it is a real number, otherwise the default 5000.

    Some shells export PORT=0 as a placeholder; passing 0 to Flask would silently pick a
    random port and make the app hard to find, so we normalise it here.
    """
    try:
        port = int(os.environ.get("PORT", ""))
    except (TypeError, ValueError):
        return 5000
    return port if port > 0 else 5000


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=_port(), debug=False)
