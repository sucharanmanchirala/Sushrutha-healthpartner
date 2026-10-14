# Susrutha Health Partner

**AI-assisted health accessibility and early assistance for Hyderabad — a working prototype.**

> Susrutha (सुश्रुत) means "well-heard". The tool is named after Sushruta, the ancient Indian
> physician regarded as the father of surgery — because listening well is the first act of care.

Susrutha helps someone who feels unwell answer one question fast: **"what should I do next?"**
It turns plain-language symptoms into (a) an honest pattern comparison against published health
information, (b) an urgency level with the red flags to watch for, and (c) a concrete hospital or
testing facility nearby, with directions.

---

## 1. Quick start

```bash
# 1. install the single dependency
pip install -r requirements.txt

# 2. run
python app.py

# 3. open
http://127.0.0.1:5000
```

Verified on **Python 3.11** and **Python 3.14** (the project `.venv`), Windows.
Run the test suite any time with:

```bash
python -m unittest discover -s tests -v
```

---

## 2. What it does (feature map)

| # | Feature | Where | What it does |
|---|---------|-------|--------------|
| 1 | **Symptom Checker & Risk Awareness** | *Symptom Checker* tab | Select symptoms → weighted comparison against 15 conditions → ranked pattern alignment, urgency level (self-care / routine / same-day / emergency), red flags, precautions, home care and recommended tests |
| 2 | **Facility Discovery (Hyderabad)** | *Find Care* tab | Condition or specialty + your area → map of 21 government hospitals, private hospitals and diagnostic labs, sorted by distance or by specialty relevance, with Google Maps directions |
| 3 | **Health Information Assistance** | *Health Library* tab | 15 sourced guides: symptoms, precautions, red flags, home care for minor illnesses, tests, specialties and source URLs |
| 4 | **Susrutha Assistant (chatbot)** | chat bubble, bottom-right | Rule-based assistant for basic queries: condition explanations, prevention, first aid (ORS recipe), tests, "where do I go", "when should I see a doctor", privacy — and an instant emergency pathway to 108 |
| 5 | **Emergency pathway** | red button in the header, everywhere | 108 / 112 / 104 / 1075 plus the nearest emergency departments |
| 6 | **Privacy by design** | everywhere | No login, no database, no third-party calls; inputs are used in memory for one result and never stored |

---

## 3. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.11+** | Required by the problem statement; one language for the engine, the API and the tests |
| Web framework | **Flask 3** | Minimal, readable, no magic — the whole server is one file the jury can read |
| Front end | **Vanilla HTML5 + CSS3 + ES2020 JavaScript** (no build step, no framework) | Zero tooling to break during a demo; full control over UI/UX; loads instantly |
| Maps | **Leaflet 1.9 + OpenStreetMap tiles** | Free, no API key, no billing, works offline-degraded (cards still render if there is no internet) |
| Data layer | **JSON knowledge base under `data/`** | Auditable, reviewable by a clinician, diff-able in git — not a black box |
| AI/ML | **None — deliberately** | Scoring is transparent, deterministic, rule-based (see §5). The brief forbids presenting AI output as a diagnosis, so we removed the black box rather than guarding it with a disclaimer |
| Tests | **`unittest` (Python standard library)** | 58 tests, zero extra dependencies |
| Fonts / icons | Google Fonts (Plus Jakarta Sans, with a system-font fallback) + inline SVG | Best-in-class typography with a graceful offline fallback |

---

## 4. Project structure

```
sankalp hackthon/
├── app.py                  # Flask app: pages + 10 REST endpoints
├── health_engine.py        # The brain: knowledge base loader, scoring, triage, chat, geo search
├── data/
│   ├── symptoms.json       # 69 plain-language symptoms in 9 body-system groups (+ emergency flags)
│   ├── conditions.json     # 15 conditions: weighted symptoms, care level, precautions, red flags,
│   │                       #   home care, tests, specialties, source URLs
│   ├── facilities.json     # 21 Hyderabad facilities with coordinates, services and honest notes
│   ├── localities.json     # 22 Hyderabad reference points for distance sorting
│   └── chatbot.json        # Chat intents, keywords and vetted answers
├── templates/index.html    # The single-page interface
├── static/css/style.css    # Design system: light + dark theme, responsive, reduced-motion aware
├── static/js/app.js        # Front-end logic: wizard, map, chat, library, API calls
├── tests/test_app.py       # 58 tests: data integrity, engine, facilities, chat, API, privacy
├── requirements.txt
└── README.md / JUDGE_GUIDE.md
```

