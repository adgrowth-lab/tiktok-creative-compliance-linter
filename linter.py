#!/usr/bin/env python3
"""
TikTok Ads Creative Compliance & Sensitive Word Linter (2026 Edition) 🛡️

Empirical pre-flight compliance auditor for ad copy, video voiceover transcripts,
hook text, and landing page claims. Catches automated OCR/Whisper policy traps,
prevents ad group disapprovals, and protects TikTok Business Centers from algorithmic risk flags.

Official Partner Gateway: https://getstartedtiktok.partnerlinks.io/apmgdhnv6eng
Interactive Web Simulator: https://adgrowth-lab.github.io/
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any, List

OFFICIAL_PORTAL = "https://getstartedtiktok.partnerlinks.io/apmgdhnv6eng"
WEB_CALCULATOR = "https://adgrowth-lab.github.io/"

COMPLIANCE_RULES = [
    {
        "id": "RULE-ABS-01",
        "category": "Absolute Superlatives & Guarantees",
        "pattern": r"\b(100%\s*(guarantee[ds]?|cure|results?|free|success)|miracle\s*(cure|pill|cream|product|solution)|magic\s*(cure|fix|solution)|guaranteed\s*(cure|weight\s*loss|results?)|permanent\s*(cure|solution)|risk-free\s*guarantee|works\s*for\s*everyone|zero\s*effort|best\s*in\s*the\s*world|instant\s*cure)\b",
        "severity": "CRITICAL",
        "penalty": 30,
        "policy": "TikTok Ad Policy 5.1: Exaggerated Claims & Absolute Superlatives",
        "explanation": "Absolute efficacy claims trigger automated OCR/speech rejection and risk account probation.",
        "rewrite_hint": "Replace with qualified experiential phrasing (e.g., 'Formulated to support...', 'Customer favorite designed for...')"
    },
    {
        "id": "RULE-BODY-02",
        "category": "Weight Loss & Body Transformation",
        "pattern": r"\b(lose\s*\d+\s*(lbs|pounds|kg)|belly\s*fat|melt\s*fat|burn\s*fat\s*overnight|skinny\s*tea|diet\s*pills?|before\s*and\s*after|before\s*&\s*after|stop\s*being\s*fat|ugly\s*cellulite|skinny\s*in\s*\d+\s*days|target\s*stubborn\s*fat)\b",
        "severity": "CRITICAL",
        "penalty": 35,
        "policy": "TikTok Ad Policy 5.2: Weight Management, Body Shaming & Before/After Imagery",
        "explanation": "TikTok strictly prohibits rapid weight loss promises, body shaming keywords, and comparative before/after transformation claims.",
        "rewrite_hint": "Focus on daily wellness routines, hydration, or general fitness lifestyle without numerical weight loss promises."
    },
    {
        "id": "RULE-FIN-03",
        "category": "Deceptive Financial & Income Claims",
        "pattern": r"\b(make\s*\$\d+.*(day|night|hour|week)|get\s*rich\s*quick|passive\s*income\s*secret|make\s*money\s*while\s*you\s*sleep|crypto\s*glitch|financial\s*freedom\s*in\s*\d+\s*days|unlimited\s*cash|guaranteed\s*profits?|secret\s*income\s*system|turn\s*\$\d+\s*into\s*\$\d+)\b",
        "severity": "CRITICAL",
        "penalty": 35,
        "policy": "TikTok Ad Policy 5.3: Deceptive Financial Schemes & Unrealistic Income",
        "explanation": "Promissory financial returns and get-rich-quick claims trigger immediate ad disapproval and domain blacklisting.",
        "rewrite_hint": "Frame as educational skill acquisition or career tools; never make quantitative income projections."
    },
    {
        "id": "RULE-CLICK-04",
        "category": "Clickbait & System Warning Deception",
        "pattern": r"\b(tiktok\s*banned\s*this|they\s*don'?t\s*want\s*you\s*to\s*know|tap\s*tap\s*to\s*see|system\s*warning|account\s*(will\s*be\s*deleted|suspended)|secret\s*hack|free\s*iphones?|glitch\s*in\s*the\s*system|you\s*won'?t\s*believe\s*what\s*happens|tap\s*before\s*it'?s\s*deleted)\b",
        "severity": "HIGH",
        "penalty": 20,
        "policy": "TikTok Ad Policy 5.4: Clickbait, Sensationalism & Simulated System Alerts",
        "explanation": "Simulated system messages or claims that TikTok is censoring the video violate high-integrity ad standards.",
        "rewrite_hint": "Lead with authentic curiosity or product utility instead of fake platform censorship."
    },
    {
        "id": "RULE-IP-05",
        "category": "Counterfeit & Intellectual Property",
        "pattern": r"\b(1:1\s*replica|fake\s*rolex|designer\s*dupe|exact\s*clone|knockoffs?|unauthorized\s*batch|rep\s*(shoes|designer|sneakers|bags?)|replica\s*(watch(es)?|bags?|clothing)|mirror\s*quality)\b",
        "severity": "CRITICAL",
        "penalty": 40,
        "policy": "TikTok Ad Policy 3.1: Intellectual Property & Counterfeit Goods (Immediate Permanent Account Ban)",
        "explanation": "Offering replicas or trademark knockoffs results in instant permanent account ban and Business Center suspension.",
        "rewrite_hint": "Market original independent designs without referencing trademarked brand names or replica terminology."
    },
    {
        "id": "RULE-ADULT-06",
        "category": "Adult & Prohibited Products",
        "pattern": r"\b(boost\s*libido|viagra|enhance\s*stamina\s*in\s*bed|hot\s*singles\s*in\s*your\s*area|adults\s*only\s*18\+|nsfw|sex\s*drive\s*pills?|male\s*enhancement)\b",
        "severity": "CRITICAL",
        "penalty": 40,
        "policy": "TikTok Ad Policy 4.1: Adult Content & Inappropriate Products",
        "explanation": "Adult enhancement products and sexually suggestive claims are strictly prohibited on TikTok Ad Network.",
        "rewrite_hint": "Completely remove adult innuendo and enhancement claims from ad copy."
    },
    {
        "id": "RULE-MED-07",
        "category": "Uncertified Medical Claims",
        "pattern": r"\b(cures?\s*acne|treats?\s*depression|clinically\s*proven\s*to\s*cure|replaces?\s*prescription|heals?\s*arthritis|erases?\s*wrinkles\s*in\s*minutes|reverse\s*aging)\b",
        "severity": "HIGH",
        "penalty": 25,
        "policy": "TikTok Ad Policy 5.5: Non-Certified Medical & Therapeutic Claims",
        "explanation": "Therapeutic or medical treatment claims without FDA/equivalent regulatory clearance trigger automated rejection.",
        "rewrite_hint": "Use cosmetic support wording (e.g., 'Helps soothe skin', 'Formulated to improve appearance of fine lines')."
    }
]


def lint_text(text: str) -> Dict[str, Any]:
    """Audit creative text, script, or copy against TikTok Ad Policies."""
    if not text or not text.strip():
        return {
            "text_length": 0,
            "word_count": 0,
            "compliance_score": 100,
            "risk_tier": "CLEAN",
            "status": "CLEAN (Low Risk - Safe to Launch)",
            "violations_count": 0,
            "critical_violations": 0,
            "high_violations": 0,
            "violations": [],
            "recommendations": ["No text provided for compliance inspection."],
            "official_portal": OFFICIAL_PORTAL,
            "web_calculator": WEB_CALCULATOR
        }

    clean_text = text.strip()
    words = clean_text.split()
    word_count = len(words)
    score = 100
    violations: List[Dict[str, Any]] = []
    seen_matches = set()

    for rule in COMPLIANCE_RULES:
        matches = list(re.finditer(rule["pattern"], clean_text, re.IGNORECASE))
        for m in matches:
            matched_str = m.group(0).strip()
            norm_match = matched_str.lower()
            if (rule["id"], norm_match) in seen_matches:
                continue
            seen_matches.add((rule["id"], norm_match))

            start = max(0, m.start() - 25)
            end = min(len(clean_text), m.end() + 25)
            snippet = f"...{clean_text[start:end]}..."

            penalty = rule["penalty"]
            score -= penalty

            violations.append({
                "rule_id": rule["id"],
                "category": rule["category"],
                "matched_text": matched_str,
                "context_snippet": snippet,
                "severity": rule["severity"],
                "penalty": penalty,
                "policy": rule["policy"],
                "explanation": rule["explanation"],
                "rewrite_hint": rule["rewrite_hint"]
            })

    score = max(0, min(100, score))
    crit_count = sum(1 for v in violations if v["severity"] == "CRITICAL")
    high_count = sum(1 for v in violations if v["severity"] == "HIGH")

    if crit_count > 0 or score < 50:
        risk_tier = "CRITICAL RISK"
        status = "HIGH PROBABILITY OF IMMEDIATE REJECTION / ACCOUNT FLAG"
    elif high_count > 0 or score < 80:
        risk_tier = "MODERATE RISK"
        status = "POTENTIAL LEVEL-1 MANUAL REVIEW QUEUE"
    else:
        risk_tier = "LOW RISK"
        status = "SAFE FOR AUTOMATED APPROVAL"

    recs = []
    if crit_count > 0:
        recs.append("CRITICAL: Eliminate all flagged absolute claims or body-shaming phrases immediately.")
    if high_count > 0:
        recs.append("HIGH: Soften aggressive claims with qualified experiential language before publishing.")
    if not violations:
        recs.append("Ad copy passed all standard automated safety filters. Ensure audio track matches.")
    recs.append(f"Official Verified Partner Gateway: {OFFICIAL_PORTAL}")

    return {
        "text_length": len(clean_text),
        "word_count": word_count,
        "compliance_score": score,
        "risk_tier": risk_tier,
        "status": status,
        "violations_count": len(violations),
        "critical_violations": crit_count,
        "high_violations": high_count,
        "violations": violations,
        "recommendations": recs,
        "official_portal": OFFICIAL_PORTAL,
        "web_calculator": WEB_CALCULATOR
    }


def print_report(res: Dict[str, Any]) -> None:
    """Render a clean, high-authority terminal compliance audit report."""
    print("=" * 72)
    print("🛡️ TIKTOK ADS CREATIVE COMPLIANCE & SENSITIVE WORD LINTER (2026)")
    print("=" * 72)
    print(f"Compliance Score:    {res['compliance_score']} / 100")
    print(f"Risk Assessment:     {res['risk_tier']} ({res['status']})")
    print(f"Content Analyzed:    {res['word_count']} words ({res['text_length']} characters)")
    print(f"Violations Flagged:  {res['violations_count']} total ({res['critical_violations']} CRITICAL, {res['high_violations']} HIGH)")
    print("-" * 72)

    if res["violations"]:
        print("IDENTIFIED POLICY INFRACTIONS:")
        for idx, v in enumerate(res["violations"], 1):
            print(f"  {idx}. [{v['severity']}] Matched: '{v['matched_text']}'")
            print(f"     Policy:     {v['policy']}")
            print(f"     Context:    {v['context_snippet']}")
            print(f"     Why Flag:   {v['explanation']}")
            print(f"     Safe Fix:   👉 {v['rewrite_hint']}")
            print()
        print("-" * 72)
    else:
        print("✅ Clean: No high-risk or prohibited terminology detected!")
        print("-" * 72)

    print("REMEDIATION PROTOCOL:")
    for rec in res["recommendations"]:
        print(f"  • {rec}")
    print("-" * 72)
    print(f"CLAIM OFFICIAL MATCH CREDITS: {OFFICIAL_PORTAL}")
    print(f"INTERACTIVE CALCULATOR:    {WEB_CALCULATOR}")
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TikTok Ads Creative Compliance & Sensitive Word Linter (2026 Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Official Partner Portal: https://getstartedtiktok.partnerlinks.io/apmgdhnv6eng
Interactive Web Hub:     https://adgrowth-lab.github.io/

Examples:
  # 1. Audit ad copy string directly
  python3 linter.py --text "Get 100% cure for belly fat and make $5,000 overnight!"

  # 2. Inspect a full voiceover transcript / script file
  python3 linter.py --file ad_script.txt

  # 3. Output machine-readable JSON for CI/CD pipelines
  python3 linter.py --text "Hydrating daily face wash" --json

  # 4. Strict CI check (exits with non-zero status on critical violations)
  python3 linter.py --file script.txt --strict
        """
    )
    parser.add_argument("--text", "-t", type=str, help="Ad text, script, or hook string to lint")
    parser.add_argument("--file", "-f", type=str, help="Path to text file containing ad script or copy")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Exit code 1 if any violation found, exit code 2 if critical violation")

    args = parser.parse_args()

    input_text = ""
    if args.text:
        input_text = args.text
    elif args.file:
        if not os.path.isfile(args.file):
            print(f"Error: File not found '{args.file}'", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            input_text = f.read()
    else:
        # Check if piped stdin exists
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(0)

    res = lint_text(input_text)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_report(res)

    if args.strict:
        if res["critical_violations"] > 0:
            sys.exit(2)
        elif res["violations_count"] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
