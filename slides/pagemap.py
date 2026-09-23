#!/usr/bin/env python3
"""Map every frame of the deck to its PDF page range, using the built .nav file.

    python3 pagemap.py                      print the map
    python3 pagemap.py --renumber FILE      rewrite the [Slide N] / [Slides a-b] brackets
                                            in a speaker script whose headers carry frame titles

Run `make` first. Overlays (\\pause) and allowframebreaks expand a frame over several
pages; this reads the real ranges, so the script stays keyed to what a PDF viewer shows.
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
NAV = HERE / "build/slides.tex/slides/slides.nav"

FRAME_RE = re.compile(r"\\begin\{frame\}(?:\[[^\]]*\])?(?:\{((?:[^{}]|\{[^{}]*\})*)\})?")

def uncommented(src):
    return re.sub(r"(?<!\\)%.*", "", src)

def clean(t):
    t = re.sub(r"\\(emph|textbf|texttt|mbox)\{([^{}]*)\}", r"\2", t)
    t = t.replace("\\,", " ").replace("~", " ").replace("\\&", "&")
    return re.sub(r"\s+", " ", t).strip()

def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()

def document_order():
    """Frame titles in the order the document emits them."""
    frames = ["Title"]
    body = (HERE / "slides.tex").read_text()
    body = body[body.index(r"\begin{document}"):]
    section = None
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("%"):
            continue
        m = re.match(r"\\input\{sections/([^}]+)\}", s)
        if m:
            if m.group(1) != "outline":
                src = uncommented((HERE / f"sections/{m.group(1)}.tex").read_text())
                sec = re.search(r"\\section\{([^}]*)\}", src)
                fallback = clean(sec.group(1)) if sec else "(untitled)"
                frames += [clean(t or "") or fallback for t in FRAME_RE.findall(src)]
            continue
        if s.startswith(r"\outlineframe"):
            frames.append("Outline"); continue
        m = re.match(r"\\section\{([^}]*)\}", s)
        if m:
            section = m.group(1).strip(); continue
        m = FRAME_RE.match(s)
        if m:
            frames.append(clean(m.group(1) or "") or (section or "Thank you"))
    return frames

def nav_ranges():
    if not NAV.exists():
        sys.exit("no build/slides.tex/slides/slides.nav: run make first")
    seen = {}
    for sec, sub, idx, a, b in re.findall(
            r"\\slideentry \{(\d+)\}\{(\d+)\}\{(\d+)\}\{(\d+)/(\d+)\}", NAV.read_text()):
        seen[(int(sec), int(sub), int(idx))] = (int(a), int(b))   # last entry = widest range
    return [seen[k] for k in sorted(seen)]

def page_map():
    titles, ranges = document_order(), nav_ranges()
    if len(titles) != len(ranges):
        sys.exit(f"frame count mismatch: {len(titles)} frames in the sources, "
                 f"{len(ranges)} in the nav file (stale build?)")
    return list(zip(titles, ranges))

def bracket(a, b):
    return f"[Slide {a}]" if a == b else f"[Slides {a}\u2013{b}]"

HEADER_RE = re.compile(r"^\[Slides? [^\]]*\]\s*(?P<title>.*?)(?:\s+\((?P<time>\d+:\d\d)\))?(?:\s+\u2014\s+(?P<tail>.*))?\s*$")

def renumber(path):
    """Rewrite each header line `[Slides a-b]  Title  (m:ss)  — note`: the bracket and the
    click count come from the build, the title, time and any other note are kept."""
    by_title = {}
    for t, r in page_map():
        by_title.setdefault(norm(t), []).append(r)     # "Outline" occurs several times, in order
    used, out, unmatched = {}, [], []
    for line in pathlib.Path(path).read_text().splitlines():
        m = HEADER_RE.match(line)
        if not m:
            out.append(line); continue
        title, time, tail = m.group("title").strip(), m.group("time"), m.group("tail")
        if tail and re.fullmatch(r"\d+ clicks?", tail.strip()):
            tail = None
        key = norm(title)
        if key not in by_title:
            unmatched.append(line); out.append(line); continue
        i = used.get(key, 0); used[key] = i + 1
        a, b = by_title[key][min(i, len(by_title[key]) - 1)]
        parts = [bracket(a, b), title]
        if time: parts.append(f"({time})")
        if tail: parts.append(f"\u2014 {tail}")
        if b > a: parts.append(f"\u2014 {b - a} clicks")
        out.append("  ".join(parts))
    pathlib.Path(path).write_text("\n".join(out) + "\n")
    print(f"renumbered {path}: {sum(used.values())} headers, {len(unmatched)} unmatched")
    for u in unmatched: print("   ", u)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--renumber":
        renumber(sys.argv[2])
    else:
        for t, (a, b) in page_map():
            print(f"{bracket(a, b):<16} {t}" + (f"   ({b - a} clicks)" if b > a else ""))
