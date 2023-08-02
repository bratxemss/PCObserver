import customtkinter as ctk
from PIL import Image
from Client import Client


class LoginWindow:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.window = ctk.CTk()
        self.window.geometry("800x600")
        self.window.title("PCO")
        self.window.iconbitmap("img/Logo.ico")
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(1, weight=1)

        main_frame = ctk.CTkFrame(master=self.window, fg_color="#212121")
        main_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        main_frame.grid_columnconfigure(3, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)

        img = ctk.CTkImage(Image.open("img/ss.png"), size=(100, 70))
        label_img = ctk.CTkLabel(master=self.window, image=img, text="")
        label_img.grid(row=0, column=1, padx=15, sticky="w")

        label_login = ctk.CTkLabel(master=main_frame, text="Login", font=("Robot", 16))
        tg_login_entry = ctk.CTkEntry(master=main_frame, placeholder_text="Token", width=200)
        login_button = ctk.CTkButton(master=main_frame, text="Enter")
        checkbox = ctk.CTkCheckBox(master=main_frame, text="Remember Me")

        label_login.grid(row=0, column=3, padx=5, pady=5, sticky="n")
        tg_login_entry.grid(row=1, column=3, padx=5, pady=5, sticky="n")
        login_button.grid(row=2, column=3, padx=5, pady=5, sticky="n")
        checkbox.grid(row=3, column=3, padx=5, pady=5, sticky="n")

        def login():
            user_input = tg_login_entry.get()
            Client(command="connect", data={"user_id": user_input})

        login_button.configure(command=login)
        self.window.mainloop()


print(LoginWindow())
