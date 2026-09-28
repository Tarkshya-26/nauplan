"""Fill the official SIH 2026 idea template WITHOUT changing its format.

Rules followed:
  * every template shape stays where it is (title, oval, logo, footer bar, footer text, slide no.)
  * every template pointer/prompt stays word-for-word, as a bold heading in its own paragraph
  * content goes UNDER each pointer, in the same text box, same font (Arial), same bullet style
  * the only added graphic is the flow chart that slide 3's own pointer asks for
  * slide 7 (Important Instructions) is removed, as its own note allows (6-slide limit)
"""
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from lxml import etree

from content_freight import TEAM_NAME, TEAM_ID, TITLE_VALUES, IDEA_TITLE, SUBTITLE, SLIDES, FLOW, PICTURES, STATUS_BOX

TEMPLATE_BLUE = RGBColor(0x00, 0x70, 0xC0)  # template footer bar colour
BLACK = RGBColor(0x00, 0x00, 0x00)
A = "http://schemas.openxmlformats.org/drawingml/2006/main"

prs = Presentation("template.pptx")
S = list(prs.slides)


def shape_by_name(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    raise KeyError(name)


def para_text(p):
    return "".join(t.text or "" for t in p.iter(qn("a:t")))


# ---------------------------------------------------------------- run / paragraph builders
def make_rpr(template_rpr, size, bold=False, underline=False, color=None):
    rpr = copy.deepcopy(template_rpr) if template_rpr is not None else etree.Element(qn("a:rPr"))
    rpr.tag = qn("a:rPr")
    rpr.set("lang", "en-US")
    rpr.set("sz", str(int(size * 100)))
    rpr.set("dirty", "0")
    if bold:
        rpr.set("b", "1")
    elif "b" in rpr.attrib:
        del rpr.attrib["b"]
    if underline:
        rpr.set("u", "sng")
    elif "u" in rpr.attrib:
        del rpr.attrib["u"]
    for fill in rpr.findall(qn("a:solidFill")):
        rpr.remove(fill)
    if color is not None:
        sf = etree.Element(qn("a:solidFill"))
        c = etree.SubElement(sf, qn("a:srgbClr"))
        c.set("val", str(color))
        rpr.insert(0, sf)
    # make sure Arial is the font (template body font)
    if rpr.find(qn("a:latin")) is None:
        lat = etree.SubElement(rpr, qn("a:latin"))
        lat.set("typeface", "Arial")
        cs = etree.SubElement(rpr, qn("a:cs"))
        cs.set("typeface", "Arial")
    return rpr


def add_run(p, text, rpr, link=None, part=None):
    r = etree.SubElement(p, qn("a:r"))
    rp = copy.deepcopy(rpr)
    r.append(rp)
    if link and part is not None:
        rid = part.relate_to(link, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                             is_external=True)
        h = etree.SubElement(rp, qn("a:hlinkClick"))
        h.set(qn("r:id"), rid)
    t = etree.SubElement(r, qn("a:t"))
    t.text = text
    if text != text.strip():
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def make_ppr(template_ppr, marL, indent, bu_font, bu_char, algn="l", space_after=None, space_before=None,
             line_pct=None, bu_color=None):
    ppr = copy.deepcopy(template_ppr) if template_ppr is not None else etree.Element(qn("a:pPr"))
    ppr.set("marL", str(int(Inches(marL))))
    ppr.set("indent", str(int(-Inches(indent))))
    ppr.set("algn", algn)
    for child in list(ppr):
        ppr.remove(child)
    # schema order: lnSpc, spcBef, spcAft, buClr..., buFont, buChar
    if line_pct:
        ln = etree.SubElement(ppr, qn("a:lnSpc"))
        etree.SubElement(ln, qn("a:spcPct")).set("val", str(int(line_pct * 1000)))
    if space_before is not None:
        sb = etree.SubElement(ppr, qn("a:spcBef"))
        etree.SubElement(sb, qn("a:spcPts")).set("val", str(int(space_before * 100)))
    if space_after is not None:
        sa = etree.SubElement(ppr, qn("a:spcAft"))
        etree.SubElement(sa, qn("a:spcPts")).set("val", str(int(space_after * 100)))
    if bu_char is None:
        etree.SubElement(ppr, qn("a:buNone"))
    else:
        if bu_color is not None:
            bc = etree.SubElement(ppr, qn("a:buClr"))
            etree.SubElement(bc, qn("a:srgbClr")).set("val", str(bu_color))
        bf = etree.SubElement(ppr, qn("a:buFont"))
        bf.set("typeface", bu_font)
        if bu_font == "Wingdings":
            bf.set("pitchFamily", "2")
            bf.set("charset", "2")
        bc = etree.SubElement(ppr, qn("a:buChar"))
        bc.set("char", bu_char)
    return ppr


def new_para(ppr):
    p = etree.Element(qn("a:p"))
    p.append(ppr)
    return p


# ---------------------------------------------------------------- body filler
def fill_body(slide, tb, spec, part):
    """Rebuild the template text box paragraphs: pointer (verbatim, bold) then its content lines."""
    txBody = tb._element.find(qn("p:txBody"))
    old_ps = txBody.findall(qn("a:p"))
    # template formatting samples
    tmpl = {}
    for p in old_ps:
        tx = para_text(p).strip()
        if tx:
            tmpl[tx] = p
    first_rpr = None
    for p in old_ps:
        r = p.find(qn("a:r"))
        if r is not None:
            first_rpr = r.find(qn("a:rPr"))
            break
    for p in old_ps:
        txBody.remove(p)

    sz = spec["sizes"]
    for block in spec["blocks"]:
        kind = block["kind"]
        if kind == "heading":  # slide-2 style underlined heading, keeps template Wingdings bullet
            src = tmpl[block["text"]]
            p = new_para(copy.deepcopy(src.find(qn("a:pPr"))))
            src_rpr = src.find(qn("a:r")).find(qn("a:rPr"))
            rpr = copy.deepcopy(src_rpr)
            rpr.set("sz", str(int(sz["heading"] * 100)))
            add_run(p, block["text"], rpr)
            ppr = p.find(qn("a:pPr"))
            sa = etree.Element(qn("a:spcAft"))
            etree.SubElement(sa, qn("a:spcPts")).set("val", str(int(block.get("after", 6) * 100)))
            ppr.insert(0, sa)
            txBody.append(p)
        elif kind == "pointer":  # template pointer, verbatim, bold
            src = tmpl.get(block["text"].strip())
            if src is None:
                src = tmpl.get(block["text"])
            src_ppr = src.find(qn("a:pPr")) if src is not None else None
            src_rpr = src.find(qn("a:r")).find(qn("a:rPr")) if src is not None else first_rpr
            algn = src_ppr.get("algn", "l") if src_ppr is not None else "l"
            ppr = make_ppr(src_ppr, 0.375, 0.375, "Arial", "•", algn=algn,
                           space_before=block.get("before", sz.get("pointer_before", 8)), space_after=2)
            p = new_para(ppr)
            add_run(p, block["text"].strip(), make_rpr(src_rpr, sz["pointer"], bold=True,
                                                       color=block.get("color")))
            txBody.append(p)
        elif kind in ("item", "plain", "ref"):
            level = block.get("level", 2)
            if kind == "plain":
                ppr = make_ppr(None, block.get("marL", 0.375), 0, "Arial", None, algn="l",
                               space_after=block.get("after", 2), space_before=block.get("before", 0))
            else:
                marL = 0.75 if level == 2 else 1.05
                ppr = make_ppr(None, marL, 0.25, "Wingdings", "§", algn="l",
                               space_after=block.get("after", sz.get("item_after", 1)), space_before=0)
            p = new_para(ppr)
            size = block.get("size", sz["item"])
            for seg in block["runs"]:
                if isinstance(seg, str):
                    seg = {"t": seg}
                rpr = make_rpr(first_rpr, size, bold=seg.get("b", False), underline=seg.get("u", False),
                               color=seg.get("color"))
                add_run(p, seg["t"], rpr, link=seg.get("link"), part=part)
            txBody.append(p)
    # geometry: keep template x & width; only move the box up under the title
    g = spec.get("geom")
    if g:
        x, y, w, h = g
        if x is not None:
            tb.left = Inches(x)
        tb.top = Inches(y)
        if w is not None:
            tb.width = Inches(w)
        tb.height = Inches(h)
    bodyPr = txBody.find(qn("a:bodyPr"))
    for af in list(bodyPr):
        bodyPr.remove(af)
    etree.SubElement(bodyPr, qn("a:noAutofit"))


# ---------------------------------------------------------------- slide 7 out
sldIdLst = prs.slides._sldIdLst
last = sldIdLst[-1]
prs.part.drop_rel(last.rId)
sldIdLst.remove(last)

# ---------------------------------------------------------------- oval: Your Team Name -> team name
for s in S[1:6]:
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == "Your Team Name":
            r = sh.text_frame.paragraphs[0].runs[0]
            r.text = TEAM_NAME
            r.font.bold = True

# ---------------------------------------------------------------- slide 1: labels bold, values added
s1 = S[0]
tb9 = shape_by_name(s1, "TextBox 9")
ps = [p for p in tb9.text_frame.paragraphs]
lab_ps = [p for p in ps if p.runs]
for p, (label, value) in zip(lab_ps, TITLE_VALUES):
    r0 = p.runs[0]
    for extra in p.runs[1:]:
        p._p.remove(extra._r)
    r0.text = label + " "
    r0.font.bold = True
    r0.font.size = Pt(21)
    vr_el = copy.deepcopy(r0._r)
    p._p.append(vr_el)
    vr = p.runs[-1]
    vr.text = value
    vr.font.bold = False
    vr.font.size = Pt(20)
    p.line_spacing = 1.15
    p.space_after = Pt(9)
    p._p.get_or_add_pPr().set("algn", "l")
# the template's leading empty paragraph: keep it, but small
ps[0].space_after = Pt(0)
ps[0]._p.get_or_add_pPr()
end = ps[0]._p.find(qn("a:endParaRPr"))
if end is not None:
    end.set("sz", "800")
tb9.top = Inches(2.0)
tb9.width = Inches(6.95)
b9 = tb9._element.find(qn("p:txBody")).find(qn("a:bodyPr"))
for c in list(b9):
    b9.remove(c)
etree.SubElement(b9, qn("a:noAutofit"))
tb9.height = Inches(5.3)
# idea title replaces the "TITLE PAGE" placeholder text (same run, same style)
sub = shape_by_name(s1, "Subtitle 3")
sub_runs = [r for p in sub.text_frame.paragraphs for r in p.runs if r.text.strip()]
sub_runs[0].text = SUBTITLE
# title-page headings bold (they already are in the template; make sure)
for name in ("Title 7", "Subtitle 3"):
    for p in shape_by_name(s1, name).text_frame.paragraphs:
        for r in p.runs:
            r.font.bold = True

# ---------------------------------------------------------------- slide 2 title
t = S[1].shapes.title
runs = [r for p in t.text_frame.paragraphs for r in p.runs if r.text.strip()]
runs[0].text = IDEA_TITLE

# ---------------------------------------------------------------- slides 2..6 bodies
for idx, spec in SLIDES.items():
    slide = S[idx]
    fill_body(slide, shape_by_name(slide, "TextBox 8"), spec, slide.part)


# ---------------------------------------------------------------- slide 3 flow chart (template asks for it)
def rect(slide, x, y, w, h, lines, fill=None, lw=1.5, bold_first=True, size=14, sub_size=11.5):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.solid()
        s.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    s.line.color.rgb = TEMPLATE_BLUE
    s.line.width = Pt(lw)
    s.shadow.inherit = False
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.auto_size = MSO_AUTO_SIZE.NONE
    for side in ("margin_left", "margin_right"):
        setattr(tf, side, Inches(0.06))
    for side in ("margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0.02))
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = line
        r.font.name = "Arial"
        r.font.size = Pt(size if i == 0 else sub_size)
        r.font.bold = bold_first and i == 0
        r.font.color.rgb = BLACK
    return s


def arrow(slide, x1, y1, x2, y2, label=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = TEMPLATE_BLUE
    c.line.width = Pt(1.75)
    ln = c.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    return c


def label(slide, x, y, w, h, text, size=10.5, italic=True, align=PP_ALIGN.LEFT, bold=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0))
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = "Arial"
    r.font.size = Pt(size)
    r.font.italic = italic
    r.font.bold = bold
    r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
    return tb


def draw_diagram(slide, d):
    X, Y, W = d["x"], d["y"], d["w"]
    gap = 0.2
    # row 1: users
    n1 = len(d["row1"])
    w1 = (W - gap * (n1 - 1)) / n1
    h1 = d["h1"]
    for i, lines in enumerate(d["row1"]):
        rect(slide, X + i * (w1 + gap), Y, w1, h1, lines)
    # arrows row1 -> backend
    y_a1 = Y + h1
    y_b = y_a1 + d["arrow"]
    for i in range(n1):
        cx = X + i * (w1 + gap) + w1 / 2
        arrow(slide, cx, y_a1, cx, y_b)
    label(slide, X + w1 / 2 + 0.1, y_a1 + 0.03, 3.8, 0.25, d["link1"], size=11)
    # row 2: backend
    h2 = d["h2"]
    rect(slide, X, y_b, W, h2, d["row2"], fill=RGBColor(0xEA, 0xF3, 0xFB))
    # arrows backend -> row3
    y_a2 = y_b + h2
    y_c = y_a2 + d["arrow"]
    n3 = len(d["row3"])
    w3 = (W - gap * (n3 - 1)) / n3
    for i in range(n3):
        cx = X + i * (w3 + gap) + w3 / 2
        arrow(slide, cx, y_a2, cx, y_c)
    # row 3: data / ML / external
    h3 = d["h3"]
    for i, lines in enumerate(d["row3"]):
        rect(slide, X + i * (w3 + gap), y_c, w3, h3, lines)
    cy = y_c + h3 + 0.05
    for key in ("caption", "caption2"):
        if d.get(key):
            label(slide, X, cy, W, 0.26, d[key], size=11.5, italic=False, align=PP_ALIGN.CENTER)
            cy += 0.25


def draw_flow(slide, f):
    """Left-to-right pipeline the slide-3 pointer asks for: stage boxes joined by arrows."""
    X, Y, W, H, gap = f["x"], f["y"], f["w"], f["h"], f["gap"]
    n = len(f["stages"])
    bw = (W - gap * (n - 1)) / n
    hh, fs = f.get("head_h", 0.42), f.get("font", 12)
    for i, st in enumerate(f["stages"]):
        x = X + i * (bw + gap)
        rect(slide, x, Y, bw, hh, [st["head"]], fill=RGBColor(0xEA, 0xF3, 0xFB), size=f.get("head_font", 13))
        body = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(Y + hh), Inches(bw), Inches(H - hh))
        body.fill.solid(); body.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        body.line.color.rgb = TEMPLATE_BLUE; body.line.width = Pt(1.5); body.shadow.inherit = False
        tf = body.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = Inches(0.08); tf.margin_top = Inches(0.06); tf.margin_bottom = Inches(0.02)
        for j, line in enumerate(st["lines"]):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(3)
            r = p.add_run(); r.text = "• " + line
            r.font.name = "Arial"; r.font.size = Pt(fs); r.font.color.rgb = BLACK
        if i < n - 1:
            ay = Y + H / 2
            arrow(slide, x + bw + 0.03, ay, x + bw + gap - 0.03, ay)
    cy = Y + H + 0.06
    for cap in f["captions"]:
        label(slide, X, cy, W, 0.24, cap, size=11, italic=False, align=PP_ALIGN.CENTER)
        cy += 0.23


def draw_pictures(slide, pics, status):
    """Screenshots of the working prototype, each with a caption, plus a short status box."""
    from PIL import Image
    for pic in pics:
        im = Image.open(pic["path"]).crop(pic["crop"])
        out = f"_crop_{pic['path']}"
        im.save(out)
        shape = slide.shapes.add_picture(out, Inches(pic["x"]), Inches(pic["y"]), height=Inches(pic["h"]))
        shape.line.color.rgb = TEMPLATE_BLUE
        shape.line.width = Pt(1)
        label(slide, pic["x"], pic["y"] + pic["h"] + 0.02, shape.width / 914400, 0.2, pic["caption"],
              size=9.5, italic=True, align=PP_ALIGN.LEFT)
    s = status
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(s["x"]), Inches(s["y"]), Inches(s["w"]), Inches(s["h"]))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xEA, 0xF3, 0xFB)
    box.line.color.rgb = TEMPLATE_BLUE; box.line.width = Pt(1.5); box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Inches(0.12); tf.margin_top = Inches(0.08)
    p = tf.paragraphs[0]; p.space_after = Pt(4)
    r = p.add_run(); r.text = s["head"]
    r.font.name = "Arial"; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = BLACK
    for line in s["lines"]:
        p = tf.add_paragraph(); p.space_after = Pt(2)
        r = p.add_run(); r.text = "• " + line
        r.font.name = "Arial"; r.font.size = Pt(10.5); r.font.color.rgb = BLACK


draw_flow(S[2], FLOW)
draw_pictures(S[2], PICTURES, STATUS_BOX)

prs.save("SIH2026_NauPlan_Vector66.pptx")
print("saved")
