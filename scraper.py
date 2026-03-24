import json

from playwright.sync_api import sync_playwright


def safe_text(element, selector):
    """Return child element text or None."""
    try:
        child = element.locator(selector).first
        if child.count() == 0:
            return None
        value = child.inner_text().strip()
        return value or None
    except Exception:
        return None


def safe_attr(element, selector, attr):
    """Return child element attribute value or None."""
    try:
        child = element.locator(selector).first
        if child.count() == 0:
            return None
        value = child.get_attribute(attr)
        if value is None:
            return None
        value = value.strip()
        return value or None
    except Exception:
        return None


def scrape_entertainment(page):
    """
    Navigate to Ekantipur entertainment page and scrape top 5 articles.

    Args:
        page: Playwright page object

    Returns:
        list[dict]: List of article dictionaries with title, image_url, category, author
    """
    try:
        print("[ENTERTAINMENT] Navigation started")
        page.goto("https://ekantipur.com/entertainment", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        print("[ENTERTAINMENT] Page loaded")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(2000)
        page.wait_for_selector("img.loaded")

        article_cards = page.locator("div.category > div.category-inner-wrapper")
        print(f"[ENTERTAINMENT] Total cards found: {article_cards.count()}")
        card_count = min(article_cards.count(), 5)

        results = []

        for i in range(card_count):
            card = article_cards.nth(i)
            title = safe_text(card, "div.category-description h2") or ""
            author = safe_text(card, "div.category-description div.author-name p a") or ""
            image_url = (
                safe_attr(card, "div.category-image a figure img.loaded", "src")
                or safe_attr(card, "div.category-image a figure img.loaded", "data-src")
                or ""
            )
            category = "मनोरञ्जन"

            results.append(
                {
                    "title": title,
                    "image_url": image_url,
                    "category": category,
                    "author": author,
                }
            )
            print(f"[ENTERTAINMENT] Extracted article {i + 1}: {title}")

        print(f"[ENTERTAINMENT] Total extracted: {len(results)}")
        return results
    except Exception:
        return []


def scrape_cartoon(page):
    """
    Navigate to Ekantipur cartoon page and scrape cartoon of the day.

    Args:
        page: Playwright page object

    Returns:
        dict: Dictionary with title, image_url, author
    """
    try:
        print("[CARTOON] Search started")
        page.goto("https://ekantipur.com/cartoon", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(2000)
        page.wait_for_selector("img.loaded")

        container = page.locator(".cartoon-wrapper").first
        print("[CARTOON] Cartoon section found")

        image_url = (
            safe_attr(container, ".cartoon-image figure a img.loaded", "src")
            or safe_attr(container, ".cartoon-image figure a img.loaded", "data-src")
            or safe_attr(container, ".cartoon-image figure a img.loaded", "data-original")
        )

        title = safe_text(container, ".cartoon-description p")

        author = None
        author_candidates = container.locator(".cartoon-description p")
        candidate_count = author_candidates.count()
        if candidate_count > 1:
            candidate = author_candidates.nth(1).inner_text().strip()
            author = candidate or None
        elif candidate_count == 1:
            candidate = author_candidates.first.inner_text().strip()
            author = candidate or None

        print(f"[CARTOON] Title extracted: {title}")
        print(f"[CARTOON] Author extracted: {author}")
        return {"title": title, "image_url": image_url, "author": author}
    except Exception:
        return {"title": None, "image_url": None, "author": None}


def main():
    results = {"entertainment_news": [], "cartoon_of_the_day": None}

    print("[MAIN] Scraping started")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="ne-NP",
        )
        page = context.new_page()

        results["entertainment_news"] = scrape_entertainment(page)
        print("[MAIN] Entertainment scraping completed")

        results["cartoon_of_the_day"] = scrape_cartoon(page)
        print("[MAIN] Cartoon scraping completed")

        with open("output.json", "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=2)

        print("[MAIN] Done. Data saved to output.json")

        context.close()
        browser.close()

    return results

if __name__ == "__main__":
    main()
