# web_searcher.py
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# Import keys from our new config file
try:
    from config import API_KEY, CSE_ID
except ImportError:
    print("ERROR: config.py not found or API_KEY/CSE_ID not set.")
    print("Please create config.py and add your Google API Key and Custom Search Engine ID.")
    API_KEY = None
    CSE_ID = None

# Vendor map remains useful for identifying the source.
VENDOR_MAP = {
    "ti.com": "TI",
    "analog.com": "ADI",
    "st.com": "ST",
    "infineon.com": "INF",
    "nxp.com": "NXP",
    "microchip.com": "Microchip",
    "renesas.com": "Renesas",
    "onsemi.com": "Onsemi",
    "maximintegrated.com": "Maxim",
    "vishay.com": "Vishay",
    "rohm.com": "ROHM",
    "silabs.com": "SiLabs",
    "monolithicpower.com": "MPS"
}


def search_web_for_notes(query: str, num_results_total: int = 10):
    """
    Searches for documents using the Google Custom Search API for high-quality, reliable results.
    """
    if not API_KEY or not CSE_ID or "YOUR_" in API_KEY:
        print("Google API keys are not configured. Web search is disabled.")
        # Yield an error message to display in the GUI
        yield {
            "id": "ERROR",
            "title": "Google API Key or CSE ID is not configured in config.py",
            "url": "",
            "source": "Configuration"
        }
        return

    # The Google API returns results in pages of 10.
    # We will make requests until we have enough results.
    collected_urls = set()

    try:
        # Build the service object for interacting with the API
        service = build("customsearch", "v1", developerKey=API_KEY)

        # The API allows a max of 10 results per request. We may need to make multiple requests.
        # The 'start' parameter controls pagination (1, 11, 21, etc.).
        for i in range(0, 20, 10):  # Let's make a max of 2 requests (20 results)
            if len(collected_urls) >= num_results_total:
                break

            print(f"Requesting results {i + 1}-{i + 10} from Google...")

            # The 'fileType' parameter is a powerful and reliable filter.
            res = service.cse().list(
                q=query,
                cx=CSE_ID,
                fileType='pdf',
                num=10,  # Request 10 items
                start=i + 1
            ).execute()

            # The API returns an empty 'items' key if there are no results.
            if 'items' not in res:
                print("-> No more results from Google.")
                break

            for item in res['items']:
                url = item['link']

                # Basic sanity checks
                if not url or url in collected_urls:
                    continue

                try:
                    domain = url.split('/')[2].replace('www.', '')

                    vendor = "Unknown"
                    source_domain = domain
                    for domain_key, vendor_name in VENDOR_MAP.items():
                        if domain_key in domain:
                            vendor = vendor_name
                            source_domain = domain_key
                            break

                    # The title from Google is generally much cleaner.
                    title = item.get('title', 'No Title')

                    yield {
                        "id": vendor,
                        "title": title,
                        "url": url,
                        "source": f"Web ({source_domain})"
                    }
                    collected_urls.add(url)

                    if len(collected_urls) >= num_results_total:
                        break

                except IndexError:
                    continue  # Skip malformed URLs

            # The free tier has a limit of 100 queries per day. A small delay is polite.
            time.sleep(0.5)

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        yield {
            "id": "ERROR",
            "title": f"Google API Error: {e.resp.status}",
            "url": "",
            "source": "API Error"
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        yield {
            "id": "ERROR",
            "title": f"An unexpected error occurred: {e}",
            "url": "",
            "source": "App Error"
        }