#!/usr/bin/env python3
"""
PromptProbe — Suite Runner
Runs all JSON attacks in ./attacks against a selected adapter and emits:
 - JSON log (full)
 - HTML report (summary)
 - JUnit XML (for CI gates)

Usage:
  python harness/run_suite.py --adapter echo --out ./reports
  OPENAI_API_KEY=... python harness/run_suite.py --adapter openai_http --model gpt-4o-mini
  OLLAMA_BASE=http://127.0.0.1:11434 python harness/run_suite.py --adapter ollama_local --model qwen2.5:14b

Exit codes:
  0: all tests passed
  1: one or more attacks succeeded (i.e., vulnerability present)
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from dateutil import tz
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Local imports
from harness.scorer import evaluate_attack
from harness.reporters.junit import write_junit
from harness.reporters.html import write_html
from adapters.base import load_adapter

ROOT = Path(__file__).resolve().parents[1]
ATTACKS_DIR = ROOT / "attacks"
DEFAULT_OUT = ROOT / "reports"

console = Console()

class Attack(BaseModel):
    id: str
    title: str
    category: str = Field(description="e.g., LLM01: Prompt Injection, RAG-Abuse")
    severity: str = Field(pattern="^(low|medium|high|critical)$")
    prompt: str
    system: Optional[str] = None
    expect_fail_if: List[str] = Field(default_factory=list, description="Substrings that indicate a failure (vuln triggered)")
    expect_fail_regex: List[str] = Field(default_factory=list, description="Regex patterns that indicate failure")
    expect_pass_if: List[str] = Field(default_factory=list, description="Substrings that indicate resistance")
    notes: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class AttackResult(BaseModel):
    attack_id: str
    ok: bool
    score: int
    reasons: List[str] = Field(default_factory=list)
    response_preview: str
    adapter_meta: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: int

def load_attacks(dirpath: Path) -> List[Attack]:
    items: List[Attack] = []
    for p in sorted(dirpath.glob("*.json")):
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            data = [data]
        for obj in data:
            try:
                items.append(Attack(**obj))
            except ValidationError as ve:
                raise SystemExit(f"[ATTACKS] Validation error in {p.name}: {ve}")
    if not items:
        raise SystemExit("[ATTACKS] No attacks found.")
    return items

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone(tz.gettz("Asia/Kolkata")).isoformat()

def ensure_outdir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def truncate(s: str, n: int = 600) -> str:
    s = s.replace("\r", " ").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, choices=["echo", "openai_http", "ollama_local"])
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL") or os.getenv("OLLAMA_MODEL") or "unset")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--attacks", type=Path, default=ATTACKS_DIR)
    ap.add_argument("--rate-limit", type=float, default=0.0, help="Seconds to sleep between requests")
    ap.add_argument("--max", type=int, default=0, help="If >0, cap number of attacks for quick runs")
    args = ap.parse_args()

    console.rule("[bold]PromptProbe Suite")
    console.print(f"Adapter: [bold]{args.adapter}[/] | Model: [bold]{args.model}[/] | Attacks: {args.attacks}")

    attacks = load_attacks(args.attacks)
    if args.max > 0:
        attacks = attacks[: args.max]

    adapter = load_adapter(args.adapter, model=args.model)
    outdir = ensure_outdir(args.out)

    results: List[AttackResult] = []
    failures = 0

    table = Table(title="PromptProbe — Execution")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", overflow="fold")
    table.add_column("OK", style="bold")
    table.add_column("Score")
    table.add_column("Latency")

    for atk in attacks:
        # Build message
        system_msg = atk.system or "You are a helpful assistant. Follow internal policies strictly."
        user_msg = atk.prompt

        t0 = time.perf_counter()
        resp, meta = adapter.generate(user=user_msg, system=system_msg)
        dt_ms = int((time.perf_counter() - t0) * 1000)

        ok, score, reasons = evaluate_attack(
            response=resp,
            expect_fail_if=atk.expect_fail_if,
            expect_fail_regex=atk.expect_fail_regex,
            expect_pass_if=atk.expect_pass_if,
        )
        if not ok:
            failures += 1

        results.append(
            AttackResult(
                attack_id=atk.id,
                ok=ok,
                score=score,
                reasons=reasons,
                response_preview=truncate(resp),
                adapter_meta=meta,
                latency_ms=dt_ms,
            )
        )

        table.add_row(atk.id, atk.title, "PASS" if ok else "[red]FAIL[/red]", str(score), f"{dt_ms} ms")
        if args.rate_limit > 0:
            time.sleep(args.rate_limit)

    console.print(table)

    # Artifacts
    run_id = uuid.uuid4().hex[:8]
    stamp = now_iso()
    json_log = {
        "run_id": run_id,
        "timestamp": stamp,
        "adapter": args.adapter,
        "model": args.model,
        "results": [r.model_dump() for r in results],
    }
    (outdir / "last_run.json").write_text(json.dumps(json_log, indent=2), encoding="utf-8")

    write_html(outdir / "report.html", attacks, results, adapter_name=args.adapter, model=args.model, run_id=run_id, timestamp=stamp)
    write_junit(outdir / "junit.xml", attacks, results, suite_name=f"PromptProbe-{args.adapter}-{args.model}")

    console.print(Panel.fit(f"[bold]{'OK' if failures == 0 else 'FAIL'}[/] — {len(results)} attacks, {failures} failures • Reports: {outdir}"))
    sys.exit(0 if failures == 0 else 1)

if __name__ == "__main__":
    main()
