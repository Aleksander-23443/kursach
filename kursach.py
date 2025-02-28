from tkinter import *
from tkinter import ttk
import pandas as pd
import threading
import numpy as np
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog


class DataProcessApp:
    def __init__(self, root):
        self.root = root
        # root["bg"] = "green"
        self.root.title(
            "Программа для очистки и подготовки данных для машинного обучения"
        )
        self.root.geometry("1000x900")
        self.root.resizable(width=False, height=False)
        self.data = None
        self.original_data = None
        self.columns_for_drop = []

        # создание стиля
        self.style = ttk.Style()
        self.style.configure(style="Custom.TLabel", font=("Arial", 15))

        # блок загрузки данных
        self.load_frame = ttk.Frame(
            master=self.root, height=600, width=300, relief=RAISED
        )
        self.load_frame.place(x=0, y=0)

        self.image = Image.open("image_data_process.png")
        self.image = self.image.resize((290, 290))
        self.photo = ImageTk.PhotoImage(self.image)
        self.label_image = ttk.Label(master=self.load_frame, image=self.photo)
        self.label_image.place(x=0, y=40)

        self.load_button = ttk.Button(
            master=self.load_frame, text="Загрузить txt файл", command=self.load_data
        )
        self.load_button.place(x=50, y=400, height=30, width=200)

        # блок просмотра части файла
        self.watch_frame = ttk.Frame(
            master=self.root, height=600, width=400, relief=RAISED
        )
        self.watch_frame.place(x=300, y=0)

        self.label_watch = ttk.Label(
            master=self.watch_frame, text="Загруженный файл", style="Custom.TLabel"
        )
        self.label_watch.place(x=110, y=10)

        self.tree = ttk.Treeview(self.watch_frame, columns=[], show="headings")
        self.tree.place(x=5, y=50, height=500, width=390)

        # блок обработки данных
        self.dataProcessing_frame = ttk.Frame(
            master=self.root, height=600, width=300, relief=RAISED
        )
        self.dataProcessing_frame.place(x=700, y=0)

        self.process_label = ttk.Label(
            master=self.dataProcessing_frame,
            text="Очистка и подготовка данных",
            style="Custom.TLabel",
        )
        self.process_label.place(x=5, y=10)

        self.delete_columns_btn = ttk.Button(
            master=self.dataProcessing_frame,
            text="Выбрать столбцы для удаления",
            command=self.choice_columns_for_drop,
        )
        self.delete_columns_btn.place(x=60, y=460, height=30, width=200)

        self.process_btn = ttk.Button(
            master=self.dataProcessing_frame,
            text="Очистить и подготовить дынные",
            command=self.start_processing,
        )
        self.process_btn.place(x=60, y=500, height=30, width=200)

        # блок статуса
        self.status_frame = ttk.Frame(
            master=self.root, height=300, width=400, relief=RAISED
        )
        self.status_frame.place(x=0, y=600)

        self.status_var = StringVar()
        self.status_var.set("Статус: Ожидание загрузки данных")
        self.status_label = ttk.Label(
            master=self.status_frame,
            textvariable=self.status_var,
            style="Custom.TLabel",
        )
        self.status_label.place(x=10, y=10)

        # блок сохранения изменённого файла

        self.save_frame = ttk.Frame(
            master=self.root, height=300, width=600, relief=RAISED
        )
        self.save_frame.place(x=400, y=600)

        self.save_btn = ttk.Button(
            master=self.save_frame,
            text="Сохранить в формате CSV",
            command=self.save_data,
        )
        self.save_btn.place(x=200, y=150, height=30, width=200)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", ".txt")])

        if not file_path:
            return

        try:
            temp_data = pd.read_csv(
                file_path, sep=r"\s+", engine="python", na_filter=False
            )
            temp_data = temp_data.dropna(axis=1, how="all")
            if temp_data.empty:
                messagebox.showerror(
                    title="Ошибка",
                    message="Файл пуст. Выберите другой файл.",
                )
                return
            if len(temp_data.columns) == 0:
                messagebox.showerror(
                    title="Ошибка",
                    message="Файл не содержит данных или заголовков столбцов.",
                )
                return

            if not all(temp_data.dtypes.apply(lambda x: np.issubdtype(x, np.number))):
                messagebox.showwarning(
                    title="Предупреждение",
                    message="Некоторые столбцы содержат нечисловые значения.",
                )

            self.original_data = temp_data.copy()
            self.data = self.original_data.copy()
            self.update_treeview()
            self.status_var.set("Статус: Данные загружены")

        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Не удалось загрузить файл: {e}"
            )

    def start_processing(self):
        if self.data is not None:
            threading.Thread(target=self.process_data).start()
        else:
            messagebox.showwarning(
                title="Предупреждение",
                message="Сначала загрузите данные"
            )

    def update_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.tree["columns"] = list(range(1, len(self.data.columns) + 1))

        for i in range(len(self.data.columns)):
            self.tree.heading(i + 1, text=str(i + 1))
            self.tree.column(i + 1, stretch=False, width=100)
            self.root.update_idletasks()

        for ind, row in self.data.iterrows():
            self.tree.insert(
                "", END, iid=ind, text=f"Строка {ind+1}", values=row.tolist()
            )

    def process_data(self):
        try:

            if self.columns_for_drop:
                self.data.drop(
                    self.data.columns[self.columns_for_drop], axis=1, inplace=True
                )
            self.data.drop_duplicates(inplace=True)
            self.data.dropna(inplace=True)
            self.update_treeview()
            self.status_var.set("Статус: Данные очищены и подготовлены")
        except Exception as e:
            messagebox.showerror(
                title="Ошибка",
                message=f"Ошибка при обработке данных: {e}"
            )

    def save_data(self):
        if self.data is None:
            messagebox.showwarning(
                title="Предупреждение",
                message="Нет данных для сохранения"
            )
            return

        if hasattr(self, "original_data") and self.original_data.equals(self.data):
            confirm = messagebox.askyesno(
                title="Подтверждение",
                message="Данные не были изменены. Вы уверены, что хотите сохранить файл?",
            )
            if not confirm:
                return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV файлы", "*.csv")]
        )
        if file_path:
            self.data.to_csv(file_path, index=False)
            messagebox.showinfo(title="Успех",
                                message="Файл успешно сохранен")

    def choice_columns_for_drop(self):
        if self.data is not None:
            self.columns_for_drop = simpledialog.askstring(
                title="Выбор столбцов",
                prompt="Введите номера столбцов для удаление:",
            )
            if self.columns_for_drop:
                self.columns_for_drop = [
                    int(i) - 1 for i in self.columns_for_drop.split(",")
                ]
                self.status_var.set("Статус: выбраны столбцы для удаления")
        else:
            messagebox.showwarning(
                title="Предупреждение",
                message="Сначала загрузите данные"
            )


if __name__ == "__main__":
    root = Tk()
    app = DataProcessApp(root)
    root.mainloop()
