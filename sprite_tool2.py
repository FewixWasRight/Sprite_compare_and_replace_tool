import os
import shutil
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import re

# folder path
SOURCE_DIR = r"C:\Users\bluep\Desktop\spritework\sprite_tool\source_sprites"
TARGET_DIR = r"C:\Users\bluep\Desktop\spritework\sprite_tool\target_sprites"

IMAGE_SIZE = 128

# nat sort
def natural_sort_key(f):
    match = re.search(r'(\d+)', f)
    return int(match.group(1)) if match else 0

# root
root = tk.Tk()  
root.title("Sprite Compare & Replace Tool")  
  
# folder path 
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

def refresh_folders():
    global SOURCE_DIR, TARGET_DIR, source_index, target_index
    SOURCE_DIR = source_path_entry.get()
    TARGET_DIR = target_path_entry.get()
    load_files()
    source_index = 0
    target_index = 0
    update_images()

refresh_button = tk.Button(folder_frame, text="Refresh", command=refresh_folders)
refresh_button.grid(row=2, column=1, pady=5)



# loading funny sprities :3
def load_files():
    global source_files, target_files
    global source_index, target_index
    global SOURCE_DIR, TARGET_DIR

    SOURCE_DIR = source_path_entry.get()
    TARGET_DIR = target_path_entry.get()

    source_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".png")]
    target_files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".png")]

    source_files.sort(key=natural_sort_key)
    target_files.sort(key=natural_sort_key)
    
    source_index = 0
    target_index = 0

load_files()



# image
def load_image(path):
    img = Image.open(path)
    img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.NEAREST)
    return ImageTk.PhotoImage(img)
image_frame = tk.Frame(root)
image_frame.pack(pady=10)

source_image_label = tk.Label(image_frame)
source_image_label.grid(row=0, column=0, padx=20)
target_image_label = tk.Label(image_frame)
target_image_label.grid(row=0, column=1, padx=20)



# vars
source_var = tk.StringVar()
source_var.set(source_files[0])
target_var = tk.StringVar()
target_var.set(target_files[0])



# updating sprites (more often than mojang updates their game)
def update_images():
    global source_photo, target_photo
    source_path = os.path.join(SOURCE_DIR, source_files[source_index])
    source_photo = load_image(source_path)
    source_image_label.config(image=source_photo)
    source_combo['values'] = source_files
    source_var.set(source_files[source_index])

    target_path = os.path.join(TARGET_DIR, target_files[target_index])
    target_photo = load_image(target_path)
    target_image_label.config(image=target_photo)
    target_combo['values'] = target_files
    target_var.set(target_files[target_index])



# changing images
def next_source():
    global source_index
    source_index = (source_index + 1) % len(source_files)
    update_images()

def prev_source():
    global source_index
    source_index = (source_index - 1) % len(source_files)
    update_images()

def next_target():
    global target_index
    target_index = (target_index + 1) % len(target_files)
    update_images()

def prev_target():
    global target_index
    target_index = (target_index - 1) % len(target_files)
    update_images()



# i'm replacing sprites and shit 'cause i'm in fucking SCRT
def replace_target():
    source_path = os.path.join(SOURCE_DIR, source_files[source_index])
    target_path = os.path.join(TARGET_DIR, target_files[target_index])
    shutil.copy(source_path, target_path)
    print(f"Replaced {target_files[target_index]} with {source_files[source_index]}")



# call me maybe callbacks
def source_selected(event=None):
    global source_index
    value = source_var.get()
    if value in source_files:
        source_index = source_files.index(value)
        update_images()

def target_selected(event=None):
    global target_index
    value = target_var.get()
    if value in target_files:
        target_index = target_files.index(value)
        update_images()



# autocomplete 
def bind_autocomplete(combo, var, file_list, update_callback):
    def on_key(event):
        typed = var.get()
        matches = [f for f in file_list if f.lower().startswith(typed.lower())]
        if matches:
            var.set(matches[0])
            update_callback()
        return "break"
    combo.bind("<Tab>", on_key)
  
source_combo = ttk.Combobox(image_frame, textvariable=source_var, values=source_files, width=30)
source_combo.grid(row=1, column=0, pady=5)
source_combo.bind("<<ComboboxSelected>>", source_selected)
bind_autocomplete(source_combo, source_var, source_files, source_selected)

target_combo = ttk.Combobox(image_frame, textvariable=target_var, values=target_files, width=30)
target_combo.grid(row=1, column=1, pady=5)
target_combo.bind("<<ComboboxSelected>>", target_selected)
bind_autocomplete(target_combo, target_var, target_files, target_selected)



# button scrolling
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="<< Source", command=prev_source).grid(row=0, column=0)
tk.Button(button_frame, text="Source >>", command=next_source).grid(row=0, column=1)
tk.Button(button_frame, text="<< Target", command=prev_target).grid(row=0, column=2)
tk.Button(button_frame, text="Target >>", command=next_target).grid(row=0, column=3)

replace_button = tk.Button(
    root,
    text="Replace",
    command=replace_target,
    bg="red",
    fg="white"
)
replace_button.pack(pady=10)



# init
update_images()
root.mainloop()