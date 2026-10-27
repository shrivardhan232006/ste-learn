#!/usr/bin/env python3
"""ste_lint.py — heuristic ASD-STE100 checker for lesson pages.

Usage:
    python3 ste_lint.py lesson.html [--json]

What it reads
    Text inside <main> from <p>, <li>, <figcaption>, <dd>, <td>, <blockquote>
    and any element with a data-ste attribute. Code (<code>, <pre>, <kbd>),
    <svg>, <script>, <style>, and elements marked data-ste="skip" are ignored.

    Procedural text (limit 20 words / sentence):
        <ol class="steps"> items, or any element with data-ste="procedure".
    Descriptive text (limit 25 words / sentence): everything else.

    Technical nouns: every <dfn>, every element with data-term="...", and
    every <dt> in the glossary are added to an allow-list, so their -ing
    forms and words are not flagged.

Severity
    ERROR  must fix (sentence too long, paragraph > 6 sentences, semicolon,
           complex verb tense)
    WARN   check and fix unless it is an approved technical noun
           (passive voice, -ing form, non-STE word, phrasal verb)

Exit code 1 if any ERROR is found. This is a heuristic helper, not a
certified STE checker. Always do a human read as well.
"""
import json
import re
import sys
from html.parser import HTMLParser

DESCRIPTIVE_MAX = 25
PROCEDURAL_MAX = 20
PARAGRAPH_MAX = 6

BLOCK_TAGS = {"p", "li", "figcaption", "dd", "td", "blockquote", "h1", "h2", "h3", "h4"}
HEADING_TAGS = {"h1", "h2", "h3", "h4"}
IGNORE_TAGS = {"code", "pre", "kbd", "svg", "script", "style", "math", "samp", "var", "button", "nav", "aside"}

# word -> suggestion (illustrative list, not the STE dictionary)
NON_STE = {
    "utilize": "use", "utilise": "use", "utilization": "use", "employ": "use",
    "ensure": "make sure", "assure": "make sure",
    "perform": "do", "performs": "does", "performed": "did",
    "commence": "start", "initiate": "start", "begin": "start", "begins": "starts",
    "terminate": "stop", "cease": "stop",
    "prior": "before", "subsequently": "then / after", "thereafter": "after that",
    "obtain": "get", "acquire": "get", "receive": "get",
    "require": "need / must", "requires": "needs", "required": "necessary / must",
    "indicate": "show", "indicates": "shows", "demonstrate": "show",
    "numerous": "many", "various": "different / many", "several": "some / a number of",
    "however": "but", "therefore": "because of this / thus",
    "hence": "thus / because of this",
    "furthermore": "also", "moreover": "also", "additionally": "also",
    "should": "must (instruction) / can (possibility)",
    "may": "can", "might": "can", "could": "can",
    "would": "(rewrite in simple present or future)",
    "basically": "(delete)", "simply": "(delete)", "just": "(delete) / only",
    "really": "(delete)", "very": "(delete or be specific)", "actually": "(delete)",
    "around": "approximately (numbers) / near (position)",
    "lots": "many", "huge": "large", "tiny": "small", "big": "large",
    "figure out": "find", "etc": "(give the full list)", "e.g.": "for example",
    "i.e.": "that is", "via": "through / with", "vs": "compared with",
    "allows": "lets / makes it possible", "allow": "let", "enable": "let / make it possible",
    "enables": "lets", "verify": "make sure / examine", "locate": "find",
    "inspect": "examine", "assist": "help", "facilitate": "help",
    "consists": "has / contains", "comprises": "has / contains",
    "regarding": "about", "concerning": "about", "whilst": "while",
    "whereas": "but", "although": "but", "though": "but",
}

PHRASAL = [
    "set up", "carry out", "find out", "look into", "look at", "figure out",
    "point out", "come up", "go through", "make up", "take off", "turn out",
    "break down", "build up", "end up", "pick up", "put together", "fill in",
    "keep up", "work out", "deal with", "get rid of", "look for", "come back",
]

COMPLEX_TENSE = re.compile(
    r"\b(has|have|had)\s+(been|\w+ed|done|made|seen|given|taken|shown|known|gone|written)\b"
    r"|\b(is|are|was|were)\s+being\b"
    r"|\bwill\s+have\b"
    r"|\b(would|should|could|might)\s+(have|be)\b",
    re.I,
)

