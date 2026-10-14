"""
Susrutha Health Partner - localization module
==============================================

All user-facing interface strings for the three supported languages live here so that
translated text is never scattered through templates or JavaScript.

Scope (deliberately conservative):
    * This module translates the APPLICATION INTERFACE: navigation, buttons, labels,
      headings, instructions, notifications, and the Daily Health Activity content.
    * It does NOT translate the medical knowledge base (conditions, precautions, red
      flags, chatbot answers, facility records). Those stay in their original English so
      that no medical meaning is ever altered by translation. The UI states clearly when
      content is only available in English.

Machine-readable values (symptom ids, condition ids, API field names, form values,
care-level codes) are never translated - only human-readable labels are.

Usage:
    from i18n import t, SUPPORTED, DEFAULT_LANG
    t("nav.home", "te")          # -> "హోమ్"
    t("nav.home")                # -> "Home"  (English is the default)

    t("js.selected", "hi").format(n=3)   # -> "3 चुने गए"
"""

from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "en"
SUPPORTED = ("en", "te", "hi")
LANG_NAMES = {"en": "English", "te": "తెలుగు", "hi": "हिन्दी"}

# ---------------------------------------------------------------------------
# English - source of truth for every key. Kept in sync with templates/index.html
# so that switching back to English reproduces the original interface exactly.
# ---------------------------------------------------------------------------
EN: Dict[str, str] = {
    # --- navigation / chrome ---
    "nav.home": "Home",
    "nav.checker": "Symptom&nbsp;Checker",
    "nav.care": "Find&nbsp;Care",
    "nav.library": "Health&nbsp;Library",
    "nav.activity": "Daily&nbsp;Activity",
    "emg.btn": "Emergency 108",
    "emg.short": "Emergency: 108",
    # --- hero ---
    "hero.eyebrow": "Healthcare accessibility · Hyderabad",
    "hero.title": 'Understand your symptoms.<br><span class="grad">Find the right care.</span> In minutes.',
    "hero.lead": (
        "Susrutha Health Partner is a free, privacy-first health assistant. Describe how you feel, "
        "see how your symptoms line up with common conditions using published WHO, CDC and NHS "
        "information, learn how urgent your situation is — then find a hospital or testing "
        "facility near you in Hyderabad."
    ),
    "hero.cta1": "Check my symptoms →",
    "hero.cta2": "📍 Find care near me",
    "trust.1": "✅ Not a diagnosis — decision support",
    "trust.2": "🔒 No login, no data stored",
    "trust.3": "📚 Sourced from WHO · CDC · NHS",
    "mini.ask": "Ask about symptoms or services…",
    # --- stats ---
    "stat.conditions": "conditions in the knowledge base",
    "stat.symptoms": "symptoms you can select",
    "stat.facilities": "Hyderabad facilities mapped",
    "stat.sources": "public health sources",
    # --- home sections ---
    "home.features": "Four ways Susrutha helps you",
    "home.sub": 'Every feature answers one question: <em>“what should I do next?”</em>',
    "feat1.t": "1 · Symptom Checker",
    "feat1.b": (
        "Tick your symptoms, add age and duration. We score your pattern against published "
        "symptom descriptions and show which conditions fit best — with the red flags to watch "
        "for and the exact urgency level."
    ),
    "feat1.link": "Try it →",
    "feat2.t": "2 · Find Care in Hyderabad",
    "feat2.b": (
        "Pick a condition or specialty and see government hospitals, private hospitals and "
        "diagnostic labs on a live map — with distance from your area, what each one offers and "
        "one-tap directions."
    ),
    "feat2.link": "Open the map →",
    "feat3.t": "3 · Health Library",
    "feat3.b": (
        "Plain-language guides for 15 common conditions: symptoms, precautions, warning signs, "
        "home care for minor illnesses and the tests a doctor would usually advise."
    ),
    "feat3.link": "Browse library →",
    "feat4.t": "4 · Susrutha Assistant",
    "feat4.b": (
        "A transparent, rule-based assistant that answers everyday health questions, explains "
        "first aid like the ORS recipe, and routes emergencies straight to 108."
    ),
    "feat4.link": "Chat now →",
    "home.steps": "How a check works",
    "step1.t": "Tell us the symptoms",
    "step1.b": "Search or tick from 70 plain-language symptoms grouped by body system.",
    "step2t.t": "Add your context",
    "step2t.b": (
        "Age, how many days, and risk factors like pregnancy or diabetes — optional and never "
        "stored."
    ),
    "step3t.t": "See the pattern",
    "step3t.b": (
        "A weighted match against each condition's published symptom list, ranked and honestly "
        "labelled."
    ),
    "step4.t": "Act on the urgency",
    "step4.b": (
        "Self-care, routine visit, same-day doctor or emergency — plus where to go in Hyderabad."
    ),
    "home.is": "🛡️ What Susrutha is — and is not",
    "is.1": "<strong>Is:</strong> a health-literacy and navigation tool. It summarises public health guidance and helps you reach care faster.",
    "is.2": "<strong>Is not:</strong> a doctor, a diagnosis, or a prescription. Symptoms overlap across many illnesses, and only a clinician can examine, test and confirm.",
    "is.3": "<strong>Is:</strong> transparent. Every condition card names its source (WHO, CDC, NHS, MedlinePlus) so you can verify it.",
    "is.4": "<strong>Is not:</strong> a data collector. No account, no database, no tracking of your health inputs.",
    # --- symptom checker ---
    "chk.eyebrow": "Core feature · early assistance",
    "chk.title": "Symptom Checker &amp; Risk Awareness",
    "chk.intro": (
        "Choose what you feel. Susrutha compares your pattern with published symptom "
        "descriptions and tells you how urgent it looks and what to do next."
    ),
    "dot.symptoms": "Symptoms",
    "dot.about": "About you",
    "dot.result": "Result",
    "chk.q": "What are you feeling?",
    "sym.search": "Search symptoms — e.g. fever, joint pain, burning urine…",
    "btn.clear": "Clear",
    "chk.tip": "Tip: select everything you notice — more detail means a better match.",
    "btn.continue": "Continue →",
    "s2.title": "Tell us a little about you",
    "s2.privacy": "🔒 stays in your browser",
    "s2.intro": (
        "All of this is optional, but it changes how urgent your situation is. Nothing is saved "
        "or sent anywhere except the fields you see here — they are used only to compute your "
        "result."
    ),
    "f.age": "Age (years)",
    "ph.age": "e.g. 28",
    "f.days": "How many days have you had this?",
    "days.none": "Not sure",
    "days.d0": "Started today",
    "days.d1": "1 day",
    "days.d2": "2–3 days",
    "days.d5": "4–7 days",
    "days.d10": "More than a week",
    "days.d20": "More than 2 weeks",
    "f.sev": "How severe does it feel?",
    "sev.mild": "Mild — I can do my normal day",
    "sev.mod": "Moderate — it is disturbing me",
    "sev.sev": "Severe — I cannot manage it",
    "f.pregnant": "Pregnant (or possibly pregnant)",
    "f.chronic": "Any long-term conditions?",
    "f.chronichint": "(select all that apply)",
    "btn.back": "← Back",
    "btn.guidance": "Get my guidance →",
    "btn.restart": "↺ Start over",
    "btn.edit": "Edit answers",
    # --- find care ---
    "fc.eyebrow": "Core feature · facility discovery",
    "fc.title": "Find Care in Hyderabad",
    "fc.intro": (
        "Government and private hospitals plus diagnostic laboratories — filtered by the "
        "condition or specialty you need, sorted by distance from your area."
    ),
    "fc.cond": "What do you need care for?",
    "fc.any": "Any condition",
    "fc.spec": "or a specialty",
    "fc.allspec": "All specialties",
    "fc.area": "Your area",
    "fc.type": "Type",
    "sector.all": "All facilities",
    "sector.gov": "Government",
    "sector.pri": "Private",
    "sector.lab": "Diagnostic labs",
    "fc.sort": "Sort by",
    "order.auto": "Best for me (auto)",
    "order.dist": "Nearest first",
    "order.rel": "Best specialty match",
    "fc.useloc": "📍 Use my exact location",
    "fc.facilities": "Facilities",
    "fc.noteTitle": "ℹ️ Before you travel",
    "fc.note": (
        "Facility names and areas are real; map pins are approximate. Always call the hospital "
        "to confirm the entrance, OPD timings, and that the test you need is available the same "
        "day. In an emergency, go to the nearest emergency department rather than travelling "
        "across the city."
    ),
    # --- library ---
    "lib.eyebrow": "Core feature · health information assistance",
    "lib.title": "Health Library",
    "lib.intro": (
        "Plain-language guides built from WHO, CDC, NHS and MedlinePlus material. Each card "
        "shows how urgent the condition usually is and the red flags that mean “see a doctor now”."
    ),
    "lib.search": "Search a condition, a symptom or a topic — e.g. dengue, rash, blood sugar…",
    # --- daily activity ---
    "act.eyebrow": "Wellbeing · small, everyday habits",
    "act.title": "Daily Health Activity",
    "act.intro": (
        "One gentle activity is featured each day. It is optional, always safe to skip, and "
        "only ever a small suggestion for general wellbeing — not medical advice."
    ),
    "act.complete": "Mark as completed",
    "act.skip": "Not today / skip",
    "act.weekTitle": "This week",
    # --- footer ---
    "foot.disclaimer": "Medical disclaimer",
    "foot.discText": (
        "This tool provides general health information from public sources (WHO, CDC, NHS, "
        "MedlinePlus) to help you decide what to do next. It is NOT a diagnosis and it cannot "
        "rule out serious illness. Always consult a qualified doctor about your own health."
    ),
    "foot.privacy": "Privacy",
    "foot.privacyText": (
        "No login, no database, no tracking of health inputs. Assessments are computed in "
        "memory and shown only to you."
    ),
    "foot.base": "Prototype · demo data labelled as such · 2026",
    "foot.emg": "Emergency: 108 · Ambulance 108 · National 112 · Health helpline 104",
    # --- chat chrome ---
    "chat.fab": "Ask Susrutha",
    "chat.name": "Susrutha Assistant",
    "chat.sub": "Health information · not a doctor",
    "chat.placeholder": "Ask about symptoms, prevention, tests or facilities…",
    "chat.send": "Send",
    # --- first-run notice ---
    "notice.title": "Welcome to Susrutha Health Partner",
    "notice.sub": "Healthcare accessibility &amp; early assistance · Hyderabad",
    "notice.intro": (
        "This tool helps you <strong>understand symptoms, learn what they could mean and find "
        "the right facility</strong> in Hyderabad. Before you start, please note:"
    ),
    "notice.1": "✅ It gives general information from <strong>WHO, CDC, NHS and MedlinePlus</strong> sources.",
    "notice.2": "❌ It is <strong>not a diagnosis</strong> and cannot rule out serious illness.",
    "notice.3": "🔒 It stores nothing — no login, no database, nothing shared.",
    "notice.4": "🚑 For emergencies call <strong>108 / 112</strong> or reach the nearest emergency department.",
    "notice.tail": (
        "By continuing you understand that a qualified doctor must confirm any condition and "
        "prescribe treatment."
    ),
    "notice.ok": "I understand — continue",
    "notice.emg": "🚑 Emergency numbers",
    "emg.modalTitle": "🚨 Emergency help",
    "emg.modalIntro": (
        "If someone is unconscious, not breathing, has chest pain, heavy bleeding, a seizure or "
        "sudden weakness, call for help immediately."
    ),
    "emg.modalTail": (
        "Then open <strong>Find Care</strong> to see the nearest emergency departments in "
        "Hyderabad, or use Google Maps for turn-by-turn directions."
    ),
    "emg.understand": "I understand",
    # --- dynamic strings used from JavaScript ---
    "js.analysing": "Analysing…",
    "js.guidance": "Get my guidance →",
    "js.selected": "{n} selected",
    "js.shown": "{n} shown",
    "js.careFor": "Care for {name}",
    "js.allFacilities": "All facilities",
    "js.conditions": "{n} conditions",
    "js.trayEmpty": "Nothing selected yet — tick the symptoms that apply to you.",
    "js.metaNear": "{n} facilities match · nearest first",
    "js.metaRel": "{n} facilities match · best specialty match first",
    "js.metaNearAdd": "{n} facilities match · nearest first · add your area for distances",
    "js.metaRelAdd": "{n} facilities match · best specialty match first · add your area for distances",
    "js.metaAllNear": "Showing all {n} mapped facilities · nearest first",
    "js.metaAll": "Showing all {n} mapped facilities · pick a condition or your area to narrow this down",
    "js.locUse": "📍 Use my exact location",
    "js.locWorking": "📍 Locating…",
    "js.locDone": "📍 Using your exact location",
    "js.toast.assessFail": "Something went wrong. Please try again.",
    "js.toast.needSymptom": "Please select at least one symptom first.",
    "js.toast.noGeo": "Geolocation is not available in this browser.",
    "js.toast.noLoc": "No location received — pick your area from the list instead.",
    "js.toast.geoFail": "Location not available — pick your area from the list instead.",
    "js.toast.loadFail": "Could not load the knowledge base. Is the Python server running?",
    "js.toast.guideFail": "Could not open that guide.",
    "js.toast.emergency": "Emergency guidance shown — call 108 if this is happening now.",
    "js.chatFail": "Sorry, I could not reach the server. Please make sure the Python app is running.",
    # --- scope note + result panel / library / tiers (English) ---
    "lang.note": "Interface translated. Medical content (conditions, precautions, chatbot answers, facility details) stays in English.",
    "lib.all": "All",
    "lib.readGuide": "Read the guide →",
    "tier.best": "Best match",
    "tier.good": "Good match",
    "tier.general": "General care",
    "care.selfcare": "Self-care at home",
    "care.routine": "Routine appointment",
    "care.urgent": "Urgent - see a doctor today",
    "care.emergency": "Emergency - act now",
    "band.strong": "Strong",
    "band.moderate": "Moderate",
    "band.fair": "Fair",
    "band.weak": "Weak",
    "res.emgTitle": "🚨 This pattern needs emergency care now",
    "res.emgCall": "Seek emergency care immediately. Call 108 for an ambulance or 112.",
    "res.emgList": "Do not wait for an appointment or test result. Go to the nearest emergency department.",
    "res.todo": "🧭 What to do now",
    "res.red": "🚩 Red flags — go to an emergency department if any of these happen",
    "res.precautions": "🛡️ Precautions",
    "res.homecare": "🏠 Care you can start at home",
    "res.match": "🔬 How your pattern lines up",
    "res.matchNote": "Ranked by how many of your symptoms appear in each condition's published description. This is a similarity score, **not a probability or a diagnosis**.",
    "res.matchOf": "{n} of your symptoms match: {list}",
    "res.matchAlso": "usually also seen with: {list}",
    "res.tests": "🧪 Tests a doctor may advise",
    "res.testsNote": "Tests are ordered by a clinician based on your timeline — never start treatment on a guess.",
    "res.who": "👩‍⚕️ Who to see in Hyderabad",
    "res.input": "📋 Your input",
    "res.inputNote": "Only used to compute this result. Nothing was saved or shared.",
    "res.source": "📚 Source for this guidance",
    "res.findCare": "🏥 Find care for this",
    "res.ask": "💬 Ask Susrutha",
    "res.insufficient": "⚠️ You selected fewer than two symptoms, so the guidance above is deliberately cautious. Add more symptoms (and how long you have had them) for a more useful pattern comparison.",
    "res.ambiguity": "🔀 More than one condition fits your symptoms almost equally well. That is normal — many illnesses share the same early symptoms. A clinician may need a test to tell them apart.",
    "res.riskFactors": "Risk factors considered: {list}",
}

