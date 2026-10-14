# Susrutha Health Partner — Jury Explanation & Demo Script

Everything you need to (a) defend the prototype, (b) drive it live for 5 minutes without a hitch,
and (c) answer the questions judges actually ask.

---

## 1. The 30-second pitch

> "In India, when someone gets a fever, three things go wrong: they don't know how serious it is,
> they don't know which hospital to go to, and they either panic or ignore it. Susrutha Health
> Partner fixes all three in one screen. You tell it your symptoms in plain language — it tells you
> how urgent it looks, what the warning signs are, and the nearest government hospital or
> diagnostic lab in Hyderabad with directions. It uses only published WHO, CDC and NHS information,
> it works with no login, it stores nothing, and it will never pretend to diagnose you — because we
> removed the black box instead of hiding behind a disclaimer."

**One-line technical summary for the technical judge:**
"A Flask API and a transparent, weighted, rule-based triage engine over an auditable JSON
knowledge base — no ML, because a wrong diagnosis is a safety failure, not a UX failure."

---

## 2. Requirement-by-requirement: what they asked, where you show it

| Problem-statement requirement | How we meet it | Click this in the demo |
|---|---|---|
| User-friendly interface to access health info/services | Single-page app, light + dark theme, mobile responsive, 3-step wizard, live map, floating assistant | Open the site, toggle ☀️/🌙 |
| At least one core feature | We implemented **three**: facility discovery, health-information assistance, preliminary risk awareness | Tabs: Find Care, Health Library, Symptom Checker |
| Reliable health information sources or clearly labelled sample data | Every condition card prints its WHO/CDC/NHS source URLs; facility data is labelled "approximate pins, confirm before travelling" | Open any Health Library card → bottom source line |
| Guidance + recommend professional medical assistance | Every result ends with "what to do now", a red-flag list, and where to go; emergencies escalate to 108 immediately | Run the dengue scenario, then the chest-pain scenario |
| Functional prototype with at least one test scenario | 3 documented scenarios + a 58-test automated suite | `python -m unittest discover -s tests -v` |
| User data privacy | No login, no database, no third-party calls; a test asserts no DB driver exists in the code | The consent modal + footer privacy line |
| Don't present AI output as a definitive diagnosis | The engine returns *pattern alignment* + *urgency*, never a disease verdict; it states "not a diagnosis" and names the tests a doctor would order | Read the "How your pattern lines up" card aloud |

---

## 3. Live demo script (5 minutes)

**Setup (before the judges walk in):** `pip install -r requirements.txt` → `python app.py` →
open `http://127.0.0.1:5000`. Leave the browser open on the Home page in **light** theme.

### Step 0 — Home (20 s)
Point at the three trust chips: *not a diagnosis*, *no login, no data stored*, *sourced from WHO ·
CDC · NHS*. Point at the stat strip (15 conditions · 69 symptoms · 21 facilities · 4 sources).
*"Everything you're about to see runs on this machine; there is no external AI service."*

### Step 1 — Scenario A: "Fever with pain behind the eyes" (dengue) — 90 s
1. **Symptom Checker** → tick **Mild fever**, **High fever**, **Pain behind the eyes**,
   **Joint pain**, **Skin rash** (use the search box: type "behind eyes" to show the search works).
2. **Continue** → Age `28`, days `2–3 days`, severity `Moderate`, tick **Diabetes**.
3. **Get my guidance**.
4. Read out loud, in this order:
   - the amber banner: **"Urgent — see a doctor today"** with the "risk factors considered" chip
     (because age + diabetes raised the urgency);
   - the ranked matches: **Dengue Fever** first, and the honest line that *Malaria* also matches
     some symptoms — *"that's why it says a test may be needed, not a verdict"*;
   - the **red flags** card: *bleeding gums, blood in vomit, cold clammy skin*;
   - the **precautions** card: the exact WHO guidance *"avoid aspirin and ibuprofen until dengue is
     ruled out"* — this is the kind of detail a generic chatbot gets wrong;
   - the **tests** card: CBC with platelet count, NS1 antigen, Dengue IgM/IgG.
5. Click **"Find care for this"** → Find Care opens with Dengue selected. Change *Your area* to
   **Gachibowli** → distances appear; change *Sort by* to **Best specialty match** → the
   **Fever Hospital, Nallakunta**, **NIMS**, **Osmania General** and **Gandhi Hospital** jump to
   the top with a **Best match** badge. Click **Directions**.

