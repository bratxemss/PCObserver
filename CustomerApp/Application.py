import asyncio
import customtkinter as ctk
import threading
from PIL import Image

from Client import Client


class Window:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.window = ctk.CTk()
        self.window.geometry("800x600")
        self.window.title("PCO")
        self.window.iconbitmap("img/Logo.ico")
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(1, weight=1)

        self.main_frame = ctk.CTkFrame(master=self.window, fg_color="#212121")
        self.main_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        self.main_frame.grid_columnconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        #
        img = ctk.CTkImage(Image.open("img/ss.png"), size=(100, 70))
        label_img = ctk.CTkLabel(master=self.window, image=img, text="")
        label_img.grid(row=0, column=1, padx=15, sticky="w")

        self.error_label = ctk.CTkLabel(master=self.main_frame, text="", font=("Robot", 16))
        self.error_label.grid(row=5, column=3, padx=5, pady=15, sticky="s")

        def on_closing():
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", on_closing)


class LoginWindow(Window):
    def __init__(self):
        super().__init__()
        self.id = None
        self.client = Client(self)
        self.thread_reader = None

        self.label_login = ctk.CTkLabel(master=self.main_frame, text="Telegram ID", font=("Robot", 16))
        self.tg_login_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="Token", width=200)
        self.login_button = ctk.CTkButton(master=self.main_frame, text="Enter")
        self.checkbox = ctk.CTkCheckBox(master=self.main_frame, text="Remember Me")

        self.label_login.grid(row=0, column=3, padx=5, pady=5, sticky="n")
        self.tg_login_entry.grid(row=1, column=3, padx=5, pady=5, sticky="n")
        self.login_button.grid(row=2, column=3, padx=5, pady=5, sticky="n")
        self.checkbox.grid(row=3, column=3, padx=5, pady=5, sticky="n")

        self.login_button.configure(command=self.login)

    def get_application_list(self, apps):
        return print(apps)

    def change_window(self):
        tabview = ctk.CTkTabview(master=self.main_frame)
        tabview.add("Application")
        tabview.add("Favorite")

        info_frame = ctk.CTkFrame(master=self.main_frame, fg_color="#212121")  # 212121
        path_frame = ctk.CTkFrame(tabview.tab("Application"), )

        button_add_to_favorite = ctk.CTkButton(tabview.tab("Application"), text="Add to Favorite", width=12,
                                               height=4)
        button_delete = ctk.CTkButton(tabview.tab("Application"), text="Delete", width=12, height=4)
        button_add_to_list = ctk.CTkButton(master=path_frame, text="Add to list", width=12, height=4)
        open_folder_button = ctk.CTkButton(tabview.tab("Application"), text="Open path", width=12, height=4)

        info_label = ctk.CTkLabel(text="", width=5, height=4, master=info_frame)
        path_entry = ctk.CTkEntry(master=path_frame, placeholder_text="Path")
        filter_entry = ctk.CTkEntry(tabview.tab("Application"), placeholder_text="Filter")
        list_of_apps = ctk.CTkOptionMenu(tabview.tab("Application"), values=["Applications"])

        self.label_login.destroy()
        self.tg_login_entry.destroy()
        self.login_button.destroy()
        self.checkbox.destroy()

        self.main_frame.configure(fg_color='#1a1a1a')
        self.main_frame.grid(row=1, column=1, columnspan=5, rowspan=5, padx=0, pady=0)
        tabview.grid(row=1, column=1, columnspan=5, rowspan=5, padx=20, pady=20, sticky="nsew")

        info_frame.configure(height=100)
        self.main_frame.columnconfigure(5, weight=1)
        self.main_frame.rowconfigure(5, weight=1)

        list_of_favorite_apps = ctk.CTkOptionMenu(tabview.tab("Favorite"), values=["Favorite"])

        delete_favorite_button = ctk.CTkButton(tabview.tab("Favorite"), text="Delete Favoriite", width=12, height=4)
        f_open_folder_button = ctk.CTkButton(tabview.tab("Favorite"), text="Open path", width=12, height=4)
        favorite_filter_entry = ctk.CTkEntry(tabview.tab("Favorite"), placeholder_text="Filter")

        # list_of_favorite_apps.configure(values=FavoriteList)
        list_of_favorite_apps.grid(row=0, column=5, padx=300)
        list_of_favorite_apps.configure(width=200, height=30, corner_radius=10)

        favorite_filter_entry.grid(row=1, column=5, pady=5, )

        f_open_folder_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)
        delete_favorite_button.grid(row=1, column=0, sticky="nsew", pady=10, padx=20)

        list_of_apps.grid(row=0, column=5, padx=300)
        list_of_apps.configure(width=200, height=30, corner_radius=10)
        filter_entry.grid(row=1, column=5, padx=300)
        path_frame.grid(column=5)
        open_folder_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)

        info_label.grid(row=5, column=3, )

        path_entry.grid(row=0, column=1, pady=5, padx=25)

        filter_entry.configure(width=200)
        button_add_to_list.grid(row=0, column=6, sticky="nsew", pady=10, padx=20)
        button_add_to_favorite.grid(row=1, column=0, sticky="nsew", pady=10, padx=20)
        button_delete.grid(row=2, column=0, sticky="nsew", pady=10, padx=20)

        open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
        delete_favorite_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                         hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                         height=45)
        button_add_to_list.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
        button_add_to_favorite.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                         hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                         height=45)
        button_delete.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                height=45)
        f_open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                       hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                       height=45)
        (self.client.send_message({
            "command": "get_info",
            "user_id": self.id
        }))

    def login(self):
        self.client.telegram_id = self.tg_login_entry.get()

        self.thread_reader = threading.Thread(target=self.client.run_connection, daemon=True)
        if not self.thread_reader.is_alive():
            self.thread_reader.start()

    def process_answer(self, message, color):
        self.error_label.configure(text=message, text_color=color)
        if message == "Connected successfully":
            self.id = self.client.telegram_id
            self.change_window()





if __name__ == "__main__":
    app = LoginWindow()
    app.window.mainloop()
