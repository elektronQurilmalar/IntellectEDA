# web_searcher.py
from googlesearch import search
import time

SEARCH_SITES = [
    "site:ti.com/lit/an",
    "site:analog.com/en/technical-documentation/application-notes",
    "site:st.com/resource/en/application_note",
    "site:infineon.com/dgdl",
    "site:nxp.com/docs/en/application-note"
]


def search_web_for_notes(query: str, num_results_total: int = 10):
    """
    Ищет App Notes в интернете.
    Эта версия использует самый минималистичный вызов search() для 100% совместимости.
    """
    try:
        # 1. Формируем единый поисковый запрос
        sites_query_part = " OR ".join(SEARCH_SITES)
        full_sites_filter = f"({sites_query_part})"
        full_query = f'"{query}" filetype:pdf {full_sites_filter}'

        print(f"Выполняю единый веб-поиск...")
        print(f"Запрос: {full_query}")

        # 2. ОКОНЧАТЕЛЬНОЕ ИСПРАВЛЕНИЕ:
        #    Вызываем search() только с одним аргументом - строкой запроса.
        #    Никаких именованных аргументов.
        search_results_generator = search(full_query)

        # 3. Обрабатываем результаты и контролируем их количество ВРУЧНУЮ
        results_count = 0
        for url in search_results_generator:
            vendor = "Unknown"
            source_domain = "web"
            if "ti.com" in url:
                vendor, source_domain = "TI", "ti.com"
            elif "analog.com" in url:
                vendor, source_domain = "ADI", "analog.com"
            elif "st.com" in url:
                vendor, source_domain = "ST", "st.com"
            elif "infineon.com" in url:
                vendor, source_domain = "INF", "infineon.com"
            elif "nxp.com" in url:
                vendor, source_domain = "NXP", "nxp.com"

            try:
                title = url.split('/')[-1].replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
            except:
                title = "Untitled Document"

            yield {
                "id": vendor,
                "title": title,
                "url": url,
                "source": f"Web ({source_domain})"
            }

            # Увеличиваем счетчик и выходим из цикла, если набрали достаточно
            results_count += 1
            if results_count >= num_results_total:
                print(f"Достигнут лимит в {num_results_total} результатов.")
                break

        # Небольшая пауза после успешного поиска, чтобы снизить нагрузку при следующем запросе
        time.sleep(1)

    except Exception as e:
        print(f"Ошибка при выполнении единого веб-поиска: {e}")
        if "429" in str(e):
            print("Google временно заблокировал IP. Попробуйте через несколько минут.")
        time.sleep(1)