import os
import requests

url = "https://www.bnr.ro/files/xml/years/nbrfxrates2026.xml"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

print("Status:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))
print("Primele 500 caractere:")
print(response.text[:500])

raise Exception("STOP - Debug")
