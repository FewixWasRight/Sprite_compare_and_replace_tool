import os
import shutil
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import re


# configs
SOURCE_DIR = r"C:\\"
TARGET_DIR = r"C:\\"
IMAGE_SIZE = 128



# sorting key
def natural_sort_key(f):
    match = re.search(r'(\d+)', f)
    return int(match.group(1)) if match else 0

def load_image(path):
    img = Image.open(path)
    img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.NEAREST)
    return ImageTk.PhotoImage(img)



# roots
root = tk.Tk()
root.geometry("500x360")
root.resizable(True, True)
root.title("Sprite Compare & Replace Tool")



# misc
source_files = []
target_files = []
source_index = 0
target_index = 0
source_photo = None
target_photo = None



# folders
folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)

tk.Label(folder_frame, text="Source sprites folder:").grid(row=0, column=0, sticky="e")
source_path_entry = tk.Entry(folder_frame, width=60)
source_path_entry.grid(row=0, column=1, padx=5)
source_path_entry.insert(0, SOURCE_DIR)

tk.Label(folder_frame, text="Target sprites folder:").grid(row=1, column=0, sticky="e")
target_path_entry = tk.Entry(folder_frame, width=60)
target_path_entry.grid(row=1, column=1, padx=5)
target_path_entry.insert(0, TARGET_DIR)



# images
image_frame = tk.Frame(root)
image_frame.pack(pady=10)

source_image_label = tk.Label(image_frame, text="No source image")
source_image_label.grid(row=0, column=0, padx=20)

target_image_label = tk.Label(image_frame, text="No target image")
target_image_label.grid(row=0, column=1, padx=20)



# combo
source_var = tk.StringVar()
target_var = tk.StringVar()

source_combo = ttk.Combobox(image_frame, textvariable=source_var, width=30, state="readonly")
source_combo.grid(row=1, column=0, pady=5)

target_combo = ttk.Combobox(image_frame, textvariable=target_var, width=30, state="readonly")
target_combo.grid(row=1, column=1, pady=5)



# buttins
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="<< Source", command=lambda: change_source(-1)).grid(row=0, column=0)
tk.Button(button_frame, text="Source >>", command=lambda: change_source(1)).grid(row=0, column=1)
tk.Button(button_frame, text="<< Target", command=lambda: change_target(-1)).grid(row=0, column=2)
tk.Button(button_frame, text="Target >>", command=lambda: change_target(1)).grid(row=0, column=3)

replace_button = tk.Button(
    root,
    text="Replace",
    bg="red",
    fg="white",
    command=lambda: replace_target()
)
replace_button.pack(pady=10)



# image loading
def load_files():
    global source_files, target_files, source_index, target_index

    src = source_path_entry.get()
    tgt = target_path_entry.get()

    source_files = []
    target_files = []

    if os.path.isdir(src):
        source_files = [f for f in os.listdir(src) if f.lower().endswith(".png")]
        source_files.sort(key=natural_sort_key)

    if os.path.isdir(tgt):
        target_files = [f for f in os.listdir(tgt) if f.lower().endswith(".png")]
        target_files.sort(key=natural_sort_key)

    source_index = 0
    target_index = 0

    source_combo["values"] = source_files
    target_combo["values"] = target_files

    source_var.set(source_files[0] if source_files else "")
    target_var.set(target_files[0] if target_files else "")

def safe_update_images():
    global source_photo, target_photo

    # source
    if source_files:
        path = os.path.join(source_path_entry.get(), source_files[source_index])
        source_photo = load_image(path)
        source_image_label.config(image=source_photo, text="")
    else:
        source_image_label.config(image="", text="No source image")
    # target
    if target_files:
        path = os.path.join(target_path_entry.get(), target_files[target_index])
        target_photo = load_image(path)
        target_image_label.config(image=target_photo, text="")
    else:
        target_image_label.config(image="", text="No target image")

def change_source(delta):
    global source_index
    if not source_files:
        return
    source_index = (source_index + delta) % len(source_files)
    source_var.set(source_files[source_index])
    safe_update_images()

def change_target(delta):
    global target_index
    if not target_files:
        return
    target_index = (target_index + delta) % len(target_files)
    target_var.set(target_files[target_index])
    safe_update_images()

def replace_target():
    if not source_files or not target_files:
        return
    src = os.path.join(source_path_entry.get(), source_files[source_index])
    tgt = os.path.join(target_path_entry.get(), target_files[target_index])
    shutil.copy(src, tgt)
    print(f"Replaced {target_files[target_index]} with {source_files[source_index]}")

def refresh_folders():
    load_files()
    safe_update_images()



# updates
source_combo.bind(
    "<<ComboboxSelected>>",
    lambda e: (
        set_source_index(source_var.get())
    )
)

target_combo.bind(
    "<<ComboboxSelected>>",
    lambda e: (
        set_target_index(target_var.get())
    )
)

def set_source_index(value):
    global source_index
    if value in source_files:
        source_index = source_files.index(value)
        safe_update_images()

def set_target_index(value):
    global target_index
    if value in target_files:
        target_index = target_files.index(value)
        safe_update_images()

refresh_button = tk.Button(folder_frame, text="Refresh", command=refresh_folders)
refresh_button.grid(row=2, column=1, pady=5)



# init
load_files()
root.after(100, safe_update_images)
root.mainloop()