# ---------------------------------------------------------------------------
# Telugu (తెలుగు)
# ---------------------------------------------------------------------------
TE: Dict[str, str] = {
    "nav.home": "హోమ్",
    "nav.checker": "లక్షణాల&nbsp;తనిఖీ",
    "nav.care": "చికిత్స&nbsp;కనుగొనండి",
    "nav.library": "ఆరోగ్య&nbsp;గ్రంథాలయం",
    "nav.activity": "రోజువారీ&nbsp;కార్యకలాపం",
    "emg.btn": "అత్యవసరం 108",
    "emg.short": "అత్యవసరం: 108",
    "hero.eyebrow": "వైద్య సేవల అందుబాటు · హైదరాబాద్",
    "hero.title": 'మీ లక్షణాలను అర్థం చేసుకోండి.<br><span class="grad">సరైన చికిత్సను కనుగొనండి.</span> కొన్ని నిమిషాల్లో.',
    "hero.lead": (
        "సుశ్రుత హెల్త్ పార్ట్‌నర్ ఉచితమైన, గోప్యతకు ప్రాధాన్యమిచ్చే ఆరోగ్య సహాయకుడు. మీకు ఎలా "
        "అనిపిస్తోందో వివరించండి; WHO, CDC, NHS ప్రచురించిన సమాచారం ఆధారంగా మీ లక్షణాలు సాధారణ "
        "రుగ్మతలతో ఎలా సరిపోతాయో చూడండి; మీ పరిస్థితి ఎంత అత్యవసరమో తెలుసుకోండి — ఆ తర్వాత "
        "హైదరాబాద్‌లో మీ సమీపంలోని ఆసుపత్రి లేదా పరీక్షా కేంద్రాన్ని కనుగొనండి."
    ),
    "hero.cta1": "నా లక్షణాలను తనిఖీ చేయండి →",
    "hero.cta2": "📍 నా సమీపంలో చికిత్స కనుగొనండి",
    "trust.1": "✅ ఇది నిర్ధారణ కాదు — నిర్ణయానికి సహాయం",
    "trust.2": "🔒 లాగిన్ అవసరం లేదు, డేటా నిల్వ చేయబడదు",
    "trust.3": "📚 మూలాలు: WHO · CDC · NHS",
    "mini.ask": "లక్షణాలు లేదా సేవల గురించి అడగండి…",
    "stat.conditions": "జ్ఞాన భాండాగారంలో రుగ్మతలు",
    "stat.symptoms": "మీరు ఎంచుకోగల లక్షణాలు",
    "stat.facilities": "హైదరాబాద్ సౌకర్యాలు మ్యాప్ చేయబడ్డాయి",
    "stat.sources": "బహిరంగ ఆరోగ్య మూలాలు",
    "home.features": "సుశ్రుత మీకు సహాయపడే నాలుగు మార్గాలు",
    "home.sub": 'ప్రతి ఫీచర్ ఒకే ప్రశ్నకు సమాధానం ఇస్తుంది: <em>“నేను తర్వాత ఏం చేయాలి?”</em>',
    "feat1.t": "1 · లక్షణాల తనిఖీ",
    "feat1.b": (
        "మీ లక్షణాలను ఎంచుకోండి, వయస్సు, రోజులు జోడించండి. మేము మీ స్థితిని ప్రచురించిన లక్షణాల "
        "వివరణలతో పోల్చి, ఏ రుగ్మతలకు ఎక్కువగా సరిపోతుందో చూపిస్తాము — గమనించాల్సిన ఎర్ర జెండాలతో "
        "పాటు, అత్యవసర స్థాయిని కూడా."
    ),
    "feat1.link": "ప్రయత్నించండి →",
    "feat2.t": "2 · హైదరాబాద్‌లో చికిత్స కనుగొనండి",
    "feat2.b": (
        "ఒక రుగ్మత లేదా నిపుణతను ఎంచుకుని, ప్రభుత్వ, ప్రైవేట్ ఆసుపత్రులు మరియు పరీక్షా "
        "ప్రయోగశాలలను ప్రత్యక్ష మ్యాప్‌లో చూడండి — మీ ప్రాంతం నుండి దూరం, ప్రతి ఒక్కటి ఏమి "
        "అందిస్తుందో, ఒక్క క్లిక్‌తో దారి."
    ),
    "feat2.link": "మ్యాప్ తెరవండి →",
    "feat3.t": "3 · ఆరోగ్య గ్రంథాలయం",
    "feat3.b": (
        "15 సాధారణ రుగ్మతలకు సరళమైన మార్గదర్శకాలు: లక్షణాలు, జాగ్రత్తలు, హెచ్చరిక సంకేతాలు, "
        "చిన్న అనారోగ్యాలకు ఇంటి సంరక్షణ, మరియు వైద్యుడు సాధారణంగా సూచించే పరీక్షలు."
    ),
    "feat3.link": "గ్రంథాలయం చూడండి →",
    "feat4.t": "4 · సుశ్రుత సహాయకుడు",
    "feat4.b": (
        "పారదర్శకమైన, నియమాధారిత సహాయకుడు — రోజువారీ ఆరోగ్య ప్రశ్నలకు సమాధానం ఇస్తాడు, ORS "
        "వంటి ప్రాథమిక చికిత్సను వివరిస్తాడు, మరియు అత్యవసర పరిస్థితులను నేరుగా 108‌కి తీసుకువెళుతాడు."
    ),
    "feat4.link": "ఇప్పుడు చాట్ చేయండి →",
    "home.steps": "తనిఖీ ఎలా పనిచేస్తుంది",
    "step1.t": "లక్షణాలు చెప్పండి",
    "step1.b": "శరీర వ్యవస్థల వారీగా సమూహీకరించిన 70 సరళమైన లక్షణాల నుండి శోధించండి లేదా ఎంచుకోండి.",
    "step2t.t": "మీ వివరాలు జోడించండి",
    "step2t.b": "వయస్సు, ఎన్ని రోజులు, గర్భధారణ లేదా మధుమేహం వంటి ప్రమాద కారకాలు — ఐచ్ఛికం, ఎప్పుడూ నిల్వ చేయబడవు.",
    "step3t.t": "పద్ధతి చూడండి",
    "step3t.b": "ప్రతి రుగ్మత యొక్క ప్రచురించిన లక్షణాల జాబితాతో బరువు-ప్రాధాన్య సరిపోలిక, క్రమబద్ధంగా, నిజాయితీగా లేబుల్ చేయబడింది.",
    "step4.t": "అత్యవసరత ప్రకారం చర్య తీసుకోండి",
    "step4.b": "స్వీయ సంరక్షణ, రోజువారీ సందర్శన, అదే రోజు వైద్యుడు లేదా అత్యవసరం — అలాగే హైదరాబాద్‌లో ఎక్కడికి వెళ్లాలి.",
    "home.is": "🛡️ సుశ్రుత ఏమిటి — మరియు ఏమి కాదు",
    "is.1": "<strong>ఇది:</strong> ఆరోగ్య అవగాహన, దిశను చూపే సాధనం. ఇది బహిరంగ ఆరోగ్య మార్గదర్శకాలను సంగ్రహించి, మీరు త్వరగా సంరక్షణకు చేరుకోవడానికి సహాయపడుతుంది.",
    "is.2": "<strong>ఇది కాదు:</strong> వైద్యుడు, నిర్ధారణ లేదా మందు. లక్షణాలు అనేక వ్యాధులలో ఉమ్మడిగా ఉంటాయి; పరీక్షించి, నిర్ధారించేది వైద్య నిపుణుడు మాత్రమే.",
    "is.3": "<strong>ఇది:</strong> పారదర్శకమైనది. ప్రతి రుగ్మత కార్డు తన మూలాన్ని (WHO, CDC, NHS, MedlinePlus) పేర్కొంటుంది, కాబట్టి మీరు ధృవీకరించుకోవచ్చు.",
    "is.4": "<strong>ఇది కాదు:</strong> డేటా సేకరణ. ఖాతా లేదు, డేటాబేస్ లేదు, మీ ఆరోగ్య సమాచారం ట్రాకింగ్ చేయబడదు.",
    "chk.eyebrow": "ప్రధాన ఫీచర్ · ప్రారంభ సహాయం",
    "chk.title": "లక్షణాల తనిఖీ &amp; ప్రమాద అవగాహన",
    "chk.intro": (
        "మీకు ఏమి అనిపిస్తోందో ఎంచుకోండి. సుశ్రుత మీ స్థితిని ప్రచురించిన లక్షణాల వివరణలతో "
        "పోల్చి, అది ఎంత అత్యవసరంగా కనిపిస్తుందో, తర్వాత ఏం చేయాలో చెబుతుంది."
    ),
    "dot.symptoms": "లక్షణాలు",
    "dot.about": "మీ గురించి",
    "dot.result": "ఫలితం",
    "chk.q": "మీకు ఏమి అనిపిస్తోంది?",
    "sym.search": "లక్షణాలను శోధించండి — ఉదా. జ్వరం, కీళ్ల నొప్పి, మూత్రం వెలువడేటప్పుడు మంట…",
    "btn.clear": "తొలగించు",
    "chk.tip": "చిట్కా: మీరు గమనించే ప్రతిదాన్ని ఎంచుకోండి — ఎక్కువ వివరాలు మెరుగైన సరిపోలికకు దారి తీస్తాయి.",
    "btn.continue": "కొనసాగించండి →",
    "s2.title": "మీ గురించి కొంచెం చెప్పండి",
    "s2.privacy": "🔒 మీ బ్రౌజర్‌లోనే ఉంటుంది",
    "s2.intro": (
        "ఇవన్నీ ఐచ్ఛికమే, కానీ ఇవి మీ పరిస్థితి ఎంత అత్యవసరమో మారుస్తాయి. మీరు ఇక్కడ చూస్తున్న "
        "ఫీల్డ్‌లు మినహా మరేమీ నిల్వ చేయబడవు లేదా ఎక్కడికీ పంపబడవు — అవి మీ ఫలితాన్ని లెక్కించడానికి మాత్రమే ఉపయోగించబడతాయి."
    ),
    "f.age": "వయస్సు (సంవత్సరాలు)",
    "ph.age": "ఉదా. 28",
    "f.days": "ఇది ఎన్ని రోజుల నుండి ఉంది?",
    "days.none": "ఖచ్చితంగా తెలియదు",
    "days.d0": "ఈ రోజు ప్రారంభమైంది",
    "days.d1": "1 రోజు",
    "days.d2": "2–3 రోజులు",
    "days.d5": "4–7 రోజులు",
    "days.d10": "వారం కంటే ఎక్కువ",
    "days.d20": "2 వారాల కంటే ఎక్కువ",
    "f.sev": "ఇది ఎంత తీవ్రంగా అనిపిస్తోంది?",
    "sev.mild": "తేలిక — నేను నా సాధారణ రోజును చేయగలను",
    "sev.mod": "మధ్యస్థం — ఇది నన్ను ఇబ్బంది పెడుతోంది",
    "sev.sev": "తీవ్రం — నేను భరించలేకపోతున్నాను",
    "f.pregnant": "గర్భవతి (లేదా గర్భవతి కావచ్చు)",
    "f.chronic": "దీర్ఘకాలిక రుగ్మతలు ఏమైనా ఉన్నాయా?",
    "f.chronichint": "(అన్నీ వర్తిస్తే ఎంచుకోండి)",
    "btn.back": "← వెనుకకు",
    "btn.guidance": "నా మార్గదర్శనం పొందండి →",
    "btn.restart": "↺ మళ్లీ ప్రారంభించండి",
    "btn.edit": "సమాధానాలను సవరించండి",
    "fc.eyebrow": "ప్రధాన ఫీచర్ · సౌకర్యాల కనుగొనుట",
    "fc.title": "హైదరాబాద్‌లో చికిత్స కనుగొనండి",
    "fc.intro": (
        "ప్రభుత్వ, ప్రైవేట్ ఆసుపత్రులు మరియు పరీక్షా ప్రయోగశాలలు — మీకు అవసరమైన రుగ్మత లేదా "
        "నిపుణత ప్రకారం వడపోత, మీ ప్రాంతం నుండి దూరం ప్రకారం క్రమబద్ధం."
    ),
    "fc.cond": "మీకు ఏం కోసం చికిత్స కావాలి?",
    "fc.any": "ఏదైనా రుగ్మత",
    "fc.spec": "లేదా నిపుణత",
    "fc.allspec": "అన్ని నిపుణతలు",
    "fc.area": "మీ ప్రాంతం",
    "fc.type": "రకం",
    "sector.all": "అన్ని సౌకర్యాలు",
    "sector.gov": "ప్రభుత్వ",
    "sector.pri": "ప్రైవేట్",
    "sector.lab": "పరీక్షా ప్రయోగశాలలు",
    "fc.sort": "క్రమబద్ధం చేయండి",
    "order.auto": "నాకు అనుకూలం (స్వయంచాలక)",
    "order.dist": "సమీపమైనది మొదట",
    "order.rel": "మెరుగైన నిపుణత సరిపోలిక",
    "fc.useloc": "📍 నా ఖచ్చితమైన స్థానాన్ని ఉపయోగించండి",
    "fc.facilities": "సౌకర్యాలు",
    "fc.noteTitle": "ℹ️ ప్రయాణించే ముందు",
    "fc.note": (
        "సౌకర్యాల పేర్లు, ప్రాంతాలు నిజమైనవి; మ్యాప్ పిన్‌లు సుమారుగా మాత్రమే. ప్రవేశ ద్వారం, OPD "
        "సమయాలు, మరియు మీకు అవసరమైన పరీక్ష అదే రోజు అందుబాటులో ఉందో లేదో తెలుసుకోవడానికి ఆసుపత్రికి "
        "తప్పకుండా ఫోన్ చేయండి. అత్యవసర పరిస్థితిలో నగరం అంతటా ప్రయాణించడం కంటే సమీపపు అత్యవసర విభాగానికి వెళ్లండి."
    ),
    "lib.eyebrow": "ప్రధాన ఫీచర్ · ఆరోగ్య సమాచార సహాయం",
    "lib.title": "ఆరోగ్య గ్రంథాలయం",
    "lib.intro": (
        "WHO, CDC, NHS, MedlinePlus సమాచారం ఆధారంగా తయారు చేసిన సరళమైన మార్గదర్శకాలు. ప్రతి "
        "కార్డు ఆ రుగ్మత సాధారణంగా ఎంత అత్యవసరమో, మరియు “వెంటనే వైద్యుడిని కలవండి” అనే ఎర్ర "
        "జెండాలను చూపుతుంది."
    ),
    "lib.search": "రుగ్మత, లక్షణం లేదా అంశాన్ని శోధించండి — ఉదా. డెంగ్యూ, దద్దుర్లు, రక్తంలో చక్కెర…",
    "act.eyebrow": "ఆరోగ్యం · చిన్న, రోజువారీ అలవాట్లు",
    "act.title": "రోజువారీ ఆరోగ్య కార్యకలాపం",
    "act.intro": (
        "ప్రతి రోజు ఒక సులభమైన కార్యకలాపం చూపబడుతుంది. ఇది ఐచ్ఛికం, దీన్ని ఎప్పుడైనా వదిలివేయవచ్చు, "
        "ఇది సాధారణ ఆరోగ్యం కోసం ఒక చిన్న సూచన మాత్రమే — వైద్య సలహా కాదు."
    ),
    "act.complete": "పూర్తయినట్లు గుర్తించండి",
    "act.skip": "ఈ రోజు వద్దు / దాటవేయి",
    "act.weekTitle": "ఈ వారం",
    "foot.disclaimer": "వైద్య నిరాకరణ",
    "foot.discText": (
        "ఈ సాధనం మీరు తర్వాత ఏం చేయాలో నిర్ణయించుకోవడానికి సహాయపడటానికి బహిరంగ మూలాల (WHO, CDC, "
        "NHS, MedlinePlus) నుండి సాధారణ ఆరోగ్య సమాచారాన్ని అందిస్తుంది. ఇది నిర్ధారణ కాదు, తీవ్రమైన "
        "అనారోగ్యాన్ని కూడా తోసిపుచ్చలేదు. మీ ఆరోగ్యం గురించి ఎల్లప్పుడూ అర్హత గల వైద్యుడిని సంప్రదించండి."
    ),
    "foot.privacy": "గోప్యత",
    "foot.privacyText": (
        "లాగిన్ లేదు, డేటాబేస్ లేదు, ఆరోగ్య సమాచారం ట్రాకింగ్ లేదు. అంచనాలు మెమరీలో లెక్కించబడి "
        "మీకు మాత్రమే చూపబడతాయి."
    ),
    "foot.base": "ప్రోటోటైప్ · డెమో డేటా · 2026",
    "foot.emg": "అత్యవసరం: 108 · అంబులెన్స్ 108 · జాతీయం 112 · ఆరోగ్య హెల్ప్‌లైన్ 104",
    "chat.fab": "సుశ్రుత్‌ను అడగండి",
    "chat.name": "సుశ్రుత సహాయకుడు",
    "chat.sub": "ఆరోగ్య సమాచారం · వైద్యుడు కాదు",
    "chat.placeholder": "లక్షణాలు, నివారణ, పరీక్షలు లేదా సౌకర్యాల గురించి అడగండి…",
    "chat.send": "పంపండి",
    "notice.title": "సుశ్రుత హెల్త్ పార్ట్‌నర్‌కు స్వాగతం",
    "notice.sub": "వైద్య సేవల అందుబాటు &amp; ప్రారంభ సహాయం · హైదరాబాద్",
    "notice.intro": (
        "ఈ సాధనం హైదరాబాద్‌లో <strong>లక్షణాలను అర్థం చేసుకోవడానికి, అవి ఏమి అర్థం చేసుకోవచ్చో "
        "తెలుసుకోవడానికి, సరైన సౌకర్యాన్ని కనుగొనడానికి</strong> మీకు సహాయపడుతుంది. ప్రారంభించే ముందు ఇది గుర్తుంచుకోండి:"
    ),
    "notice.1": "✅ ఇది <strong>WHO, CDC, NHS, MedlinePlus</strong> మూలాల నుండి సాధారణ సమాచారాన్ని ఇస్తుంది.",
    "notice.2": "❌ ఇది <strong>నిర్ధారణ కాదు</strong> మరియు తీవ్రమైన అనారోగ్యాన్ని తోసిపుచ్చలేదు.",
    "notice.3": "🔒 ఏమీ నిల్వ చేయబడదు — లాగిన్ లేదు, డేటాబేస్ లేదు, ఏదీ పంచబడదు.",
    "notice.4": "🚑 అత్యవసర పరిస్థితుల్లో <strong>108 / 112</strong>‌కి ఫోన్ చేయండి లేదా సమీపపు అత్యవసర విభాగానికి వెళ్లండి.",
    "notice.tail": "కొనసాగించడం ద్వారా, ఏదైనా రుగ్మతను అర్హత గల వైద్యుడు నిర్ధారించి, చికిత్స సూచించాలని మీరు అర్థం చేసుకుంటున్నారు.",
    "notice.ok": "నాకు అర్థమైంది — కొనసాగించండి",
    "notice.emg": "🚑 అత్యవసర నంబర్లు",
    "emg.modalTitle": "🚨 అత్యవసర సహాయం",
    "emg.modalIntro": (
        "ఎవరైనా స్పృహ లేకుండా, శ్వాస తీసుకోలేకపోతుండి, ఛాతి నొప్పి, భారీ రక్తస్రావం, మెత్తని "
        "తిప్పట లేదా ఒక్కసారిగా బలహీనత ఉంటే, వెంటనే సహాయాన్ని పిలవండి."
    ),
    "emg.modalTail": (
        "ఆ తర్వాత <strong>చికిత్స కనుగొనండి</strong> ట్యాబ్‌ను తెరిచి హైదరాబాద్‌లోని సమీపపు అత్యవసర "
        "విభాగాలను చూడండి, లేదా దారి కోసం Google Maps ఉపయోగించండి."
    ),
    "emg.understand": "నాకు అర్థమైంది",
    "js.analysing": "విశ్లేషిస్తోంది…",
    "js.guidance": "నా మార్గదర్శనం పొందండి →",
    "js.selected": "{n} ఎంపిక",
    "js.shown": "{n} చూపబడింది",
    "js.careFor": "{name} కోసం చికిత్స",
    "js.allFacilities": "అన్ని సౌకర్యాలు",
    "js.conditions": "{n} రుగ్మతలు",
    "js.trayEmpty": "ఇంకా ఏమీ ఎంపిక కాలేదు — మీకు వర్తించే లక్షణాలను ఎంచుకోండి.",
    "js.metaNear": "{n} సౌకర్యాలు సరిపోలాయి · సమీపమైనవి మొదట",
    "js.metaRel": "{n} సౌకర్యాలు సరిపోలాయి · మెరుగైన నిపుణత మొదట",
    "js.metaNearAdd": "{n} సౌకర్యాలు సరిపోలాయి · సమీపమైనవి మొదట · దూరాల కోసం మీ ప్రాంతాన్ని జోడించండి",
    "js.metaRelAdd": "{n} సౌకర్యాలు సరిపోలాయి · మెరుగైన నిపుణత మొదట · దూరాల కోసం మీ ప్రాంతాన్ని జోడించండి",
    "js.metaAllNear": "మ్యాప్ చేయబడిన అన్ని {n} సౌకర్యాలు · సమీపమైనవి మొదట",
    "js.metaAll": "మ్యాప్ చేయబడిన అన్ని {n} సౌకర్యాలు · పరిమితం చేయడానికి రుగ్మత లేదా మీ ప్రాంతాన్ని ఎంచుకోండి",
    "js.locUse": "📍 నా ఖచ్చితమైన స్థానాన్ని ఉపయోగించండి",
    "js.locWorking": "📍 స్థానం కనుగొంటోంది…",
    "js.locDone": "📍 మీ ఖచ్చితమైన స్థానం ఉపయోగించబడుతోంది",
    "js.toast.assessFail": "ఏదో తప్పు జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.",
    "js.toast.needSymptom": "దయచేసి ముందుగా కనీసం ఒక లక్షణాన్ని ఎంచుకోండి.",
    "js.toast.noGeo": "ఈ బ్రౌజర్‌లో స్థాన సేవ అందుబాటులో లేదు.",
    "js.toast.noLoc": "స్థానం రాలేదు — జాబితా నుండి మీ ప్రాంతాన్ని ఎంచుకోండి.",
    "js.toast.geoFail": "స్థానం అందుబాటులో లేదు — జాబితా నుండి మీ ప్రాంతాన్ని ఎంచుకోండి.",
    "js.toast.loadFail": "జ్ఞాన భాండాగారం లోడ్ కాలేదు. పైథాన్ సర్వర్ నడుస్తోందా?",
    "js.toast.guideFail": "ఆ మార్గదర్శకాన్ని తెరవడంలో సమస్య వచ్చింది.",
    "js.toast.emergency": "అత్యవసర మార్గదర్శనం చూపబడింది — ఇది జరుగుతుంటే 108‌కి ఫోన్ చేయండి.",
    "js.chatFail": "క్షమించండి, సర్వర్‌ను చేరుకోలేకపోయాను. పైథాన్ యాప్ నడుస్తోందో లేదో చూడండి.",
    "lang.note": "ఇంటర్‌ఫేస్ అనువదించబడింది. వైద్య సమాచారం (రుగ్మతలు, జాగ్రత్తలు, చాట్ సమాధానాలు, సౌకర్యాల వివరాలు) ఇంగ్లీషులోనే ఉంటాయి.",
    "lib.all": "అన్నీ",
    "lib.readGuide": "మార్గదర్శకం చదవండి →",
    "tier.best": "మెరుగైన సరిపోలిక",
    "tier.good": "మంచి సరిపోలిక",
    "tier.general": "సాధారణ సంరక్షణ",
    "care.selfcare": "ఇంట్లోనే స్వీయ సంరక్షణ",
    "care.routine": "సాధారణ అపాయింట్‌మెంట్",
    "care.urgent": "అత్యవసరం - ఈ రోజే వైద్యుడిని కలవండి",
    "care.emergency": "అత్యవసరం - ఇప్పుడే చర్య తీసుకోండి",
    "band.strong": "బలమైన",
    "band.moderate": "మధ్యస్థ",
    "band.fair": "సగటు",
    "band.weak": "బలహీన",
    "res.emgTitle": "🚨 ఈ స్థితికి ఇప్పుడే అత్యవసర వైద్యం అవసరం",
    "res.emgCall": "వెంటనే అత్యవసర వైద్యం పొందండి. అంబులెన్స్ కోసం 108 లేదా 112‌కి ఫోన్ చేయండి.",
    "res.emgList": "అపాయింట్‌మెంట్ లేదా ఫలితం కోసం ఎదురు చూడవద్దు. సమీపపు అత్యవసర విభాగానికి వెళ్లండి.",
    "res.todo": "🧭 ఇప్పుడు ఏం చేయాలి",
    "res.red": "🚩 ఎర్ర జెండాలు — ఇవి ఉంటే అత్యవసర విభాగానికి వెళ్లండి",
    "res.precautions": "🛡️ జాగ్రత్తలు",
    "res.homecare": "🏠 మీరు ఇంట్లో ప్రారంభించగల సంరక్షణ",
    "res.match": "🔬 మీ స్థితి ఎలా సరిపోతోంది",
    "res.matchNote": "ప్రతి రుగ్మత ప్రచురించిన వివరణలో మీ లక్షణాలు ఎన్ని కనిపిస్తాయో దాని ప్రకారం క్రమబద్ధం. ఇది సరిపోలిక స్కోరు మాత్రమే — **సంభావ్యత కాదు, నిర్ధారణ కాదు**.",
    "res.matchOf": "మీ {n} లక్షణాలు సరిపోలాయి: {list}",
    "res.matchAlso": "సాధారణంగా దీనితో పాటు కనిపించేవి: {list}",
    "res.tests": "🧪 వైద్యుడు సూచించే పరీక్షలు",
    "res.testsNote": "పరీక్షలు వైద్యుడు మీ సమయ క్రమాన్ని బట్టి సూచిస్తారు — అంచనా ఆధారంగా చికిత్స ప్రారంభించవద్దు.",
    "res.who": "👩‍⚕️ హైదరాబాద్‌లో ఎవరిని కలవాలి",
    "res.input": "📋 మీ ఇన్‌పుట్",
    "res.inputNote": "ఈ ఫలితాన్ని లెక్కించడానికి మాత్రమే ఉపయోగించబడింది. ఏమీ నిల్వ లేదా పంచబడలేదు.",
    "res.source": "📚 ఈ మార్గదర్శనానికి మూలం",
    "res.findCare": "🏥 దీని కోసం సంరక్షణ కనుగొనండి",
    "res.ask": "💬 సుశ్రుత్‌ను అడగండి",
    "res.insufficient": "⚠️ రెండు లక్షణాల కంటే తక్కువ ఎంచుకున్నారు కాబట్టి పై మార్గదర్శనం ఉద్దేశపూర్వకంగా జాగ్రత్తగా ఉంది. మెరుగైన పోలిక కోసం మరిన్ని లక్షణాలు (వాటిని ఎన్ని రోజులుగా ఉన్నాయో) జోడించండి.",
    "res.ambiguity": "🔀 మీ లక్షణాలకు రెండు రుగ్మతలు దాదాపు సమానంగా సరిపోతాయి. ఇది సాధారణమే — చాలా అనారోగ్యాలు ఒకే ప్రారంభ లక్షణాలను పంచుకుంటాయి. తేడా చెప్పడానికి వైద్యుడు పరీక్ష అవసరం కావచ్చు.",
    "res.riskFactors": "పరిగణించిన ప్రమాద కారకాలు: {list}",
}