### Step 2 — Scenario B: "Small illness gets small advice" — 45 s
1. **Symptom Checker** → Clear → tick **Runny nose**, **Sneezing**, **Sore throat**.
2. Age `24`, `1 day`, `Mild` → **Get my guidance**.
3. Show: **"Self-care at home"** in green, home-care steps, and *"usually no tests needed"*.
   *"The system is not a scaremonger — it only escalates when the pattern or the person's risk
   factors justify it. That's the difference between triage and a panic machine."*

### Step 3 — Scenario C: the emergency path — 30 s
1. Go back, **Clear**, tick **Chest pain** + **Difficulty breathing** → Continue → Get guidance.
2. A **red emergency banner** appears with **108 / 112** as tappable links and the reason:
   *"This pattern needs emergency care now."*
3. *"Red-flag symptoms bypass the scoring entirely. Safety first, severity second."*

### Step 4 — The chatbot — 45 s
Open **Ask Susrutha** (bottom-right) and send, in order:
- `I have fever with chills and headache` → it acknowledges the exact symptoms, gives a quick read
  and hands off to the checker with an **Open Symptom Checker** button.
- `how do I prevent malaria` → concrete prevention steps (nets, repellent, drain stagnant water).
- `how do I make ORS?` → the WHO recipe: 1 litre water + 6 teaspoons sugar + ½ teaspoon salt.
- `are you a doctor?` → *"No — I am not a doctor and I cannot diagnose or prescribe"* + what it
  can do instead.
- `I have severe chest pain` → the bubble turns **red** with the 108 instruction.
*"Every answer is traceable to the same knowledge base — this is a transparent assistant, not a
language model improvising."*

### Step 5 — Health Library + privacy — 30 s
Search `rash` → Typhoid, Dengue, Chikungunya appear. Open **Dengue Fever** → scroll to the source
line: *WHO — Dengue and severe dengue*. Then point at the footer privacy line and the consent
modal from the start: *"nothing is stored, and there is a unit test that proves there is no
database in the codebase."*

### Step 6 (only if a judge is technical) — the tests
```bash
python -m unittest discover -s tests -v
```
58 tests: data integrity, the engine, facility ranking, the chatbot, the HTTP API and privacy.
Point out two of them: *"a red-flag symptom always escalates"* and *"the app declares no database
layer"*.

---

## 4. How it works — say it in plain words

**The flow of one tap:**
`Browser → POST /api/assess → Python engine → weighted comparison + triage gate → JSON → rendered`

**The knowledge base (`data/*.json`).** Four files. The important one, `conditions.json`, lists 15
conditions, and for each one it stores: the symptoms with a weight (3 = classic feature, 1 =
sometimes present), the care level, the precautions, the red flags, the home-care steps, the tests
a clinician would order, the specialties to see, and the source URLs. *This is a file a doctor can
review and correct — that was the whole point.*

**The scoring (the only maths in the project).**
For each condition: `coverage` = how much of the condition's symptom picture is present;
`fit` = how much of what you reported the condition explains.
`score = 0.65 × coverage + 0.35 × fit`. Rank, show the top four, and print the **missing key
symptoms** too — *"usually also seen with: bleeding gums…"* — so the user sees what is *not*
matching, not just what is.

**The triage gate (deliberately separate).** Matching tells you *what* it might be; triage tells you
*how fast to act*. Any emergency-flagged symptom → emergency, full stop. Otherwise we start from
the top condition's care level and **raise it one step** for each risk factor: child under 5,
age 60+, pregnancy, chronic illness, "severe", or more than a week of symptoms. A single symptom
can never return "self-care".

**Facility ranking (`/api/facilities`).** Each facility is tagged with the departments it offers.
To stop "Dengue" from matching all 21 facilities, we weight each department by **rarity**
(inverse frequency): "Fever / Tropical Diseases" is offered by very few hospitals, so it counts
much more than "General Medicine", which everyone offers. Then: *nearest first* if the user gave a
location, or *best specialty match first* if they didn't — with a **Best match / Good match /
General care** tier on every card. Distances are straight-line (Haversine) from the chosen area or
the browser's geolocation.

