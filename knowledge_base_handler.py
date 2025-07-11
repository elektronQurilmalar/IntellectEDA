# knowledge_base_handler.py
import json
from pathlib import Path
import webbrowser
import re

DB_PATH = Path("db/app_notes.json")


def load_db() -> list:
    """Загружает базу знаний из файла JSON."""
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(exist_ok=True)
        with open(DB_PATH, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_db(db: list):
    """Сохраняет базу знаний в файл JSON."""
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def _clean_title(title: str) -> str:
    """Убирает из заголовка мусорные слова, расширения и GET-параметры."""
    # ИЗМЕНЕНИЕ: Исправлена ошибка в регулярном выражении. (?i) теперь в начале.
    title = re.sub(r'(?i)^\[?pdf\]?\s*[:-]?\s*', '', title)

    title = title.split('?')[0]

    if title.lower().endswith('.pdf'):
        title = title[:-4]

    title = re.sub(r'[\-_]', ' ', title)
    title = re.sub(r'\s[a-fA-F0-9]{16,}', '', title)
    return title.strip()


def add_document_to_db(doc: dict, query: str):
    """Добавляет новый документ в базу, если его еще нет."""
    db = load_db()

    if any(d.get('url') == doc.get('url') for d in db):
        print(f"Документ {doc.get('url')} уже в базе.")
        return

    cleaned_title = _clean_title(doc.get('title', 'Untitled'))

    new_doc = {
        "id": doc.get('id', 'WEB-SRC'),
        "title": cleaned_title,
        "url": doc.get('url'),
        "keywords": list(set(re.split(r'\s+|,|\-', cleaned_title.lower()) + query.lower().split())),
        "source": doc.get('source', 'Web')
    }
    db.append(new_doc)
    save_db(db)
    print(f"Документ '{new_doc['title']}' добавлен в базу.")


def search_local_db(query: str, db: list) -> list:
    """Ищет App Notes в локальной базе по ключевым словам (целые слова)."""
    if not query:
        return []

    query_words = set(query.lower().split())
    results = []

    for doc in db:
        searchable_words = set(re.split(r'\s+|,|\-|_', doc.get('title', '').lower()))
        if 'keywords' in doc:
            searchable_words.update(doc.get('keywords', []))

        if query_words.issubset(searchable_words):
            results.append(doc)

    return results


def open_url(url: str):
    """Открывает URL в браузере."""
    webbrowser.open_new_tab(url)