IRREGULAR_PP = {
    "done", "made", "seen", "given", "taken", "shown", "known", "written", "built",
    "sent", "kept", "held", "found", "put", "set", "cut", "read", "run", "begun",
    "chosen", "drawn", "driven", "eaten", "fallen", "flown", "forgotten", "frozen",
    "gotten", "hidden", "lost", "meant", "paid", "said", "sold", "spent", "stolen",
    "struck", "taught", "thought", "told", "understood", "won", "worn", "broken",
    "spoken", "brought", "bought", "caught", "fed", "led", "left", "lit", "made",
    "split", "spread", "shut", "hit", "hurt", "let", "quit", "bound", "ground", "wound",
}
BE = r"(is|are|was|were|be|been|being)"
PASSIVE = re.compile(rf"\b{BE}\s+(\w+ly\s+)?(\w+ed|\w+en)\b|\b{BE}\s+(\w+ly\s+)?(\w+)\b", re.I)

ING_OK = {
    "during", "thing", "things", "something", "nothing", "anything", "everything",
    "string", "strings", "ring", "rings", "spring", "springs", "king", "wing", "wings",
    "bring", "sing", "swing", "sting", "ceiling", "morning", "evening", "building",
    "buildings", "bearing", "bearings", "wiring", "piping", "tubing", "housing",
    "housings", "fitting", "fittings", "coupling", "couplings", "lining", "casing",
    "opening", "openings", "warning", "warnings", "setting", "settings", "drawing",
    "drawings", "heading", "headings", "meaning", "training", "rating", "ratings",
    "landing", "bushing", "bushings", "shielding", "packing", "padding",
}

ADJ_ED_OK = {"approved", "related", "connected", "installed", "damaged", "used", "named",
             "shown", "given", "known", "fixed", "closed", "opened", "attached"}

WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-\.%/°×+]*")


def count_words(sentence: str) -> int:
    # numbers, symbols, abbreviations and hyphenated groups count as one word
    return len(WORD.findall(sentence))


def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    # protect common abbreviations and decimals
    protected = re.sub(r"\b(e\.g|i\.e|etc|vs|Fig|No|approx|Dr|Prof|Mr|Ms)\.", lambda m: m.group(0).replace(".", "§"), text)
    protected = re.sub(r"(\d)\.(\d)", r"\1§\2", protected)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])", protected)
    return [p.replace("§", ".").strip() for p in parts if p.strip()]


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.main_depth = 0
        self.stack = []          # list of (tag, attrs)
        self.ignore = 0
        self.blocks = []         # dicts: tag, kind, text, line
        self.cur = None
        self.terms = set()
        self.term_capture = None
        self.has_main = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.in_main = True
            self.has_main = True
        void = tag in {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}
        if not void:
            self.stack.append((tag, a))
        if "data-term" in a and a["data-term"]:
            self.terms.add(a["data-term"].lower())
        if tag in ("dfn", "dt") or "data-term" in a:
            self.term_capture = ""
        if tag in IGNORE_TAGS or a.get("data-ste") == "skip":
            self.ignore += 1 if not void else 0
            return
        if self.ignore or not self.in_main:
            return
        if (tag in BLOCK_TAGS or "data-ste" in a) and self.cur is None:
            kind = "descriptive"
            classes = []
            for t, at in self.stack:
                classes += (at.get("class") or "").split()
                if at.get("data-ste") == "procedure":
                    kind = "procedure"
            if tag == "li" and any(t == "ol" and "steps" in (at.get("class") or "").split() for t, at in self.stack):
                kind = "procedure"
            if tag in HEADING_TAGS:
                kind = "heading"
            self.cur = {"tag": tag, "kind": kind, "text": "", "line": self.getpos()[0], "depth": len(self.stack)}

    def handle_endtag(self, tag):
        # pop to matching tag
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                idx = i
                break
        if idx is None:
            return
        popped = self.stack[idx:]
        self.stack = self.stack[:idx]
        for t, a in popped:
            if t in IGNORE_TAGS or a.get("data-ste") == "skip":
                self.ignore = max(0, self.ignore - 1)
            if (t in ("dfn", "dt") or "data-term" in a) and self.term_capture is not None:
                term = self.term_capture.strip().lower()
                if term:
                    self.terms.add(term)
                self.term_capture = None
        if self.cur is not None and len(self.stack) < self.cur["depth"]:
            if self.cur["text"].strip():
                self.blocks.append(self.cur)
            self.cur = None
        if tag == "main":
            self.in_main = False

    def handle_data(self, data):
        if self.term_capture is not None:
            self.term_capture += data
        if self.ignore or self.cur is None:
            if self.cur is not None and self.ignore:
                self.cur["text"] += " "
            return
        self.cur["text"] += data


