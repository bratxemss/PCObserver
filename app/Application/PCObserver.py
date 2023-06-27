import mysql.connector.pooling
import customtkinter as ctk
import secrets
import os
import subprocess
import threading
import time
import win32com.client
import psutil
import webbrowser
from PIL import Image

pool_config = {
    'pool_name': 'my_connection_pool',
    'pool_size': 10,
    'host': 'd26893.mysql.zonevs.eu',
    'port': 3306,
    'user': 'd26893_smirnov',
    'password': 'GxnvlPQL8MA21PfZSRQF',
    'database': 'd26893_smirnov',
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

window = ctk.CTk()
window.geometry("800x600")
window.title("PCO")
window.iconbitmap("Logo.ico")

window.columnconfigure(5, weight=1)
window.rowconfigure(5, weight=1)


def create_connection():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        return connection, cursor

    except mysql.connector.Error as error:
        return "Error: {}".format(error)


def repeat_string(string):
    return string.strip('"')


def kill(process_path):
    try:
        print(f'Killing processes with path: {process_path}')
        processes = psutil.process_iter()
        for process in processes:
            try:
                process_info = process.as_dict(attrs=['pid', 'name', 'cmdline'])
                if process_info['cmdline']:
                    for arg in process_info['cmdline']:
                        if process_path in arg:
                            print(f'Found process: {process_info["name"]} | {process_info["cmdline"]}')
                            process.terminate()
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)


def switcher(key):
    connection, cursor = create_connection()
    table_name = 'PCID_{}'.format(key)
    try:
        sql = 'SELECT Application, switcher, status, path FROM {}'.format(table_name)
        cursor.execute(sql)
        data = cursor.fetchall()
        for row in data:
            if row[1] == 1:
                if row[2] == "not running":
                    if row[3].endswith(".url"):
                        webbrowser.open(row[3])
                    else:
                        subprocess.Popen(row[3], shell=True)
                    update_sql = 'UPDATE {} SET Status="running" WHERE path=%s'.format(table_name)
                    cursor.execute(update_sql, (row[3],))
                    connection.commit()
                    update_sql = 'UPDATE {} SET switcher=0 WHERE path=%s'.format(table_name)
                    cursor.execute(update_sql, (row[3],))
                    connection.commit()

                if row[2] == 'running':
                    try:
                        kill(row[3])
                        update_sql = 'UPDATE {} SET Status="not running" WHERE path=%s'.format(table_name)
                        cursor.execute(update_sql, (row[3],))
                        connection.commit()
                        update_sql = 'UPDATE {} SET memory=%s WHERE path=%s'.format(table_name)
                        cursor.execute(update_sql, (get_memory_usage(row[0]), row[3],))
                        connection.commit()
                    except Exception as e:
                        print("Error", e)

                    update_sql = 'UPDATE {} SET switcher=0 WHERE path=%s'.format(table_name)
                    cursor.execute(update_sql, (row[3],))
                    connection.commit()
        if connection.is_connected():
            # Release the connection back to the pool
            connection.close()
    except Exception as e:
        print("Error", e)


def main_thread(key):
    def thread_function():
        global stop_thread
        stop_thread = False
        while not stop_thread:
            switcher(key)
            time.sleep(2)  # Пауза в 2 секунд

    thread = threading.Thread(target=thread_function)
    thread.start()


def generate_key():
    key = secrets.token_hex(5)
    return key


def is_file_running(file_path):
    for process in psutil.process_iter():
        try:
            if process.name() == file_path:
                print(f"{file_path} is running")
                return True
        except psutil.AccessDenied:
            print(f"{file_path}AccessDenied")
            pass
    print(f"{file_path} OFF")
    return False


def get_memory_usage(process_name):
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            mem_info = proc.memory_info()
            total_memory_usage = mem_info.rss
            for child in proc.children(recursive=True):
                child_mem_info = child.memory_info()
                total_memory_usage += child_mem_info.rss
            return f'{round(total_memory_usage / 1024 ** 2, 2)} MB'
    return 0


