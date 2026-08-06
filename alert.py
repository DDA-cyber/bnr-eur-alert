import os
import requests
import xml.etree.ElementTree as ET

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

LIMIT = 5.18

url = "https://www.bnr.ro/nbrfxrates.xml"

xml = requests.get(url, timeout=30).content

root = ET.fromstring(xml)

namespace = {"ns": "http://www.bnr.ro/xsd"}

eur = None

for rate in root.findall(".//ns:Rate", namespace):
    if rate.attrib.get("currency") == "EUR":
        eur = float(rate.text)
        break

if eur is None:
    raise Exception("Nu am găsit cursul EUR.")

if eur >= LIMIT:
    text = f"🚨 ALERTĂ BNR\n\nEUR = {eur:.4f} RON\nPragul de 5.18 a fost depășit."

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

print(eur)
