from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "Digital_Nagar_Palika_Brochure_Hinglish.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

INK = colors.HexColor("#173B35")
GREEN = colors.HexColor("#0E6955")
DEEP = colors.HexColor("#083F36")
MINT = colors.HexColor("#E9F3EF")
PALE = colors.HexColor("#F4F7F4")
GOLD = colors.HexColor("#E7A344")
MUTED = colors.HexColor("#5E716C")
LINE = colors.HexColor("#DCE7E1")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Kicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=GOLD, spaceAfter=7, tracking=1.2))
styles.add(ParagraphStyle(name="HeroTitle", fontName="Helvetica-Bold", fontSize=27, leading=33, textColor=WHITE, spaceAfter=9))
styles.add(ParagraphStyle(name="HeroBody", fontName="Helvetica", fontSize=11, leading=17, textColor=colors.HexColor("#E5F1EC")))
styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=19, leading=24, textColor=INK, spaceBefore=2, spaceAfter=8))
styles.add(ParagraphStyle(name="Intro", fontName="Helvetica", fontSize=10, leading=15, textColor=MUTED, spaceAfter=10))
styles.add(ParagraphStyle(name="CardTitle", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="CardBody", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED))
styles.add(ParagraphStyle(name="BodySmall", fontName="Helvetica", fontSize=9, leading=13, textColor=INK))
styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=10, leading=15, textColor=INK))
styles.add(ParagraphStyle(name="WhiteTitle", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=WHITE, spaceAfter=4))
styles.add(ParagraphStyle(name="WhiteBody", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#E5F1EC")))
styles.add(ParagraphStyle(name="CenterSmall", fontName="Helvetica-Bold", fontSize=8, leading=11, alignment=TA_CENTER, textColor=GREEN))
styles.add(ParagraphStyle(name="Footer", fontName="Helvetica", fontSize=8, leading=10, textColor=MUTED))


class Hero(Flowable):
    def __init__(self, width, height, kicker, title, body):
        super().__init__()
        self.width, self.height = width, height
        self.kicker, self.title, self.body = kicker, title, body

    def draw(self):
        c = self.canv
        c.setFillColor(DEEP)
        c.roundRect(0, 0, self.width, self.height, 14, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.circle(self.width - 50, self.height - 50, 43, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.circle(self.width - 50, self.height - 50, 7, fill=1, stroke=0)
        y = self.height - 31
        p = Paragraph(self.kicker, styles["Kicker"])
        _, h = p.wrap(self.width - 52, 24)
        p.drawOn(c, 25, y - h)
        y -= h + 10
        p = Paragraph(self.title, styles["HeroTitle"])
        _, h = p.wrap(self.width - 60, 90)
        p.drawOn(c, 25, y - h)
        y -= h + 8
        p = Paragraph(self.body, styles["HeroBody"])
        _, h = p.wrap(self.width - 50, 58)
        p.drawOn(c, 25, max(16, y - h))


def card(title, body, width):
    data = [[Paragraph(title, styles["CardTitle"])], [Paragraph(body, styles["CardBody"])]]
    t = Table(data, colWidths=[width], rowHeights=[None, 68], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 13),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    w, _ = A4
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 15 * mm, w - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(GREEN)
    canvas.drawString(18 * mm, 10 * mm, "DIGITAL NAGAR PALIKA")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(w - 18 * mm, 10 * mm, f"Hinglish | {doc.page}")
    canvas.restoreState()


class BrochureDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=22 * mm, title="Digital Nagar Palika - Hinglish Brochure", author="Digital Nagar Palika")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="standard", frames=frame, onPage=footer)])


doc = BrochureDoc(OUTPUT)
W = doc.width
story = []

# Page 1 - positioning and value proposition.
story += [
    Hero(W, 204, "NAGAR SEVA. AB AUR AASAN.", "Shahar ki seva,<br/>seedhi aapke phone par.", "Digital Nagar Palika - nagrik services aur municipal operations ke liye ek secure, mobile-first platform foundation. Marathi, Hindi aur English ke liye tayyar; ward se district tak expand karne ke liye designed."),
    Spacer(1, 17),
    Paragraph("Har nagrik ko ek saaf raasta. Har adhikari ko ek accountable workflow.", styles["Section"]),
    Paragraph("Phone par complaint ya service request. Office mein triage, assignment, approval aur audit. Maqsad hai process ko simple banana - bina official decision ya citizen data par control kam kiye.", styles["Intro"]),
]
gap = 10
cw = (W - 2 * gap) / 3
row = [
    card("Nagrik ke liye", "Complaint, status, notices, services aur verified contacts - ek easy mobile experience ke vision ke saath.", cw),
    card("Municipal team ke liye", "Ward-scoped work queues, approvals, records aur audit trail - role ke mutabik access.", cw),
    card("Leadership ke liye", "Ward aur department level par actionable aggregates; sensitive citizen records par least privilege.", cw),
]
grid = Table([row], colWidths=[cw, cw, cw], hAlign="LEFT")
grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), gap)]))
story += [grid, Spacer(1, 16)]
strip = Table([[Paragraph("MOBILE-FIRST", styles["CenterSmall"]), Paragraph("3 BHASHAON KA SUPPORT", styles["CenterSmall"]), Paragraph("WARD-SCOPED ACCESS", styles["CenterSmall"]), Paragraph("AUDIT-READY DESIGN", styles["CenterSmall"])]], colWidths=[W / 4] * 4, rowHeights=[34])
strip.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), MINT), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
story += [strip, Spacer(1, 7), Paragraph("Platform foundation - features municipality configuration, integrations aur phased implementation ke saath activate honge.", styles["Footer"]), PageBreak()]

