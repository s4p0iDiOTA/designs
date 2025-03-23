import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.colorchooser import askcolor  


# File paths
input_file_path = 'album_page_layout.json'
output_file_path = 'album_page_layout.json'

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
            "pg_num_pos": ["bottom_center", "bottom_right"],
            "page_orientation": ["protrait", "landscape"],
            "font": ["Arial", "Default"],
            "horiz_algmnt": ["left", "center", "right", "uniform"],
            "vert_algmnt": ["top", "center", "bottom", "uniform"],
            "arrange": ["year_up","year_down","value_up","value_down","catlg_up", None]
        }
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self,columns=("value",), show="tree headings")
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.heading("#0", text="Key")
        self.tree.heading("value", text="Value...double click")
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

    def get_full_key_path(self, item):
        key_path = []
        while item:
            key_path.insert(0, self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return ".".join(key_path)

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        key_path = self.get_full_key_path(item)  # Get the full key path
        key = self.tree.item(item, "text")
        value = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else ""

        if key == "font":
            # Open the font selection window
            self.show_font_selection(item, key_path, key, value)
        elif key in self.radio_buttons:
            self.show_radio_buttons(item, key_path, key, value)
        else:
            new_value = self.prompt_for_value(key, value)
            if new_value is not None:
                self.tree.item(item, values=(new_value,))
                if item in self.entry_widgets:
                    self.entry_widgets[item].delete(0, tk.END)
                    self.entry_widgets[item].insert(0, new_value)
                self.update_data(self.data, key_path, new_value)
            
    def show_radio_buttons(self, item, key_path, key, value):  ##
        options = self.radio_buttons.get(key, [])
        if not options:
            print(f"No radio button options found for key: {key}")    ##
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
                                command=lambda: self.update_radio_value(item, key_path, var.get(), frame)) ##
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
        
    def update_radio_value(self, item, key_path, new_value, frame):   ##
        self.tree.item(item, values=(new_value,))
        self.update_data(self.data, key_path, new_value)     ##
        frame.destroy()

    def prompt_for_value(self, key, value):
        # Check if the key corresponds to a color input
        if "color" in key.lower():
            # Open the color chooser dialog
            color = askcolor(title=f"Select color for {key}", parent=self)
            if color[0]:  # If a color is selected
                # Convert the RGB values to floats between 0.0 and 1.0
                rgb_color = tuple(map(lambda x: round(x / 255, 3), color[0]))
                print(f"Selected color for {key}: {rgb_color}")
                return rgb_color
            else:
                # If no color is selected, return the original value
                return value
        else:
            # Use simpledialog for non-color inputs
            new_value = simpledialog.askstring("Input", f"Enter value for {key}:", initialvalue=value, parent=self)
            return float(new_value)

    import tkinter.font as tkFont

    def show_font_selection(self, item, key_path, key, value):
        # List of fonts supported by PyMuPDF
        supported_fonts = [
            "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
            "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
            "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
            "Symbol", "ZapfDingbats"
        ]

        # Create a new Toplevel window for font selection
        font_window = tk.Toplevel(self)
        font_window.title("Select Font")
        font_window.geometry("400x400")

        # Calculate the position to center the font window inside the main window
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()

        font_window_width = 400
        font_window_height = 400

        # Center the font window inside the main window
        x = main_x + (main_width - font_window_width) // 2
        y = main_y + (main_height - font_window_height) // 2
        font_window.geometry(f"{font_window_width}x{font_window_height}+{x}+{y}")

        # Create a frame for the Treeview
        tree_frame = tk.Frame(font_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a Treeview to display fonts and samples
        tree = ttk.Treeview(tree_frame, columns=("Font Name", "Sample"), show="headings", height=15)
        tree.heading("Font Name", text="Font Name")
        tree.heading("Sample", text="Sample")
        tree.column("Font Name", width=200, anchor=tk.W)
        tree.column("Sample", width=180, anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True)

        # Populate the Treeview with supported fonts and samples
        sample_text = "AaBbCc123"
        for font in supported_fonts:
            tree.insert("", tk.END, values=(font, sample_text), tags=(font,))

        # Apply the font to the sample text in the second column
        for font in supported_fonts:
            tree.tag_configure(font, font=(font, 12))  # Set the font for the sample text

        # Create a frame for the button
        button_frame = tk.Frame(font_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Function to handle font selection
        def select_font():
            selected_item = tree.selection()
            if selected_item:
                selected_font = tree.item(selected_item, "values")[0]
                # Update the Treeview and JSON data
                self.tree.item(item, values=(selected_font,))
                self.update_data(self.data, key_path, selected_font)
                font_window.destroy()

        # Button to confirm font selection
        select_button = tk.Button(button_frame, text="Select", command=select_font)
        select_button.pack()

        # Close the window when the user clicks outside or presses the close button
        font_window.transient(self)
        font_window.grab_set()
        font_window.focus_set()
        
    def update_data(self, data, key_path, new_value):
        keys = key_path.split(".")  # Split the key path into individual keys
        current_key = keys[0]

        if len(keys) == 1:
            # If this is the last key in the path, update its value
            if current_key in data:
                data[current_key] = new_value
            return

        # If there are more keys in the path, recurse into the nested dictionary
        if current_key in data and isinstance(data[current_key], dict):
            self.update_data(data[current_key], ".".join(keys[1:]), new_value)

    def save_data(self):
        # Save the data to the output file
        write_json(output_file_path, self.data)
        messagebox.showinfo("Info", f"Updated data saved to {output_file_path}")
        self.destroy()  # Close the application 

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