#!/usr/bin/env python3
"""Generate unique brand product images for every product using Gemini API.

Every product gets its own distinct image. Organized into 6 category folders
matching the app structure: sodas/, energy/, water/, chips/, candy/, cookies/.

Skips images that already exist on disk.
"""

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

# Every product in the app, with variant-specific prompts.
# Format: { "category": [ ("filename.jpg", "detailed description"), ... ] }
BRANDS = {
    "sodas": [
        ("coca-cola.jpg", "Coca-Cola Classic 12oz red aluminum can with white Coca-Cola script logo"),
        ("coke-zero.jpg", "Coke Zero Sugar 12oz can, BLACK can with red Coca-Cola Zero Sugar logo"),
        ("diet-coke.jpg", "Diet Coke 12oz can, SILVER/GRAY can with Diet Coke logo in red"),
        ("sprite.jpg", "Sprite 12oz can, green and silver can with Sprite logo and lemon-lime imagery"),
        ("sprite-zero.jpg", "Sprite Zero Sugar 12oz can, dark green/black can with Sprite Zero logo"),
        ("pepsi.jpg", "Pepsi 12oz can, blue can with red/white/blue Pepsi globe logo"),
        ("pepsi-zero.jpg", "Pepsi Zero Sugar 12oz can, BLACK can with Pepsi Zero Sugar logo"),
        ("diet-pepsi.jpg", "Diet Pepsi 12oz can, SILVER/LIGHT BLUE can with Diet Pepsi logo"),
        ("dr-pepper.jpg", "Dr Pepper 12oz can, dark maroon/red can with Dr Pepper logo"),
        ("diet-dr-pepper.jpg", "Diet Dr Pepper 12oz can, lighter maroon/silver can with Diet Dr Pepper text"),
        ("dr-pepper-zero.jpg", "Dr Pepper Zero Sugar 12oz can, dark maroon/black can with Dr Pepper Zero Sugar logo"),
        ("mountain-dew.jpg", "Mountain Dew 12oz can, bright green can with Mountain Dew logo"),
        ("diet-mtn-dew.jpg", "Diet Mountain Dew 12oz can, lighter green/silver can with Diet Mtn Dew text"),
        ("aw-root-beer.jpg", "A&W Root Beer 12oz can, brown/orange can with A&W Root Beer bullseye logo"),
        ("canada-dry.jpg", "Canada Dry Ginger Ale 12oz can, green can with Canada Dry shield logo"),
        ("fanta.jpg", "Fanta Orange 12oz can, bright orange can with Fanta logo and orange fruit"),
        ("olipop.jpg", "Olipop prebiotic soda can, colorful vintage-styled slim can with Olipop logo"),
    ],
    "energy": [
        ("monster-original.jpg", "Monster Energy Original 16oz can, BLACK can with green Monster M claw logo"),
        ("monster-zero-ultra.jpg", "Monster Zero Ultra 16oz can, WHITE can with silver/white Monster M claw logo"),
        ("monster-lo-carb.jpg", "Monster Lo-Carb 16oz can, dark BLUE can with blue Monster M claw logo"),
        ("monster-zero-sugar.jpg", "Monster Zero Sugar 16oz can, black can with green Monster M logo and Zero Sugar text"),
        ("redbull.jpg", "Red Bull Energy Drink 8.4oz can, blue/silver can with Red Bull logo and two red bulls"),
        ("redbull-sugar-free.jpg", "Red Bull Sugar Free 8.4oz can, blue/SILVER can with Red Bull Sugar Free text"),
        ("celsius-kiwi-guava.jpg", "Celsius Live Fit Kiwi Guava flavor 12oz can, GREEN can with kiwi and guava fruit"),
        ("celsius-orange.jpg", "Celsius Live Fit Sparkling Orange flavor 12oz can, ORANGE can with orange fruit imagery"),
        ("celsius-watermelon.jpg", "Celsius Live Fit Watermelon flavor 12oz can, PINK/RED can with watermelon imagery"),
        ("celsius-peach-vibe.jpg", "Celsius Peach Vibe 12oz can, PEACH colored can with Celsius Vibe branding"),
        ("celsius-tropical-vibe.jpg", "Celsius Tropical Vibe 12oz can, YELLOW/TROPICAL colored can with Celsius Vibe branding"),
        ("celsius-retro-vibe.jpg", "Celsius Retro Vibe 12oz can, RETRO styled purple/pink can with Celsius Vibe branding"),
        ("alani-nu.jpg", "Alani Nu energy drink slim can, pastel colored can with Alani Nu script logo"),
        ("nos.jpg", "NOS energy drink 16oz can, blue can with NOS logo and flame graphics"),
        ("gatorade-lemon-lime.jpg", "Gatorade Lemon Lime 20oz bottle, GREEN/YELLOW bottle with Gatorade lightning bolt logo"),
        ("gatorade-orange.jpg", "Gatorade Orange 20oz bottle, ORANGE bottle with Gatorade lightning bolt logo"),
        ("gatorade-fruit-punch.jpg", "Gatorade Fruit Punch 20oz bottle, RED/PINK bottle with Gatorade lightning bolt logo"),
        ("gatorade-glacier-freeze.jpg", "Gatorade Glacier Freeze 20oz bottle, LIGHT BLUE bottle with Gatorade lightning bolt logo"),
        ("gatorade-zero.jpg", "Gatorade Zero Sugar 20oz bottle, BLACK label bottle with Gatorade Zero branding"),
        ("powerade.jpg", "Powerade sports drink 20oz bottle, blue bottle with Powerade logo"),
        ("bodyarmor.jpg", "BodyArmor sports drink bottle, dark bottle with BodyArmor shield logo"),
    ],
    "water": [
        ("aquafina.jpg", "Aquafina purified water 16.9oz bottle, clear bottle with blue Aquafina label"),
        ("dasani.jpg", "Dasani purified water 16.9oz bottle, clear bottle with blue Dasani label"),
        ("members-mark.jpg", "Member's Mark purified water bottle, clear bottle with blue Member's Mark label"),
        ("lacroix.jpg", "LaCroix sparkling water can, white can with colorful LaCroix logo"),
        ("bubly.jpg", "Bubly sparkling water can, colorful can with bubly lowercase logo and smile face"),
        ("perrier.jpg", "Perrier sparkling mineral water green glass bottle with Perrier label"),
        ("arizona-green-tea.jpg", "Arizona Green Tea 23oz tall can, green can with cherry blossom artwork and Japanese characters"),
    ],
    "chips": [
        ("lays-classic.jpg", "Lay's Classic Original potato chips bag, YELLOW bag with Lay's logo"),
        ("lays-bbq.jpg", "Lay's BBQ flavor potato chips bag, DARK RED/BROWN bag with Lay's BBQ text"),
        ("lays-sour-cream.jpg", "Lay's Sour Cream & Onion potato chips bag, GREEN bag with Lay's logo"),
        ("doritos-nacho.jpg", "Doritos Nacho Cheese tortilla chips bag, RED bag with Doritos triangle logo"),
        ("doritos-cool-ranch.jpg", "Doritos Cool Ranch tortilla chips bag, BLUE bag with Doritos logo"),
        ("cheetos-crunchy.jpg", "Cheetos Crunchy cheese snacks bag, ORANGE bag with Chester Cheetah"),
        ("cheetos-flamin-hot.jpg", "Cheetos Flamin' Hot snacks bag, RED/BLACK bag with Chester Cheetah and flames"),
        ("cheetos-puffs.jpg", "Cheetos Puffs cheese snacks bag, ORANGE bag with Chester Cheetah and Puffs text"),
        ("fritos.jpg", "Fritos Original corn chips bag, yellow bag with Fritos logo"),
        ("ruffles.jpg", "Ruffles Original ridged potato chips bag, dark blue bag with Ruffles logo"),
        ("takis-fuego.jpg", "Takis Fuego rolled tortilla chips bag, purple bag with Takis logo and flames"),
        ("sunchips.jpg", "SunChips Harvest Cheddar bag, golden/brown bag with SunChips logo"),
        ("veggie-straws.jpg", "Sensible Portions Veggie Straws bag, green bag with colorful straw chips"),
    ],
    "candy": [
        ("snickers.jpg", "Snickers candy bar in wrapper, brown wrapper with Snickers logo and caramel/peanut"),
        ("reeses.jpg", "Reese's Peanut Butter Cups package, orange wrapper with Reese's logo"),
        ("kitkat.jpg", "KitKat candy bar in red wrapper with KitKat logo"),
        ("twix.jpg", "Twix candy bar in gold wrapper with Twix logo"),
        ("butterfinger.jpg", "Butterfinger candy bar in bright yellow wrapper with Butterfinger logo"),
        ("milky-way.jpg", "Milky Way candy bar in brown/blue wrapper with Milky Way logo"),
        ("3-musketeers.jpg", "3 Musketeers candy bar in silver/blue wrapper with 3 Musketeers logo"),
        ("mms-milk.jpg", "M&M's Milk Chocolate bag, BROWN bag with M&M's characters and Milk Chocolate text"),
        ("mms-peanut.jpg", "M&M's Peanut bag, YELLOW bag with M&M's characters and Peanut text"),
        ("skittles.jpg", "Skittles candy bag, red bag with Skittles rainbow logo"),
        ("hersheys-milk.jpg", "Hershey's Milk Chocolate bar, BROWN wrapper with silver Hershey's text"),
        ("hersheys-cookies.jpg", "Hershey's Cookies 'n' Creme bar, WHITE wrapper with Cookies 'n' Creme text"),
        ("hersheys-almonds.jpg", "Hershey's with Almonds bar, BROWN wrapper with Almonds text and almond imagery"),
    ],
    "cookies": [
        ("oreos.jpg", "Oreos chocolate sandwich cookies package, dark blue Oreo package with cookie image"),
        ("oreos-golden.jpg", "Golden Oreos package, GOLD/YELLOW package with Golden Oreo cookie image"),
        ("chips-ahoy.jpg", "Chips Ahoy chocolate chip cookies blue package with cookie and chocolate chips"),
        ("famous-amos.jpg", "Famous Amos chocolate chip cookies brown bag with Famous Amos logo"),
        ("planters-cashews.jpg", "Planters Cashews container, blue/yellow container with Mr. Peanut and Cashews text"),
        ("planters-peanuts.jpg", "Planters Dry Roasted Peanuts jar, blue/yellow jar with Mr. Peanut and Peanuts text"),
        ("planters-honey.jpg", "Planters Honey Roasted Peanuts jar, YELLOW jar with Mr. Peanut and honey imagery"),
        ("nature-valley-oats.jpg", "Nature Valley Oats 'n Honey granola bar box, GREEN box with Nature Valley logo"),
        ("nature-valley-sweet.jpg", "Nature Valley Sweet & Salty Nut bar box, DARK BLUE box with Nature Valley logo"),
        ("nature-valley-pb.jpg", "Nature Valley Peanut Butter Dark Chocolate bar box, BROWN box with Nature Valley logo"),
        ("kind-bar.jpg", "KIND bar, clear wrapper showing nuts and grains with KIND logo"),
        ("rxbar.jpg", "RXBAR protein bar, minimal design wrapper with RXBAR logo and ingredients listed"),
    ],
}