def get_file_info(file_path):
    file_path = repeat_string(file_path)
    file_path = r"{}".format(file_path)
    file_info = {}
    shell = win32com.client.Dispatch("WScript.Shell")
    # Get file name
    file = os.path.basename(file_path)
    file_info[file] = {}
    # Get path
    if file_path.endswith('.lnk'):
        file_info[file]['path'] = shell.CreateShortCut(file_path).Targetpath
    else:
        file_info[file]['path'] = file_path

    # Calculate size
    file_size = 0
    for path, dirs, files in os.walk(os.path.dirname(file_info[file]['path'])):
        for f in files:
            fp = os.path.join(path, f)
            file_size += os.path.getsize(fp)
    file_info_size = file_size
    if 1024 <= file_size < (1024 ** 2):
        file_info[file]['size'] = f"{round(file_info_size / 1024, 2)} KB"
    elif (1024 ** 2) <= file_size < (1024 ** 3):
        file_info[file]['size'] = f"{round(file_info_size / (1024 ** 2), 2)} MB"
    elif file_size >= (1024 ** 3):
        file_info[file]['size'] = f"{round(file_info_size / (1024 ** 3), 2)} GB"

    if is_file_running(file):
        file_info[file]['memory'] = get_memory_usage(file)
        file_info[file]['status'] = 'running'
    else:
        file_info[file]['memory'] = 0
        file_info[file]['status'] = 'not running'
    return file_info


def search_process(name):  # dontuseble
    process_list = []
    name = name.split(".")[0]
    for process in psutil.process_iter(['name']):
        if name in process.info['name']:
            process_list.append(process.info['name'])
    for i in process_list:
        print(f'application{name} have process as {i}')
    return process_list


def is_valid_path(path):
    if os.path.exists(path):
        return True
    else:
        return False


def is_running(key):
    print("is_running")
    connection, cursor = create_connection()
    table_name = 'PCID_{}'.format(key)
    sql = 'SELECT path FROM {}'.format(table_name)
    cursor.execute(sql)
    data = cursor.fetchall()
    running_exe_paths = []
    not_running_exe_paths = []
    for file_path in data:
        print(file_path)
        if file_path[0].endswith('.exe'):
            if os.path.exists(file_path[0]) and os.path.isfile(file_path[0]):
                process_running = False
                for process in psutil.process_iter(['name', 'exe']):
                    if process.info['exe'] == file_path[0]:
                        running_exe_paths.append(file_path[0])
                        process_running = True
                        break
                if not process_running:
                    not_running_exe_paths.append(file_path[0])
    connection.commit()
    print("Running EXE paths:")
    print(running_exe_paths)
    print("Not running EXE paths:")
    print(not_running_exe_paths)

    for i in running_exe_paths:
        update_sql = 'UPDATE {} SET Status=%s WHERE path=%s'.format(table_name)
        cursor.execute(update_sql, ("running", i,))
        connection.commit()

    for i in not_running_exe_paths:
        update_sql = 'UPDATE {} SET Status=%s WHERE path=%s'.format(table_name)
        cursor.execute(update_sql, ("not running", i,))
        connection.commit()

    if connection.is_connected():
        # Release the connection back to the pool
        connection.close()


