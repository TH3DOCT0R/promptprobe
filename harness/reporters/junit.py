from pathlib import Path
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def write_junit(path: Path, attacks, results, suite_name: str = "PromptProbe"):
    ts = Element("testsuite", name=suite_name, tests=str(len(results)), failures=str(sum(0 if r.ok else 1 for r in results)))
    for a, r in zip(attacks, results):
        tc = SubElement(ts, "testcase", classname=a.category, name=f"{a.id} {a.title}")
        if not r.ok:
            fail = SubElement(tc, "failure", message="PromptProbe failure")
            fail.text = "\n".join(r.reasons) + f"\n\nResponse: {r.response_preview}"
        sysout = SubElement(tc, "system-out")
        sysout.text = f"score={r.score} latency_ms={r.latency_ms}"
    pretty = minidom.parseString(tostring(ts)).toprettyxml(indent="  ")
    path.write_text(pretty, encoding="utf-8")