# ---------------------------------------------------------------------------
# Hindi (हिन्दी)
# ---------------------------------------------------------------------------
HI: Dict[str, str] = {
    "nav.home": "होम",
    "nav.checker": "लक्षण&nbsp;जाँच",
    "nav.care": "उपचार&nbsp;खोजें",
    "nav.library": "स्वास्थ्य&nbsp;पुस्तकालय",
    "nav.activity": "दैनिक&nbsp;गतिविधि",
    "emg.btn": "आपातकाल 108",
    "emg.short": "आपातकाल: 108",
    "hero.eyebrow": "स्वास्थ्य सेवाओं की पहुँच · हैदराबाद",
    "hero.title": 'अपने लक्षणों को समझें.<br><span class="grad">सही उपचार खोजें.</span> कुछ ही मिनटों में.',
    "hero.lead": (
        "सुश्रुत हेल्थ पार्टनर एक मुफ़्त, गोपनीयता-प्रथम स्वास्थ्य सहायक है. बताइए कि आपको कैसा "
        "महसूस हो रहा है; WHO, CDC और NHS की प्रकाशित जानकारी के आधार पर देखिए कि आपके लक्षण "
        "आम बीमारियों से कैसे मेल खाते हैं; जानिए कि आपकी स्थिति कितनी गंभीर है — फिर हैदराबाद में "
        "अपने पास का अस्पताल या जाँच केंद्र खोजिए."
    ),
    "hero.cta1": "मेरे लक्षण जाँचें →",
    "hero.cta2": "📍 पास में देखभाल खोजें",
    "trust.1": "✅ यह निदान नहीं है — निर्णय में सहायता",
    "trust.2": "🔒 कोई लॉगिन नहीं, कोई डेटा संग्रहीत नहीं",
    "trust.3": "📚 स्रोत: WHO · CDC · NHS",
    "mini.ask": "लक्षणों या सेवाओं के बारे में पूछें…",
    "stat.conditions": "ज्ञान कोश में स्थितियाँ",
    "stat.symptoms": "आप जो लक्षण चुन सकते हैं",
    "stat.facilities": "हैदराबाद की सुविधाएँ मानचित्र पर",
    "stat.sources": "सार्वजनिक स्वास्थ्य स्रोत",
    "home.features": "सुश्रुत आपकी मदद के चार तरीके",
    "home.sub": 'हर सुविधा एक ही सवाल का जवाब देती है: <em>“अब मुझे क्या करना चाहिए?”</em>',
    "feat1.t": "1 · लक्षण जाँच",
    "feat1.b": (
        "अपने लक्षण चुनें, उम्र और दिन जोड़ें. हम आपकी स्थिति की तुलना प्रकाशित लक्षण-विवरणों से करते "
        "हैं और बताते हैं कि कौन-सी बीमारियाँ सबसे अच्छी मेल खाती हैं — ध्यान देने योग्य चेतावनी संकेतों "
        "और सटीक तात्कालिकता स्तर के साथ."
    ),
    "feat1.link": "आज़माएँ →",
    "feat2.t": "2 · हैदराबाद में उपचार खोजें",
    "feat2.b": (
        "कोई स्थिति या विशेषता चुनें और सरकारी अस्पताल, निजी अस्पताल तथा जाँच प्रयोगशालाएँ लाइव "
        "मानचित्र पर देखें — आपके क्षेत्र से दूरी, हर जगह क्या मिलता है, और एक क्लिक में दिशा-निर्देश."
    ),
    "feat2.link": "मानचित्र खोलें →",
    "feat3.t": "3 · स्वास्थ्य पुस्तकालय",
    "feat3.b": (
        "15 आम बीमारियों के सरल मार्गदर्शिका: लक्षण, सावधानियाँ, चेतावनी संकेत, हल्की बीमारियों में "
        "घरेलू देखभाल, और डॉक्टर जो जाँच कराने की सलाह देते हैं."
    ),
    "feat3.link": "पुस्तकालय देखें →",
    "feat4.t": "4 · सुश्रुत सहायक",
    "feat4.b": (
        "एक पारदर्शी, नियम-आधारित सहायक जो रोज़मर्रा के स्वास्थ्य सवालों के जवाब देता है, ORS जैसी "
        "प्राथमिक उपचार विधि समझाता है, और आपातकाल में सीधे 108 तक पहुँचाता है."
    ),
    "feat4.link": "अभी चैट करें →",
    "home.steps": "जाँच कैसे काम करती है",
    "step1.t": "लक्षण बताएँ",
    "step1.b": "शरीर के आधार पर समूहबद्ध 70 सरल लक्षणों में से खोजें या चुनें.",
    "step2t.t": "अपनी जानकारी जोड़ें",
    "step2t.b": "उम्र, कितने दिन, और गर्भावस्था या मधुमेह जैसे जोखिम कारक — वैकल्पिक और कभी संग्रहीत नहीं.",
    "step3t.t": "पैटर्न देखें",
    "step3t.b": "हर बीमारी की प्रकाशित लक्षण सूची के साथ वेटेड मिलान, क्रमबद्ध और स्पष्ट रूप से लेबल किया गया.",
    "step4.t": "तात्कालिकता के अनुसार कार्य करें",
    "step4.b": "घरेलू देखभाल, नियमित भेंट, उसी दिन डॉक्टर या आपातकाल — और हैदराबाद में कहाँ जाएँ.",
    "home.is": "🛡️ सुश्रुत क्या है — और क्या नहीं",
    "is.1": "<strong>है:</strong> स्वास्थ्य साक्षरता और दिशा-निर्देश का एक उपकरण. यह सार्वजनिक स्वास्थ्य सलाह का सार देता है और आपको जल्दी देखभाल तक पहुँचने में मदद करता है.",
    "is.2": "<strong>नहीं है:</strong> डॉक्टर, निदान या पर्चा. लक्षण कई बीमारियों में मिलते-जुलते हैं; परीक्षण और पुष्टि केवल चिकित्सक कर सकते हैं.",
    "is.3": "<strong>है:</strong> पारदर्शी. हर बीमारी कार्ड अपना स्रोत (WHO, CDC, NHS, MedlinePlus) बताता है, ताकि आप जाँच सकें.",
    "is.4": "<strong>नहीं है:</strong> डेटा संग्रहण. न खाता, न डेटाबेस, आपकी स्वास्थ्य जानकारी कोई ट्रैकिंग नहीं.",
    "chk.eyebrow": "मुख्य सुविधा · प्रारंभिक सहायता",
    "chk.title": "लक्षण जाँच और जोखिम की जानकारी",
    "chk.intro": (
        "बताइए कि आपको क्या महसूस हो रहा है. सुश्रुत आपकी स्थिति की तुलना प्रकाशित लक्षण-विवरणों "
        "से करता है और बताता है कि यह कितना गंभीर दिखता है और आगे क्या करना चाहिए."
    ),
    "dot.symptoms": "लक्षण",
    "dot.about": "आपके बारे में",
    "dot.result": "परिणाम",
    "chk.q": "आपको क्या महसूस हो रहा है?",
    "sym.search": "लक्षण खोजें — जैसे बुखार, जोड़ों में दर्द, पेशाब में जलन…",
    "btn.clear": "साफ़ करें",
    "chk.tip": "सुझाव: जो कुछ भी आप महसूस कर रहे हैं उसे चुनें — अधिक विवरण से बेहतर मिलान होता है.",
    "btn.continue": "जारी रखें →",
    "s2.title": "अपने बारे में थोड़ा बताएँ",
    "s2.privacy": "🔒 आपके ब्राउज़र में ही रहता है",
    "s2.intro": (
        "यह सब वैकल्पिक है, पर इससे आपकी स्थिति की गंभीरता बदलती है. आपके यहाँ दिखने वाले फ़ील्ड के "
        "अलावा कुछ भी संग्रहीत या कहीं भेजा नहीं जाता — उनका उपयोग केवल आपका परिणाम निकालने के लिए होता है."
    ),
    "f.age": "उम्र (वर्ष)",
    "ph.age": "जैसे 28",
    "f.days": "यह कितने दिनों से है?",
    "days.none": "पक्का नहीं",
    "days.d0": "आज शुरू हुआ",
    "days.d1": "1 दिन",
    "days.d2": "2–3 दिन",
    "days.d5": "4–7 दिन",
    "days.d10": "एक हफ़्ते से अधिक",
    "days.d20": "2 हफ़्तों से अधिक",
    "f.sev": "यह कितना गंभीर लगता है?",
    "sev.mild": "हल्का — मैं अपना सामान्य दिन बिता सकता/सकती हूँ",
    "sev.mod": "मध्यम — यह परेशान कर रहा है",
    "sev.sev": "गंभीर — मैं संभाल नहीं पा रहा/रही",
    "f.pregnant": "गर्भवती (या संभवतः गर्भवती)",
    "f.chronic": "कोई दीर्घकालिक समस्या?",
    "f.chronichint": "(जो लागू हों सभी चुनें)",
    "btn.back": "← वापस",
    "btn.guidance": "मार्गदर्शन पाएँ →",
    "btn.restart": "↺ फिर से शुरू करें",
    "btn.edit": "उत्तर संपादित करें",
    "fc.eyebrow": "मुख्य सुविधा · सुविधाओं की खोज",
    "fc.title": "हैदराबाद में उपचार खोजें",
    "fc.intro": (
        "सरकारी और निजी अस्पताल तथा जाँच प्रयोगशालाएँ — आपकी स्थिति या विशेषता के अनुसार छाँटी गईं, "
        "आपके क्षेत्र से दूरी के अनुसार क्रमबद्ध."
    ),
    "fc.cond": "आपको किसके लिए देखभाल चाहिए?",
    "fc.any": "कोई भी स्थिति",
    "fc.spec": "या कोई विशेषता",
    "fc.allspec": "सभी विशेषताएँ",
    "fc.area": "आपका क्षेत्र",
    "fc.type": "प्रकार",
    "sector.all": "सभी सुविधाएँ",
    "sector.gov": "सरकारी",
    "sector.pri": "निजी",
    "sector.lab": "जाँच प्रयोगशालाएँ",
    "fc.sort": "क्रमबद्ध करें",
    "order.auto": "मेरे लिए सर्वोत्तम (स्वतः)",
    "order.dist": "नज़दीकी पहले",
    "order.rel": "बेहतर विशेषता मिलान",
    "fc.useloc": "📍 मेरा सटीक स्थान उपयोग करें",
    "fc.facilities": "सुविधाएँ",
    "fc.noteTitle": "ℹ️ यात्रा से पहले",
    "fc.note": (
        "सुविधाओं के नाम और क्षेत्र वास्तविक हैं; मानचित्र पिन अनुमानित हैं. प्रवेश द्वार, OPD समय, और "
        "आपको ज़रूरी जाँच उसी दिन उपलब्ध है या नहीं — यह पक्का करने के लिए अस्पताल को हमेशा फ़ोन करें. "
        "आपातकाल में शहर भर जाने के बजाय नज़दीकी आपातकालीन विभाग जाएँ."
    ),
    "lib.eyebrow": "मुख्य सुविधा · स्वास्थ्य जानकारी सहायता",
    "lib.title": "स्वास्थ्य पुस्तकालय",
    "lib.intro": (
        "WHO, CDC, NHS और MedlinePlus की सामग्री से बने सरल मार्गदर्शिका. हर कार्ड बताता है कि वह "
        "स्थिति आम तौर पर कितनी गंभीर है, और वे चेतावनी संकेत जिनका मतलब है “अभी डॉक्टर से मिलें”."
    ),
    "lib.search": "कोई स्थिति, लक्षण या विषय खोजें — जैसे डेंगू, चकत्ते, रक्त शर्करा…",
    "act.eyebrow": "कल्याण · छोटी, रोज़मर्रा की आदतें",
    "act.title": "दैनिक स्वास्थ्य गतिविधि",
    "act.intro": (
        "हर दिन एक सरल गतिविधि दिखाई जाती है. यह वैकल्पिक है, कभी भी छोड़ी जा सकती है, और केवल "
        "सामान्य कल्याण के लिए एक छोटा सुझाव है — चिकित्सा सलाह नहीं."
    ),
    "act.complete": "पूर्ण चिह्नित करें",
    "act.skip": "आज नहीं / छोड़ें",
    "act.weekTitle": "यह सप्ताह",
    "foot.disclaimer": "चिकित्सा अस्वीकरण",
    "foot.discText": (
        "यह उपकरण आगे आपको क्या करना चाहिए, यह तय करने में मदद के लिए सार्वजनिक स्रोतों (WHO, CDC, "
        "NHS, MedlinePlus) से सामान्य स्वास्थ्य जानकारी देता है. यह निदान नहीं है और गंभीर बीमारी को "
        "खारिज नहीं कर सकता. अपने स्वास्थ्य के बारे में हमेशा योग्य डॉक्टर से सलाह लें."
    ),
    "foot.privacy": "गोपनीयता",
    "foot.privacyText": (
        "न लॉगिन, न डेटाबेस, न स्वास्थ्य जानकारी की ट्रैकिंग. आकलन मेमोरी में निकाले जाते हैं और केवल "
        "आपको दिखाए जाते हैं."
    ),
    "foot.base": "प्रोटोटाइप · डेमो डेटा · 2026",
    "foot.emg": "आपातकाल: 108 · एम्बुलेंस 108 · राष्ट्रीय 112 · स्वास्थ्य हेल्पलाइन 104",
    "chat.fab": "सुश्रुत से पूछें",
    "chat.name": "सुश्रुत सहायक",
    "chat.sub": "स्वास्थ्य जानकारी · डॉक्टर नहीं",
    "chat.placeholder": "लक्षणों, रोकथाम, जाँच या सुविधाओं के बारे में पूछें…",
    "chat.send": "भेजें",
    "notice.title": "सुश्रुत हेल्थ पार्टनर में आपका स्वागत है",
    "notice.sub": "स्वास्थ्य सेवाओं की पहुँच और प्रारंभिक सहायता · हैदराबाद",
    "notice.intro": (
        "यह उपकरण हैदराबाद में <strong>लक्षणों को समझने, उनका मतलब जानने और सही सुविधा खोजने</strong> "
        "में आपकी मदद करता है. शुरू करने से पहले यह ध्यान रखें:"
    ),
    "notice.1": "✅ यह <strong>WHO, CDC, NHS और MedlinePlus</strong> के स्रोतों से सामान्य जानकारी देता है.",
    "notice.2": "❌ यह <strong>निदान नहीं है</strong> और गंभीर बीमारी को खारिज नहीं कर सकता.",
    "notice.3": "🔒 कुछ भी संग्रहीत नहीं — न लॉगिन, न डेटाबेस, कुछ भी साझा नहीं.",
    "notice.4": "🚑 आपातकाल में <strong>108 / 112</strong> पर कॉल करें या नज़दीकी आपातकालीन विभाग जाएँ.",
    "notice.tail": "जारी रखकर आप समझते हैं कि कोई भी स्थिति योग्य डॉक्टर की पुष्टि और उपचार के पर्चे से ही तय होती है.",
    "notice.ok": "मैं समझता/समझती हूँ — जारी रखें",
    "notice.emg": "🚑 आपातकालीन नंबर",
    "emg.modalTitle": "🚨 आपातकालीन सहायता",
    "emg.modalIntro": (
        "अगर कोई बेहोश है, साँस नहीं ले पा रहा, छाती में दर्द है, तेज़ रक्तस्राव है, दौरा पड़ रहा है "
        "या अचानक कमज़ोरी है, तो तुरंत मदद बुलाएँ."
    ),
    "emg.modalTail": (
        "फिर <strong>देखभाल खोजें</strong> टैब खोलकर हैदराबाद के नज़दीकी आपातकालीन विभाग देखें, या "
        "दिशा-निर्देशों के लिए Google Maps उपयोग करें."
    ),
    "emg.understand": "मैं समझता/समझती हूँ",
    "js.analysing": "विश्लेषण हो रहा है…",
    "js.guidance": "मार्गदर्शन पाएँ →",
    "js.selected": "{n} चुने गए",
    "js.shown": "{n} दिखाए गए",
    "js.careFor": "{name} के लिए देखभाल",
    "js.allFacilities": "सभी सुविधाएँ",
    "js.conditions": "{n} स्थितियाँ",
    "js.trayEmpty": "अभी कुछ नहीं चुना — अपने लक्षण चुनें.",
    "js.metaNear": "{n} सुविधाएँ मेल खाती हैं · नज़दीकी पहले",
    "js.metaRel": "{n} सुविधाएँ मेल खाती हैं · बेहतर विशेषता पहले",
    "js.metaNearAdd": "{n} सुविधाएँ मेल खाती हैं · नज़दीकी पहले · दूरी के लिए अपना क्षेत्र जोड़ें",
    "js.metaRelAdd": "{n} सुविधाएँ मेल खाती हैं · बेहतर विशेषता पहले · दूरी के लिए अपना क्षेत्र जोड़ें",
    "js.metaAllNear": "मानचित्र पर सभी {n} सुविधाएँ · नज़दीकी पहले",
    "js.metaAll": "मानचित्र पर सभी {n} सुविधाएँ · सीमित करने के लिए कोई स्थिति या क्षेत्र चुनें",
    "js.locUse": "📍 मेरा सटीक स्थान उपयोग करें",
    "js.locWorking": "📍 स्थान खोजा जा रहा है…",
    "js.locDone": "📍 आपका सटीक स्थान उपयोग हो रहा है",
    "js.toast.assessFail": "कुछ गलत हुआ. कृपया फिर से प्रयास करें.",
    "js.toast.needSymptom": "कृपया पहले कम से कम एक लक्षण चुनें.",
    "js.toast.noGeo": "इस ब्राउज़र में स्थान सेवा उपलब्ध नहीं है.",
    "js.toast.noLoc": "स्थान नहीं मिला — सूची से अपना क्षेत्र चुनें.",
    "js.toast.geoFail": "स्थान उपलब्ध नहीं — सूची से अपना क्षेत्र चुनें.",
    "js.toast.loadFail": "ज्ञान कोश लोड नहीं हुआ. क्या पाइथन सर्वर चल रहा है?",
    "js.toast.guideFail": "वह मार्गदर्शिका नहीं खुल सकी.",
    "js.toast.emergency": "आपातकालीन मार्गदर्शन दिखाया गया — यह हो रहा हो तो 108 पर कॉल करें.",
    "js.chatFail": "क्षमा करें, सर्वर तक नहीं पहुँच सका. कृपया जाँचें कि पाइथन ऐप चल रहा है.",
    "lang.note": "इंटरफ़ेस अनुवादित है. चिकित्सा सामग्री (स्थितियाँ, सावधानियाँ, चैट उत्तर, सुविधा विवरण) अंग्रेज़ी में ही रहती है.",
    "lib.all": "सभी",
    "lib.readGuide": "मार्गदर्शिका पढ़ें →",
    "tier.best": "सर्वोत्तम मिलान",
    "tier.good": "अच्छा मिलान",
    "tier.general": "सामान्य देखभाल",
    "care.selfcare": "घरेलू देखभाल",
    "care.routine": "नियमित अपॉइंटमेंट",
    "care.urgent": "अत्यावश्यक - आज ही डॉक्टर से मिलें",
    "care.emergency": "आपातकाल - अभी कार्य करें",
    "band.strong": "मज़बूत",
    "band.moderate": "मध्यम",
    "band.fair": "ठीक-ठाक",
    "band.weak": "कमज़ोर",
    "res.emgTitle": "🚨 इस स्थिति में अभी आपातकालीन देखभाल ज़रूरी है",
    "res.emgCall": "तुरंत आपातकालीन देखभाल लें. एम्बुलेंस के लिए 108 या 112 पर कॉल करें.",
    "res.emgList": "अपॉइंटमेंट या परिणाम की प्रतीक्षा न करें. नज़दीकी आपातकालीन विभाग जाएँ.",
    "res.todo": "🧭 अब क्या करें",
    "res.red": "🚩 चेतावनी संकेत — ये हों तो आपातकालीन विभाग जाएँ",
    "res.precautions": "🛡️ सावधानियाँ",
    "res.homecare": "🏠 घर पर शुरू की जा सकने वाली देखभाल",
    "res.match": "🔬 आपकी स्थिति कैसे मेल खाती है",
    "res.matchNote": "हर बीमारी के प्रकाशित विवरण में आपके लक्षण कितने आते हैं, उसी के अनुसार क्रमबद्ध. यह मिलान स्कोर है, **संभावना या निदान नहीं**.",
    "res.matchOf": "आपके {n} लक्षण मेल खाते हैं: {list}",
    "res.matchAlso": "आमतौर पर इसके साथ ये भी दिखते हैं: {list}",
    "res.tests": "🧪 डॉक्टर जो जाँच करा सकते हैं",
    "res.testsNote": "जाँच डॉक्टर आपकी समय-सीमा के अनुसार लिखते हैं — अनुमान पर उपचार शुरू न करें.",
    "res.who": "👩‍⚕️ हैदराबाद में किससे मिलें",
    "res.input": "📋 आपकी जानकारी",
    "res.inputNote": "केवल यह परिणाम निकालने के लिए उपयोग हुआ. कुछ भी संग्रहीत या साझा नहीं हुआ.",
    "res.source": "📚 इस मार्गदर्शन का स्रोत",
    "res.findCare": "🏥 इसके लिए देखभाल खोजें",
    "res.ask": "💬 सुश्रुत से पूछें",
    "res.insufficient": "⚠️ आपने दो से कम लक्षण चुने हैं, इसलिए ऊपर की सलाह जानबूझकर सतर्क है. बेहतर मिलान के लिए और लक्षण तथा कितने दिनों से है, जोड़ें.",
    "res.ambiguity": "🔀 आपके लक्षणों से दो बीमारियाँ लगभग बराबर मेल खाती हैं. यह सामान्य है — कई बीमारियों के शुरुआती लक्षण एक जैसे होते हैं. फ़र्क़ बताने के लिए डॉक्टर को जाँच करनी पड़ सकती है.",
    "res.riskFactors": "ध्यान में रखे गए जोखिम कारक: {list}",
}

