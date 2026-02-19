import os
import asyncio
import aiohttp
import aiofiles
import pandas as pd
from tqdm import tqdm
from urllib.parse import quote
from PIL import Image
from io import BytesIO

# ==========================
# USER INPUT
# ==========================

PIXABAY_API_KEY = input("Enter your Pixabay API Key:\n").strip()

if not PIXABAY_API_KEY:
    print("API Key required.")
    exit()

while True:
    CSV_FILE = input(
        "\nEnter full path of your CSV file:\n"
    ).strip('"')

    if os.path.isfile(CSV_FILE):
        break
    else:
        print("File not found. Try again.")

DOWNLOAD_FOLDER = input(
    "\nEnter download folder (Press Enter for 'country_images'):\n"
).strip()

if not DOWNLOAD_FOLDER:
    DOWNLOAD_FOLDER = "country_images"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ==========================
# LOAD CSV
# ==========================

df = pd.read_csv(CSV_FILE)

if "Country" not in df.columns or "Place" not in df.columns:
    raise Exception("CSV must contain 'Country' and 'Place' headers")

print(f"\nTotal rows: {len(df)}\n")

# ==========================
# CONFIG
# ==========================

CONCURRENT_REQUESTS = 10
RETRY_LIMIT = 3
MAX_WIDTH = 1920
WEBP_QUALITY = 85

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

# ==========================
# FETCH IMAGE FROM PIXABAY
# ==========================

async def fetch_image_url(session, query):
    url = "https://pixabay.com/api/"

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": 3,
        "safesearch": "true"
    }

    for _ in range(RETRY_LIMIT):
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    hits = data.get("hits", [])
                    if hits:
                        return hits[0]["largeImageURL"]
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

                    # Open image
                    img = Image.open(BytesIO(image_bytes))

                    # Resize if needed
                    if img.width > MAX_WIDTH:
                        ratio = MAX_WIDTH / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

                    # Convert to WebP
                    webp_path = filepath.replace(".jpg", ".webp")
                    img.save(webp_path, "WEBP", quality=WEBP_QUALITY)

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
        filename = f"{safe_country}_{safe_place}.jpg"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        webp_path = filepath.replace(".jpg", ".webp")

        # Skip if WebP already exists
        if os.path.exists(webp_path):
            return "Skipped"

        query = f"{place}, {country}"

        image_url = await fetch_image_url(session, query)

        if image_url:
            success = await download_and_convert(session, image_url, filepath)
            return "Downloaded" if success else "Failed"
        else:
            return "No Image"

# ==========================
# MAIN
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
