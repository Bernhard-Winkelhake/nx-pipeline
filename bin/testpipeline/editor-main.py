import json
import tkinter as tk
from tkinter import ttk, messagebox
import os

# JSON-Dateiname im gleichen Ordner
JSON_FILENAME = "config.json"

class JSONEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON UI Editor")
        self.data = None
        self.entries = {}

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.save_btn = ttk.Button(self.root, text="JSON speichern", command=self.save_json)
        self.save_btn.pack(pady=10)

        self.load_json_from_file(JSON_FILENAME)

    def load_json_from_file(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {file_path}")
            return

        try:
            with open(file_path, "r") as f:
                self.data = json.load(f)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden: {e}")
            return

        self.entries.clear()
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        for section, content in self.data.items():
            if section == "attributes":
                continue  # Nicht anzeigen
            is_bool = section == "checks"
            self.add_section(section, content, is_bool)

    def add_section(self, section_name, section_data, is_bool=False):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=section_name)

        for i, (key, value) in enumerate(section_data.items()):
            ttk.Label(frame, text=key).grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if is_bool and isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                cb = ttk.Checkbutton(frame, variable=var)
                cb.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                self.entries[f"{section_name}.{key}"] = var
            else:
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(frame, textvariable=var)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="we")
                self.entries[f"{section_name}.{key}"] = var

    def save_json(self):
        updated_json = {}

        for key, var in self.entries.items():
            section, name = key.split(".")
            if section not in updated_json:
                updated_json[section] = {}

            value = var.get()

            if section == "checks":
                value = var.get()
            elif section == "layers":
                try:
                    value = int(value)
                except ValueError:
                    messagebox.showerror("Fehler", f"'{name}' muss eine Zahl sein.")
                    return

            updated_json[section][name] = value

        # attributes beibehalten wie geladen
        updated_json["attributes"] = self.data.get("attributes", {})

        try:
            with open(JSON_FILENAME, "w") as f:
                json.dump(updated_json, f, indent=2)
            messagebox.showinfo("Erfolg", f"JSON gespeichert in '{JSON_FILENAME}'")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONEditorApp(root)
    root.mainloop()