def start_app():
    print("start")
    main_thread(key)
    desktop_files = {}
    your_favorite_list = {}
    connection, cursor = create_connection()
    table_name = 'PCID_{}'.format(key)
    sql = 'CREATE TABLE IF NOT EXISTS {} (Application CHAR(100), Path CHAR(200), ' \
          'size CHAR(100) DEFAULT "0", memory CHAR(100) DEFAULT "0", Status CHAR(20) ' \
          'DEFAULT "offline", switcher SMALLINT DEFAULT 0,Favorite CHAR(50) DEFAULT "No")'.format(table_name)
    cursor.execute(sql)
    connection.commit()
    sql = 'SELECT Application, Path, size, memory, Status FROM {}'.format(table_name)
    cursor.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        application, path, size, memory, status = row
        desktop_files[application] = {'path': path, 'size': size, 'memory': memory, 'status': status}

    sorted_running_exe_files = sorted(desktop_files.items(), key=lambda sorted_item: sorted_item[0][0])
    # Select the rows where the Favorite column equals to 'Yes'
    sql = 'SELECT Application, Path, size, memory, Status FROM {} WHERE Favorite = "Yes"'.format(table_name)
    cursor.execute(sql)
    # Fetch all the rows
    rows = cursor.fetchall()

    # Iterate over the rows and store the data in a dictionary
    for row in rows:
        application, path, size, memory, status = row
        your_favorite_list[application] = {'path': path, 'size': size, 'memory': memory, 'status': status}

    # Pack the Listbox and Scrollbar side by side
    labelLogin.destroy()
    LoginButton.destroy()

    tabview = ctk.CTkTabview(master=Mainframe)
    tabview.add("Application")
    tabview.add("Favorite")
    info_frame = ctk.CTkFrame(master=Mainframe, fg_color="#212121")  # 212121
    path_frame = ctk.CTkFrame(tabview.tab("Application"), )  # 212121

    button_add_to_favorite = ctk.CTkButton(tabview.tab("Application"), text="Add to Favorite", width=12, height=4)
    button_delete = ctk.CTkButton(tabview.tab("Application"), text="Delete", width=12, height=4)
    button_add_to_list = ctk.CTkButton(master=path_frame, text="Add to list", width=12, height=4)
    open_folder_button = ctk.CTkButton(tabview.tab("Application"), text="Open path", width=12, height=4)

    info_label = ctk.CTkLabel(text="", width=5, height=4, master=info_frame)
    path_entry = ctk.CTkEntry(master=path_frame, placeholder_text="Path")
    filter_entry = ctk.CTkEntry(tabview.tab("Application"), placeholder_text="Filter")
    list_of_apps = ctk.CTkOptionMenu(tabview.tab("Application"), values=["Applications"])

    Mainframe.configure(fg_color='#1a1a1a')
    Mainframe.grid(row=1, column=1, columnspan=5, rowspan=5, padx=0, pady=0)
    tabview.grid(row=1, column=1, columnspan=5, rowspan=5, padx=20, pady=20, sticky="nsew")

    info_frame.configure(height=100)
    Mainframe.columnconfigure(5, weight=1)
    Mainframe.rowconfigure(5, weight=1)

    list_of_favorite_apps = ctk.CTkOptionMenu(tabview.tab("Favorite"), values=["Favorite"])

    delete_favorite_button = ctk.CTkButton(tabview.tab("Favorite"), text="Delete Favoriite", width=12, height=4)
    f_open_folder_button = ctk.CTkButton(tabview.tab("Favorite"), text="Open path", width=12, height=4)
    f_filter_entry = ctk.CTkEntry(tabview.tab("Favorite"), placeholder_text="Filter")

    item_list = []
    for item in desktop_files:
        item_list.append(item)
    list_of_apps.configure(values=item_list)

    favorite_list = []
    for item in your_favorite_list:
        favorite_list.append(item)

    list_of_favorite_apps.configure(values=favorite_list)
    list_of_favorite_apps.grid(row=0, column=5, padx=300)
    list_of_favorite_apps.configure(width=200, height=30, corner_radius=10)

    f_filter_entry.grid(row=1, column=5, pady=5, )

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
                                 hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80, height=45)
    delete_favorite_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
    button_add_to_list.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                 hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80, height=45)
    button_add_to_favorite.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                     hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80,
                                     height=45)
    button_delete.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                            hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80, height=45)
    f_open_folder_button.configure(corner_radius=7, border_width=1, border_spacing=2, fg_color="#909090",
                                   hover_color="#565656", text_color="#060D0D", font=("Robot", 15), width=80, height=45)

    is_running(key)

    def add_to_favorite(event=None):
        try:
            # Create table for storing information about EXE files
            favorite_table = 'PCID_{}'.format(key)
            exe_file = list_of_apps.get()

            data = desktop_files[exe_file]
            favorites = {"path": data['path'], "size": data['size'], "memory": data['memory'], "status": data['status']}
            if exe_file in your_favorite_list:
                your_favorite_list[exe_file].update(favorites)
            else:
                your_favorite_list[exe_file] = favorites
            favorite_sql = 'UPDATE {} SET Favorite = %s WHERE Application = %s'.format(favorite_table)
            print(exe_file)
            cursor.execute(favorite_sql, ("Yes", exe_file))
            connection.commit()
            favorite_list.append(exe_file)
            list_of_favorite_apps.configure(values=favorite_list)
        except Exception as e:
            print("Error", e)

    button_add_to_favorite.configure(command=add_to_favorite)

    def open_folder(event=None, list_app=None):
        exe_file = list_app.get()
        if exe_file in desktop_files:
            data = desktop_files[exe_file]
            file_path = data['path']
            folder_path = os.path.dirname(file_path)
            subprocess.run(['explorer', folder_path])
        else:
            pass

    open_folder_button.configure(command=lambda: open_folder(list_app=list_of_apps))
    f_open_folder_button.configure(command=lambda: open_folder(list_app=list_of_favorite_apps))

    def delete(event=None):
        try:
            value = list_of_apps.get()
            item_list.remove(value)
            list_of_apps.configure(values=["Apps"])
            info_label.configure(text="")
            delete_table_name = 'PCID_{}'.format(key)
            delete_sql = 'DELETE FROM {} WHERE Application = %s'.format(delete_table_name)
            cursor.execute(delete_sql, (value,))
            connection.commit()
            list_of_apps.configure(values=item_list)
        except Exception as e:
            print("Error", e)

    button_delete.configure(command=delete)

    def delete_from_f(event=None):
        try:
            value = list_of_favorite_apps.get()
            favorite_list.remove(value)
            list_of_favorite_apps.configure(values=["Apps"])
            favorite_table_name = 'PCID_{}'.format(key)
            favorite_sql = 'UPDATE {} SET Favorite = %s WHERE Application = %s'.format(favorite_table_name)
            cursor.execute(favorite_sql, ("No", value))
            connection.commit()
            list_of_favorite_apps.configure(values=favorite_list)
        except Exception as e:
            print("Error", e)

    delete_favorite_button.configure(command=delete_from_f)

    def show_info(event=None, list_app=None, label=None):
        try:
            value = list_app.get()
            if value:
                data = desktop_files[value]
                info_frame.grid(row=5, column=5, pady=90, sticky="s")
                label.configure(
                    text=f"Name: {value}\nPath: {data['path']}\nSize of path folder: {data['size']}\nMemory: "
                         f"{data['memory']}\nStatus: {data['status']}",
                    font=("Robot", 18))
        except KeyError:
            pass

    list_of_apps.bind("<Button-1>",
                      lambda event: window.after(1, lambda: show_info(event, list_app=list_of_apps, label=info_label)))
    list_of_favorite_apps.bind("<Button-1>", lambda event: window.after(1, lambda: show_info(event, list_app=list_of_favorite_apps, label=info_label)))

    def add(event=None):
        try:
            file_dict = get_file_info(path_entry.get())
            name = list(file_dict.keys())[0]
            info = file_dict[name]
            if is_valid_path(info['path']):
                main_path = info['path']
                main_size = info['size']
                main_memory = info['memory']
                main_status = info['status']
                main_sql = 'INSERT INTO {} (Application, Path, size, memory, Status) VALUES (%s, %s, %s, %s, %s)'.format(
                    table_name)
                cursor.execute(main_sql, (name, main_path, main_size, main_memory, main_status))
                connection.commit()
                path_entry.delete(0, 'end')
                item_list.append(name)
                list_of_apps.configure(values=item_list)
                desktop_files[name] = {'path': main_path, 'size': main_size, 'memory': main_memory,
                                       'status': main_status}
            else:
                pass
        except Exception as e:
            print("Error", e)

    path_entry.bind('<Return>', add)
    button_add_to_list.configure(command=add)

    def filter_listbox(event=None, entry=None, list_app=None):
        user_input = entry.get()
        current_values = list_app.cget("values")
        list_app.configure(values=[])

        filtered_items = []
        for list_item in current_values:
            if user_input.lower() in list_item.lower():
                filtered_items.append(list_item)
        if user_input == "":
            filtered_items = item_list
        list_app.configure(values=filtered_items)

    filter_entry.bind("<KeyRelease>", lambda event: filter_listbox(event=event, entry=filter_entry, list_app=list_of_apps))
    f_filter_entry.bind("<KeyRelease>", lambda event: filter_listbox(event=event, entry=f_filter_entry, list_app=list_of_favorite_apps))
    return sorted_running_exe_files


