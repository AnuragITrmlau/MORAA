"""Test the frontend Gemini analysis route with the test ring image."""
import base64
import httpx

with open("test_ring.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {"imageBase64": b64, "mimeType": "image/png"}

r = httpx.post("http://localhost:3000/api/gemini/analyze", json=payload, timeout=120)
print("HTTP:", r.status_code)
data = r.json()
print("success:", data.get("success"))
if data.get("success"):
    d = data.get("data") or {}
    print("category:", d.get("category"))
    print("jewelleryType:", d.get("jewelleryType"))
    print("metalDetection:", d.get("metalDetection"))
    print("gemstoneDetection:", d.get("gemstoneDetection"))
    print("model:", (data.get("metadata") or {}).get("model"))
else:
    print("error:", data.get("error"))
