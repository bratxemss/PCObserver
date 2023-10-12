import asyncio
import customtkinter as ctk
import threading
import logging
import os
import subprocess

from PIL import Image
from shlex import split
from Client import Client


class Window:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        logging.basicConfig(filemode="console", encoding="utf-8", level=logging.INFO)
        self.logger = logging.getLogger("Application ")
        self.window = ctk.CTk()
        self.window.geometry("800x600")
        self.window.title("PCO")
        self.window.iconbitmap("img/Logo.ico")
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.resizable(False, False)

        self.main_frame = ctk.CTkFrame(master=self.window, fg_color="#212121")
        self.main_frame.grid(row=1, column=1, columnspan=5, rowspan=5, padx=20, pady=20, sticky="nsew")
        self.main_frame.columnconfigure(5, weight=1)
        self.main_frame.rowconfigure(5, weight=1)

        self.button_restart_connection = ctk.CTkButton(master=self.window, text="Restart connection", width=12,
                                               height=4)
        self.button_restart_connection.grid(row=2, column=1, padx=30, pady=30,sticky="e")
        self.button_restart_connection.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)

        self.error_label = ctk.CTkLabel(master=self.window, text="", font=("Robot", 16))
        self.error_label.grid(row=0, column=1, padx=5, pady=15, sticky="nsew")

        self.img = Image.open("img/ss.png")
        img_for_app = ctk.CTkImage(self.img, size=(100, 70))
        label_img = ctk.CTkLabel(master=self.window, image=img_for_app, text="")
        label_img.grid(row=0, column=1, padx=15, sticky="w")


