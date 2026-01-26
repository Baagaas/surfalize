import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from surfalize import Surface
from tkinter import filedialog
import matplotlib.pyplot as plt

ax = None

def on_file_selected(file_path: str):
    # Replace this with your desired action
    print(f"You selected: {file_path}")

    global ax  # Use the ax defined in list_files_with_events

    surf = Surface.load(file_path).level()
    if ax is None or not plt.fignum_exists(ax.figure.number):
        fig, ax = surf.plot_2d()
        plt.show(block=False)
    else:
        ax.clear()
        #Remove old colorbars if present
        for extra_ax in ax.figure.axes[1:]:
            extra_ax.remove()
        surf.plot_2d(ax=ax)
        ax.figure.canvas.draw()
        ax.figure.canvas.flush_events()

def list_files_with_events(folder_path):

    def update_file_list(*_):
        folder_path = folder_var.get()
        pattern = filter_var.get()
        if not pattern:
            pattern = "*"
        matched_file_paths = list(Path(folder_path).glob(pattern))
        listbox.delete(0, tk.END)
        for file_path in matched_file_paths:
            listbox.insert(tk.END, file_path.name)
        # Store current list for selection callbacks
        listbox.file_paths = matched_file_paths
        print(f"Listed files with pattern: {listbox.file_paths}")

    # Set up the main window
    global ax
    ax = None
    root = tk.Tk()
    root.title("File List")

    # Folder selection frame
    folder_frame = tk.Frame(root)
    folder_frame.pack(padx=10, pady=(10, 0), fill='x')

    folder_var = tk.StringVar(value=str(folder_path))
    folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=60)
    folder_entry.pack(side='left', fill='x', expand=True)

    def on_folder_select():
        selected_folder = filedialog.askdirectory(initialdir=folder_var.get(), title="Select Folder")
        if selected_folder:
            folder_var.set(selected_folder)
            update_file_list()
        else:
            messagebox.showinfo("Folder Selection", "No folder selected.")

    select_button = tk.Button(folder_frame, text="Select Folder", command=on_folder_select)
    select_button.pack(side='left', padx=(5, 0))

    # Update folder_path when folder_var changes
    def on_folder_var_change(*_):
        nonlocal folder_path
        folder_path = folder_var.get()
        update_file_list()

    folder_var.trace_add('write', on_folder_var_change)

    filter_frame = tk.Frame(root)
    filter_frame.pack(padx=10, pady=(10, 0), fill='x')

    tk.Label(filter_frame, text="Filter (glob pattern):").pack(side='left')
    filter_var = tk.StringVar(value="*.sur")
    filter_entry = tk.Entry(filter_frame, textvariable=filter_var, width=30)
    filter_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)

    # Add a vertical scrollbar to the listbox if the list is too long
    listbox_frame = tk.Frame(root)
    listbox_frame.pack(padx=10, pady=10, fill='both', expand=True)

    scrollbar = tk.Scrollbar(listbox_frame, orient='vertical')
    listbox = tk.Listbox(listbox_frame, width=60, height=20, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    listbox.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    listbox.file_paths = []

    # Add a refresh button
    refresh_button = tk.Button(root, text="Refresh", command=update_file_list)
    refresh_button.pack(padx=10, pady=(0, 10), fill='x')

    # Event handlers
    def on_enter_orclick(_):
        selection = listbox.curselection()
        if selection:
            filename = listbox.file_paths[selection[0]]
            on_file_selected(filename)

    filter_var.trace_add('write', update_file_list)
    filter_entry.bind('<Return>', update_file_list)
    listbox.bind('<Double-Button-1>', on_enter_orclick)
    listbox.bind('<Return>', on_enter_orclick)

    update_file_list()
    root.mainloop()

data_path = Path.cwd() / 'data'
# data_path = r'Y:\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\cropped'
list_files_with_events(data_path)