---

## 5. How the symptom check actually works (no machine learning)

1. **Vocabulary.** 69 symptoms are grouped by body system. Some are flagged `emergency: true`
   (for example *difficulty breathing*, *chest pain*, *confusion*, *blood in vomit*).
2. **Weighted match.** Every condition lists its symptoms with a weight from 1 to 3. Weight 3 =
   the classic feature of that illness, weight 1 = a feature that sometimes occurs.
   For each condition we compute:
   - `coverage` = (sum of weights of the symptoms you selected) ÷ (total weight of the condition)
   - `fit` = (number of your symptoms that the condition lists) ÷ (number of symptoms you selected)
   - `score` = 0.65 × coverage + 0.35 × fit
3. **Ranking + honesty.** The best candidate becomes 100% and the others are shown relative to it.
   Each match is labelled *Strong / Moderate / Fair / Weak*, and when the top two are within 20% of
   each other, the app explicitly says that more than one condition fits and a test may be needed.
4. **Triage gate (separate from matching).** Urgency is decided independently of which disease
   matched:
   - any emergency-flagged symptom → **Emergency**;
   - otherwise start from the top condition's care level and raise it one step for each risk factor:
     age under 5, age 60+, pregnancy, diabetes / heart / kidney / liver disease / low immunity,
     symptoms described as severe, or symptoms lasting more than a week;
   - a single selected symptom can never produce "self-care".
5. **Early assistance, not a verdict.** The result always contains what to do now, the red flags,
   precautions, home care (for minor illnesses only), likely tests, which specialty to see, the
   source it came from, and the disclaimer.

---

## 6. Data sources

Health content is a plain-language summary of public guidance from:

- **WHO** — Dengue, Malaria, Chikungunya, Typhoid, Diarrhoeal disease, COVID-19
- **CDC** — Malaria, Typhoid, Flu, COVID-19, Diabetes
- **NHS** — Common cold, Flu, Food poisoning, UTI, Anaemia, Migraine, Allergic rhinitis, Conjunctivitis, Type 2 diabetes
- **MedlinePlus** — general symptom reference
- **India: NCVBDC (MoHFW)** — vector-borne disease programme (dengue/malaria context for Telangana)

Every condition in the library prints its own source URLs. **Emergency numbers** used: 108
(ambulance, Telangana), 112 (national), 104 (health helpline), 1075 (health advice).

Facility names, areas and addresses are real Hyderabad institutions. **Map pins are approximate**
(not surveyed entrances) and the UI says so; the app tells the user to call ahead and confirm
timings and test availability.

---

## 7. Privacy and safety

- No accounts, no cookies, no analytics, no outbound API calls. The server holds only JSON files.
- Health inputs live in the browser tab and in one in-memory request; nothing is written to disk
  (there is a test that asserts no database driver exists in the codebase).
- The tool never says "you have X". It reports *pattern alignment* and *urgency*, always with the
  disclaimer, and it escalates to emergency care or a doctor rather than to self-treatment.
- Antibiotic and prescription guidance is always "ask a clinician", never a drug name and dose.

---

## 8. API reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness + counts |
| GET | `/api/meta` | App metadata, sources, emergency numbers, disclaimer |
| GET | `/api/symptoms` | Symptom vocabulary grouped by body system |
| GET | `/api/library?q=` | Condition cards (optionally searched) |
| GET | `/api/conditions/<id>` | One full condition guide |
| GET | `/api/specialties` | Specialty list for the filters |
| POST | `/api/assess` | `{symptoms: [...], profile: {...}}` → matches + triage + guidance |
| GET | `/api/facilities?condition=&specialty=&lat=&lng=&sector=&order=` | Facility discovery |
| POST | `/api/chat` | `{message}` → assistant reply, actions, suggestions |
| GET | `/api/emergency` | Emergency numbers + nearest emergency hospitals |

---

## 9. Limitations (say these before the jury asks)

- 15 conditions and 21 facilities are a curated demo slice, not a clinical database.
- Weights, thresholds and the care levels were authored by us from published material; they have
  **not** been clinically validated. A production version would need physician review, a
  larger coded vocabulary (ICD-10/SNOMED CT) and real-time bed/bed-availability data.
- Map pins are approximate; distances are straight-line (Haversine), not road distance.
- The chatbot is rule-based, so it is honest about what it does not know rather than inventing an
  answer — that is a design decision, not a missing feature.
- Not a medical device: it cannot diagnose, prescribe, or replace a clinician.
