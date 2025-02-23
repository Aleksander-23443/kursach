from tkinter import *
from tkinter import ttk

class DataProcessApp:
    def __init__(self, root):
        self.root = root
        #root["bg"] = "green"
        self.root.title("Программа для очистки и подготовки данных для машинного обучения")
        self.root.geometry("1000x900")
        self.root.resizable(width=False, height=False)

        #блок загрузки данных
        self.load_frame = ttk.Frame(master=self.root, height=600, width=300, relief=RAISED)
        self.load_frame.place(x=0, y=0)

        self.load_button = ttk.Button(master=self.load_frame, text="Загрузить txt файл")
        self.load_button.place(x=83, y=400)



        #блок просмотра части файла
        self.watch_frame = ttk.Frame(master=self.root, height=600, width=400, relief=RAISED, borderwidth=2)
        self.watch_frame.place(x=300, y=0)


        #блок обработки данных
        self.dataProcessing_frame = ttk.Frame(master=self.root, height=600, width=300, relief=RAISED)
        self.dataProcessing_frame.place(x=700, y=0)












if __name__ == "__main__":
    root = Tk()
    app = DataProcessApp(root)
    root.mainloop()