def update_status(is_online):
    connection, cursor = create_connection()
    status = "Online" if is_online else "Offline"
    sql = "UPDATE user_data_from_tg SET PC_Application_status = %s WHERE PCToken = %s"
    cursor.execute(sql, (status, key))
    connection.commit()
    cursor.close()
    if connection.is_connected:
        connection.close()


def check_token(event=None):
    if "Error" in create_connection():
        labelLogin.configure(
            text=f'Cant connect to database\n {create_connection()}')
        return
    connection, cursor = create_connection()
    # Get the user's input from the Entry widget
    user_input = TgLoginEntry.get()
    sql = 'SELECT UserToken, PCToken FROM user_data_from_tg WHERE UserToken = %s'
    cursor.execute(sql, (user_input,))
    result = cursor.fetchone()
    global key
    if result is not None:
        is_online = True
        # Check if PCToken is None
        if result[1] is None:
            # Generate a new key
            key = generate_key()
            # Execute an UPDATE query to update the key column in the row with the matching token
            sql = 'UPDATE user_data_from_tg SET PCToken = %s WHERE UserToken = %s'
            cursor.execute(sql, (key, user_input))
            connection.commit()
            update_status(is_online)
            # Insert new key into the PCID field of the userpcinfo table
            LoginButton.configure(command=start_app)
            TgLoginEntry.destroy()
            labelLogin.configure(
                text=f'You PC ID is {key} You can request your Token again and bot will also give you a PC id')

        else:
            # Retrieve the key from the database and store it as a global variable
            key = result[1]
            LoginButton.configure(command=start_app)
            update_status(is_online)
            TgLoginEntry.destroy()
            labelLogin.configure(
                text=f'You PC ID is {key} You can request your Token again and bot will also give you a PC id')

    else:
        labelLogin.configure(text="Incorrect Token")
    try:
        checkbox.destroy()
    except Exception as e:
        print("Error", e)
    if connection.is_connected:
        # Release the connection back to the pool
        connection.close()


