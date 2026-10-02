"""Generate fictional sample handbooks (English + German) for testing the app."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

EN = ("Nordlicht Robotics - Employee Handbook", [
    ("1. Paid leave", [
        "Every employee receives 28 days of paid leave per year.",
        "Up to 5 unused leave days can be carried over into the next year.",
        "Leave requests must be submitted at least 10 days in advance."]),
    ("2. Working hours", [
        "The standard working week is 38 hours.",
        "Core hours, when everyone must be available, are 10:00 to 15:00.",
        "Employees may work from home up to 3 days per week."]),
    ("3. Business travel", [
        "Travel costs are refunded within 14 days after the expense report is filed.",
        "Meals during business trips are capped at 45 euros per day.",
        "Hotel stays are limited to 120 euros per night."]),
    ("4. Equipment and IT", [
        "Laptops are replaced every 3 years.",
        "A broken laptop must be reported to the IT helpdesk within 2 days.",
        "The IT helpdesk phone extension is 4400."]),
    ("5. Learning budget", [
        "Each employee has a learning budget of 1,500 euros per year for courses and conferences.",
        "Courses above 500 euros need approval from the team lead."]),
])
DE = ("Nordlicht Robotics - Mitarbeiterhandbuch", [
    ("1. Bezahlter Urlaub", [
        "Jeder Mitarbeiter erhält 28 Tage bezahlten Urlaub pro Jahr.",
        "Bis zu 5 nicht genommene Urlaubstage können ins nächste Jahr übertragen werden.",
        "Urlaubsanträge müssen mindestens 10 Tage im Voraus gestellt werden."]),
    ("2. Arbeitszeit", [
        "Die reguläre Wochenarbeitszeit beträgt 38 Stunden.",
        "Die Kernzeit, in der alle erreichbar sein müssen, ist von 10:00 bis 15:00 Uhr.",
        "Mitarbeiter dürfen bis zu 3 Tage pro Woche im Homeoffice arbeiten."]),
    ("3. Dienstreisen", [
        "Reisekosten werden innerhalb von 14 Tagen nach Einreichung der Abrechnung erstattet.",
        "Mahlzeiten auf Dienstreisen sind auf 45 Euro pro Tag begrenzt.",
        "Hotelübernachtungen sind auf 120 Euro pro Nacht begrenzt."]),
    ("4. Ausstattung und IT", [
        "Laptops werden alle 3 Jahre ersetzt.",
        "Ein defekter Laptop muss innerhalb von 2 Tagen beim IT-Helpdesk gemeldet werden.",
        "Die Durchwahl des IT-Helpdesks ist 4400."]),
    ("5. Weiterbildungsbudget", [
        "Jeder Mitarbeiter hat ein Weiterbildungsbudget von 1.500 Euro pro Jahr für Kurse und Konferenzen.",
        "Kurse über 500 Euro müssen vom Teamleiter genehmigt werden."]),
])

def build(path, data):
    title, sections = data
    s = getSampleStyleSheet()
    story = [Paragraph(title, s["Title"]), Spacer(1, 12)]
    for head, lines in sections:
        story.append(Paragraph(head, s["Heading2"]))
        for line in lines:
            story.append(Paragraph(line, s["BodyText"]))
        story.append(Spacer(1, 10))
    SimpleDocTemplate(path, pagesize=A4, title=title).build(story)

build("documents/nordlicht_handbook_en.pdf", EN)
build("documents/nordlicht_handbuch_de.pdf", DE)