class LoginWindow(Window):
    def __init__(self):
        super().__init__()
        self.favorite_filter_entry = None
        self.f_open_folder_button = None
        self.delete_favorite_button = None
        self.list_of_favorite_apps = None
        self.button_add_to_favorite = None
        self.apps = None
        self.favorite_list = []
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

        self.label_login.grid(row=0, column=5, padx=5, pady=5, sticky="n")
        self.tg_login_entry.grid(row=1, column=5, padx=5, pady=5, sticky="n")
        self.login_button.grid(row=2, column=5, padx=5, pady=5, sticky="n")
        self.checkbox.grid(row=3, column=5, padx=5, pady=5, sticky="n")

        self.login_button.configure(command=self.login)
        self.values = None
        self.read_save_file()

    def change_window(self):
        tabview = ctk.CTkTabview(master=self.main_frame)
        tabview.add("Application")
        tabview.add("Favorite")

        self.info_frame = ctk.CTkFrame(master=self.main_frame, fg_color="#212121")  # 212121

        path_frame = ctk.CTkFrame(tabview.tab("Application"), )

        self.button_add_to_favorite = ctk.CTkButton(tabview.tab("Application"), text="Add to Favorite", width=12,
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

        self.list_of_favorite_apps = ctk.CTkOptionMenu(tabview.tab("Favorite"), values=["Favorite"])

        self.delete_favorite_button = ctk.CTkButton(tabview.tab("Favorite"), text="Delete Favoriite", width=12, height=4)
        self.f_open_folder_button = ctk.CTkButton(tabview.tab("Favorite"), text="Open path", width=12, height=4)
        self.favorite_filter_entry = ctk.CTkEntry(tabview.tab("Favorite"), placeholder_text="Filter")

        # list_of_favorite_apps.configure(values=FavoriteList)
        self.list_of_favorite_apps.grid(row=0, column=5, padx=300)
        self.list_of_favorite_apps.configure(width=200, height=30, corner_radius=10)

        self.favorite_filter_entry.grid(row=1, column=5, pady=5, )

        self.f_open_folder_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)
        self.delete_favorite_button.grid(row=1, column=0, sticky="nsew", pady=10, padx=20)

        self.list_of_apps.grid(row=0, column=5, padx=300)
        self.list_of_apps.configure(width=200, height=30, corner_radius=10)
        self.filter_entry.grid(row=1, column=5, padx=300)
        path_frame.grid(column=5)
        self.open_folder_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)

        self.info_label.grid(row=5, column=3, padx=5, pady=(0, 15), sticky="s")

        self.path_entry.grid(row=0, column=1, pady=5, padx=25)

        self.filter_entry.configure(width=200)
        self.button_add_to_list.grid(row=0, column=6, sticky="nsew", pady=10, padx=20)
        self.button_add_to_favorite.grid(row=1, column=0, sticky="nsew", pady=10, padx=20)
        self.button_delete.grid(row=2, column=0, sticky="nsew", pady=10, padx=20)

        self.open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
        self.delete_favorite_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                         hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                         height=45)
        self.button_add_to_list.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
        self.button_add_to_favorite.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                         hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                         height=45)
        self.button_delete.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                height=45)
        self.f_open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                       hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                       height=45)

    def login(self, telegram_id=None):
        if not telegram_id:
            telegram_id = self.tg_login_entry.get()
        self.client.telegram_id = telegram_id
        self.save()
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

    def render_applications(self, apps, label=None):
        label.configure(values=[apps[i]["name"] for i in range(len(apps))])

    def set_functional(self, apps, telegram_id):
        print(apps)
        self.list_of_apps.bind("<Button-1>", lambda event: self.window.after(1,
                                                                             lambda: self.show_info
                                                                             (event, list_of_app=self.list_of_apps, label=self.info_label)))

        self.filter_entry.bind("<KeyRelease>", lambda event: self.filter_listbox(event=event, entry=self.filter_entry,
                                                                                 list_app=self.list_of_apps))
        self.favorite_filter_entry.bind("<KeyRelease>", lambda event: self.filter_listbox(event=event, entry=self.favorite_filter_entry,
                                                                                 list_app=self.list_of_favorite_apps))

        self.list_of_favorite_apps.bind("<Button-1>", lambda event: self.window.after(1,
                                                                             lambda: self.show_info
                                                                             (event, list_of_app=self.list_of_favorite_apps,label=self.info_label)))

        self.f_open_folder_button.configure(command=lambda: self.open_path(list_app=self.list_of_favorite_apps))
        self.open_folder_button.configure(command=lambda: self.open_path(list_app=self.list_of_apps))

        self.path_entry.bind('<Return>', lambda event: self.add_application(apps, telegram_id, label=self.list_of_apps))
        self.button_add_to_list.configure(command=lambda: self.add_application(apps, telegram_id=telegram_id,
                                                                               label=self.list_of_apps))
        self.button_delete.configure(command=lambda: self.delete_application(telegram_id,
                                                                             list_app=self.list_of_apps))
        self.button_add_to_favorite.configure(command=lambda: self.add_to_favorite(telegram_id=telegram_id,))
        self.delete_favorite_button.configure(command=lambda: self.remove_from_favorite(telegram_id))
        self.button_restart_connection.configure(command=lambda: self.restart_connection())

    def open_path(self, event=None, list_app=None):
        current_selection_in_list = list_app.get()
        data = [self.values[current_selection_in_list]][0]
        file_path = data[0]
        try:
            folder_path = os.path.dirname(file_path)
            subprocess.run(['explorer', folder_path])
            self.logger.info(f'Opening path {folder_path}')
        except Exception as ex:
            self.logger.warning(ex)

    def show_info(self, event=None, list_of_app=None, label=None):
        try:
            self.values = {self.apps[i]["name"]: [self.apps[i]["path"], self.size_reader(int(self.apps[i]["size"]))] for i in range(len(self.apps))}
            current_selection_in_list = list_of_app.get()
            if current_selection_in_list:
                data = [self.values[current_selection_in_list]][0]
                self.info_frame.grid(row=5, column=3, padx=(60, 70), pady=(0, 15), sticky="s")
                label.configure(
                     text=f"Name: {current_selection_in_list}\nPath: {data[0]}\nSize of path folder: {data[1]}",
                     font=("Robot", 18))
        except Exception as ex:
            self.logger.warning(f'{ex}')

    def turn_application(self, app_id, command):
        for i in self.apps:
            if int(i["id"]) == int(app_id):
                app_path = i["path"]
                if command == "ON_" and not self.is_app_running(app_path):
                    if app_path.endswith(".url"):
                        from webbrowser import open
                        open(self.get_url_from_file(app_path))
                        success = True
                        message = f"{i['name']} turned on"
                    else:
                        subprocess.Popen(app_path, shell=True)
                        success = True
                        message = f"{i['name']} turned on"
                    self.logger.info(f"Turning on {i['name']} ---> {app_path}")
                elif command == "OFF_" and self.is_app_running(app_path):
                    if app_path.endswith(".url"):
                        success = False
                        message = "cant turning off the .url applications"
                        self.logger.warning(message)
                    else:
                        self.kill(app_path)
                        self.logger.info(f"Turning off {i['name']} ---> {app_path}")
                        success = True
                        message = f"{i['name']} turned off"
                else:
                    success = False
                    message = f"{i['name']}conflict request"

                self.process_answer(data={"success": success, "message": message})
                break

    def create_save_file(self, savedata):
        user_folder = os.path.expanduser('~')
        pco_folder = os.path.join(user_folder, 'PCO')
        if not os.path.exists(pco_folder):
            os.makedirs(pco_folder)
        file_path = os.path.join(pco_folder, 'PCOSave.txt')
        with open(file_path, 'w') as file:
            file.write(savedata)
        return pco_folder

    def read_save_file(self):
        user_folder = os.path.expanduser('~')
        file_path = os.path.join(user_folder, 'PCO', 'PCOSave.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
                if content:
                    self.tg_login_entry.insert(0,str(content))
                else:
                    pass
        else:
            pass

    def save(self):
        try:
            if self.checkbox.get():
                info = self.create_save_file(self.client.telegram_id)
                self.logger.info(f"New save file 'PCOSave.txt' was created in {info}")
        except:
            pass

    def get_url_from_file(self, file_path):
        from re import search
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            url_match = search(r'URL=(.+)', content)
            if url_match:
                url = url_match.group(1)
                return url
            else:
                return None

    def kill(self, process_path):
        from psutil import  process_iter
        try:
            self.logger.info(f'Killing processes with path: {process_path}')
            processes = process_iter()
            for process in processes:
                try:
                    process_info = process.as_dict(attrs=['pid', 'name', 'cmdline'])
                    if process_info['cmdline']:
                        for arg in process_info['cmdline']:
                            if process_path in arg:
                                self.logger.info(f'Found process: {process_info["name"]} | {process_info["cmdline"]}')
                                process.terminate()
                except Exception as ex:
                    self.logger.warning(ex)
        except Exception as ex:
            self.logger.warning(ex)

    def filter_listbox(self,event=None, entry=None, list_app=None,):
        user_input = entry.get()
        current_values = [self.apps[i]["name"] for i in range(len(self.apps))]
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

    def add_application(self, apps, telegram_id, label=None):
        command = "register_app"
        file_path = self.path_entry.get()
        self.path_entry.delete(0, 'end')
        if self.is_valid_path(file_path):
            file, file_path, file_size= self.get_file_info(file_path)
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
            asyncio.run(
                self.client.send_message(message))
            self.logger.info("request sent")
        self.render_applications(apps, label=label)
        self.logger.info("list updated")
        return

    def delete_application(self, telegram_id, list_app=None):
        command = "delete_app"
        message = None
        current_selection_in_list = list_app.get()
        for item in self.apps:
            try:
                if item["name"] == current_selection_in_list:
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
                    self.apps.remove(item)
                    self.render_applications(self.apps, label=list_app)
                    self.logger.info(f"{item['name']} was deleted")
            except Exception as ex:
                self.logger.warning(ex)
        if message:
            asyncio.run(
                self.client.send_message(message))

    def add_to_favorite(self, telegram_id, event=None):
        try:
            message = None
            command = "add_to_favorite"
            current_selection_in_list = self.list_of_apps.get()
            for item in self.apps:
                if item["name"] == current_selection_in_list and not item["favorite"]:
                    item["favorite"] = True
                    self.favorite_list.append(item)
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
                    self.logger.info(f"{item['name']} was added to favorite")

            if message:
                asyncio.run(
                    self.client.send_message(message))

            self.list_of_favorite_apps.configure(
                values=[item["name"] for item in self.favorite_list if item["favorite"]])
        except Exception as ex:
            self.logger.warning(ex)

    def remove_from_favorite(self,telegram_id,event=None):
        try:
            message = None
            command = "remove_from_favorite"
            values = [self.apps[i] for i in range(len(self.apps)) if self.apps[i]["favorite"]]
            current_selection_in_list = self.list_of_favorite_apps.get()
            for item in values:
                if item["name"] == current_selection_in_list and item["favorite"]:
                    item["favorite"] = False
                    self.favorite_list.remove(item)
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
                    self.logger.info(f"{item['name']} was removed from favorite")
            if message:
                asyncio.run(
                    self.client.send_message(message))
            self.list_of_favorite_apps.configure(
                values=[item["name"] for item in self.favorite_list if item["favorite"]])
        except Exception as ex:
            self.logger.warning(ex)

    def is_valid_path(self, file_path):
        split_path = split(file_path)
        joined_path = os.path.join(*split_path)
        if os.path.exists(joined_path):
            return True
        else:
            return False

    def is_app_running(self,file_path):
        from psutil import process_iter, AccessDenied
        for proc in process_iter():
            try:
                if proc.exe() == file_path:
                    return True
            except AccessDenied:
                pass

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
                self.logger.warning(ex)
        elif file_path.endswith(".desktop"):  # linux
            import xdg.DesktopEntry
            try:
                entry = xdg.DesktopEntry.DesktopEntry(file_path)
                file_path = entry.getPath()
            except Exception as ex:
                self.logger.warning(ex)
        for path, dirs, files in os.walk(os.path.dirname(file_path)):
            for f in files:
                fp = os.path.join(path, f)
                file_size += os.path.getsize(fp)
        file_path = os.path.abspath(file_path)

        print(file, file_path, file_size)
        return file, file_path, file_size

    def restart_connection(self):
        return self.login(self.client.telegram_id)

    def set_volume(self, command):
        from platform import system
        if system() == 'Windows':
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_volume = volume.GetMasterVolumeLevelScalar()
            if command == "Volume_up":
                new_volume = min(current_volume + 0.1, 1.0)
                volume.SetMasterVolumeLevelScalar(new_volume, None)
                self.logger.info("Volume increased by 0.1")
            elif command == "Volume_down":
                new_volume = max(current_volume - 0.1, 0.0)
                volume.SetMasterVolumeLevelScalar(new_volume, None)
                self.logger.info("Volume decreased by 0.1")
        elif system() == 'Linux':
            from pulsectl import Pulse
            if command == "Volume_up":
                with Pulse('increase_volume') as pulse:
                    default_sink = pulse.sink_list()[0]
                    current_volume = default_sink.volume.value_flat
                    new_volume = min(current_volume + 0.1, 1.0)
                    pulse.volume_set_all_chans(default_sink, new_volume)
                    self.logger.info("Volume increased by 0.1")
            elif command == "Volume_down":
                with Pulse('increase_volume') as pulse:
                    default_sink = pulse.sink_list()[0]
                    current_volume = default_sink.volume.value_flat
                    new_volume = max(current_volume - 0.1, 0.0)
                    pulse.volume_set_all_chans(default_sink, new_volume)
                    self.logger.info("Volume decreased by 0.1")



if __name__ == "__main__":
    app = LoginWindow()
    app.window.mainloop()