# Page 2 - workflow and operational model.
story += [
    Paragraph("Service ka safar - citizen se resolution tak", styles["Section"]),
    Paragraph("Ek complaint ko phone se field action aur citizen feedback tak trace karne ka clear workflow.", styles["Intro"]),
]
steps = [
    ("01  REPORT", "Nagrik category, description aur location deta hai. QR se area choose hota hai - private household data nahi khulta."),
    ("02  TRIAGE", "Authorized team complaint ko ward/department ke hisaab se dekhti aur zimmedar officer ko assign karti hai."),
    ("03  ACTION", "Field officer work update, notes aur evidence record karta hai; har status change audit hota hai."),
    ("04  CLOSE THE LOOP", "Nagrik update dekhta hai, outcome par feedback de sakta hai aur zarurat par issue reopen kar sakta hai."),
]
step_rows = []
for title, body in steps:
    step_rows.append([Paragraph(title, styles["CardTitle"]), Paragraph(body, styles["BodySmall"])])
step_table = Table(step_rows, colWidths=[37 * mm, W - 37 * mm], rowHeights=[49] * 4)
step_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), WHITE),
    ("BOX", (0, 0), (-1, -1), 0.6, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("TEXTCOLOR", (0, 0), (0, -1), GREEN),
    ("BACKGROUND", (0, 0), (0, -1), MINT),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 11),
    ("RIGHTPADDING", (0, 0), (-1, -1), 11),
]))
story += [step_table, Spacer(1, 17), Paragraph("Ek hi platform. Kaam ke hisaab se modules.", styles["Section"])]
module_cards = [
    card("Citizen services", "Complaints, announcements, service catalogue, schemes, feedback aur notifications.", cw),
    card("Municipal operations", "Household verification, ward dashboards, documents, field visits aur approvals.", cw),
    card("Future-ready", "GIS layers, payment adapters, AI-assisted trends aur taluka/district aggregates.", cw),
]
mg = Table([module_cards], colWidths=[cw, cw, cw])
mg.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), gap)]))
story += [mg, Spacer(1, 13)]
callout = Table([[Paragraph("AI madad kare - faisla adhikari ka", styles["CardTitle"]), Paragraph("AI complaint sort, trends summarize aur approved knowledge se jawab draft kar sakta hai. Eligibility, rejection, approval ya legal decision authorized official hi karega.", styles["CardBody"])]], colWidths=[48 * mm, W - 48 * mm])
callout.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF5E6")), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#F0D7AF")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
story += [callout, PageBreak()]

# Page 3 - trust, implementation and the sales close.
story += [
    Paragraph("Trust pe bana platform. Ground reality ke saath rollout.", styles["Section"]),
    Paragraph("Government technology mein bharosa slogans se nahi - scoped access, approved content, tested recovery aur accountable operations se banta hai.", styles["Intro"]),
]
trust = [
    [Paragraph("DATA KI HIFAZAT", styles["CardTitle"]), Paragraph("Least-privilege roles, tenant/ward scope, masking, audit aur private document handling ke liye architecture.", styles["CardBody"])],
    [Paragraph("OFFICIAL CONTROL", styles["CardTitle"]), Paragraph("Emergency contacts, schemes aur notices verified source aur municipal approval ke baad hi publish hon.", styles["CardBody"])],
    [Paragraph("RECOVERY READY", styles["CardTitle"]), Paragraph("Encrypted backup, monitoring, incident process aur restore rehearsal ko deployment gate banayein.", styles["CardBody"])],
]
trust_table = Table(trust, colWidths=[43 * mm, W - 43 * mm], rowHeights=[50] * 3)
trust_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), WHITE), ("BACKGROUND", (0, 0), (0, -1), MINT), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
story += [trust_table, Spacer(1, 17), Paragraph("Pilot se scale tak - measured steps", styles["Section"])]
phases = [
    [Paragraph("1. DISCOVER", styles["CardTitle"]), Paragraph("Processes, data policy, official sources, roles aur integrations map karein.", styles["CardBody"])],
    [Paragraph("2. CONFIGURE", styles["CardTitle"]), Paragraph("Municipality branding, wards, services, languages aur approval flows set karein.", styles["CardBody"])],
    [Paragraph("3. PILOT", styles["CardTitle"]), Paragraph("Synthetic data se security, access, usability, backup aur staff training validate karein.", styles["CardBody"])],
    [Paragraph("4. EXPAND", styles["CardTitle"]), Paragraph("Authorized production gate ke baad modules aur phir taluka/district aggregates rollout karein.", styles["CardBody"])],
]
phase_table = Table([phases], colWidths=[W / 4] * 4)
phase_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 11), ("BOTTOMPADDING", (0, 0), (-1, -1), 11)]))
story += [phase_table, Spacer(1, 17)]
cta = Table([[Paragraph("Aapki Nagar Palika ka agla kadam?", styles["WhiteTitle"]), Paragraph("Ek discovery workshop schedule karein. Pehle workflow aur data policy samjhein; phir scoped pilot, acceptance criteria aur deployment plan tayyar karein.", styles["WhiteBody"])]], colWidths=[54 * mm, W - 54 * mm])
cta.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), DEEP), ("BOX", (0, 0), (-1, -1), 0, DEEP), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 13), ("BOTTOMPADDING", (0, 0), (-1, -1), 13)]))
story += [cta, Spacer(1, 8), Paragraph("Imandaar vaada: koi software 0 failure guarantee nahi kar sakta. Humara focus hai failure ko detect, contain, recover aur learn karne layak system banana.", styles["Footer"]), Spacer(1, 6), Paragraph("Note: yeh platform foundation aur proposed delivery vision ka brochure hai. Login, live municipal integrations, production workflows aur provider configuration rollout scope mein implement aur verify hone baaki hain.", styles["Footer"])]

doc.build(story)
print(OUTPUT)
