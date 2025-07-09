# gui.py
import tkinter as tk
from tkinter import ttk
import threading

# Импортируем нашу логику
from knowledge_base_handler import load_db, search_local_db, open_url, add_document_to_db
from web_searcher import search_web_for_notes


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IntellectuEDA - Самообучающийся Поисковик")
        self.geometry("950x600")

        # Устанавливаем основной фон окна в фирменном сером цвете
        self.configure(bg="#ECECEC")

        self.db = load_db()
        self.all_results = []

        # Сначала создаем виджеты, потом применяем стили
        self._create_widgets()
        self._setup_styles()

    def _safe_after(self, func):
        """
        Безопасная обертка для self.after, которая проверяет,
        существует ли еще окно перед выполнением.
        """
        try:
            if self.winfo_exists():
                self.after(0, func)
        except tk.TclError:
            # Это может произойти, если окно разрушается прямо сейчас
            print("Окно было закрыто, обновление GUI отменено.")

    def _setup_styles(self):
        """Настраивает внешний вид в стиле macOS."""
        # Цветовая палитра
        BG_COLOR = "#ECECEC"  # Основной фон окна
        TEXT_COLOR = "#333333"  # Основной цвет текста
        ENTRY_BG = "#FFFFFF"  # Фон для полей ввода и списка
        SELECT_BG = "#007AFF"  # Цвет выделения (классический синий macOS)
        SELECT_FG = "#FFFFFF"  # Цвет текста при выделении
        BUTTON_BG = "#FFFFFF"  # Фон кнопок (в macOS они часто белые)
        BORDER_COLOR = "#C2C2C2"  # Цвет рамок
        HEADER_BG = "#F5F5F5"  # Фон заголовков

        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # 'clam' - хорошая основа для кастомизации

        # Общие стили для всех элементов
        # Используем шрифт Segoe UI, если доступен (стандарт для Windows)
        default_font = ('Segoe UI', 10)
        try:
            self.tk.call('font', 'metrics', default_font)
        except tk.TclError:
            default_font = ('TkDefaultFont', 10)  # Запасной вариант

        self.style.configure('.',
                             background=BG_COLOR,
                             foreground=TEXT_COLOR,
                             font=default_font
                             )

        # Стили для конкретных виджетов
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, padding=5)
        self.style.configure('TLabelframe', background=BG_COLOR, bordercolor=BORDER_COLOR)
        self.style.configure('TLabelframe.Label', background=BG_COLOR, foreground=TEXT_COLOR)

        # Поле ввода
        self.style.configure('TEntry',
                             fieldbackground=ENTRY_BG,
                             foreground=TEXT_COLOR,
                             borderwidth=1,
                             bordercolor=BORDER_COLOR,
                             insertcolor=TEXT_COLOR,  # Цвет курсора
                             padding=7)

        # Кнопка
        self.style.configure('TButton',
                             background=BUTTON_BG,
                             foreground=TEXT_COLOR,
                             borderwidth=1,
                             bordercolor=BORDER_COLOR,
                             padding=(10, 5),
                             font=(default_font[0], 10, 'bold'))
        self.style.map('TButton',
                       background=[('active', '#E5E5E5')],
                       bordercolor=[('focus', SELECT_BG)])

        # Treeview (таблица результатов)
        self.style.configure('Treeview',
                             background=ENTRY_BG,
                             fieldbackground=ENTRY_BG,
                             foreground=TEXT_COLOR,
                             rowheight=28,  # Увеличиваем высоту строк
                             font=(default_font[0], 11))
        # Убираем рамку вокруг всего Treeview
        self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Заголовки таблицы
        self.style.configure('Treeview.Heading',
                             background=HEADER_BG,
                             foreground=TEXT_COLOR,
                             font=(default_font[0], 10, 'bold'),
                             padding=8)
        self.style.map('Treeview.Heading', background=[('active', '#E5E5E5')])

        # Цвет выделения строки
        self.style.map('Treeview',
                       background=[('selected', SELECT_BG)],
                       foreground=[('selected', SELECT_FG)])

        # Цвета для тегов строк (менее кричащие)
        self.results_tree.tag_configure('Local DB', background='#E8F5E9', foreground='#1B5E20')
        self.results_tree.tag_configure('Web', background='#FFF8E1', foreground='#E65100')

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Рамка для поиска с отступами
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(5, 15))

        entry_font = ('Segoe UI', 12)
        try:
            self.tk.call('font', 'metrics', entry_font)
        except tk.TclError:
            entry_font = ('TkDefaultFont', 12)

        self.search_entry = ttk.Entry(search_frame, font=entry_font)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._start_search_thread())

        self.search_button = ttk.Button(search_frame, text="Найти", command=self._start_search_thread)
        self.search_button.pack(side=tk.LEFT)

        # Рамка для результатов
        results_frame = ttk.LabelFrame(main_frame, text="Результаты", padding=(10, 5))
        results_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("source", "title")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        self.results_tree.heading("source", text="Источник")
        self.results_tree.heading("title", text="Название")
        self.results_tree.column("source", width=180, stretch=tk.NO, anchor='w')
        self.results_tree.column("title", width=700, anchor='w')

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)

        # Размещаем через grid для лучшего контроля
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.results_tree.bind("<Double-1>", self._on_item_double_click)

        # Статус-бар
        self.status_label = ttk.Label(self, text="Готов к работе.", padding=(10, 5))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _start_search_thread(self):
        # ... (этот метод без изменений)
        self.search_button.config(state=tk.DISABLED)
        self.results_tree.delete(*self.results_tree.get_children())
        self.all_results = []
        query = self.search_entry.get()
        if not query:
            self.status_label.config(text="Введите поисковый запрос.")
            self.search_button.config(state=tk.NORMAL)
            return
        thread = threading.Thread(target=self._perform_search, args=(query,))
        thread.start()

    def _perform_search(self, query):
        """Основная логика поиска: сначала локально, потом в вебе."""
        # --- ИСПОЛЬЗУЕМ БЕЗОПАСНЫЙ ВЫЗОВ ---
        self._safe_after(lambda: self.status_label.config(text="Ищу в локальной базе..."))

        local_results = search_local_db(query, self.db)
        self._safe_after(lambda: self._update_gui_with_results(local_results))

        existing_urls = {doc['url'] for doc in local_results}

        self._safe_after(lambda: self.status_label.config(text="Дополняю результаты из интернета..."))

        web_search_generator = search_web_for_notes(query, num_results_total=20)

        for web_doc in web_search_generator:
            if web_doc['url'] not in existing_urls:
                self._safe_after(lambda: self._update_gui_with_results([web_doc]))
                existing_urls.add(web_doc['url'])

        # --- ИСПОЛЬЗУЕМ БЕЗОПАСНЫЙ ВЫЗОВ ДЛЯ ЗАВЕРШЕНИЯ ---
        self._safe_after(
            lambda: self.status_label.config(text=f"Поиск завершен. Найдено {len(self.all_results)} результатов."))
        self._safe_after(lambda: self.search_button.config(state=tk.NORMAL))

    def _update_gui_with_results(self, results: list):
        """Обновляет Treeview (вызывается через _safe_after)."""
        for doc in results:
            source = doc.get("source", "N/A")
            tag = 'Local DB' if 'Local' in source else 'Web'
            self.results_tree.insert("", tk.END, values=(source, doc["title"]), tags=(tag,))
            self.all_results.append(doc)

    def _on_item_double_click(self, event):
        # ... (этот метод без изменений)
        if not self.results_tree.selection(): return
        selected_item_id = self.results_tree.selection()[0]
        item_index = self.results_tree.index(selected_item_id)
        doc_to_open = self.all_results[item_index]
        url = doc_to_open.get('url')
        if url:
            open_url(url)
            if "Web" in doc_to_open.get("source", ""):
                query = self.search_entry.get()
                add_document_to_db(doc_to_open, query)
                self.db = load_db()
                self.status_label.config(text=f"Документ '{doc_to_open['title'][:30]}...' добавлен в базу.")