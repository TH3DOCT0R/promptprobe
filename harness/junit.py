from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def to_junit(testname: str, results: list[dict]) -> str:
    """
    results: [{attack,id,metrics:{passed,leakage,tool_abuse,override}}]
    """
    suite = Element("testsuite", name=testname)
    for r in results:
        case = SubElement(suite, "testcase", name=r["attack"])
        if not r["metrics"]["passed"]:
            fail = SubElement(case, "failure", message="policy_violation")
            details = []
            for k in ("leakage","tool_abuse","override"):
                if r["metrics"].get(k): details.append(k)
            fail.text = " ; ".join(details) or "failed"
    xml_str = tostring(suite, encoding="utf-8")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")
