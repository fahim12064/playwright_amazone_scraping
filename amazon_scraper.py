from playwright.sync_api import sync_playwright
import time
import random
import csv

def wait_like_human(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def scrape_amazon():
    search_term = input("🔍 Enter your search term (e.g. mouse, laptop): ").strip()
    csv_file = f"{search_term}_products.csv"

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Price"])

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir='./amazon_user',
                headless=True,
                viewport={'width': 1280, 'height': 800}
            )
            page = browser.pages[0] if browser.pages else browser.new_page()

            page.goto("https://www.amazon.com/")
            page.fill("input[name='field-keywords']", search_term)
            page.press("input[name='field-keywords']", "Enter")
            page.wait_for_timeout(5000)

            print("⚠️ If CAPTCHA appears, please solve it manually in the browser.")
            input("🔴 Press ENTER after CAPTCHA is solved and products are visible...")

            page_num = 1
            max_pages = 3

            while page_num <= max_pages:
                print(f"\n🔎 Scraping Page {page_num}...\n")
                items = page.locator("div[data-component-type='s-search-result']")
                count = items.count()
                print(f"✅ Total products found: {count}")

                for i in range(count):
                    item = items.nth(i)
                    try:
                        title = item.locator("h2 span").inner_text()
                    except:
                        title = "N/A"
                    try:
                        price = item.locator("span.a-offscreen").first.inner_text()
                    except:
                        price = "N/A"

                    writer.writerow([title, price])
                    print(f"{i+1}. {title} | {price}")

                try:
                    next_button = page.locator("ul.a-pagination li.a-last a")
                    if next_button.is_visible():
                        wait_like_human()
                        next_button.click()
                        page.wait_for_timeout(5000)
                        page_num += 1
                    else:
                        raise Exception("Next button not visible")

                except Exception:
                    try:
                        page_num += 1
                        next_url = f"https://www.amazon.com/s?k={search_term}&page={page_num}"
                        print(f"➡️ Trying to load page {page_num} via URL...")
                        page.goto(next_url)
                        page.wait_for_timeout(5000)
                    except:
                        print("🚫 No more pages or failed to load next page.")
                        break

            browser.close()

    print(f"\n✅ Data saved to: {csv_file}")

if __name__ == "__main__":
    scrape_amazon()
