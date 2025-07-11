# gui.py
import tkinter as tk
from tkinter import ttk
import threading

# Импортируем нашу логику
from knowledge_base_handler import load_db, search_local_db, open_url, add_document_to_db
from web_searcher import search_web_for_notes


# НОВЫЙ КЛАСС: Кнопка с закругленными углами
class RoundedButton(tk.Canvas):
    # ИЗМЕНЕНИЕ: Добавлен параметр parent_bg, убран bg=parent.cget('bg')
    def __init__(self, parent, text, command, width, height, radius, bg_color, fg_color, hover_color, press_color,
                 parent_bg):
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, borderwidth=0)
        self.command = command
        self.radius = radius
        self.colors = {
            "normal": bg_color,
            "hover": hover_color,
            "press": press_color,
            "text": fg_color
        }
        self.state = 'normal'  # 'normal', 'hover', 'press'

        self.rect = self._draw_rounded_rect(0, 0, width, height, radius, self.colors['normal'])
        self.text_item = self.create_text(width / 2, height / 2, text=text, fill=self.colors['text'],
                                          font=('Segoe UI', 10, 'bold'))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._is_enabled = True

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, color):
        return self.create_polygon(
            x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r,
            x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
            x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
            x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1,
            smooth=True, fill=color, outline=""
        )

    def _on_enter(self, event):
        if not self._is_enabled: return
        self.state = 'hover'
        self.itemconfig(self.rect, fill=self.colors['hover'])

    def _on_leave(self, event):
        if not self._is_enabled: return
        self.state = 'normal'
        self.itemconfig(self.rect, fill=self.colors['normal'])

    def _on_press(self, event):
        if not self._is_enabled: return
        self.state = 'press'
        self.itemconfig(self.rect, fill=self.colors['press'])

    def _on_release(self, event):
        if not self._is_enabled: return
        # Проверяем, что отпускание кнопки произошло внутри виджета
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self._on_enter(event)  # Возвращаем цвет ховера
            if self.command:
                self.command()
        else:
            self._on_leave(event)

    def config(self, state=None):
        if state == tk.DISABLED:
            self._is_enabled = False
            self.itemconfig(self.rect, fill="#D3D3D3")  # Серый цвет для неактивной кнопки
            self.itemconfig(self.text_item, fill="#A9A9A9")
        elif state == tk.NORMAL:
            self._is_enabled = True
            self.itemconfig(self.rect, fill=self.colors['normal'])
            self.itemconfig(self.text_item, fill=self.colors['text'])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IntellectuEDA - Самообучающийся Поисковик")
        self.geometry("1000x650")  # Немного увеличим окно

        self.db = load_db()
        self.all_results = []

        # Сначала настраиваем стили, потом создаем виджеты
        self._setup_styles()
        self._create_widgets()

    def _safe_after(self, func):
        try:
            if self.winfo_exists():
                self.after(0, func)
        except tk.TclError:
            print("Окно было закрыто, обновление GUI отменено.")

    def _setup_styles(self):
        # Цветовая палитра
        self.BG_COLOR = "#F0F0F0"
        self.TEXT_COLOR = "#333333"
        self.ENTRY_BG = "#FFFFFF"
        self.SELECT_BG = "#007AFF"
        self.SELECT_FG = "#FFFFFF"
        self.BORDER_COLOR = "#CCCCCC"
        self.HEADER_BG = "#EAEAEA"

        # Устанавливаем основной фон окна
        self.configure(bg=self.BG_COLOR)

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        default_font = ('Segoe UI', 10)
        try:
            self.tk.call('font', 'metrics', default_font)
        except tk.TclError:
            default_font = ('TkDefaultFont', 10)

        self.style.configure('.',
                             background=self.BG_COLOR,
                             foreground=self.TEXT_COLOR,
                             font=default_font)

        self.style.configure('TFrame', background=self.BG_COLOR)
        self.style.configure('TLabel', background=self.BG_COLOR, padding=5)
        self.style.configure('TLabelframe', background=self.BG_COLOR, bordercolor=self.BORDER_COLOR, relief=tk.GROOVE)
        self.style.configure('TLabelframe.Label', background=self.BG_COLOR, foreground=self.TEXT_COLOR)

        # Поле ввода со скругленными углами
        self.style.configure('TEntry',
                             fieldbackground=self.ENTRY_BG,
                             foreground=self.TEXT_COLOR,
                             borderwidth=1,
                             bordercolor=self.BORDER_COLOR,
                             insertcolor=self.TEXT_COLOR,
                             padding=10,  # Увеличили внутренний отступ
                             relief=tk.FLAT)

        # Treeview (таблица результатов)
        self.style.configure('Treeview',
                             background=self.ENTRY_BG,
                             fieldbackground=self.ENTRY_BG,
                             foreground=self.TEXT_COLOR,
                             rowheight=30,
                             font=(default_font[0], 11),
                             relief=tk.FLAT)
        self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        self.style.configure('Treeview.Heading',
                             background=self.HEADER_BG,
                             foreground=self.TEXT_COLOR,
                             font=(default_font[0], 10, 'bold'),
                             padding=10)
        self.style.map('Treeview.Heading', background=[('active', '#DCDCDC')])
        self.style.map('Treeview',
                       background=[('selected', self.SELECT_BG)],
                       foreground=[('selected', self.SELECT_FG)])

    def _create_widgets(self):
        # ИЗМЕНЕНИЕ: Увеличены отступы для "воздуха"
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(5, 20))  # Увеличен нижний отступ

        entry_font = ('Segoe UI', 14)  # Увеличили шрифт в поле ввода
        try:
            self.tk.call('font', 'metrics', entry_font)
        except tk.TclError:
            entry_font = ('TkDefaultFont', 14)

        self.search_entry = ttk.Entry(search_frame, font=entry_font)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)  # ipady для увеличения высоты
        self.search_entry.bind("<Return>", lambda e: self._start_search_thread())

        # ИЗМЕНЕНИЕ: Используем нашу новую скругленную кнопку и явно передаем цвет фона родителя
        self.search_button = RoundedButton(
            parent=search_frame,
            text="Найти",
            command=self._start_search_thread,
            width=110, height=44, radius=22,
            bg_color="#007AFF", fg_color="#FFFFFF",
            hover_color="#0056b3", press_color="#004085",
            parent_bg=self.BG_COLOR  # Явно передаем цвет фона
        )
        self.search_button.pack(side=tk.LEFT, padx=(10, 0))

        results_frame = ttk.LabelFrame(main_frame, text="Результаты", padding=(10, 10))
        results_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("source", "title")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        self.results_tree.heading("source", text="Источник")
        self.results_tree.heading("title", text="Название")

        # ИЗМЕНЕНИЕ: Увеличиваем ширину колонки "Источник"
        self.results_tree.column("source", width=220, stretch=tk.NO, anchor='w')
        self.results_tree.column("title", width=700, anchor='w')

        # Цвета для тегов строк
        self.results_tree.tag_configure('Local DB', background='#E8F5E9', foreground='#1B5E20')
        self.results_tree.tag_configure('Web', background='#E3F2FD', foreground='#0D47A1')

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.results_tree.bind("<Double-1>", self._on_item_double_click)

        self.status_label = ttk.Label(self, text="Готов к работе.", padding=(10, 5), anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _start_search_thread(self):
        self.search_button.config(state=tk.DISABLED)
        self.results_tree.delete(*self.results_tree.get_children())
        self.all_results = []
        query = self.search_entry.get()
        if not query:
            self.status_label.config(text="Введите поисковый запрос.")
            self.search_button.config(state=tk.NORMAL)
            return
        thread = threading.Thread(target=self._perform_search, args=(query,), daemon=True)
        thread.start()

    def _perform_search(self, query):
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

        self._safe_after(
            lambda: self.status_label.config(text=f"Поиск завершен. Найдено {len(self.all_results)} результатов."))
        self._safe_after(lambda: self.search_button.config(state=tk.NORMAL))

    def _update_gui_with_results(self, results: list):
        for doc in results:
            source = doc.get("source", "N/A")
            tag = 'Local DB' if 'Local' in source else 'Web'
            self.results_tree.insert("", tk.END, values=(source, doc["title"]), tags=(tag,))
            self.all_results.append(doc)

    def _on_item_double_click(self, event):
        if not self.results_tree.selection(): return
        selected_item_id = self.results_tree.selection()[0]
        item_index = self.results_tree.index(selected_item_id)
        doc_to_open = self.all_results[item_index]
        url = doc_to_open.get('url')
        if url:
            open_url(url)
            if "Web" in doc_to_open.get("source", ""):
                query = self.search_entry.get()
                # Перезагружаем базу на случай, если она изменилась
                self.db = load_db()
                add_document_to_db(doc_to_open, query)
                self.db = load_db()  # Перезагружаем снова, чтобы иметь актуальную версию
                self.status_label.config(text=f"Документ '{doc_to_open['title'][:40]}...' добавлен в базу.")