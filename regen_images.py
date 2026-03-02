#!/usr/bin/env python3
"""Regenerate specific brand images that didn't come out as clean product shots."""

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
BASE_DIR = "/Users/nickparolini/Desktop/viny-machine-tap/images/brands"

# Images that need regeneration - stronger, more explicit prompts
REGEN = [
    # Chips - these showed loose chips instead of sealed bags
    ("chips", "doritos.jpg",
     "A single sealed bag of Doritos Nacho Cheese tortilla chips, standing upright on a plain white background. "
     "The bag is the iconic red/orange Doritos bag with the triangle Doritos logo. "
     "Product packaging photography, studio lighting, no people, no hands, just the sealed bag."),
    ("chips", "pringles.jpg",
     "A single Pringles Original chips canister standing upright on a plain white background. "
     "The iconic red cylindrical Pringles tube/can with the Pringles logo and mustache mascot Julius Pringles on front. "
     "Product packaging photography, studio lighting, no people, no hands, just the sealed canister."),
    ("chips", "fritos.jpg",
     "A single sealed bag of Fritos Original corn chips standing upright on a plain white background. "
     "The bag is yellow and red with the Fritos logo. "
     "Product packaging photography, studio lighting, no people, no hands, just the sealed bag."),
    ("chips", "sunchips.jpg",
     "A single sealed bag of SunChips Harvest Cheddar multigrain snacks standing upright on a plain white background. "
     "The bag is green with the SunChips sun logo. "
     "Product packaging photography, studio lighting, no people, no hands, just the sealed bag."),
    # Soda - Mountain Dew showed a glass instead of a can
    ("soda", "mountaindew.jpg",
     "A single Mountain Dew 12oz aluminum soda can on a plain white background. "
     "The can is bright green with the Mountain Dew logo and branding. "
     "Product packaging photography, studio lighting, no people, no hands, just the single can."),
    # Water - these showed store shelves or handheld bottles
    ("water", "dasani.jpg",
     "A single Dasani purified water bottle standing upright on a plain white background. "
     "Clear plastic bottle with the blue Dasani label. "
     "Product packaging photography, studio lighting, no people, no hands, just the single bottle."),
    ("water", "aquafina.jpg",
     "A single Aquafina purified drinking water bottle standing upright on a plain white background. "
     "Clear plastic bottle with the blue Aquafina label and mountain design. "
     "Product packaging photography, studio lighting, no people, no hands, just the single bottle."),
    ("water", "smartwater.jpg",
     "A single Smartwater vapor distilled water bottle standing upright on a plain white background. "
     "Tall slim clear bottle with the blue smartwater label. "
     "Product packaging photography, studio lighting, no people, no hands, just the single bottle."),
    ("water", "gatorade.jpg",
     "A single Gatorade Thirst Quencher sports drink bottle standing upright on a plain white background. "
     "The iconic green Gatorade bottle with the orange Gatorade G lightning bolt logo. Lemon Lime flavor. "
     "Product packaging photography, studio lighting, no people, no hands, just the single bottle."),
]

def generate_image(prompt, output_path, retries=2):
    """Generate a single image using Gemini API."""
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
    total = len(REGEN)
    failed = []

    print(f"Regenerating {total} images with improved prompts...")
    print(f"=" * 50)

    for i, (category, filename, prompt) in enumerate(REGEN, 1):
        output_path = os.path.join(BASE_DIR, category, filename)

        sys.stdout.write(f"  ({i}/{total}) {category}/{filename}... ")
        sys.stdout.flush()

        success, result = generate_image(prompt, output_path)

        if success:
            os.system(f'sips -s format jpeg -Z 400 "{output_path}" --out "{output_path}" 2>/dev/null')
            size_kb = os.path.getsize(output_path) // 1024
            print(f"OK ({size_kb}K)")
        else:
            print(f"FAILED: {result}")
            failed.append((category, filename, result))

        time.sleep(1.5)

    print(f"\n{'=' * 50}")
    print(f"Done: {total - len(failed)}/{total} succeeded")
    if failed:
        print(f"Failed ({len(failed)}):")
        for cat, fn, err in failed:
            print(f"  {cat}/{fn}: {err}")


if __name__ == "__main__":
    main()
