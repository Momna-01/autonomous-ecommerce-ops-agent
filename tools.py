import csv
import requests
from collections import Counter
from crewai.tools import tool
from crewai_tools import SerperDevTool

# Tool 1: SEO keyword research (Serper key chahiye)
seo_search = SerperDevTool()

# Tool 2: Shopify product data (key ki zaroorat nahi)
@tool("Shopify Product Fetcher")
def shopify_product(store_url: str) -> str:
    """Shopify store ke products ka title, price aur type laata hai.
    Input: store ka URL, jaise https://allbirds.com"""
    try:
        r = requests.get(store_url.rstrip("/") + "/products.json?limit=5", timeout=10)
        r.raise_for_status()
        products = r.json().get("products", [])
        if not products:
            return "Koi product nahi mila."
        out = []
        for p in products:
            price = p["variants"][0]["price"] if p.get("variants") else "N/A"
            out.append(f"Title: {p['title']} | Price: {price} | Type: {p.get('product_type', '')}")
        return "\n".join(out)
    except Exception as e:
        return f"Shopify data fetch nahi hua: {e}"

# Tool 3: Customer reviews analyzer (CSV se)
@tool("Review Analyzer")
def review_analyzer(csv_path: str) -> str:
    """CSV file se customer reviews padh kar rating summary aur
    positive/negative examples deta hai. CSV columns: review, rating"""
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return "CSV khali hai."
        ratings = [int(r["rating"]) for r in rows]
        avg = sum(ratings) / len(ratings)
        positive = [r["review"] for r in rows if int(r["rating"]) >= 4][:5]
        negative = [r["review"] for r in rows if int(r["rating"]) <= 2][:5]
        return (
            f"Total reviews: {len(rows)}\n"
            f"Average rating: {avg:.2f}\n"
            f"Rating distribution: {dict(Counter(ratings))}\n"
            f"Positive examples: {positive}\n"
            f"Negative examples: {negative}"
        )
    except FileNotFoundError:
        return "CSV file nahi mili, path check karo."
    except Exception as e:
        return f"Reviews analyze nahi hue: {e}"