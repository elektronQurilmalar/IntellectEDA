# gui.py
import customtkinter as ctk
import threading
from functools import partial

# Импортируем нашу логику
from knowledge_base_handler import load_db, search_local_db, open_url, add_document_to_db
from web_searcher import search_web_for_notes

# Устанавливаем базовую тему и цвет
ctk.set_appearance_mode("Light")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IntellectEDA - Technical Document Finder")
        self.geometry("1000x650")

        self.db = load_db()
        self.all_results = []
        self.result_widgets = []

        # Настраиваем сетку основного окна
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Создание виджетов ---
        self._create_widgets()

    def _safe_after(self, func):
        """Безопасная обертка для self.after."""
        try:
            if self.winfo_exists():
                self.after(0, func)
        except Exception:
            print("Window was closed.")

    def _create_widgets(self):
        # --- Фрейм для поиска ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter the interface or component name...",
            height=40,
            font=("Segoe UI", 14)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<Return>", lambda e: self._start_search_thread())

        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self._start_search_thread,
            height=40,
            font=("Segoe UI", 14, "bold")
        )
        self.search_button.grid(row=0, column=1, padx=(10, 0))

        # --- Фрейм для результатов ---
        results_outer_frame = ctk.CTkFrame(self)
        results_outer_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="nsew")
        results_outer_frame.grid_rowconfigure(0, weight=1)
        results_outer_frame.grid_columnconfigure(0, weight=1)

        # Создаем прокручиваемый фрейм для списка результатов
        self.results_frame = ctk.CTkScrollableFrame(
            results_outer_frame,
            label_text="Results",
            label_font=("Segoe UI", 12, "bold")
        )
        self.results_frame.grid(row=0, column=0, sticky="nsew")

        # --- Статус-бар ---
        self.status_label = ctk.CTkLabel(self, text="Ready to work.", anchor="w", font=("Segoe UI", 12))
        self.status_label.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="ew")

    def _clear_results(self):
        """Очищает список результатов в GUI."""
        for widget in self.result_widgets:
            widget.destroy()
        self.result_widgets = []
        self.all_results = []

    def _start_search_thread(self):
        self.search_button.configure(state="disabled")
        self._clear_results()

        query = self.search_entry.get()
        if not query:
            self.status_label.configure(text="Enter a search term...")
            self.search_button.configure(state="normal")
            return

        self.status_label.configure(text="Searching...")
        thread = threading.Thread(target=self._perform_search, args=(query,), daemon=True)
        thread.start()

    def _perform_search(self, query):
        """Основная логика поиска: сначала локально, потом в вебе."""
        # Поиск в локальной базе
        self._safe_after(lambda: self.status_label.configure(text="Searching in local base..."))
        local_results = search_local_db(query, self.db)
        if local_results:
            self._safe_after(lambda: self._add_results_to_gui(local_results))

        existing_urls = {doc['url'] for doc in local_results}

        # Поиск в интернете
        self._safe_after(lambda: self.status_label.configure(text="Adding results from the internet..."))
        web_search_generator = search_web_for_notes(query)
        web_results = []
        for web_doc in web_search_generator:
            if web_doc['url'] not in existing_urls:
                web_results.append(web_doc)
                existing_urls.add(web_doc['url'])

        if web_results:
            self._safe_after(lambda: self._add_results_to_gui(web_results))

        # Завершение
        self._safe_after(
            lambda: self.status_label.configure(text=f"Search is finished. {len(self.all_results)} results found."))
        self._safe_after(lambda: self.search_button.configure(state="normal"))

    def _add_results_to_gui(self, results: list):
        """Добавляет карточки результатов в прокручиваемый фрейм."""
        for doc in results:
            self.all_results.append(doc)

            # --- Создание карточки для одного результата ---
            card = ctk.CTkFrame(self.results_frame, fg_color=("gray90", "gray25"), corner_radius=8)
            card.pack(fill="x", padx=5, pady=(0, 7))

            source_text = doc.get("source", "N/A")
            is_local = "Local" in source_text
            source_color = "#106A43" if is_local else "#0B5E8F"

            # Источник (цветной)
            source_label = ctk.CTkLabel(
                card,
                text=source_text,
                font=("Segoe UI", 11, "bold"),
                text_color=source_color,
                anchor="w"
            )
            source_label.pack(fill="x", padx=10, pady=(5, 0))

            # Заголовок (основной текст)
            title_label = ctk.CTkLabel(
                card,
                text=doc.get("title", "No title"),
                font=("Segoe UI", 14),
                anchor="w",
                justify="left",
                wraplength=800  # Автоматический перенос строк
            )
            title_label.pack(fill="x", padx=10, pady=(2, 10))

            # Привязка событий к карточке и дочерним элементам
            # partial используется, чтобы передать аргумент (doc) в функцию
            on_click_with_doc = partial(self._on_item_click, doc)
            card.bind("<Button-1>", on_click_with_doc)
            source_label.bind("<Button-1>", on_click_with_doc)
            title_label.bind("<Button-1>", on_click_with_doc)

            self.result_widgets.append(card)

    def _on_item_click(self, doc_to_open, event=None):
        """Обрабатывает клик по карточке результата."""
        url = doc_to_open.get('url')
        if not url: return

        print(f"Opening the URL: {url}")
        open_url(url)

        # Если документ из веба, добавляем его в локальную базу
        if "Web" in doc_to_open.get("source", ""):
            query = self.search_entry.get()
            add_document_to_db(doc_to_open, query)
            self.db = load_db()  # Обновляем кэш базы данных
            self.status_label.configure(text=f"Document '{doc_to_open['title'][:40]}...' was added to the base.")