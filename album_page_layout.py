import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

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
        self.geometry("600x700")
        self.data = data
        self.entry_widgets = {}
        self.radio_buttons = {
            "paper_type": ["letter", "A4","A3","tabloid","customized","legal"],	
            "style": ["thick_fine_line", "fine_line"],
            "show": ["true", "false"],
            "position": ["top_left", "top_center", "top_right"],
            "pg_num_position": ["bottom_left", "bottom_center", "bottom_right"],
            "page_orientation": ["protrait", "landscape"],
            "font": ["Arial", "Default"],
            "horizontal_alignment": ["left", "center", "right", "uniform"],
            "vertical_alignment": ["top", "center", "bottom", "uniform"]
        }
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self,columns=("value",), show="tree headings")
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.heading("#0", text="Key")
        self.tree.heading("value", text="Value")
        self.tree.column("value", stretch=tk.YES)

        self.populate_tree("", self.data)

        self.tree.bind("<Double-1>", self.on_double_click)

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
                    self.after(100, self.add_entry_widget, node, value)
  
    def add_entry_widget(self, node, value):
        entry = ttk.Entry(self.tree, width=10)
        entry.insert(0, value)
        bbox = self.tree.bbox(node)
        if bbox:
            entry.place(x=bbox[2], y=bbox[1])
        self.entry_widgets[node] = entry

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        key = self.tree.item(item, "text")
        value = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else ""
        
        if key in self.radio_buttons:
            self.show_radio_buttons(item, key, value)
        else:
            new_value = self.prompt_for_value(key, value)
            if new_value is not None:
                self.tree.item(item, values=(new_value,))
                if item in self.entry_widgets:
                    self.entry_widgets[item].delete(0, tk.END)
                    self.entry_widgets[item].insert(0, new_value)
                self.update_data(self.data, key, new_value)
            
    def show_radio_buttons(self, item, key, value):
        options = self.radio_buttons.get(key, [])
        if not options:
            print(f"No radio button options found for key: {key}")
            return

        var = tk.StringVar(value=value)
        frame = tk.Frame(self.tree, relief=tk.RAISED, borderwidth=1)  # Add a border for visibility
        self.tree.update_idletasks()  # Force Treeview to update its layout
        bbox = self.tree.bbox(item)

        if not bbox:
            print(f"Bounding box not found for item: {item}. Using default position.")
            frame.place(x=10, y=10)  # Default position if bbox is None
        else:
            print(f"Bounding box for item {item}: {bbox}")
            # Place the frame relative to the Treeview widget using bbox coordinates
            frame.place(x=bbox[2]/4, y=bbox[1])  # Add spacing to the right of the item

        # Add radio buttons to the frame
        for option in options:
            rb = tk.Radiobutton(frame, text=option, variable=var, value=option,
                                command=lambda: self.update_radio_value(item, key, var.get(), frame))
            rb.pack(side=tk.LEFT)

        # Set focus to the frame
        frame.focus_set()

        # Close the frame when the cursor moves out
        def close_frame(event):
            frame.destroy()

        # Bind <FocusOut> to close the frame when it loses focus
        frame.bind("<FocusOut>", close_frame)

        # Bind <Enter> and <Leave> to track cursor movement
        frame.bind("<Enter>", lambda event: print("Cursor entered the frame"))
        frame.bind("<Leave>", close_frame)
        
    def update_radio_value(self, item, key, new_value, frame):
        self.tree.item(item, values=(new_value,))
        self.update_data(self.data, key, new_value)
        frame.destroy()

    def prompt_for_value(self, key, value):
        # Use the main window (self) as the parent for the dialog
        new_value = simpledialog.askstring("Input", f"Enter value for {key}:", initialvalue=value, parent=self)
        return new_value

    def update_data(self, data, key, new_value):
        for k, v in data.items():
            if k == key:
                data[k] = new_value
                return
            elif isinstance(v, dict):
                self.update_data(v, key, new_value)

    def save_data(self):
        self.data["page_options"]["paper_type"] = self.paper_type_var.get()
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