def lint(path):
    html = open(path, encoding="utf-8").read()
    c = Collector()
    c.feed(html)
    if not c.has_main:
        # no <main>: lint whole body
        c2 = Collector()
        c2.in_main = True
        c2.feed(html)
        c = c2
    term_words = set()
    for t in c.terms:
        term_words.update(re.findall(r"[a-z\-]+", t))
    issues = []

    def add(sev, rule, block, msg, snippet):
        issues.append({"severity": sev, "rule": rule, "line": block["line"], "message": msg, "text": snippet[:160]})

    for b in c.blocks:
        text = re.sub(r"\s+", " ", b["text"]).strip()
        if not text or b["kind"] == "heading":
            continue
        sentences = split_sentences(text)
        limit = PROCEDURAL_MAX if b["kind"] == "procedure" else DESCRIPTIVE_MAX
        for s in sentences:
            n = count_words(s)
            if n > limit:
                add("ERROR", "sentence-length", b, f"{n} words (max {limit} for {b['kind']} text)", s)
        if b["tag"] == "p" and len(sentences) > PARAGRAPH_MAX:
            add("ERROR", "paragraph-length", b, f"{len(sentences)} sentences (max {PARAGRAPH_MAX})", text)
        if ";" in text:
            add("ERROR", "semicolon", b, "Do not join sentences with a semicolon. Write two sentences.", text)
        for m in COMPLEX_TENSE.finditer(text):
            add("ERROR", "verb-tense", b, f"Complex verb form '{m.group(0)}'. Use simple present, past or future.", text)
        low = text.lower()
        for m in re.finditer(rf"\b{BE}\s+(?:\w+ly\s+)?(\w+)\b", low):
            w = m.group(2)
            if (w.endswith("ed") or w.endswith("en") or w in IRREGULAR_PP) and w not in ADJ_ED_OK and w not in term_words \
                    and w not in {"open", "often", "even", "seven", "eleven", "then", "when", "ten", "token", "screen", "green", "between", "golden", "kitchen", "garden"}:
                # check for a following "by" → strong passive signal
                after = low[m.end(): m.end() + 30]
                sev = "WARN"
                add(sev, "passive-voice", b,
                    f"Possible passive '{m.group(0)}'{' (with by-agent)' if ' by ' in ' ' + after else ''}. Use active voice if you know the agent.", text)
        for m in re.finditer(r"\b([A-Za-z]+ing)\b", text):
            w = m.group(1).lower()
            if len(w) <= 4 or w in ING_OK or w in term_words:
                continue
            add("WARN", "ing-form", b, f"'-ing' form '{m.group(1)}'. Allowed only in a technical noun (add to glossary) — else rewrite.", text)
        for w, sug in NON_STE.items():
            if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", low) and w not in term_words:
                add("WARN", "word-choice", b, f"'{w}' is not a usual STE word. Try: {sug}", text)
        for p in PHRASAL:
            if re.search(rf"\b{p}\b", low):
                add("WARN", "phrasal-verb", b, f"Phrasal verb '{p}'. Use one approved verb.", text)

    # de-duplicate identical messages on the same block
    seen, out = set(), []
    for i in issues:
        k = (i["line"], i["rule"], i["message"])
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out, c


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    issues, c = lint(path)
    if "--json" in sys.argv:
        print(json.dumps(issues, indent=2))
    else:
        errs = [i for i in issues if i["severity"] == "ERROR"]
        warns = [i for i in issues if i["severity"] == "WARN"]
        for i in errs + warns:
            print(f"{i['severity']:5} L{i['line']:<5} {i['rule']:<16} {i['message']}\n      » {i['text']}")
        print(f"\n{len(c.blocks)} text blocks checked · {len(c.terms)} technical nouns allowed · "
              f"{len(errs)} errors · {len(warns)} warnings")
    sys.exit(1 if any(i["severity"] == "ERROR" for i in issues) else 0)


if __name__ == "__main__":
    main()
