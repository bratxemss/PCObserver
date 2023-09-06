import customtkinter as ctk
import threading
import os
import subprocess


from PIL import Image
from shlex import split
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
        self.window.resizable(False, False)

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
        self.button_delete = None
        self.thread_reader = None
        self.button_add_to_list = None
        self.list_of_apps = None
        self.filter_entry = None
        self.info_label = None
        self.open_folder_button = None
        self.info_frame = None
        self.path_entry = None
        self.client = Client(self)

        self.label_login = ctk.CTkLabel(master=self.main_frame, text="Telegram ID", font=("Robot", 16))
        self.tg_login_entry = ctk.CTkEntry(master=self.main_frame, placeholder_text="Token", width=200)
        self.login_button = ctk.CTkButton(master=self.main_frame, text="Enter")
        self.checkbox = ctk.CTkCheckBox(master=self.main_frame, text="Remember Me")

        self.label_login.grid(row=0, column=3, padx=5, pady=5, sticky="n")
        self.tg_login_entry.grid(row=1, column=3, padx=5, pady=5, sticky="n")
        self.login_button.grid(row=2, column=3, padx=5, pady=5, sticky="n")
        self.checkbox.grid(row=3, column=3, padx=5, pady=5, sticky="n")

        self.login_button.configure(command=self.login)
        self.values = None

    def change_window(self):
        tabview = ctk.CTkTabview(master=self.main_frame)
        tabview.add("Application")
        tabview.add("Favorite")

        self.info_frame = ctk.CTkFrame(master=self.main_frame, fg_color="#212121")  # 212121

        path_frame = ctk.CTkFrame(tabview.tab("Application"), )

        button_add_to_favorite = ctk.CTkButton(tabview.tab("Application"), text="Add to Favorite", width=12,
                                               height=4)
        self.button_delete = ctk.CTkButton(tabview.tab("Application"), text="Delete", width=12, height=4)
        self.button_add_to_list = ctk.CTkButton(master=path_frame, text="Add to list", width=12, height=4)
        self.open_folder_button = ctk.CTkButton(tabview.tab("Application"), text="Open path", width=12, height=4)

        self.info_label = ctk.CTkLabel(text="", width=5, height=4, master=self.info_frame)

        self.path_entry = ctk.CTkEntry(master=path_frame, placeholder_text="Path")
        self.filter_entry = ctk.CTkEntry(tabview.tab("Application"), placeholder_text="Filter")
        self.list_of_apps = ctk.CTkOptionMenu(tabview.tab("Application"), values=["Applications"])

        self.label_login.destroy()
        self.tg_login_entry.destroy()
        self.login_button.destroy()
        self.checkbox.destroy()

        self.main_frame.grid(row=1, column=1, columnspan=5, rowspan=5, padx=20, pady=20, sticky="nsew")
        tabview.grid(row=1, column=1, columnspan=5, rowspan=5, sticky="n")

        self.info_frame.configure(height=100,)
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

        self.list_of_apps.grid(row=0, column=5, padx=300)
        self.list_of_apps.configure(width=200, height=30, corner_radius=10)
        self.filter_entry.grid(row=1, column=5, padx=300)
        path_frame.grid(column=5)
        self.open_folder_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)

        self.info_label.grid(row=5, column=3, padx=5, pady=(0, 15), sticky="s")

        self.path_entry.grid(row=0, column=1, pady=5, padx=25)

        self.filter_entry.configure(width=200)
        self.button_add_to_list.grid(row=0, column=6, sticky="nsew", pady=10, padx=20)
        button_add_to_favorite.grid(row=1, column=0, sticky="nsew", pady=10, padx=20)
        self.button_delete.grid(row=2, column=0, sticky="nsew", pady=10, padx=20)

        self.open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
        delete_favorite_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                         hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                         height=45)
        self.button_add_to_list.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
        button_add_to_favorite.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                         hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                         height=45)
        self.button_delete.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                height=45)
        f_open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                       hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                       height=45)

    def login(self):
        self.client.telegram_id = self.tg_login_entry.get()

        self.thread_reader = threading.Thread(target=self.client.run_connection, daemon=True)
        if not self.thread_reader.is_alive():
            self.thread_reader.start()

    def process_answer(self, data):
        message = data.get("message")
        success = data.get("success")

        if not success:
            color = "#be0000"  # red
        else:
            color = "#33b631"  # green
            if not message:
                message = "Unexpected error, please restart application"

        self.error_label.configure(text=message, text_color=color)

    def render_applications(self, apps):
        self.list_of_apps.configure(values=[apps[i]["name"] for i in range(len(apps))])

    def set_functional(self, apps, telegram_id):
        self.list_of_apps.bind("<Button-1>", lambda event: self.window.after(1,
                                                                             lambda: self.show_info
                                                                             (event, apps=apps, label=self.info_label)))
        self.filter_entry.bind("<KeyRelease>", lambda event: self.filter_listbox(event=event, entry=self.filter_entry,
                                                                                 list_app=self.list_of_apps, apps=apps))

        self.open_folder_button.configure(command=lambda: self.open_path(list_app=self.list_of_apps))

        self.path_entry.bind('<Return>', lambda event: self.add_application(apps, telegram_id))
        self.button_add_to_list.configure(command=lambda: self.add_application(apps, telegram_id=telegram_id))
        self.button_delete.configure(command=lambda: self.delete_application(apps, telegram_id))

    def open_path(self, event=None, list_app=None):
        current_selection_in_list = list_app.get()
        data = [self.values[current_selection_in_list]][0]
        file_path = data[0]
        try:
            folder_path = os.path.dirname(file_path)
            subprocess.run(['explorer', folder_path])
        except Exception as ex:
            print(ex)

    def show_info(self, event=None, apps=None, label=None):
        try:
            self.values = {apps[i]["name"]: [apps[i]["path"], self.size_reader(int(apps[i]["size"]))] for i in range(len(apps))}
            current_selection_in_list = self.list_of_apps.get()
            if current_selection_in_list:
                data = [self.values[current_selection_in_list]][0]
                self.info_frame.grid(row=5, column=3, padx=(60, 70), pady=(0, 15), sticky="s")
                label.configure(
                     text=f"Name: {current_selection_in_list}\nPath: {data[0]}\nSize of path folder: {data[1]}",
                     font=("Robot", 18))
        except KeyError:
            pass

    def filter_listbox(self, apps, event=None, entry=None, list_app=None,):
        user_input = entry.get()
        current_values = [apps[i]["name"] for i in range(len(apps))]
        list_app.configure(values=[])
        filtered_items = []
        for item in current_values:
            if user_input.lower() in item.lower():
                filtered_items.append(item)
        if user_input == "":
            filtered_items = current_values
        list_app.configure(values=filtered_items)
        entry.bind('<Return>', lambda event: entry.delete(0, 'end'))

    def size_reader(self, file_size: int):
        if 1024 <= file_size < (1024 ** 2):
            size = f"{round(file_size / 1024, 2)} KB"
        elif (1024 ** 2) <= file_size < (1024 ** 3):
            size = f"{round(file_size / (1024 ** 2), 2)} MB"
        elif file_size >= (1024 ** 3):
            size = f"{round(file_size / (1024 ** 3), 2)} GB"
        else:
            size = f"{file_size} B"
        return size

    def repeat_string(self, string):
        return string.strip('"')

    def add_application(self, apps, telegram_id):
        command = "register_app"
        file_path = self.path_entry.get()
        self.path_entry.delete(0, 'end')
        if self.is_valid_path(file_path):
            file, file_path, file_size = self.get_file_info(file_path)
            message = {
                "command": command,
                "data":
                    {
                        "user_id": telegram_id,
                        "application": {
                            "name": file,
                            "path": file_path,
                            "size": file_size,
                            "status": False,
                            "favorite": False
                        }
                    }
            }
            try:
                self.client.send_message(message)
            except Exception as ex:
                print("Error", ex)
            print("request sended")
        self.render_applications(apps)
        print("list updated")

        return

    def delete_application(self, apps, telegram_id, list_app=None):
        command = "delete_app"
        message = None
        current_selection_in_list = self.list_of_apps.get()
        print(self.list_of_apps.cget("values"))
        for item in apps:
            if item["name"] == current_selection_in_list:
                print(item["id"])
                app_id = item["id"]
                message = {
                    "command": command,
                    "data":
                        {
                            "user_id": telegram_id,
                            "application": {
                                "id": app_id
                            }
                        }}
                apps.remove(item)
                print(apps)
                self.render_applications(apps)

        if message:
            try:
                self.client.send_message(message)
            except Exception as ex:
                print("Error", ex)

    def is_valid_path(self, file_path):
        split_path = split(file_path)
        joined_path = os.path.join(*split_path)
        if os.path.exists(joined_path):
            return True
        else:
            return False

    def get_file_info(self, file_path):
        file_path = self.repeat_string(file_path)
        file_path = r"{}".format(file_path)
        file = os.path.basename(file_path)
        file_size = 0
        if file_path.endswith('.lnk'):  # windows
            import win32com.client
            try:
                shell = win32com.client.Dispatch("WScript.Shell")
                file_path = shell.CreateShortCut(file_path).Targetpath
            except Exception as ex:
                print(ex)
        elif file_path.endswith(".desktop"):  # linux
            import xdg.DesktopEntry
            try:
                entry = xdg.DesktopEntry.DesktopEntry(file_path)
                file_path = entry.getPath()
            except Exception as ex:
                print(ex)
        for path, dirs, files in os.walk(os.path.dirname(file_path)):
            for f in files:
                fp = os.path.join(path, f)
                file_size += os.path.getsize(fp)
        file_path = os.path.abspath(file_path)
        print(file, file_path, file_size)
        return file, file_path, file_size


if __name__ == "__main__":
    app = LoginWindow()
    app.window.mainloop()


