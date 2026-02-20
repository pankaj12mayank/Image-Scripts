# Bulk Country Places Image Downloader

High-resolution image downloader using:

* **Pexels API**
* **Pixabay API**
* CSV based bulk processing (195+ countries supported)
* Async fast download
* Auto WebP compression
* Duplicate skip
* Retry handling

---

# Project Overview

This tool downloads **high-quality travel images** for:

```
Country | Place
```

from a CSV file and stores them as:

```
Country_Place.webp
```

Supports:

* 195+ countries
* Thousands of places
* High resolution only
* Automatic WebP conversion
* Async parallel downloading

---

# CSV Format (Required)

Your CSV file must contain:

```csv
Country,Place
India,Taj Mahal
France,Eiffel Tower
Brazil,Christ the Redeemer
```

Column headers must be exactly:

```
Country
Place
```

---

# Requirements

Install dependencies:

```bash
pip install aiohttp aiofiles pandas tqdm pillow
```

---

# API Setup

## Option 1 — 📸 Pexels API

1. Go to: [https://www.pexels.com/api/](https://www.pexels.com/api/)
2. Create free account
3. Generate API key
4. Copy your API key

Free Plan Includes:

* 200 requests/hour
* 20,000 requests/month
* Commercial use allowed

---

## Option 2 — Pixabay API

1. Go to: [https://pixabay.com/api/docs/](https://pixabay.com/api/docs/)
2. Create free account
3. Generate API key

Free Plan Includes:

* 100 requests/minute
* 5,000 requests/hour
* Commercial use allowed

---

# How to Run

```bash
python image_downloader.py
```

You will be prompted for:

1. API Key
2. CSV file path
3. Download folder path

Example:

```
Enter your Pexels API Key:
xxxxx-xxxxxxx

Enter full path of CSV:
C:\Users\panka\Downloads\countries_places.csv

Enter download folder:
C:\Images
```

---

#  Features

### Async Fast Download

Parallel image downloading using asyncio.

### High Resolution Only

* Pexels → `original`
* Pixabay → `largeImageURL`

### Auto WebP Compression

All images automatically converted to:

```
.webp format
Quality optimized
Smaller file size
```

### Auto Skip Duplicates

If file exists → skipped automatically.

### Retry System

Retries failed downloads up to 3 times.

---

#  Output Structure

```
country_images/
 ├── India_Taj_Mahal.webp
 ├── France_Eiffel_Tower.webp
 ├── Brazil_Christ_the_Redeemer.webp
```

---

# Performance

With:

```
CONCURRENT_REQUESTS = 10
```

Expected speed:

* ~100 images in 1–2 minutes (depending on network)
* Handles 195+ countries easily

---

# Configuration (Inside Script)

You can modify:

```python
CONCURRENT_REQUESTS = 10
RETRY_LIMIT = 3
```

To increase performance:

```python
CONCURRENT_REQUESTS = 20
```

(Be careful not to exceed API rate limits.)

---

#  Common Errors

### FileNotFoundError

Check CSV file path is correct.

### API 401 Error

Invalid API key.

### Rate Limit Error

Reduce `CONCURRENT_REQUESTS`.

---

#  When to Use Which API?

| Feature           | Pexels        | Pixabay          |
| ----------------- | ------------- | ---------------- |
| Travel Photos     | ⭐⭐⭐⭐          | ⭐⭐⭐              |
| Landscape Quality | ⭐⭐⭐⭐          | ⭐⭐⭐              |
| API Stability     | ⭐⭐⭐⭐          | ⭐⭐⭐⭐             |
| Speed             | Fast          | Very Fast        |
| Best Overall      | ✅ Recommended | Good Alternative |

---

# Commercial Usage

Both:

* Pexels
* Pixabay

Allow commercial use without attribution (check their license pages for updates).

---

# Recommended Production Setup

For 195+ Countries Project:

* Use **Pexels as Primary**
* Use **Pixabay as Fallback**
* Increase concurrency carefully
* Store images in CDN
* Add caching layer

---

#  Future Enhancements (Optional)

* Dual API fallback system
* Logging to CSV
* Resume from last failed row
* Auto image resizing
* Multi-image download per place
* AI relevance filtering

---

#  Conclusion

This system provides:

✔ Scalable
✔ Cost-effective (Free APIs)
✔ Production-ready
✔ High-resolution
✔ Fully automated

Perfect for:

* Travel portals
* Visa platforms
* Country listing websites
* Tourism apps

---
