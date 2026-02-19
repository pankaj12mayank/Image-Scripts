import os
import asyncio
import aiohttp
import pandas as pd
from tqdm import tqdm
from urllib.parse import quote
from PIL import Image
from io import BytesIO

# ==========================
# USER INPUT SECTION
# ==========================

PEXELS_API_KEY = input("Enter your Pexels API Key:\n").strip()

if not PEXELS_API_KEY:
    print("API Key is required.")
    exit()

while True:
    CSV_FILE = input(
        "\nEnter full path of your CSV file:\n"
    ).strip('"')

    if os.path.isfile(CSV_FILE):
        print(f"\nFile found: {CSV_FILE}\n")
        break
    else:
        print("File not found. Please check and try again.\n")

DOWNLOAD_FOLDER = input(
    "\nEnter download folder path (press Enter to use default 'country_images'):\n"
).strip()

if not DOWNLOAD_FOLDER:
    DOWNLOAD_FOLDER = "country_images"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ==========================
# LOAD CSV
# ==========================

try:
    df = pd.read_csv(CSV_FILE)

    if "Country" not in df.columns or "Place" not in df.columns:
        raise Exception("CSV must contain 'Country' and 'Place' headers")

    print(f"CSV loaded successfully. Total rows: {len(df)}\n")

except Exception as e:
    print("Error loading CSV:", e)
    exit()

# ==========================
# CONFIG
# ==========================

CONCURRENT_REQUESTS = 10
RETRY_LIMIT = 3
MAX_WIDTH = 1920
WEBP_QUALITY = 85

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

# ==========================
# FETCH IMAGE URL
# ==========================

async def fetch_image_url(session, query):
    url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=1&orientation=landscape"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    for _ in range(RETRY_LIMIT):
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    photos = data.get("photos", [])
                    if photos:
                        return photos[0]["src"]["original"]
                await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)

    return None

# ==========================
# DOWNLOAD + CONVERT TO WEBP
# ==========================

async def download_and_convert(session, image_url, filepath):
    for _ in range(RETRY_LIMIT):
        try:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_bytes = await response.read()

                    img = Image.open(BytesIO(image_bytes)).convert("RGB")

                    # Resize if wider than MAX_WIDTH
                    if img.width > MAX_WIDTH:
                        ratio = MAX_WIDTH / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

                    # Save as WebP
                    img.save(filepath, "WEBP", quality=WEBP_QUALITY, method=6)

                    return True
                await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)

    return False

# ==========================
# PROCESS EACH ROW
# ==========================

async def process_row(session, country, place):
    async with semaphore:

        safe_country = country.replace(" ", "_")
        safe_place = place.replace(" ", "_")

        filename = f"{safe_country}_{safe_place}.webp"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        # Skip if already exists
        if os.path.exists(filepath):
            return "Skipped"

        query = f"{place}, {country}"

        image_url = await fetch_image_url(session, query)

        if image_url:
            success = await download_and_convert(session, image_url, filepath)
            return "Downloaded" if success else "Failed"
        else:
            return "No Image"

# ==========================
# MAIN EXECUTION
# ==========================

async def main():
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:

        tasks = []
        for _, row in df.iterrows():
            country = str(row["Country"]).strip()
            place = str(row["Place"]).strip()
            tasks.append(process_row(session, country, place))

        results = []
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            result = await f
            results.append(result)

        print("\n========== SUMMARY ==========")
        print("Downloaded:", results.count("Downloaded"))
        print("Skipped:", results.count("Skipped"))
        print("No Image:", results.count("No Image"))
        print("Failed:", results.count("Failed"))
        print("=============================")

# ==========================

if __name__ == "__main__":
    asyncio.run(main())
