"""E2E generation test: reference ring -> backend -> provider -> generated image."""
import base64
import httpx

with open("test_ring.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

prompt = (
    "Professional product photography. A gold ring with a single round red "
    "gemstone presented in a premium studio setting. Scene concept: "
    "contemporary luxury aesthetic. Background: clean, minimal surface "
    "complementing the product's material qualities. Studio lighting with "
    "controlled shadows highlighting texture and craftsmanship. Composition: "
    "hero angle, product centered with balanced negative space. Camera: 50mm "
    "f/2.8 macro lens, shallow depth of field for product isolation. High "
    "resolution, sharp focus on product details. No text, no watermarks, no "
    "human models. Aspect ratio 4:5."
)

payload = {
    "prompt": prompt,
    "aspect_ratio": "4:5",
    "reference_image": b64,
    "reference_mime_type": "image/png",
}

r = httpx.post("http://localhost:8000/api/generate-image", json=payload, timeout=240)
print("HTTP:", r.status_code)
data = r.json()
print("success:", data.get("success"))
print("provider:", data.get("provider"))
print("fallback_used:", data.get("fallback_used"))
print("model_used:", data.get("model_used"))
print("generation_time:", data.get("generation_time"))
print("error:", data.get("error"))

url = data.get("image_url") or ""
if url.startswith("data:"):
    img_b64 = url.split(",", 1)[1]
    raw = base64.b64decode(img_b64)
    with open("generated_ring.png", "wb") as f:
        f.write(raw)
    print("saved generated_ring.png bytes:", len(raw))
else:
    print("no image returned")