# ---------------------------------------------------------------------------
# Daily Health Activity section (translated on the client from API labels)
# ---------------------------------------------------------------------------
ACTIVITY_KEYS = [
    "act.eyebrow", "act.title", "act.intro", "act.complete", "act.skip", "act.weekTitle",
]

LANGUAGES: Dict[str, Dict[str, str]] = {"en": EN, "te": TE, "hi": HI}


def is_supported(lang) -> bool:
    """True when ``lang`` is one of the three supported language codes."""
    return str(lang) in SUPPORTED


def normalise(lang) -> str:
    """Return a supported language code (falls back to English)."""
    code = str(lang or "").lower()
    if code not in SUPPORTED:
        # Accept region-tagged values such as te-IN / hi-IN that browsers may send.
        base = code.split("-")[0].split("_")[0]
        code = base if base in SUPPORTED else DEFAULT_LANG
    return code


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Translate ``key`` into ``lang``.

    Falls back to English, then to the key itself, so a missing string can never
    break the interface (it becomes visibly obvious instead of blank).
    """
    code = normalise(lang)
    table = LANGUAGES.get(code, EN)
    value = table.get(key)
    if value:
        return value
    return EN.get(key, key)


def table(lang: str = DEFAULT_LANG) -> Dict[str, str]:
    """Full translation table for ``lang`` (English keys are always present)."""
    code = normalise(lang)
    if code == DEFAULT_LANG:
        return dict(EN)
    merged = dict(EN)
    merged.update(LANGUAGES.get(code, {}))
    return merged


def payload() -> Dict[str, object]:
    """Everything the browser needs to switch languages without another request."""
    return {
        "default": DEFAULT_LANG,
        "languages": [{"code": c, "name": LANG_NAMES[c]} for c in SUPPORTED],
        "tables": {code: table(code) for code in SUPPORTED},
    }
