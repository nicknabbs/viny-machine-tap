#!/usr/bin/env python3
"""Regenerate category cover images for the new 6-category structure."""

import json
import base64
import urllib.request
import urllib.error
import os
import time
import sys

API_KEY = "AIzaSyBdXHnzg0_H5oYeIASys-6sVM7iS-DYIAE"
MODEL = "gemini-3.1-flash-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
IMG_DIR = "/Users/nickparolini/Desktop/viny-machine-tap/images"

CATEGORIES = [
    ("sodas.jpg",
     "A neat row of colorful soda cans standing upright on a clean white background. "
     "Show 5 different 12oz aluminum soda cans side by side: a red Coca-Cola can, a blue Pepsi can, "
     "a green Sprite can, a dark maroon Dr Pepper can, and a green Mountain Dew can. "
     "Clean product photography, studio lighting, straight-on angle."),
    ("energy-sports.jpg",
     "A row of energy and sports drink containers on a clean white background. "
     "Show 5 different drinks: a black Monster Energy can with green M claw, "
     "a blue and silver Red Bull can, a white Celsius slim can, "
     "a green Gatorade bottle, and a blue Powerade bottle. "
     "Clean product photography, studio lighting."),
    ("water-tea.jpg",
     "A neat row of water and tea bottles on a clean white background. "
     "Show 4 different beverages: a clear Dasani water bottle, a clear Aquafina bottle, "
     "a white LaCroix sparkling water can, and a green Arizona Green Tea tall can with cherry blossom design. "
     "Clean product photography, studio lighting."),
    ("chips.jpg",
     "A flat lay arrangement of popular chip bags on a clean white background. "
     "Show 5 different colorful sealed chip bags arranged neatly: "
     "a yellow Lay's bag, a red Doritos bag, an orange Cheetos bag, a purple Takis bag, and a green SunChips bag. "
     "Bright, clean, overhead product photography with even lighting."),
    ("candy-chocolate.jpg",
     "A neat arrangement of candy bars and candy bags on a clean white background. "
     "Show 5 items: a brown Snickers bar, a red KitKat bar, an orange Reese's package, "
     "a red Skittles bag, and a brown M&M's bag. "
     "Clean product photography, studio lighting."),
    ("cookies-bars-nuts.jpg",
     "A flat lay arrangement of cookie packages, granola bars, and nut containers on a clean white background. "
     "Show 5 items: a blue Oreo package, a blue Chips Ahoy bag, "
     "a green Nature Valley granola bar box, a KIND bar in transparent wrapper, and a Planters peanuts jar. "
     "Bright, clean, overhead product photography."),
]


def generate_image(prompt, output_path, retries=2):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }).encode()

    req = urllib.request.Request(
        f"{URL}?key={API_KEY}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            for p in parts:
                if "inlineData" in p:
                    img_data = base64.b64decode(p["inlineData"]["data"])
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    return True, len(img_data)
            return False, "No image in response"
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                print(f"    Rate limited, waiting 10s...")
                time.sleep(10)
                continue
            return False, f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            if attempt < retries:
                time.sleep(5)
                continue
            return False, str(e)
    return False, "Max retries exceeded"


def main():
    total = len(CATEGORIES)
    failed = []
    print(f"Regenerating {total} category cover images...")
    print("=" * 50)

    for i, (filename, prompt) in enumerate(CATEGORIES, 1):
        output_path = os.path.join(IMG_DIR, filename)
        sys.stdout.write(f"  ({i}/{total}) {filename}... ")
        sys.stdout.flush()

        success, result = generate_image(prompt, output_path)
        if success:
            os.system(f'sips -s format jpeg -Z 600 "{output_path}" --out "{output_path}" 2>/dev/null')
            size_kb = os.path.getsize(output_path) // 1024
            print(f"OK ({size_kb}K)")
        else:
            print(f"FAILED: {result}")
            failed.append((filename, result))
        time.sleep(1.5)

    print(f"\n{'=' * 50}")
    print(f"Done: {total - len(failed)}/{total} succeeded")
    if failed:
        print(f"Failed:")
        for fn, err in failed:
            print(f"  {fn}: {err}")


if __name__ == "__main__":
    main()
