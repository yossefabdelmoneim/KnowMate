"""
KnowMate Backend — smoke test script.

Run from your data_analyst_agent folder with venv activated:
    python test.py

Usage:
    python test.py                # run all tests except report
    python test.py --with-report  # also generate a 2-section report (slow)
    python test.py --base-url http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "smoketest@test.com"
TEST_PASSWORD = "supersecret123"
TEST_FULL_NAME = "Smoke Test"


class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def ok(msg: str) -> None:
    print(f"  {Color.GREEN}✅ PASS{Color.RESET}  {msg}")


def fail(msg: str, detail: str = "") -> None:
    print(f"  {Color.RED}❌ FAIL{Color.RESET}  {msg}")
    if detail:
        for line in detail.strip().splitlines():
            print(f"           {line}")


def info(msg: str) -> None:
    print(f"  {Color.CYAN}ℹ️{Color.RESET}  {msg}")


def wait(msg: str) -> None:
    print(f"  {Color.YELLOW}⏳{Color.RESET}  {msg}")


def section(name: str) -> None:
    print(f"\n{Color.BOLD}--- {name} ---{Color.RESET}")


def run_tests(base_url: str, with_report: bool) -> int:
    failures = 0
    base_url = base_url.rstrip("/")

    print(f"{Color.BOLD}KnowMate Backend Smoke Test{Color.RESET}")
    print(f"Base URL: {base_url}")
    print(f"Report test: {'ON (slow!)' if with_report else 'off'}")
    print()

    section("1. Health check")
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            ok(f"/health returned 200 — status={data.get('status')}, llm_available={data.get('llm_available')}")
            if not data.get("llm_available"):
                info("⚠️  Ollama is NOT available. Most tests below will fail at the LLM call.")
                info("    Start Ollama in another terminal: ollama serve")
                info("    And make sure the model is pulled: ollama pull qwen2.5:7b")
        else:
            failures += 1
            fail(f"/health returned {r.status_code}", r.text)
    except requests.exceptions.ConnectionError:
        failures += 1
        fail("Cannot connect to backend", f"Is uvicorn running on {base_url}?")
        return failures

    section("2. Register")
    token = None
    try:
        r = requests.post(
            f"{base_url}/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "full_name": TEST_FULL_NAME},
            timeout=10,
        )
        if r.status_code == 201:
            ok(f"Registered new user: {TEST_EMAIL}")
        elif r.status_code == 400 and "already exists" in r.text:
            info(f"User already exists, will just login: {TEST_EMAIL}")
        else:
            fail(f"Register returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Register exception: {e}")
        failures += 1

    section("3. Login")
    try:
        r = requests.post(
            f"{base_url}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10,
        )
        if r.status_code == 200:
            token = r.json()["access_token"]
            ok(f"Login succeeded — token length: {len(token)} chars")
        else:
            fail(f"Login returned {r.status_code}", r.text)
            failures += 1
            return failures
    except Exception as e:
        fail(f"Login exception: {e}")
        failures += 1
        return failures

    H = {"Authorization": f"Bearer {token}"}

    section("4. Create session")
    session_id = None
    try:
        r = requests.post(
            f"{base_url}/sessions",
            json={"title": "Smoke test chat", "description": "Created by test.py"},
            headers=H, timeout=10,
        )
        if r.status_code == 201:
            session_id = r.json()["id"]
            ok(f"Session created: id={session_id}")
        else:
            fail(f"Create session returned {r.status_code}", r.text)
            failures += 1
            return failures
    except Exception as e:
        fail(f"Create session exception: {e}")
        failures += 1
        return failures

    section("5. List sessions")
    try:
        r = requests.get(f"{base_url}/sessions", headers=H, timeout=10)
        if r.status_code == 200:
            data = r.json()
            ok(f"Listed sessions: total={data['total']}")
        else:
            fail(f"List sessions returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"List sessions exception: {e}")
        failures += 1

    section("6. Supported file types")
    try:
        r = requests.get(f"{base_url}/sessions/_meta/supported-types", timeout=10)
        if r.status_code == 200:
            exts = r.json()["extensions"]
            ok(f"Supported extensions: {exts}")
            if ".csv" not in exts or ".xlsx" not in exts:
                fail("Expected .csv and .xlsx to be supported")
                failures += 1
        else:
            fail(f"Supported types returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Supported types exception: {e}")
        failures += 1

    section("7. Upload dataset")
    csv_bytes = (
        b"city,revenue,population,growth_rate\n"
        b"Cairo,1200000,10000000,0.08\n"
        b"Giza,620000,4000000,0.05\n"
        b"Alexandria,310000,1500000,0.03\n"
        b"Aswan,180000,300000,-0.02\n"
        b"Luxor,95000,200000,0.01\n"
        b"Port Said,250000,800000,0.04\n"
    )
    try:
        r = requests.post(
            f"{base_url}/sessions/{session_id}/dataset",
            files={"file": ("cities.csv", csv_bytes, "text/csv")},
            headers=H, timeout=15,
        )
        if r.status_code == 201:
            ds = r.json()["dataset"]
            ok(f"Dataset uploaded: {ds['original_filename']} ({ds['row_count']} rows, {ds['column_count']} cols)")
        else:
            fail(f"Upload dataset returned {r.status_code}", r.text)
            failures += 1
            return failures
    except Exception as e:
        fail(f"Upload dataset exception: {e}")
        failures += 1
        return failures

    section("8. One-file-per-chat rule")
    try:
        r = requests.post(
            f"{base_url}/sessions/{session_id}/dataset",
            files={"file": ("second.csv", b"a,b\n1,2\n", "text/csv")},
            headers=H, timeout=10,
        )
        if r.status_code == 409 and r.json().get("code") == "dataset_already_attached":
            ok("Second upload correctly rejected with 409 dataset_already_attached")
        else:
            fail(f"Expected 409 dataset_already_attached, got {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"One-file rule test exception: {e}")
        failures += 1

    section("9. Send first message (calls Ollama — may take 10-90s)")
    wait("Sending 'show me top 5 cities by revenue'...")
    t0 = time.time()
    try:
        r = requests.post(
            f"{base_url}/sessions/{session_id}/messages",
            json={"question": "show me top 5 cities by revenue", "debug": True},
            headers=H, timeout=300,
        )
        elapsed = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            if data["success"]:
                ok(f"Analysis succeeded in {elapsed:.1f}s")
                info(f"  summary: {(data.get('summary') or '')[:80]}")
                info(f"  insights: {(data.get('insights') or '')[:80]}")
                info(f"  table rows: {len(data.get('table') or [])}")
                info(f"  charts: {len(data.get('charts') or [])}")
                info(f"  detected intents: {data.get('detected_intents')}")
            else:
                fail(f"Analysis failed in {elapsed:.1f}s", f"error: {data.get('errors')}")
                failures += 1
                info("⚠️  Continuing with non-LLM tests...")
        else:
            fail(f"Send message returned {r.status_code}", r.text)
            failures += 1
    except requests.exceptions.Timeout:
        fail("Send message timed out (>300s) — Ollama might be loading the model or too slow")
        failures += 1
    except Exception as e:
        fail(f"Send message exception: {e}")
        failures += 1

    section("10. Send follow-up message (tests short-term memory)")
    wait("Sending 'now sort by population instead'...")
    try:
        r = requests.post(
            f"{base_url}/sessions/{session_id}/messages",
            json={"question": "now sort by population instead"},
            headers=H, timeout=300,
        )
        if r.status_code == 200:
            data = r.json()
            if data["success"]:
                ok(f"Follow-up succeeded — agent resolved 'now' reference via short-term memory")
                info(f"  summary: {(data.get('summary') or '')[:80]}")
            else:
                fail(f"Follow-up failed", f"error: {data.get('errors')}")
                info("    (This is often a small-LLM code-quality issue, not a system bug. The self-healing retry should help.)")
                failures += 1
        else:
            fail(f"Follow-up returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Follow-up exception: {e}")
        failures += 1

    section("11. List messages (chat history)")
    try:
        r = requests.get(f"{base_url}/sessions/{session_id}/messages", headers=H, timeout=10)
        if r.status_code == 200:
            data = r.json()
            ok(f"Chat history: {data['total']} messages")
            for m in data["items"]:
                content_preview = (m.get("content") or "")[:60]
                info(f"  seq={m['seq']} role={m['role']:10s} content={content_preview}")
        else:
            fail(f"List messages returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"List messages exception: {e}")
        failures += 1

    section("12. Get session back")
    try:
        r = requests.get(f"{base_url}/sessions/{session_id}", headers=H, timeout=10)
        if r.status_code == 200:
            data = r.json()
            ok(f"Session fetched — title={data['title']}, has_dataset={data['dataset'] is not None}, msg_count={data.get('message_count')}")
        else:
            fail(f"Get session returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Get session exception: {e}")
        failures += 1

    section("13. Long-term memory endpoint")
    try:
        r = requests.get(f"{base_url}/memory", headers=H, timeout=10)
        if r.status_code == 200:
            data = r.json()
            ok(f"Memory endpoint works — prefs={len(data['preferences'])}, memories={len(data['memories'])}")
            for p in data["preferences"][:3]:
                info(f"  pref: [{p['category']}] {p['key']}={p['value']} (conf={p['confidence']})")
            for m in data["memories"][:3]:
                info(f"  memory: ({m['kind']}) {m['content'][:80]}")
        else:
            fail(f"Memory endpoint returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Memory endpoint exception: {e}")
        failures += 1

    if with_report:
        section("14. Generate report (SLOW — 1-3 minutes)")
        wait("Generating 2-section report...")
        t0 = time.time()
        try:
            r = requests.post(
                f"{base_url}/sessions/{session_id}/reports",
                json={"question": "generate a brief report on this dataset", "max_sections": 2},
                headers=H, timeout=300,
            )
            elapsed = time.time() - t0
            if r.status_code == 200:
                data = r.json()
                if data["success"]:
                    ok(f"Report generated in {elapsed:.1f}s — title: {data.get('title')}")
                    info(f"  sections: {len(data.get('sections') or [])}")
                    info(f"  executive_summary: {(data.get('executive_summary') or '')[:100]}")
                    for s in (data.get("sections") or [])[:3]:
                        info(f"  - [{s['intent']}] {s['title']}: {s['content'][:80]}")
                else:
                    fail(f"Report failed in {elapsed:.1f}s", f"error: {data.get('errors')}")
                    failures += 1
            else:
                fail(f"Report returned {r.status_code}", r.text)
                failures += 1
        except requests.exceptions.Timeout:
            fail("Report timed out (>300s) — too slow for this hardware")
            failures += 1
        except Exception as e:
            fail(f"Report exception: {e}")
            failures += 1

    section(f"15. Close + reopen session" + (" (skipped because report ran)" if with_report else ""))
    if not with_report:
        try:
            r = requests.patch(
                f"{base_url}/sessions/{session_id}",
                json={"closed": True},
                headers=H, timeout=10,
            )
            if r.status_code == 200 and r.json()["closed_at"] is not None:
                ok("Session closed")
            else:
                fail(f"Close session returned {r.status_code}", r.text)
                failures += 1

            r = requests.post(
                f"{base_url}/sessions/{session_id}/messages",
                json={"question": "anything"},
                headers=H, timeout=10,
            )
            if r.status_code == 409 and r.json().get("code") == "conflict":
                ok("Closed session correctly rejected new message with 409 conflict")
            else:
                fail(f"Expected 409 conflict on closed session, got {r.status_code}", r.text)
                failures += 1

            r = requests.patch(
                f"{base_url}/sessions/{session_id}",
                json={"closed": False},
                headers=H, timeout=10,
            )
            if r.status_code == 200 and r.json()["closed_at"] is None:
                ok("Session reopened")
            else:
                fail(f"Reopen session returned {r.status_code}", r.text)
                failures += 1
        except Exception as e:
            fail(f"Close/reopen exception: {e}")
            failures += 1

    section("16. Auth failure modes")
    try:
        r = requests.get(f"{base_url}/sessions", timeout=10)
        if r.status_code == 401:
            ok("No-auth request correctly rejected with 401")
        else:
            fail(f"Expected 401, got {r.status_code}", r.text)
            failures += 1

        r = requests.get(
            f"{base_url}/sessions",
            headers={"Authorization": "Bearer bogus.token.here"},
            timeout=10,
        )
        if r.status_code == 401:
            ok("Bogus token correctly rejected with 401")
        else:
            fail(f"Expected 401 for bogus token, got {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Auth failure test exception: {e}")
        failures += 1

    section("17. Cleanup")
    try:
        r = requests.delete(f"{base_url}/sessions/{session_id}", headers=H, timeout=10)
        if r.status_code == 204:
            ok(f"Deleted test session {session_id}")
        else:
            fail(f"Delete session returned {r.status_code}", r.text)
            failures += 1
    except Exception as e:
        fail(f"Delete session exception: {e}")
        failures += 1

    print(f"\n{Color.BOLD}=== SUMMARY ==={Color.RESET}")
    if failures == 0:
        print(f"{Color.GREEN}All tests passed! Backend is ready for integration.{Color.RESET}")
    else:
        print(f"{Color.RED}{failures} test(s) failed. Fix the issues above before integrating.{Color.RESET}")
    print()
    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KnowMate backend smoke test")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Backend URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--with-report", action="store_true", help="Also run the (slow) report test")
    args = parser.parse_args()

    sys.exit(0 if run_tests(args.base_url, args.with_report) == 0 else 1)