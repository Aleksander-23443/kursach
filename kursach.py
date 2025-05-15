import os.path
import re
import tkinter as tk
from tkinter import ttk
import pandas as pd
import threading
import numpy as np
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog


class DataProcessApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Программа для очистки и подготовки данных для машинного обучения")
        self.geometry("1100x700")

        self.data = {}
        self.current_file = None
        self.current_data = None
        self.history = {}
        self.history_indices = {}

        self.style = ttk.Style(self)
        self.current_theme = tk.StringVar(value=self.style.theme_use())
        self.create_widgets()

    # главные составляющие интерфейса
    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        open_button = ttk.Button(top_frame, text="Открыть файл", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=20, pady=20)

        lab_for_choice_file = ttk.Label(top_frame, text="Выбрать файл:")
        lab_for_choice_file.pack(side=tk.LEFT, padx=20)

        self.file_var = tk.StringVar()

        self.file_combobox = ttk.Combobox(
            top_frame, textvariable=self.file_var, state="readonly"
        )
        self.file_combobox.pack(side=tk.LEFT, padx=20, pady=20)
        self.file_combobox.bind("<<ComboboxSelected>>", self.on_file_select)

        current_theme_label = ttk.Label(top_frame, text="Тема:")
        current_theme_label.pack(side=tk.LEFT, padx=20)
        themes = self.style.theme_names()

        self.theme_combobox = ttk.Combobox(
            top_frame, values=themes, textvariable=self.current_theme, state="readonly"
        )
        self.theme_combobox.pack(side=tk.LEFT, padx=20)
        self.theme_combobox.bind("<<ComboboxSelected>>",self.change_theme)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.tab_process = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_process, text="Обработка")
        self.create_process_tab()

        self.tab_filter = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_filter, text="Фильтрация")
        self.create_filter_tab()

        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text="История")
        self.create_history_tab()



    def parse_file(self, file_path):
        f = open(file_path, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()
        # Запрос ключей
        keys_str = simpledialog.askstring(
            title="Ключи",
            prompt="Введите ключи для парсинга через запятую(например: имя, город, возраст)",
        )
        if keys_str:
            key = [k.strip() for k in keys_str.split(",")]
        else:
            key = []
        data = []
        for line in lines:

            line = line.strip()
            if not line:
                continue
            row = {}
            parts = [p.strip() for p in re.split(r",\s*", line)]
            for part in parts:
                if ":" in part:
                    k, v = part.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if not key or k in key:
                        row[k] = v
            data.append([row.get(k, "") for k in key])
        df = pd.DataFrame(data, columns=key)
        return df

    def set_current_file(self, file_path):
        self.current_file = file_path
        self.current_data = self.data[file_path]
        self.update_process_tab()
        self.update_history_tab()
        self.update_filter_tab()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not file_path:
            return
        try:
            df = self.parse_file(file_path)
        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Не удалось открыть файл: {e}"
            )
            return

        self.data[file_path] = df

        self.history[file_path] = [
            (df.copy(), f"Открыт файл {os.path.basename(file_path)}")
        ]

        self.history_indices[file_path] = 0

        self.file_combobox["values"] = list(self.data.keys())
        self.file_combobox.set(file_path)

        self.set_current_file(file_path)

    def on_file_select(self, event=None):
        file_path = self.file_combobox.get()
        self.set_current_file(file_path)

    def create_process_tab(self):
        self.process_tree = ttk.Treeview(self.tab_process)
        self.process_tree.pack(expand=1, fill="both", side=tk.LEFT)

        vertical_scroll = ttk.Scrollbar(
            self.tab_process, orient="vertical", command=self.process_tree.yview
        )
        vertical_scroll.pack(side="right", fill="y")

        horizontal_scroll = ttk.Scrollbar(
            self.tab_process, orient="horizontal", command=self.process_tree.xview
        )
        horizontal_scroll.pack(side="bottom", fill="x")

        self.process_tree.configure(
            yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set
        )

        frame_for_button = ttk.Frame(self.tab_process)
        frame_for_button.pack(fill="y", anchor="center", padx=5, pady=5)

        change_keys_button = ttk.Button(
            frame_for_button, text="Изменить ключи", command=self.change_keys
        )
        change_keys_button.pack(side=tk.TOP, pady=15)

        delete_space_button = ttk.Button(
            frame_for_button, text="Удалить пробелы", command=self.del_spaces
        )
        delete_space_button.pack(side=tk.TOP, pady=15)

        del_special_chars_button = ttk.Button(
            frame_for_button,
            text="Удалить спецсимволы",
            command=self.remove_special_chars,
        )
        del_special_chars_button.pack(side=tk.TOP, pady=15)

        lowercase_button = ttk.Button(
            frame_for_button,
            text="Перевести в нижний регистр",
            command=self.to_lowercase,
        )
        lowercase_button.pack(side=tk.TOP, pady=15)

        delete_empty_str_button = ttk.Button(
            frame_for_button,
            text="Удалить пустые строки",
            command=self.remove_empty_rows,
        )
        delete_empty_str_button.pack(side=tk.TOP, pady=15)

        fill_missing_button = ttk.Button(
            frame_for_button,
            text="Заполнить пропуски наиболеее стречающимися",
            command=self.fill_missing_with_mode,
        )
        fill_missing_button.pack(side=tk.TOP, pady=5)

        delete_duplicate_button = ttk.Button(
            frame_for_button, text="Удалить дубликаты", command=self.remove_duplicates
        )
        delete_duplicate_button.pack(side=tk.TOP, pady=15)

        remove_columns_button = ttk.Button(
            frame_for_button, text="Удалить столбцы", command=self.delete_columns
        )
        remove_columns_button.pack(side=tk.TOP, pady=15)

        save_to_csv_button = ttk.Button(
            frame_for_button, text="Сохранить в CSV", command=self.save_to_csv
        )
        save_to_csv_button.pack(side=tk.TOP, padx=15)

        self.process_status = ttk.Label(self.tab_process, text="")
        self.process_status.pack(side=tk.RIGHT, fill="x")

    def display_data(self, df, tree):
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for i, row in df.iterrows():
            values = []
            has_empty = False
            for col in df.columns:
                val = row[col]
                if pd.isna(val) or val == "":
                    has_empty = True
                    values.append("" if pd.isna(val) else val)
                else:
                    values.append(val)
            if has_empty:
                tree.insert("", "end", values=values, tags=("empty",))
            else:
                tree.insert("", "end", values=values)

        tree.tag_configure(
            "empty", background="lightyellow", font=("TkDefaultFont", 10, "bold")
        )

    def update_process_tab(self):
        df = self.current_data
        self.display_data(df, self.process_tree)
        self.process_status.config(
            text=f"Файл: {os.path.basename(self.current_file)}, строк: {len(df)}"
        )

    def del_spaces(self):
        if self.current_data is not None:
            for col in self.current_data.select_dtypes(include=["object"]).columns:
                self.current_data[col] = self.current_data[col].str.strip()

            self.record_action("Удалены пробелы в начале/конце строк")
            self.update_process_tab()
        else:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return

    def remove_special_chars(self):
        if self.current_data is not None:
            pettern = r"[^0-9A-Za-z\u0400-\u04FF ]"
            for col in self.current_data.select_dtypes(include=["object"]).columns:
                self.current_data[col] = self.current_data[col].str.replace(
                    pettern, "", regex=True
                )
            self.update_process_tab()
            self.record_action("Удалены спецсимволы")
        else:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return

    def to_lowercase(self):
        if self.current_data is not None:
            for col in self.current_data.select_dtypes(include=["object"]).columns:
                self.current_data[col] = self.current_data[col].str.lower()

            self.update_process_tab()
            self.record_action("Переведен текст в нижний регистр")
        else:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return

    def remove_empty_rows(self):
        if self.current_data is not None:
            df = self.current_data.replace(r"^\s*$", pd.NA, regex=True)
            before = len(self.current_data)
            self.current_data = df.dropna(how="all")
            after = len(self.current_data)

            self.record_action(f"Удалено пустых строк: {before - after}")
            self.data[self.current_file] = self.current_data
            self.update_process_tab()
        else:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return

    def remove_duplicates(self):
        if self.current_data is not None:
            before = len(self.current_data)
            self.current_data = self.current_data.drop_duplicates()
            after = len(self.current_data)

            self.record_action(f"Удалено дубликатов: {before - after}")
            self.data[self.current_file] = self.current_data
            self.update_process_tab()
        else:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return

    def delete_columns(self):
        if self.current_data is None:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return
        cols = list(self.current_data.columns)
        wind = tk.Toplevel(self)
        wind.title("Удалить столбцы")

        wind_lb = ttk.Label(wind, text="Выберите столбцы для удаления:")
        wind_lb.pack(pady=5)

        listbox = tk.Listbox(wind, selectmode=tk.MULTIPLE)
        for col in cols:
            listbox.insert(tk.END, col)
        listbox.pack(fill="both", expand=1, padx=15, pady=15)

        def apply_delete():
            sel = listbox.curselection()
            sel_cols = [cols[i] for i in sel]
            if sel_cols:
                self.current_data.drop(columns=sel_cols, inplace=True)
                self.update_process_tab()
                self.record_action(f"Удалены столбцы: {', '.join(sel_cols)}")
            wind.destroy()

        button = ttk.Button(wind, text="Удалить", command=apply_delete)
        button.pack(pady=5)

        wind.transient(self)
        wind.grab_set()
        self.wait_window(wind)

    def change_keys(self):
        if not self.current_file:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )
            return

        file_path = self.current_file
        try:
            df = self.parse_file(file_path)
        except Exception as e:
            messagebox.showerror(
                title="Ошибка", message=f"Не удалось перепарсить файл: {e}"
            )
            return

        self.data[file_path] = df
        self.current_data = df
        self.history[file_path] = [(df.copy(), "Изменены ключи парсинга")]
        self.history_indices[file_path] = 0

        self.update_process_tab()
        self.update_history_tab()

    def fill_missing_with_mode(self):
        if self.current_data is not None:
            df = self.current_data.replace(r"^\s*$", pd.NA, regex=True)
            fill_count = 0

            for col in df.columns:
                if df[col].isna().any():
                    try:
                        mode = df[col].mode(dropna=True)[0]
                        missing_before = df[col].isna().sum()
                        df[col] = df[col].fillna(mode)
                        missing_after = df[col].isna().sum()
                        fill_count += missing_before - missing_after
                    except IndexError:
                        continue
            self.current_data = df
            self.data[self.current_file] = self.current_data
            self.record_action(
                f"Заполнены пропуски наиболее встречающимся (всего: {fill_count})"
            )
            self.update_process_tab()
        else:
            messagebox.showwarning(
                title="Нет данных", message="Сначала загрузите файл."
            )

    def save_to_csv(self):
        if self.current_data is None:
            return
        file_path = filedialog.askopenfilename(
            defaultextension=".csv", filetypes=[("CSV-файл", "*.csv")]
        )
        if not file_path:
            return
        try:
            self.current_data.to_csv(file_path, index=False, encoding="utf-8")
            messagebox.showinfo(
                title="Сохранено", message=f"Данные сохранены в {file_path}"
            )
        except Exception as e:
            messagebox.showerror(
                title="Ошибка", message=f"Не удалось сохранить файл: {e}"
            )

    def create_history_tab(self):
        hist_frame = ttk.Frame(self.tab_history)
        hist_frame.pack(fill="both", expand=1, padx=10, pady=10)

        self.hist_listbox = tk.Listbox(hist_frame)
        self.hist_listbox.pack(side="left", fill="both", expand=1)

        hist_scroll = ttk.Scrollbar(
            hist_frame, orient="vertical", command=self.hist_listbox.yview
        )
        hist_scroll.pack(side="right", fill="y")
        self.hist_listbox.config(yscrollcommand=hist_scroll.set)

        btn_frame = ttk.Frame(self.tab_history)
        btn_frame.pack(fill="x", pady=5)

        undo_button = ttk.Button(
            btn_frame, text="Отменить (Undo)", command=self.undo
        )
        undo_button.pack(side=tk.LEFT, padx=5)

        redobutton = ttk.Button(
            btn_frame, text="Повторить (Redo)", command=self.redo
        )
        redobutton.pack(side=tk.LEFT, padx=5)

    def undo(self):
        if self.current_file is None:
            return

        idx = self.history_indices[self.current_file]

        if idx > 0:
            self.history_indices[self.current_file] = idx - 1
            self.current_data = self.history[self.current_file][
                self.history_indices[self.current_file]
            ][0].copy()
            self.data[self.current_file] = self.current_data
            self.update_process_tab()
            self.update_history_tab()

    def redo(self):
        if self.current_file is None:
            return

        idx = self.history_indices[self.current_file]
        hist = self.history[self.current_file]

        if idx < len(hist) - 1:
            self.history_indices[self.current_file] = idx + 1
            self.current_df = self.history[self.current_file][
                self.history_indices[self.current_file]
            ][0].copy()

            self.data[self.current_file] = self.current_df

            self.update_process_tab()
            self.update_history_tab()

    def update_history_tab(self):
        self.hist_listbox.delete(0, tk.END)

        if self.current_file and self.current_file in self.history:
            hist = self.history[self.current_file]
            current_index = self.history_indices[self.current_file]

            for i, (df, desc) in enumerate(hist):
                prefix = "-> " if i == current_index else "   "
                self.hist_listbox.insert(tk.END, f"{prefix}{desc}")

    def record_action(self, description):
        if self.current_file not in self.history:
            return

        hist = self.history[self.current_file]
        idx = self.history_indices[self.current_file]

        if idx < len(hist) - 1:
            self.history[self.current_file] = hist[: idx + 1]
        df_copy = self.current_data.copy()
        self.history[self.current_file].append((df_copy, description))
        self.history_indices[self.current_file] = (
            len(self.history[self.current_file]) - 1
        )
        self.update_history_tab()


    def change_theme(self, event=None):
        theme = self.current_theme.get()
        try:
            self.style.theme_use(theme)
        except:
            pass

    def search_in_table(self):

        col = self.search_column.get()
        val = self.search_value.get()

        if not col or not val:
            return

        df = self.current_df
        mask = df[col].astype(str).str.contains(val, case=False, na=False)
        filtered = df[mask]
        self.display_data(filtered, self.filter_tree)

    def reset_filter(self):
        self.display_data(self.current_data, self.filter_tree)

    def sort_data(self, ascending=True):
        col = self.sort_column.get()
        if not col:
            return
        try:
            sorted_df = self.current_df.sort_values(by=col, ascending=ascending)
            self.display_data(sorted_df, self.filter_tree)
        except Exception as e:
            messagebox.showerror(title="Ошибка",
                                 message=f"Не удалось отсортировать: {e}"
            )




    def calculate_stats(self):
        if self.current_data is None:
            return
        df = self.current_data
        desc = ""
        for col in df.columns:
            try:
                series = pd.to_numeric(df[col], errors="coerce").dropna()
                if series.empty:
                    desc += f"{col}: нет числовых данных\n"
                    continue
                mean = series.mean()
                median = series.median()
                mode = series.mode().iloc[0] if not series.mode().empty else None
                min_val = series.min()
                max_val = series.max()
                desc += f"{col}: среднее={mean:.2f}, медиана={median:.2f}, мода={mode}, мин={min_val}, макс={max_val}\n"
            except Exception as e:
                desc += f"{col}: ошибка вычислений\n"
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, desc)

    def group_count(self):
        col = self.group_column.get()
        if not col:
            return
        df = self.current_data
        try:
            counts = df[col].value_counts()
            result = "\n".join(f"{k}: {v}" for k, v in counts.items())
            messagebox.showinfo(
                title="Группировка",
                message=f"Подсчет по столбцу {col}:\n{result}"
            )
        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Не удалось выполнить группировку: {e}"
            )


    def create_filter_tab(self):

        search_frame = ttk.LabelFrame(self.tab_filter, text="Поиск")
        search_frame.pack(fill='x', padx=5, pady=5)

        col_label = ttk.Label(search_frame, text="Столбец:")
        col_label.pack(side=tk.LEFT)

        self.search_column = tk.StringVar()
        self.search_col_combobox = ttk.Combobox(
            search_frame, textvariable=self.search_column, state="readonly"
        )
        self.search_col_combobox.pack(side=tk.LEFT, padx=5)

        meaning_label = ttk.Label(search_frame, text="Значение:")
        meaning_label.pack(side=tk.LEFT)

        self.search_value = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_value)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        finding_button = ttk.Button(
            search_frame, text="Найти", command=self.search_in_table
        )
        finding_button.pack(side=tk.LEFT, padx=5)

        reset_filter_buttton = ttk.Button(
            search_frame, text="Сбросить фильтр", command=self.reset_filter
        )
        reset_filter_buttton.pack(side=tk.LEFT, padx=5)

        sort_frame = ttk.LabelFrame(self.tab_filter, text="Сортировка")
        sort_frame.pack(fill="x", padx=5, pady=5)

        column_label_for_sort = ttk.Label(sort_frame, text="Столбец:")
        column_label_for_sort.pack(side=tk.LEFT)

        self.sort_column = tk.StringVar()

        self.sort_col_combo = ttk.Combobox(
            sort_frame, textvariable=self.sort_column, state="readonly"
        )
        self.sort_col_combo.pack(side=tk.LEFT, padx=5)

        ascending_button = ttk.Button(
            sort_frame, text="По возрастанию", command=lambda: self.sort_data(True)
        )
        ascending_button.pack(side=tk.LEFT, padx=5)

        descending_button = ttk.Button(
            sort_frame, text="По убыванию", command=lambda: self.sort_data(False)
        )
        descending_button.pack(side=tk.LEFT, padx=5)

        group_frame = ttk.LabelFrame(self.tab_filter, text="Группировка")
        group_frame.pack(fill="x", padx=5, pady=5)

        column_label_for_group = ttk.Label(group_frame, text="Столбец:")
        column_label_for_group.pack(side=tk.LEFT)

        self.group_column = tk.StringVar()

        self.group_col_combobox = ttk.Combobox(
            group_frame, textvariable=self.group_column, state="readonly"
        )
        self.group_col_combobox.pack(side=tk.LEFT, padx=5)

        amount_repeat_button = ttk.Button(
            group_frame, text="Посчитать повторы", command=self.group_count
        )
        amount_repeat_button.pack(side=tk.LEFT, padx=5)

        stats_frame = ttk.LabelFrame(self.tab_filter, text="Статистика по столбцам")
        stats_frame.pack(fill="both", padx=5, pady=5, expand=1)

        self.stats_text = tk.Text(stats_frame, height=5)
        self.stats_text.pack(fill="both", padx=5, pady=5)

        calculation_button = tk.Button(
            stats_frame, text="Рассчитать", command=self.calculate_stats
        )
        calculation_button.pack(pady=5)

        preview_frame = ttk.LabelFrame(self.tab_filter, text="Текущие данные")
        preview_frame.pack(fill="both", padx=5, pady=5, expand=1)

        self.filter_tree = ttk.Treeview(preview_frame)
        self.filter_tree.pack(expand=1, fill="both")

        vsb2 = ttk.Scrollbar(
            preview_frame, orient="vertical", command=self.filter_tree.yview
        )
        vsb2.pack(side="right", fill="y")

        hsb2 = ttk.Scrollbar(
            preview_frame, orient="horizontal", command=self.filter_tree.xview
        )
        hsb2.pack(side="bottom", fill="x")

        self.filter_tree.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)


    def update_filter_tab(self):

        if self.current_file and self.current_file in self.data:
            cols = list(self.current_df.columns)
            self.search_col_combobox["values"] = cols
            self.sort_col_combo["values"] = cols
            self.group_col_combobox["values"] = cols

            self.search_col_combobox.set("")
            self.sort_col_combo.set("")
            self.group_col_combobox.set("")

            self.display_data(self.current_df, self.filter_tree)
            self.stats_text.delete("1.0", tk.END)
        else:
            self.search_col_combobox["values"] = []
            self.sort_col_combo["values"] = []
            self.group_col_combobox["values"] = []

            self.stats_text.delete("1.0", tk.END)
            self.filter_tree.delete(*self.filter_tree.get_children())


if __name__ == "__main__":
    app = DataProcessApp()
    app.mainloop()
