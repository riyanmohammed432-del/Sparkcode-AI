import tkinter as tk
from tkinter import messagebox

def greet_user():
    """Handle button click to greet the user."""
    name = name_entry.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Please enter your name.")
        return
    messagebox.showinfo("Greeting", f"Hello, {name}!")

def clear_input():
    """Clear the text entry field."""
    name_entry.delete(0, tk.END)

# Create the main application window
root = tk.Tk()
root.title("Tkinter Example App")
root.geometry("300x200")  # Width x Height

# Create and place a label
label = tk.Label(root, text="Enter your name:", font=("Arial", 12))
label.pack(pady=10)

# Create and place a text entry field
name_entry = tk.Entry(root, font=("Arial", 12))
name_entry.pack(pady=5)

# Create and place buttons
greet_button = tk.Button(root, text="Greet", command=greet_user, bg="lightblue")
greet_button.pack(pady=5)

clear_button = tk.Button(root, text="Clear", command=clear_input, bg="lightgray")
clear_button.pack(pady=5)

# Start the Tkinter event loop
root.mainloop()
