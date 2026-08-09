import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from config import LIMIT, CURRENCY, TARGET_CURRENCY, MAX_HISTORY


# ==============================
# CONFIGURARE INTERNĂ
# ==============================

DATA_FILE = "eur_data.json"

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.bnr.ro/nbrfxrates.xml"


# ==============================
# CURS BNR
# ==============================

def get_eur_rate():

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    print("Status:", response.status_code)

    response.raise_for_status()

    root = ET.fromstring(response.content)

    namespace = {
        "ns": "http://www.bnr.ro/xsd"
    }

    for rate in root.findall(
        ".//ns:Rate",
        namespace
    ):

        if rate.attrib.get("currency") == CURRENCY:

            return float(rate.text)

    raise Exception(
        "Nu am găsit cursul EUR în XML."
    )


# ==============================
# DATE / ISTORIC
# ==============================

def load_data():

    if not os.path.exists(DATA_FILE):

        return {
            "last_rate": None,
            "history": []
        }

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if "last_rate" not in data:
            data["last_rate"] = None

        if "history" not in data:
            data["history"] = []

        return data

    except Exception:

        return {
            "last_rate": None,
            "history": []
        }


def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def add_history(data, rate):

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    data["history"].append(
        {
            "timestamp": timestamp,
            "currency": CURRENCY,
            "target": TARGET_CURRENCY,
            "rate": rate
        }
    )

    data["history"] = data["history"][
        -MAX_HISTORY:
    ]

    data["last_rate"] = rate


# ==============================
# TELEGRAM
# ==============================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()

    print("📱 Notificare Telegram trimisă.")


# ==============================
# PROGRAM PRINCIPAL
# ==============================

def main():

    print("💶 Verific cursul EUR/RON...")

    current_rate = get_eur_rate()

    data = load_data()

    previous_rate = data["last_rate"]

    print(
        f"💶 EUR = "
        f"{current_rate:.4f} RON"
    )

    print(
        f"🔔 Prag = "
        f"{LIMIT:.2f} RON"
    )


    # ==============================
    # PRIMA RULARE
    # ==============================

    if previous_rate is None:

        print(
            "ℹ️ Prima verificare."
        )

        add_history(
            data,
            current_rate
        )

        save_data(data)

        if current_rate >= LIMIT:

            message = (
                "🚨 ALERTĂ EUR/RON\n\n"
                f"💶 EUR = "
                f"{current_rate:.4f} RON\n"
                f"🔔 Prag = "
                f"{LIMIT:.2f} RON\n\n"
                "⚠️ Cursul este peste "
                "pragul stabilit."
            )

            send_telegram(message)

        return


    # ==============================
    # CURS NESCHIMBAT
    # ==============================

    if current_rate == previous_rate:

        print(
            "➡️ Cursul nu s-a schimbat."
        )

        add_history(
            data,
            current_rate
        )

        save_data(data)

        return


    # ==============================
    # CURS ÎN CREȘTERE
    # ==============================

    if current_rate > previous_rate:

        difference = (
            current_rate - previous_rate
        )

        message = (
            "📈 EUR/RON ÎN CREȘTERE\n\n"
            f"💶 Curs nou: "
            f"{current_rate:.4f} RON\n"
            f"⬆️ Creștere: "
            f"{difference:.4f} RON\n"
            f"📊 Curs anterior: "
            f"{previous_rate:.4f} RON"
        )

        if current_rate >= LIMIT:

            message += (
                f"\n\n🚨 Prag depășit: "
                f"{LIMIT:.2f} RON"
            )

        send_telegram(message)


    # ==============================
    # CURS ÎN SCĂDERE
    # ==============================

    elif current_rate < previous_rate:

        difference = (
            previous_rate - current_rate
        )

        message = (
            "📉 EUR/RON ÎN SCĂDERE\n\n"
            f"💶 Curs nou: "
            f"{current_rate:.4f} RON\n"
            f"⬇️ Scădere: "
            f"{difference:.4f} RON\n"
            f"📊 Curs anterior: "
            f"{previous_rate:.4f} RON"
        )

        if (
            previous_rate >= LIMIT
            and current_rate < LIMIT
        ):

            message += (
                f"\n\n✅ A coborât sub "
                f"pragul de {LIMIT:.2f} RON"
            )

        send_telegram(message)


    # ==============================
    # SALVARE
    # ==============================

    add_history(
        data,
        current_rate
    )

    save_data(data)

    print(
        f"💾 Istoric: "
        f"{len(data['history'])} valori"
    )

    print("✅ Script terminat.")


if __name__ == "__main__":
    main()
