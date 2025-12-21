import os
import shutil
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import re
from tkinter import filedialog


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
root.geometry("500x400")
root.resizable(True, True)
root.title("Sprite Compare & Replace Tool")



# misc
source_files = []
target_files = []
source_index = 0
target_index = 0
source_photo = None
target_photo = None
auto_delete_var = tk.BooleanVar(value=False)



# folders
folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)



# explorer shenanigans
tk.Label(folder_frame, text="Source sprites folder:").grid(row=0, column=0, sticky="e")

source_path_frame = tk.Frame(folder_frame)
source_path_frame.grid(row=0, column=1, padx=5, sticky="ew")

source_path_entry = tk.Entry(source_path_frame, width=50)
source_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

source_browse_button = tk.Button(source_path_frame, text="...", width=3)
source_browse_button.pack(side=tk.RIGHT, padx=(5, 0))

source_path_entry.insert(0, SOURCE_DIR)


tk.Label(folder_frame, text="Target sprites folder:").grid(row=1, column=0, sticky="e")

target_path_frame = tk.Frame(folder_frame)
target_path_frame.grid(row=1, column=1, padx=5, sticky="ew")

target_path_entry = tk.Entry(target_path_frame, width=50)
target_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

target_browse_button = tk.Button(target_path_frame, text="...", width=3)
target_browse_button.pack(side=tk.RIGHT, padx=(5, 0))

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

source_combo = ttk.Combobox(image_frame, textvariable=source_var, width=30)
source_combo.grid(row=1, column=0, pady=5)
source_combo.config(state="normal")

target_combo = ttk.Combobox(image_frame, textvariable=target_var, width=30)
target_combo.grid(row=1, column=1, pady=5)
target_combo.config(state="normal")



# buttons and checkbox
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="<< Source", command=lambda: change_source(-1)).grid(row=0, column=0)
tk.Button(button_frame, text="Source >>", command=lambda: change_source(1)).grid(row=0, column=1, padx=(0, 70))
tk.Button(button_frame, text="<< Target", command=lambda: change_target(-1)).grid(row=0, column=2)
tk.Button(button_frame, text="Target >>", command=lambda: change_target(1)).grid(row=0, column=3)



# auto deletion checkbox
checkbox_frame = tk.Frame(root)
checkbox_frame.pack(pady=5)
auto_delete_checkbox = tk.Checkbutton(
    checkbox_frame, 
    text="Automatic source deletion", 
    variable=auto_delete_var,
    command=lambda: update_replace_button_color()
)
auto_delete_checkbox.pack()

replace_button = tk.Button(
    root,
    text="Replace",
    bg="red",
    fg="white",
    command=lambda: replace_target()
)
replace_button.pack(pady=10)



# image loading
def load_files(preserve_indices=True):
    global source_files, target_files, source_index, target_index

    src = source_path_entry.get()
    tgt = target_path_entry.get()

    old_source = source_files[source_index] if source_files and source_index < len(source_files) else None
    old_target = target_files[target_index] if target_files and target_index < len(target_files) else None

    source_files = []
    target_files = []

    if os.path.isdir(src):
        source_files = [f for f in os.listdir(src) if f.lower().endswith(".png")]
        source_files.sort(key=natural_sort_key)

    if os.path.isdir(tgt):
        target_files = [f for f in os.listdir(tgt) if f.lower().endswith(".png")]
        target_files.sort(key=natural_sort_key)

    # restore source index
    if preserve_indices and old_source in source_files:
        source_index = source_files.index(old_source)
    else:
        source_index = min(source_index, max(len(source_files) - 1, 0))

    # restore target index
    if preserve_indices and old_target in target_files:
        target_index = target_files.index(old_target)
    else:
        target_index = min(target_index, max(len(target_files) - 1, 0))

    source_combo["values"] = source_files
    target_combo["values"] = target_files

    if source_files:
        source_var.set(source_files[source_index])
    else:
        source_var.set("")

    if target_files:
        target_var.set(target_files[target_index])
    else:
        target_var.set("")

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

    if auto_delete_var.get():
        try:
            os.remove(src)
            print(f"Deleted source file: {source_files[source_index]}")
            refresh_folders()  # keeps indices
        except Exception as e:
            print(f"Error deleting source file: {e}")
            refresh_folders()
    else:
        safe_update_images()

def update_replace_button_color():
    if auto_delete_var.get():
        replace_button.config(bg="darkred", fg="white")
    else:
        replace_button.config(bg="red", fg="white")

def refresh_folders():
    load_files(preserve_indices=True)
    safe_update_images()



# autocomplete on TAB
def autocomplete(combo, var, files):
    current = var.get().strip()
    if not current:
        return "break"

    matches = [f for f in files if f.lower().startswith(current.lower())]
    if matches:
        var.set(matches[0])
        combo.icursor(tk.END)
    combo.focus_set()
    return "break"

def on_source_enter(event):
    current = source_var.get().strip()
    if current in source_files:
        set_source_index(current)
        safe_update_images()
    else:
        # nearest match source
        matches = [f for f in source_files if current.lower() in f.lower()]
        if matches:
            source_var.set(matches[0])
            set_source_index(matches[0])
            safe_update_images()

def on_target_enter(event):
    current = target_var.get().strip()
    if current in target_files:
        set_target_index(current)
        safe_update_images()
    else:
        # nearest match target
        matches = [f for f in target_files if current.lower() in f.lower()]
        if matches:
            target_var.set(matches[0])
            set_target_index(matches[0])
            safe_update_images()



# explorer browser
def browse_source_folder():
    folder_selected = filedialog.askdirectory(
        initialdir=source_path_entry.get(),
        title="Select Source Sprites Folder"
    )
    if folder_selected:
        source_path_entry.delete(0, tk.END)
        source_path_entry.insert(0, folder_selected)
        refresh_folders()

def browse_target_folder():
    folder_selected = filedialog.askdirectory(
        initialdir=target_path_entry.get(),
        title="Select Target Sprites Folder"
    )
    if folder_selected:
        target_path_entry.delete(0, tk.END)
        target_path_entry.insert(0, folder_selected)
        refresh_folders()



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

# bind TAB
source_combo.bind("<Tab>", lambda e: autocomplete(source_combo, source_var, source_files))
target_combo.bind("<Tab>", lambda e: autocomplete(target_combo, target_var, target_files))

# bind ENTER
source_combo.bind("<Return>", on_source_enter)
target_combo.bind("<Return>", on_target_enter)



# browser button
source_browse_button.config(command=browse_source_folder)
target_browse_button.config(command=browse_target_folder)

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
refresh_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))



# init
load_files()
update_replace_button_color()
root.after(100, safe_update_images)
root.mainloop()