# imports

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import re
import winsound
import sys



# conf
SOURCE_DIR = r"C:\\"
TARGET_DIR = r"C:\\"
IMAGE_SIZE = 128
THUMB_SIZE = 16



# a bunch of defs
def natural_sort_key(f):
    match = re.search(r'(\d+)', f)
    return int(match.group(1)) if match else 0

def load_image(path, size):
    img = Image.open(path).resize((size, size), Image.NEAREST)
    return ImageTk.PhotoImage(img)

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



# window
root = tk.Tk()
root.geometry("720x550")
root.title("Sprite Compare & Replace Tool")



# states
source_files = []
target_files = []
source_index = 0
target_index = 0
source_photo = None
target_photo = None
auto_delete_var = tk.BooleanVar(value=False)

source_thumbs = {}
target_thumbs = {}



# folders
folder_frame = tk.Frame(root)
folder_frame.pack(pady=5, fill="x")

def browse(entry):
    folder = filedialog.askdirectory(initialdir=entry.get())
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)
        refresh_folders()

        refresh_button = tk.Button(
            folder_frame,
            text="Refresh",
            command=lambda: refresh_folders()
        )
        refresh_button.grid(row=2, column=0, columnspan=2, pady=(8, 0))

def folder_row(row, label, default):
    tk.Label(folder_frame, text=label).grid(row=row, column=0, sticky="e")
    frame = tk.Frame(folder_frame)
    frame.grid(row=row, column=1, sticky="ew", padx=5)

    entry = tk.Entry(frame, width=98)
    entry.pack(side="left", fill="x", expand=True)
    entry.insert(0, default)

    tk.Button(frame, text="...", width=3,
              command=lambda: browse(entry)).pack(side="right", padx=5)
    return entry

source_path_entry = folder_row(0, "Source folder:", SOURCE_DIR)
target_path_entry = folder_row(1, "Target folder:", TARGET_DIR)



# img base
image_frame = tk.Frame(root)
image_frame.pack(pady=10)

source_image_label = tk.Label(image_frame, text="No source image")
source_image_label.grid(row=0, column=0, padx=20)

target_image_label = tk.Label(image_frame, text="No target image")
target_image_label.grid(row=0, column=1, padx=20)



# 2 left right buttons

nav_frame = tk.Frame(root)
nav_frame.pack(pady=(0, 8))

tk.Button(
    nav_frame,
    text="<< Source",
    command=lambda: step_source(-1)
).grid(row=0, column=0, padx=4)

tk.Button(
    nav_frame,
    text="Source >>",
    command=lambda: step_source(1)
).grid(row=0, column=1, padx=(0, 30))

tk.Button(
    nav_frame,
    text="<< Target",
    command=lambda: step_target(-1)
).grid(row=0, column=2, padx=4)

tk.Button(
    nav_frame,
    text="Target >>",
    command=lambda: step_target(1)
).grid(row=0, column=3)



# treeview
tree_frame = tk.Frame(root)
tree_frame.pack(pady=5)

def make_panel(parent, title):
    frame = tk.Frame(parent)
    tk.Label(frame, text=title).pack(anchor="w")

    search = tk.Entry(frame)
    search.pack(fill="x")

    tree = ttk.Treeview(frame, show="tree", height=6)
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frame, command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.config(yscrollcommand=sb.set)

    return frame, search, tree

src_frame, source_search, source_tree = make_panel(tree_frame, "Source sprites")
tgt_frame, target_search, target_tree = make_panel(tree_frame, "Target sprites")

src_frame.grid(row=0, column=0, padx=10)
tgt_frame.grid(row=0, column=1, padx=10)



# load img
def populate_tree(tree, files, folder, thumbs):
    tree.delete(*tree.get_children())
    thumbs.clear()
    for f in files:
        img = load_image(os.path.join(folder, f), THUMB_SIZE)
        thumbs[f] = img
        tree.insert("", "end", iid=f, text=f, image=img)

def load_files():
    global source_files, target_files

    src = source_path_entry.get()
    tgt = target_path_entry.get()

    source_files = sorted(
        [f for f in os.listdir(src) if f.lower().endswith(".png")],
        key=natural_sort_key
    ) if os.path.isdir(src) else []

    target_files = sorted(
        [f for f in os.listdir(tgt) if f.lower().endswith(".png")],
        key=natural_sort_key
    ) if os.path.isdir(tgt) else []

    populate_tree(source_tree, source_files, src, source_thumbs)
    populate_tree(target_tree, target_files, tgt, target_thumbs)



# img update
def update_images():
    global source_photo, target_photo
    if source_files and 0 <= source_index < len(source_files):
        path = os.path.join(source_path_entry.get(), source_files[source_index])
        source_photo = load_image(path, IMAGE_SIZE)
        source_image_label.config(image=source_photo, text="")
    else:
        source_image_label.config(text="No source image", image="")

    if target_files and 0 <= target_index < len(target_files):
        path = os.path.join(target_path_entry.get(), target_files[target_index])
        target_photo = load_image(path, IMAGE_SIZE)
        target_image_label.config(image=target_photo, text="")
    else:
        target_image_label.config(text="No target image", image="")



# select
def select_source(event):
    global source_index
    sel = source_tree.selection()
    if sel:
        source_index = source_files.index(sel[0])
        update_images()

def select_target(event):
    global target_index
    sel = target_tree.selection()
    if sel:
        target_index = target_files.index(sel[0])
        update_images()

source_tree.bind("<<TreeviewSelect>>", select_source)
target_tree.bind("<<TreeviewSelect>>", select_target)



# search
def filter_tree(search, tree, files):
    query = search.get().lower()
    matches = [f for f in files if query in f.lower()]
    tree.delete(*tree.get_children())
    for f in matches:
        tree.insert("", "end", iid=f, text=f,
                    image=(source_thumbs.get(f) or target_thumbs.get(f)))
    if matches:
        tree.selection_set(matches[0])
        tree.see(matches[0])

source_search.bind("<KeyRelease>",
    lambda e: filter_tree(source_search, source_tree, source_files))
target_search.bind("<KeyRelease>",
    lambda e: filter_tree(target_search, target_tree, target_files))



# buttons def

def step_source(delta):
    global source_index
    if not source_files:
        return
    source_index = (source_index + delta) % len(source_files)
    item = source_files[source_index]
    source_tree.selection_set(item)
    source_tree.see(item)
    update_images()

def step_target(delta):
    global target_index
    if not target_files:
        return
    target_index = (target_index + delta) % len(target_files)
    item = target_files[target_index]
    target_tree.selection_set(item)
    target_tree.see(item)
    update_images()


# left right
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

def replace_target():
    if not source_files or not target_files:
        return

    src = os.path.join(source_path_entry.get(), source_files[source_index])
    tgt = os.path.join(target_path_entry.get(), target_files[target_index])
    shutil.copy(src, tgt)

    if auto_delete_var.get():
        os.remove(src)
        refresh_folders()
    else:
        update_images()

tk.Checkbutton(root, text="Automatic source deletion", variable=auto_delete_var).pack()

def Replace_click():
    winsound.PlaySound("Replace.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

tk.Button(root, text="Replace", bg="red", fg="white", command=lambda: (Replace_click(), replace_target())).pack(pady=10)

refresh_button = tk.Button(folder_frame, text="Refresh", command=lambda: refresh_folders())
refresh_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))


# init
def refresh_folders():
    load_files()
    update_images()

load_files()
root.after(100, update_images)
root.mainloop()