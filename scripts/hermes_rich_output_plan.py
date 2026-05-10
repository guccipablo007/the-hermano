#!/usr/bin/env python3
import argparse
import json

def contains_any(text, words):
    t = text.lower()
    return any(w.lower() in t for w in words)

def strip_negated_formats(text):
    t = text.lower()
    negations = [
        r"do not create\s+(a\s+)?docx", r"do not create\s+(a\s+)?word", r"not\s+(a\s+)?docx", r"not\s+(a\s+)?word",
        r"do not create\s+(a\s+)?pdf", r"not\s+(a\s+)?pdf",
        r"do not create\s+(a\s+)?pptx", r"do not create\s+(a\s+)?powerpoint", r"not\s+(a\s+)?pptx",
        r"do not create\s+(an?\s+)?html", r"not\s+(an?\s+)?html",
    ]
    import re
    for pat in negations:
        t = re.sub(pat, " ", t)
    return t

def detect_format(text):
    t = strip_negated_formats(text)
    if contains_any(t, ["powerpoint", "pptx", "ppt", "slide deck", "slides", "presentation"]): return "pptx"
    if contains_any(t, ["excel", "xlsx", "spreadsheet", "workbook", "attendance sheet", "payment tracker", "tracker sheet"]): return "xlsx"
    if contains_any(t, ["word document", "docx"]): return "docx"
    if contains_any(t, ["markdown", ".md"]): return "md"
    if contains_any(t, ["html", "webpage", "web page", "landing page", "frontpage", "front page"]): return "html"
    if contains_any(t, ["pdf", "printable"]): return "pdf"
    return "unknown"

def detect_content_type(text):
    t = text.lower()
    if contains_any(t, ["flashcard", "flashcards"]): return "flashcards"
    if contains_any(t, ["worksheet", "exercise sheet", "phonics", "cvc"]): return "worksheet"
    if contains_any(t, ["lesson", "kids", "children", "4-year", "5-year", "6-year", "kindergarten", "nursery"]): return "kids_lesson"
    if contains_any(t, ["dashboard", "kpi", "analytics", "metrics"]): return "dashboard"
    if contains_any(t, ["report", "summary", "analysis"]): return "report"
    if contains_any(t, ["invoice", "receipt", "expense"]): return "finance_document"
    if contains_any(t, ["letter", "memo", "email draft"]): return "plain_document"
    return "general"

def detect_visual_policy(text, content_type, output_format):
    explicit_none = contains_any(text, ["text only", "no pictures", "no images", "no illustration", "plain text", "without pictures"])
    explicit_required = contains_any(text, ["with pictures", "with images", "with illustrations", "with icons", "matching words", "accompanying pictures", "add pictures", "add images", "add chart", "with chart", "graphs", "graph", "diagram", "visual"])
    if explicit_none: return "none"
    if explicit_required: return "required"
    if content_type in ["flashcards", "worksheet"]: return "required"
    if content_type == "kids_lesson" and output_format in ["pptx", "pdf", "docx"]: return "required"
    if output_format == "pptx" and content_type in ["kids_lesson", "lesson"]: return "required"
    if output_format in ["html", "xlsx"]: return "auto"
    if content_type in ["dashboard", "report", "finance_document"]: return "auto"
    if content_type == "plain_document": return "none"
    return "auto"

def detect_assets(text, content_type, visual_policy, output_format):
    assets=[]
    if visual_policy == "none": return assets
    if contains_any(text, ["chart", "graph", "analytics", "metrics", "sales", "expenses", "budget", "tracker"]): assets.append("charts")
    if contains_any(text, ["diagram", "process", "workflow", "steps"]): assets.append("diagrams")
    if contains_any(text, ["picture", "pictures", "image", "images", "illustration", "illustrations", "icons", "matching words"]): assets.append("illustrations")
    if content_type in ["flashcards", "worksheet", "kids_lesson"]: assets.append("kid_friendly_illustrations")
    if output_format == "html": assets.append("visual_layout")
    if output_format == "xlsx" and visual_policy in ["auto", "required"]: assets.append("charts_if_numeric_data")
    clean=[]; seen=set()
    for a in assets:
        if a not in seen:
            clean.append(a); seen.add(a)
    return clean

def choose_route(output_format, content_type, visual_policy, assets):
    if content_type == "flashcards": return {"mode":"flashcards_pdf", "reason":"Flashcards require picture cards by default.", "implemented":True}
    if output_format == "pptx":
        if visual_policy == "required" or assets: return {"mode":"pptx_picture_file", "reason":"PPTX with visuals/pictures should embed media and verify ppt/media.", "implemented":True}
        return {"mode":"pptx_file", "reason":"Plain PPTX requested with no visual requirement.", "implemented":True}
    if output_format == "pdf":
        if visual_policy == "required": return {"mode":"rich_pdf_picture_file", "reason":"PDF requires visuals; rich PDF picture builder is implemented.", "implemented":True}
        return {"mode":"pdf_file", "reason":"PDF without required visuals can use text-first builder.", "implemented":True}
    if output_format == "docx":
        if visual_policy == "required": return {"mode":"rich_docx_picture_file", "reason":"DOCX requires visuals; rich DOCX picture builder is implemented.", "implemented":True}
        return {"mode":"docx_file", "reason":"DOCX without required visuals can use text-first builder.", "implemented":True}
    if output_format == "xlsx":
        if visual_policy in ["auto", "required"]: return {"mode":"rich_xlsx_file", "reason":"XLSX should support tables, charts, and images when useful.", "implemented":False}
        return {"mode":"xlsx_file", "reason":"Plain XLSX requested.", "implemented":False}
    if output_format == "html": return {"mode":"html_file", "reason":"HTML builder already supports visual layout and preview links.", "implemented":True}
    if output_format == "md": return {"mode":"md_file", "reason":"Markdown requested.", "implemented":True}
    return {"mode":"needs_clarification_or_best_format", "reason":"No exact output format detected.", "implemented":False}

def main():
    parser = argparse.ArgumentParser(description="Plan Hermes rich output routing.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    output_format = detect_format(args.request)
    content_type = detect_content_type(args.request)
    visual_policy = detect_visual_policy(args.request, content_type, output_format)
    assets = detect_assets(args.request, content_type, visual_policy, output_format)
    route = choose_route(output_format, content_type, visual_policy, assets)
    result = {"request": args.request, "output_format": output_format, "content_type": content_type, "visual_policy": visual_policy, "needed_assets": assets, "route": route["mode"], "route_implemented": route["implemented"], "reason": route["reason"], "success_rule": "Do not claim success unless file verification and required media verification pass."}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("RICH_OUTPUT_PLAN=OK")
        print("OUTPUT_FORMAT=" + output_format)
        print("CONTENT_TYPE=" + content_type)
        print("VISUAL_POLICY=" + visual_policy)
        print("NEEDED_ASSETS=" + ",".join(assets))
        print("ROUTE=" + route["mode"])
        print("ROUTE_IMPLEMENTED=" + str(route["implemented"]).upper())
        print("REASON=" + route["reason"])
        print("SUCCESS_RULE=" + result["success_rule"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
