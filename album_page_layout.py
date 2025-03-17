import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

# File paths
input_file_path = 'album_page_layout.json'
output_file_path = 'album_page_layout_inputs.json'

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

class JsonEditorApp(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.title("JSON Editor")
        self.geometry("600x400")
        self.data = data
        self.paper_type_var = tk.StringVar(value=self.data.get("paper_type", "letter"))
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("value",), show="tree headings")
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.heading("#0", text="Key")
        self.tree.heading("value", text="Value")
        self.tree.column("value", stretch=tk.YES)

        self.populate_tree("", self.data)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Create a frame for the paper type radiobuttons
        paper_type_frame = tk.Frame(self)
        paper_type_frame.pack(anchor=tk.W, pady=10)

        paper_type_label = tk.Label(paper_type_frame, text="Paper Type:")
        paper_type_label.pack(side=tk.LEFT)

        paper_types = ["letter", "legal", "A4", "A3", "tabloid", "customized"]
        for paper_type in paper_types:
            rb = tk.Radiobutton(paper_type_frame, text=paper_type, variable=self.paper_type_var, value=paper_type)
            rb.pack(side=tk.LEFT)

        save_button = tk.Button(self, text="Save", command=self.save_data)
        save_button.pack(pady=10)

    def populate_tree(self, parent, data):
        for key, value in data.items():
            if isinstance(value, dict):
                node = self.tree.insert(parent, "end", text=key, open=True)
                self.populate_tree(node, value)
            else:
                node = self.tree.insert(parent, "end", text=key, values=(value,))
                if isinstance(value, (int, float)):
                    self.add_entry_widget(node, value)

    def add_entry_widget(self, node, value):
        entry = ttk.Entry(self.tree, width=10)
        entry.insert(0, value)
        self.tree.set(node, column="value", value=entry.get())
        self.tree.bind("<Double-1>", lambda event, entry=entry: self.on_entry_double_click(event, entry))

    def on_entry_double_click(self, event, entry):
        item = self.tree.selection()[0]
        key = self.tree.item(item, "text")
        value = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else ""
        new_value = self.prompt_for_value(key, value)
        if new_value is not None:
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            self.tree.set(item, column="value", value=new_value)
            self.update_data(self.data, key, new_value)

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        key = self.tree.item(item, "text")
        value = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else ""
        new_value = self.prompt_for_value(key, value)
        if new_value is not None:
            self.tree.item(item, values=(new_value,))
            self.update_data(self.data, key, new_value)

    def prompt_for_value(self, key, value):
        new_value = tk.simpledialog.askstring("Input", f"Enter value for {key}:", initialvalue=value)
        return new_value

    def update_data(self, data, key, new_value):
        for k, v in data.items():
            if k == key:
                data[k] = new_value
                return
            elif isinstance(v, dict):
                self.update_data(v, key, new_value)

    def save_data(self):
        self.data["paper_type"] = self.paper_type_var.get()
        write_json(output_file_path, self.data)
        messagebox.showinfo("Info", f"Updated data saved to {output_file_path}")

def main():
    if os.path.exists(input_file_path):
        data = read_json(input_file_path)
    else:
        print(f"Input file {input_file_path} not found.")
        return

    app = JsonEditorApp(data)
    app.mainloop()

if __name__ == "__main__":
    main()