from tkinter import *
from tkinter import ttk
import pandas as pd
import threading
# from PIL import Image, ImageTk
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
        self.columns_for_drop = []

        # создание стиля
        self.style = ttk.Style()
        self.style.configure("Custom.TLabel", font=("Arial", 15))

        # блок загрузки данных
        self.load_frame = ttk.Frame(
            master=self.root, height=600, width=300, relief=RAISED
        )
        self.load_frame.place(x=0, y=0)

        # self.image = Image.open("free-icon-data-processing-4536820.png")
        # self.image = self.image.resize((290, 290))
        # self.photo = ImageTk.PhotoImage(self.image)
        # self.label_image = ttk.Label(master=self.load_frame, image=self.photo)
        # self.label_image.place(x=0, y= 40)

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
            master=self.dataProcessing_frame, text="Выбрать столбцы для удаления"
        )
        self.delete_columns_btn.place(x=60, y=460, height=30, width=200)

        self.process_btn = ttk.Button(
            master=self.dataProcessing_frame,
            text="Очистить и подготовить дынные",
            command=self.process_label,
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
            self.data = pd.read_csv(file_path, delimiter=" ")
            self.update_treeview()
            self.status_var.set("Статус: Данные загружены")

            for row in self.tree.get_children():
                self.tree.delete(row)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

                if not lines:
                    return

                num_columns = len(lines[0].strip().split())

                self.tree["columns"] = [str(i) for i in range(1, num_columns + 1)]

                for col in self.tree["columns"]:
                    self.tree.heading(col, text=f"{col}")
                    self.tree.column(col, stretch=False, width=50)
                    self.root.update_idletasks()

                for row_index, line in enumerate(lines, start=1):
                    value = line.strip().split()
                    self.tree.insert(
                        "", END, iid=row_index, text=f"Строка{row_index}", values=value
                    )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    def start_processing(self):
        if self.data is not None:
            threading.Thread(target=self.process_data).start()
        else:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")


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
        if self.data is not None:
            try:

                self.data.drop_duplicates(inplace=True)

                self.data.dropna(inplace=True)
                self.status_var.set("Данные очищены и подготовлены")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обработке данных: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")

    def save_data(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV файлы", "*.csv")]
            )
            if file_path:
                self.data.to_csv(file_path, index=False)
                messagebox.showinfo("Успех", "Файл успешно сохранен")


if __name__ == "__main__":
    root = Tk()
    app = DataProcessApp(root)
    root.mainloop()