PROMPT_PREFIX = "Professional product photo on a clean white background, studio lighting, front-facing, centered, e-commerce product photography. Show the complete product packaging clearly. The product is: "


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
    total = sum(len(brands) for brands in BRANDS.values())
    done = 0
    failed = []
    skipped = 0

    print(f"Checking {total} product images...")
    print(f"=" * 50)

    for category, brands in BRANDS.items():
        cat_dir = os.path.join(BASE_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        print(f"\n[{category.upper()}]")

        for filename, description in brands:
            done += 1
            output_path = os.path.join(cat_dir, filename)

            # Skip if image already exists
            if os.path.exists(output_path):
                print(f"  ({done}/{total}) {filename}... SKIP (exists)")
                skipped += 1
                continue

            prompt = PROMPT_PREFIX + description

            sys.stdout.write(f"  ({done}/{total}) {filename}... ")
            sys.stdout.flush()

            success, result = generate_image(prompt, output_path)

            if success:
                os.system(f'sips -s format jpeg -Z 400 "{output_path}" --out "{output_path}" 2>/dev/null')
                size_kb = os.path.getsize(output_path) // 1024
                print(f"OK ({size_kb}K)")
            else:
                print(f"FAILED: {result}")
                failed.append((category, filename, result))

            time.sleep(1)

    print(f"\n{'=' * 50}")
    print(f"Total: {total} products")
    print(f"Already existed: {skipped}")
    print(f"Generated: {done - len(failed) - skipped}")
    if failed:
        print(f"Failed ({len(failed)}):")
        for cat, fn, err in failed:
            print(f"  {cat}/{fn}: {err}")
    else:
        print("No failures!")


if __name__ == "__main__":
    main()
