# web_searcher.py
from ddgs import DDGS
import time
import random

# Расширенный список источников оставлен без изменений
SEARCH_SITES = [
    "site:ti.com/lit/an",
    "site:analog.com/en/technical-documentation/application-notes",
    "site:st.com/resource/en/application_note",
    "site:infineon.com/dgdl",
    "site:nxp.com/docs/en/application-note",
    "site:ww1.microchip.com/downloads/en/AppNotes/",
    "site:renesas.com/us/en/document/apn/",
    "site:onsemi.com/pub/Collateral/",
    "site:maximintegrated.com/en/design/technical-documents/app-notes/",
    "site:vishay.com/docs/",
    "site:rohm.com/documents/en/application-notes"
]


def search_web_for_notes(query: str, num_results_total: int = 20):
    """
    Ищет App Notes, используя полную имитацию браузера и человеческие паузы,
    чтобы гарантированно обойти мягкие блокировки.
    """
    collected_urls = set()
    num_per_site = 3

    # 1. МАСКИРОВКА: Представляемся обычным браузером. Это ключевое изменение.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

    # Применяем заголовки при создании объекта
    with DDGS(headers=headers) as ddgs:
        random.shuffle(SEARCH_SITES)

        for site_filter in SEARCH_SITES:
            if len(collected_urls) >= num_results_total:
                print(f"Достигнут лимит в {num_results_total} уникальных результатов. Завершаю поиск.")
                break

            try:
                target_domain = site_filter.split('/')[0].replace('site:', '')
                full_query = f'"{query}" filetype:pdf {site_filter}'
                print(f"Ищу на DuckDuckGo (Цель: {target_domain})...")

                search_results = ddgs.text(
                    keywords=full_query,
                    max_results=num_per_site * 2
                )

                if not search_results:
                    print("-> Ничего не найдено.")
                    # Даже после неудачного поиска делаем паузу, чтобы не частить
                    time.sleep(random.uniform(1.0, 2.0))
                    continue

                site_results_count = 0
                for r in search_results:
                    url = r['href']

                    if target_domain not in url or url in collected_urls:
                        continue

                    vendor = "Unknown"
                    source_domain = target_domain
                    if "ti.com" in url:
                        vendor = "TI"
                    elif "analog.com" in url:
                        vendor = "ADI"
                    elif "st.com" in url:
                        vendor = "ST"
                    elif "infineon.com" in url:
                        vendor = "INF"
                    elif "nxp.com" in url:
                        vendor = "NXP"
                    elif "microchip.com" in url:
                        vendor = "Microchip"
                    elif "renesas.com" in url:
                        vendor = "Renesas"
                    elif "onsemi.com" in url:
                        vendor = "Onsemi"
                    elif "maximintegrated.com" in url:
                        vendor = "Maxim"
                    elif "vishay.com" in url:
                        vendor = "Vishay"
                    elif "rohm.com" in url:
                        vendor = "ROHM"

                    title = r.get('title', url.split('/')[-1].replace('.pdf', ''))

                    yield {
                        "id": vendor,
                        "title": title,
                        "url": url,
                        "source": f"Web ({source_domain})"
                    }
                    collected_urls.add(url)
                    site_results_count += 1

                    if site_results_count >= num_per_site or len(collected_urls) >= num_results_total:
                        break

                # 2. ТЕРПЕНИЕ: Значительно увеличиваем паузу между запросами.
                sleep_duration = random.uniform(2.0, 4.0)
                print(f"-> Пауза {sleep_duration:.1f} сек...")
                time.sleep(sleep_duration)

            except Exception as e:
                print(f"Произошла непредвиденная ошибка при поиске на {target_domain}: {e}")
                time.sleep(5)  # В случае любой ошибки делаем долгую паузу
                continue