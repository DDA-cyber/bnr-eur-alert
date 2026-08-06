import os
import requests
import xml.etree.ElementTree as ET

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

LIMIT = 5.18

url = "https://www.bnr.ro/nbrfxrates.xml"

response = requests.get(
    url,
    timeout=30,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print("Status:", response.status_code)
print(response.text[:300])

response.raise_for_status()

xml = response.content

root = ET.fromstring(xml)

namespace = {"ns": "http://www.bnr.ro/xsd"}

eur = None

for rate in root.findall(".//ns:Rate", namespace):
    if rate.attrib.get("currency") == "EUR":
        eur = float(rate.text)
        break

if eur is None:
    raise Exception("Nu am găsit cursul EUR.")

print(f"Curs EUR: {eur}")

if eur >= LIMIT:
    text = (
        f"🚨 ALERTĂ BNR\n\n"
        f"EUR = {eur:.4f} RON\n"
        f"A depășit pragul de {LIMIT:.2f}."
    )

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

print("Script terminat.")
