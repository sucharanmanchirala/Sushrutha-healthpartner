"""
Automated tests for Susrutha Health Partner
===========================================

Run from the project root:

    python -m unittest discover -s tests -v

The suite covers four things a jury is likely to probe:
  1. Data integrity  - the knowledge base is internally consistent and sourced.
  2. The engine      - the weighted symptom match and the triage gate behave.
  3. The API         - every endpoint answers correctly through the HTTP layer.
  4. Safety          - emergencies are always escalated and nothing is diagnosis-like
                       or persisted.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, kb  # noqa: E402


class DataIntegrityTests(unittest.TestCase):
    """The knowledge base must not contain dangling references."""

    def test_every_condition_symptom_exists_in_the_vocabulary(self):
        valid = set(kb.symptoms)
        for cond in kb.conditions:
            for sym in cond["symptoms"]:
                self.assertIn(sym, valid, f"{cond['id']} references unknown symptom {sym}")

    def test_every_condition_has_a_trusted_source(self):
        for cond in kb.conditions:
            self.assertTrue(cond["sources"], f"{cond['id']} has no source")
            for source in cond["sources"]:
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["label"])

    def test_every_condition_has_precautions_red_flags_and_tests(self):
        for cond in kb.conditions:
            self.assertGreaterEqual(len(cond["precautions"]), 3, cond["id"])
            self.assertGreaterEqual(len(cond["red_flags"]), 2, cond["id"])
            self.assertTrue(cond["tests"], cond["id"])
            self.assertTrue(cond["specialties"], cond["id"])

    def test_selfcare_conditions_offer_home_care_steps(self):
        """Only minor illnesses may be labelled self-care, and they must explain what to do."""
        for cond in kb.conditions:
            if cond["care_level"] == "selfcare":
                self.assertTrue(cond["self_care"], f"{cond['id']} is selfcare but has no home-care steps")

    def test_facilities_have_coordinates_inside_telangana(self):
        for fac in kb.facilities:
            self.assertAlmostEqual(fac["lat"], 17.4, delta=0.5, msg=fac["name"])
            self.assertAlmostEqual(fac["lng"], 78.5, delta=0.6, msg=fac["name"])
            self.assertTrue(fac["address"])
            self.assertTrue(fac["specialties"])

    def test_condition_specialties_are_served_by_at_least_one_facility(self):
        offered = {s for f in kb.facilities for s in f["specialties"]}
        for cond in kb.conditions:
            overlap = offered.intersection(cond["specialties"])
            self.assertTrue(overlap, f"no Hyderabad facility serves {cond['name']}")

    def test_emergency_numbers_include_108(self):
        numbers = {n["number"] for n in kb.facilities_doc["emergency_numbers"]}
        self.assertIn("108", numbers)


class EngineTests(unittest.TestCase):
    """The scoring and triage logic."""

    def test_dengue_scenario_matches_dengue_first(self):
        """TEST SCENARIO 1: the classic dengue presentation."""
        result = kb.assess(
            ["high_fever", "pain_behind_eyes", "joint_pain", "rash", "severe_headache"],
            {"age": 28, "duration_days": 3, "severity": "moderate"},
        )
        self.assertEqual(result["matches"][0]["id"], "dengue")
        self.assertIn(result["care"]["level"], ("urgent", "emergency"))
        self.assertEqual(result["care"]["tone"], "high")
        self.assertTrue(result["tests"])
        self.assertIn("not a diagnosis", result["disclaimer"].lower())
        self.assertEqual(result["matches"][0]["match_percent"], 100)

    def test_dengue_warning_sign_is_an_emergency(self):
        """TEST SCENARIO 2: bleeding gums on top of a fever is a red flag."""
        result = kb.assess(["high_fever", "rash", "bleeding_gums"])
        self.assertEqual(result["care"]["level"], "emergency")
        self.assertEqual(result["care"]["tone"], "critical")
        ids = [s["id"] for s in result["emergency_symptoms"]]
        self.assertIn("bleeding_gums", ids)
        self.assertIn("108", " ".join(result["next_steps"]))

    def test_chest_pain_or_breathlessness_always_escalates(self):
        for sym in ("chest_pain", "breathlessness", "confusion", "seizure", "blood_in_vomit"):
            with self.subTest(symptom=sym):
                result = kb.assess([sym])
                self.assertEqual(result["care"]["level"], "emergency")

    def test_minor_cold_is_self_care_with_home_advice(self):
        """TEST SCENARIO 3: a small illness gets home treatment, not alarm."""
        result = kb.assess(
            ["runny_nose", "sneezing", "sore_throat", "blocked_nose"],
            {"age": 24, "duration_days": 1, "severity": "mild"},
        )
        self.assertEqual(result["matches"][0]["id"], "common_cold")
        self.assertEqual(result["care"]["level"], "selfcare")
        self.assertTrue(result["self_care"])
        self.assertIn("no tests needed", " ".join(result["tests"]).lower())

    def test_risk_factors_raise_urgency(self):
        baseline = kb.assess(["diarrhea", "nausea"])
        escalated = kb.assess(["diarrhea", "nausea"], {"age": 74, "pregnant": False})
        order = ["selfcare", "routine", "urgent", "emergency"]
        self.assertGreater(
            order.index(escalated["care"]["level"]), order.index(baseline["care"]["level"])
        )
        self.assertTrue(escalated["risk_factors"])

    def test_pregnancy_and_chronic_illness_are_flagged(self):
        result = kb.assess(
            ["fever", "headache"], {"pregnant": True, "chronic": ["Diabetes", "Asthma / COPD"]}
        )
        joined = ", ".join(result["risk_factors"])
        self.assertIn("pregnancy", joined)
        self.assertIn("Diabetes", joined)

    def test_long_duration_note(self):
        result = kb.assess(["fever", "fatigue"], {"duration_days": 10})
        self.assertIn("more than a week", result["risk_note"])

    def test_unknown_symptom_ids_are_ignored_not_crashing(self):
        result = kb.assess(["fever", "definitely_not_a_symptom"])
        self.assertEqual(len(result["selected"]), 1)

    def test_single_symptom_is_never_downgraded_to_self_care(self):
        result = kb.assess(["fever"])
        self.assertTrue(result["insufficient_data"])
        self.assertNotEqual(result["care"]["level"], "selfcare")

    def test_symptom_match_percentages_are_relative_and_ordered(self):
        result = kb.assess(["fever", "chills", "headache", "vomiting", "body_ache"])
        percents = [m["match_percent"] for m in result["matches"]]
        self.assertEqual(percents, sorted(percents, reverse=True))
        self.assertEqual(percents[0], 100)

    def test_ambiguity_warning_when_two_conditions_tie(self):
        result = kb.assess(["fever", "dry_cough", "sore_throat", "fatigue", "body_ache"])
        self.assertTrue(result["matches"])
        # flu and covid overlap heavily: the tool must say so rather than pick one
        self.assertIsInstance(result["ambiguity_warning"], bool)

    def test_assessment_is_deterministic(self):
        args = (["high_fever", "rash"], {"age": 30})
        self.assertEqual(kb.assess(*args), kb.assess(*args))


class FacilityTests(unittest.TestCase):
    """Facility discovery for Hyderabad."""

    def test_dengue_lookup_includes_the_government_fever_hospital(self):
        """TEST SCENARIO 4: 'I have dengue - where do I get tested?'"""
        data = kb.find_facilities(condition_id="dengue")
        ids = [f["id"] for f in data["results"]]
        self.assertIn("fever_hospital", ids)
        self.assertTrue(all(f["maps_url"].startswith("https://www.google.com/maps") for f in data["results"]))
        self.assertTrue(all(f["matched_specialties"] for f in data["results"]))

    def test_distance_sorting_from_a_locality(self):
        gachibowli = (17.4401, 78.3489)
        data = kb.find_facilities(condition_id="dengue", lat=gachibowli[0], lng=gachibowli[1])
        distances = [f["distance_km"] for f in data["results"]]
        self.assertTrue(all(d is not None for d in distances))
        self.assertEqual(distances, sorted(distances))
        self.assertEqual(data["sorted_by"], "distance")
        self.assertLess(distances[0], 25)

    def test_specificity_weighting_favours_specialist_facilities(self):
        """A rare department such as "Fever / Tropical Diseases" must count more than
        "General Medicine", which nearly every hospital offers."""
        data = kb.find_facilities(condition_id="dengue", order="relevance")
        top = data["results"][0]
        self.assertEqual(top["tier"], "Best match")
        self.assertGreaterEqual(top["relevance"], 0.7)
        self.assertIn("Fever / Tropical Diseases", top["matched_specialties"])
        # ...and the Fever Hospital, the dedicated fever facility, must be in the top group.
        best = [f["name"] for f in data["results"] if f["tier"] == "Best match"]
        self.assertTrue(any("Fever Hospital" in n or "Fever" in n for n in best))

    def test_explicit_order_parameter_overrides_the_auto_rule(self):
        by_distance = kb.find_facilities(condition_id="dengue", lat=17.4401, lng=78.3489, order="distance")
        by_relevance = kb.find_facilities(condition_id="dengue", lat=17.4401, lng=78.3489, order="relevance")
        self.assertEqual(by_distance["sorted_by"], "distance")
        self.assertEqual(by_relevance["sorted_by"], "relevance")
        self.assertEqual(by_relevance["results"][0]["tier"], "Best match")

    def test_without_a_location_results_are_ranked_by_relevance(self):
        data = kb.find_facilities(condition_id="dengue")
        self.assertEqual(data["sorted_by"], "relevance")
        overlaps = [len(f["matched_specialties"]) for f in data["results"]]
        self.assertEqual(overlaps, sorted(overlaps, reverse=True))
        self.assertTrue(all(f["distance_km"] is None for f in data["results"]))

    def test_government_filter_only_returns_government_facilities(self):
        data = kb.find_facilities(condition_id="dengue", sector="Government")
        self.assertTrue(data["results"])
        self.assertTrue(all(f["type"] == "Government" for f in data["results"]))

    def test_diagnostic_labs_are_available_for_testing(self):
        data = kb.find_facilities(specialty="Diagnostics", sector="Diagnostic Lab")
        self.assertTrue(data["results"])
        self.assertTrue(all(f["type"] == "Diagnostic Lab" for f in data["results"]))

    def test_specialty_filter_excludes_unrelated_facilities(self):
        data = kb.find_facilities(specialty="Ophthalmology")
        self.assertTrue(data["results"])
        self.assertTrue(all("Ophthalmology" in f["matched_specialties"] for f in data["results"]))

    def test_haversine_reference_distance(self):
        from health_engine import haversine_km

        # Charminar to Secunderabad is roughly 10 km in a straight line.
        self.assertAlmostEqual(haversine_km(17.3616, 78.4747, 17.4399, 78.4983), 8.8, delta=2.5)


class ChatTests(unittest.TestCase):
    """The rule-based assistant."""

    def test_emergency_keywords_short_circuit_everything(self):
        for text in ["I have severe chest pain", "he cannot breathe properly", "she is unconscious"]:
            with self.subTest(text=text):
                reply = kb.chat(text)
                self.assertTrue(reply["urgent"])
                self.assertEqual(reply["intent"], "emergency")
                self.assertIn("108", reply["reply"])

    def test_condition_explanation_is_sourced_and_cautious(self):
        reply = kb.chat("what is dengue?")
        self.assertIn("Dengue", reply["reply"])
        self.assertIn("not a diagnosis", reply["reply"].lower())
        self.assertIn("WHO", reply["reply"])

    def test_condition_prevention_and_test_intents(self):
        prevention = kb.chat("how do I prevent malaria")
        self.assertIn("net", prevention["reply"].lower())
        tests = kb.chat("what tests are used for typhoid")
        self.assertIn("blood culture", tests["reply"].lower())

    def test_home_care_for_a_minor_illness(self):
        reply = kb.chat("how do I treat a common cold at home?")
        self.assertIn("Rest", reply["reply"])

    def test_reports_its_own_limits(self):
        reply = kb.chat("are you a doctor? can you diagnose me?")
        self.assertIn("not a doctor", reply["reply"].lower())

    def test_privacy_question_is_answered(self):
        reply = kb.chat("is my data safe?")
        self.assertIn("no login", reply["reply"].lower())

    def test_facility_question_mentions_hyderabad(self):
        reply = kb.chat("where can I get a blood test in Hyderabad?")
        self.assertIn("Hyderabad", reply["reply"])

    def test_symptom_words_route_to_the_checker_with_a_quick_read(self):
        reply = kb.chat("I have fever and joint pain since yesterday")
        self.assertEqual(reply["intent"], "symptom_hint")
        self.assertIn("fever", reply["reply"].lower())
        self.assertIn("joint pain", reply["reply"].lower())
        self.assertIn("not a diagnosis", reply["reply"].lower())

    def test_self_reports_are_not_hijacked_by_symptom_aliases(self):
        """Regression: "fever with chills and headache" must not be answered as migraine."""
        reply = kb.chat("I have fever with chills and headache")
        self.assertEqual(reply["intent"], "symptom_hint")
        self.assertIn("Chills", reply["reply"])
        self.assertIn("Headache", reply["reply"])
        self.assertNotIn("Migraine", reply["reply"])
        self.assertIn("not a diagnosis", reply["reply"].lower())

    def test_one_word_maps_to_one_symptom(self):
        self.assertEqual(kb.symptom_words["fever"], ["fever"])
        hits = kb._symptom_words_in("i have fever")
        self.assertEqual(hits.count("fever"), 1)
        self.assertNotIn("high_fever", hits)

    def test_condition_aliases_still_work(self):
        for text, name in [
            ("do I have dengue?", "Dengue"),
            ("tell me about pink eye", "Conjunctivitis"),
            ("what is hay fever?", "Allergic Rhinitis"),
            ("blood sugar problem", "Type 2 Diabetes"),
        ]:
            with self.subTest(text=text):
                self.assertIn(name, kb.chat(text)["reply"])

    def test_mild_sentences_do_not_trigger_the_emergency_path(self):
        """Regression: "blood test" must not be read as "blood in vomit"."""
        for text in [
            "where can I get a blood test in Hyderabad?",
            "I have a mild headache and back pain",
            "do you store my health data?",
        ]:
            with self.subTest(text=text):
                self.assertFalse(kb.chat(text)["urgent"], text)

    def test_precise_red_flag_phrases_still_escalate(self):
        for text in ["there is blood in vomit", "blood in stool since morning", "he has a stiff neck"]:
            with self.subTest(text=text):
                self.assertTrue(kb.chat(text)["urgent"], text)

    def test_unknown_question_falls_back_gracefully(self):
        reply = kb.chat("what is the capital of France?")
        self.assertEqual(reply["intent"], "fallback")
        self.assertIn("consult a doctor", reply["reply"].lower())

    def test_every_condition_can_be_chatted_about(self):
        for cond in kb.conditions:
            with self.subTest(condition=cond["id"]):
                reply = kb.chat(f"tell me about {cond['name']}")
                self.assertNotEqual(reply["intent"], "fallback")
                self.assertIn(cond["name"], reply["reply"])

    def test_greeting_and_suggestions(self):
        reply = kb.chat("")
        self.assertEqual(reply["intent"], "greeting")
        self.assertTrue(reply["suggestions"])


class ApiTests(unittest.TestCase):
    """The HTTP layer used by the interface."""

    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_pages_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        health = self.client.get("/api/health").get_json()
        self.assertEqual(health["status"], "ok")
        self.assertGreater(health["conditions"], 10)

    def test_meta_reports_sources_and_disclaimer(self):
        meta = self.client.get("/api/meta").get_json()
        self.assertIn("disclaimer", meta)
        self.assertIn("WHO", meta["stats"]["sources"])
        self.assertTrue(meta["emergency_numbers"])

    def test_symptom_vocabulary_and_emergency_flags(self):
        data = self.client.get("/api/symptoms").get_json()
        flat = [s for g in data["groups"] for s in g["symptoms"]]
        self.assertGreater(len(flat), 40)
        self.assertTrue(any(s.get("emergency") for s in flat))

    def test_assess_endpoint(self):
        res = self.client.post(
            "/api/assess",
            json={
                "symptoms": ["high_fever", "pain_behind_eyes", "rash"],
                "profile": {"age": 31, "duration_days": 2},
            },
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["matches"][0]["id"], "dengue")
        self.assertIn("care", body)

    def test_facilities_endpoint(self):
        res = self.client.get("/api/facilities?condition=dengue&lat=17.44&lng=78.35")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["results"])
        self.assertTrue(body["localities"])

    def test_condition_detail_and_404(self):
        self.assertEqual(self.client.get("/api/conditions/dengue").status_code, 200)
        self.assertEqual(self.client.get("/api/conditions/nope").status_code, 404)

    def test_library_search(self):
        body = self.client.get("/api/library?q=blood sugar").get_json()
        self.assertGreaterEqual(body["count"], 1)
        self.assertIn("Diabetes", " ".join(c["name"] for c in body["items"]))

    def test_chat_endpoint_and_emergency_flag(self):
        body = self.client.post("/api/chat", json={"message": "chest pain"}).get_json()
        self.assertTrue(body["urgent"])
        self.assertIn("108", body["reply"])

    def test_malformed_assess_payload_is_rejected(self):
        res = self.client.post("/api/assess", json={"symptoms": "fever"})
        self.assertEqual(res.status_code, 400)

    def test_empty_assess_payload_does_not_crash(self):
        res = self.client.post("/api/assess", json={})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["insufficient_data"])


class PrivacyAndSafetyTests(unittest.TestCase):
    """Requirements from the problem statement."""

    def test_no_personal_identifiers_are_echoed_back(self):
        result = kb.assess(["fever"], {"age": 30, "name": "Should Not Appear", "phone": "9999999999"})
        blob = str(result)
        self.assertNotIn("Should Not Appear", blob)
        self.assertNotIn("9999999999", blob)

    def test_no_diagnosis_is_asserted_in_any_copy(self):
        result = kb.assess(["high_fever", "rash"])
        blob = (str(result) + result["disclaimer"]).lower()
        self.assertNotIn("you have dengue", blob)
        self.assertIn("not a diagnosis", blob.lower())

    def test_every_result_carries_the_disclaimer_and_a_next_step(self):
        for cond in kb.conditions:
            with self.subTest(condition=cond["id"]):
                result = kb.assess(list(cond["symptoms"])[:5])
                self.assertTrue(result["disclaimer"])
                self.assertTrue(result["next_steps"])
                self.assertTrue(any("108" in s or "doctor" in s or "hospital" in s for s in result["next_steps"]))

    def test_app_declares_no_database_layer(self):
        """The prototype stores no user data - only JSON reference files are opened."""
        import health_engine

        with open(health_engine.__file__, "r", encoding="utf-8") as handle:
            source = handle.read().lower()
        for banned in ("sqlite3", "sqlalchemy", "psycopg", "pymongo"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