**The chatbot.** A transparent rule engine: curated red-flag phrases are checked first (they win
everything), then condition names and their spoken aliases, then intent keywords (prevention,
tests, first aid, privacy, "when to see a doctor"), then symptom words, which are handed to the
symptom pathway. A generic-word stop-list ("blood", "pain", "severe") prevents mistakes such as
reading "where can I get a **blood** test" as "**blood** in vomit" — we found and fixed exactly
that bug during testing, and it is now a regression test.

---

## 5. The three questions judges always ask

**Q1. "So is this AI? Are you diagnosing?"**
> "There is no ML model, on purpose. Diagnosis is a clinical act; a wrong answer is a safety
> failure, not a UX failure. What we built is decision support: a transparent, auditable weighted
> match over published symptom descriptions, plus a triage gate. The output is deliberately worded
> as *pattern alignment* and *urgency* — never 'you have dengue'. The app gives the doctor-facing
> next step: which tests, which specialty, how fast."

**Q2. "What if your data is wrong?"**
> "Two answers. Clinically: every entry carries its WHO/CDC/NHS source URL, so anyone can verify or
> correct it, and a physician can edit one JSON file without touching code. Engineering-wise: we
> fail safe — red-flag symptoms always escalate to emergency, risk factors always *raise* urgency,
> a single symptom can never return self-care, and when two conditions score within 20% of each
> other the app says so instead of picking a winner."

**Q3. "How does this actually improve access?"**
> "It collapses the three questions people can't answer at 2 a.m. — *is this serious, what do I do,
> and where do I go* — into one screen with directions. It costs nothing, needs no account, and
> works for the government-hospital user: we rank government and diagnostic-lab options first
> among equally relevant ones and we surface the **Fever Hospital at Nallakunta** as the best match
> for a fever, which most people don't know exists."

**Others to expect, with short answers:**

- *"Where's the LLM?"* → See Q1. The chatbot is rule-based so answers are reproducible and
  citable; a small model could later be added *behind* the safety gate, never in front of it.
- *"Scalability?"* → The engine is stateless and O(conditions × symptoms); the knowledge base is
  JSON a clinician can extend to hundreds of conditions, and `conditions.json` already carries the
  source URLs needed for review. Facility data would come from HMIS/ABDM-style feeds with
  geocoding, which the API shape already anticipates.
- *"Privacy proof?"* → No login, no cookies, no persistence; the assessment lives in one request;
  a test asserts the codebase contains no database driver; the browser tab is the only place the
  inputs exist.
- *"What about language / phone?"* → Not today. It is a responsive mobile-first web app, and the
  knowledge base is JSON, so a Telugu/Hindi string layer is a translation task, not a rewrite.
- *"Why Hyderabad?"* → Where we can validate it: we built real facility data, the actual emergency
  numbers (108/112/104/1075), and the local disease reality — dengue, malaria, typhoid and
  chikungunya are the region's dominant fever differential, which is exactly the pattern this
  tool is best at.

---

## 6. If something breaks during the demo

- **Page won't load:** the server died. Re-run `python app.py` and refresh. Nothing else is
  required — there is no database to migrate and no build step.
- **No map tiles:** no internet. Say so and use the facility cards beside the map — the map is
  progressive enhancement, the list is the product. The fallback message appears automatically.
- **Geolocation hangs:** we added a 12-second guard that resets the button and tells you to pick
  your area from the list. Just pick **Gachibowli** (the IT corridor) as the demo area.
- **A judge asks for a condition we don't have:** say it plainly — 15 conditions today, and adding
  a sixteenth means adding one JSON entry with its source URL, which is the scaling story.

---

## 7. File-to-feature map (if a judge asks "show me the code")

| Judge asks about | Open this |
|---|---|
| The scoring and triage logic | `health_engine.py` → `KnowledgeBase.assess` |
| The weight tables and care levels | `data/conditions.json` |
| Emergency flags | `data/symptoms.json` (`"emergency": true`) |
| Facility ranking / rarity weighting | `health_engine.py` → `_specialty_weights`, `find_facilities` |
| Chat intents and curated answers | `data/chatbot.json` + `KnowledgeBase.chat` |
| The HTTP surface | `app.py` |
| The interface | `templates/index.html`, `static/css/style.css`, `static/js/app.js` |
| The proof it works | `tests/test_app.py` (58 tests) |
