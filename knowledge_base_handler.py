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
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(db: list):
    """Сохраняет базу знаний в файл JSON."""
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def add_document_to_db(doc: dict, query: str):
    """Добавляет новый документ в базу, если его еще нет."""
    db = load_db()

    # Проверяем, что документа с таким URL еще нет
    if any(d.get('url') == doc.get('url') for d in db):
        print(f"Документ {doc.get('url')} уже в базе.")
        return

    # Дополняем документ метаданными
    new_doc = {
        "id": doc.get('id', 'WEB-SRC'),
        "title": doc.get('title', 'Untitled'),
        "url": doc.get('url'),
        "keywords": list(set(re.split(r'\s+|,|\-', doc.get('title', '').lower()) + query.lower().split())),
        "source": doc.get('source', 'Web')  # По умолчанию источник - Web
    }
    db.append(new_doc)
    save_db(db)
    print(f"Документ '{new_doc['title']}' добавлен в базу.")


def search_local_db(query: str, db: list) -> list:
    """Ищет App Notes в локальной базе по ключевым словам."""
    if not query:
        return []

    query_words = set(query.lower().split())
    results = []

    for doc in db:
        searchable_content = (doc['title'].lower() + " " + " ".join(doc.get('keywords', []))).split()
        if query_words.issubset(searchable_content):
            results.append(doc)

    return results


def open_url(url: str):
    """Открывает URL в браузере."""
    webbrowser.open_new_tab(url)