def on_close():
    print("Window closed")
    is_online = False
    try:
        global stop_thread
        stop_thread = True
        update_status(is_online)
    except Exception as e:
        print("Error", e)
    connection, cursor = create_connection()
    if connection.is_connected():
        connection.close()
        print("connection closed")
    window.destroy()


img = ctk.CTkImage(Image.open("ss.png"), size=(100, 70))
label_IMG = ctk.CTkLabel(master=window, image=img, text="")
label_IMG.grid(row=0, column=1, padx=25, pady=5)
Mainframe = ctk.CTkFrame(master=window, fg_color="#212121")

labelLogin = ctk.CTkLabel(master=Mainframe, text="Login", font=("Robot", 16))
TgLoginEntry = ctk.CTkEntry(master=Mainframe, placeholder_text="Token", width=(200))
LoginButton = ctk.CTkButton(master=Mainframe, text="Enter")
checkbox = ctk.CTkCheckBox(master=Mainframe, text="Remember Me")

Mainframe.grid(row=1, column=1, columnspan=5, rowspan=5, padx=20, pady=20, sticky="nsew")

Mainframe.columnconfigure(5, weight=1)
Mainframe.rowconfigure(5, weight=1)

labelLogin.grid(row=0, column=5, padx=(20, 20), pady=10, )
TgLoginEntry.grid(row=1, column=5, padx=(20, 20), pady=10, )
LoginButton.grid(row=2, column=5, padx=(20, 20), pady=10, )
checkbox.grid(row=3, column=5, padx=(20, 20), pady=10, )

TgLoginEntry.bind('<Return>', check_token)

LoginButton.configure(command=check_token)

# Set the "on_close" function to be called when the window is closed
window.protocol("WM_DELETE_WINDOW", on_close)

window.mainloop()
