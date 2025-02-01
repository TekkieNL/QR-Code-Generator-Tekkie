import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import qrcode
from PIL import Image, ImageTk
import os
import sys
import csv

# Metadata
__title__ = "QR Code Generator"
__description__ = "QR Code Generator by Tekkie"
__version__ = "1.0.0"
__author__ = "Tekkie"
__copyright__ = "Copyright 2024, Tekkie"

# Functie om QR-code te genereren
def generate_qr(data, filename="qr_code.png", fill_color="black", back_color="white", logo_path=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill=fill_color, back_color=back_color).convert("RGB")
    
    if logo_path:
        try:
            logo = Image.open(logo_path)
            if logo.mode in ("RGBA", "P"):
                background = Image.new("RGB", logo.size, (255, 255, 255))
                background.paste(logo, mask=logo.split()[3])
                logo = background
            
            logo = logo.resize((50, 50))
            qr_img.paste(logo, ((qr_img.width - logo.size[0]) // 2, (qr_img.height - logo.size[1]) // 2))
        except Exception as e:
            messagebox.showwarning("Waarschuwing", f"Logo kon niet worden toegevoegd: {e}")
    
    qr_img.save(filename)
    return qr_img

# Functie om QR-code in GUI te tonen
def show_qr(img):
    img = img.resize((200, 200), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    qr_label.config(image=img_tk)
    qr_label.image = img_tk

# Hoofdfunctie om QR-code te genereren en op te slaan
def generate_and_save():
    data = entry.get()
    filename = filename_entry.get() or "qr_code.png"
    fill_color = color_fg.get()
    back_color = color_bg.get()
    logo_path = logo_entry.get()
    
    if not data:
        messagebox.showwarning("Waarschuwing", "Voer tekst of een link in!")
        return

    if not filename.endswith(".png"):
        filename += ".png"

    filepath = filedialog.asksaveasfilename(defaultextension=".png", initialfile=filename,
                                            filetypes=[("PNG bestanden", "*.png"), ("PDF bestanden", "*.pdf")])
    if not filepath:
        messagebox.showinfo("Annuleren", "Opslaan geannuleerd.")
        return
    
    try:
        img = generate_qr(data, filepath, fill_color, back_color, logo_path)
        show_qr(img)
        add_to_history(data, filepath)
        messagebox.showinfo("QR-code opgeslagen", f"QR-code opgeslagen als {filepath}")
    except Exception as e:
        messagebox.showerror("Fout bij opslaan", f"Kon QR-code niet opslaan: {e}")

# Geschiedenis bijhouden van QR-codes
def add_to_history(data, filepath):
    with open("qr_history.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data, filepath])

# Batch QR-codes genereren
def generate_batch():
    file_path = filedialog.askopenfilename(filetypes=[("CSV bestanden", "*.csv")])
    if not file_path:
        return
    
    save_dir = filedialog.askdirectory()
    if not save_dir:
        return

    with open(file_path, newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            data = row[0]
            filename = os.path.join(save_dir, f"{data}.png")
            generate_qr(data, filename)

    messagebox.showinfo("Batch voltooid", f"Batch QR-codes opgeslagen in {save_dir}")

# Functie om kleuren te kiezen
def choose_color_fg():
    color = colorchooser.askcolor()[1]
    if color:
        color_fg.set(color)

def choose_color_bg():
    color = colorchooser.askcolor()[1]
    if color:
        color_bg.set(color)

# GUI opzetten
root = tk.Tk()
root.resizable(False, False)
root.title("QR Code Generator")

# Logo-pad detecteren, compatibel met PyInstaller
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

logo_path = os.path.join(base_path, "Tekkie.png")

# Logo van Tekkie bovenaan vastzetten
try:
    logo_img = Image.open(logo_path)
    logo_img = logo_img.resize((100, 100), Image.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_tk)
    logo_label.grid(row=0, column=0, columnspan=2, pady=(10, 0), sticky="n")
except Exception as e:
    messagebox.showwarning("Waarschuwing", f"Logo kon niet worden geladen: {e}")

# Invoervelden en labels
tk.Label(root, text="Voer tekst of link in:").grid(row=1, column=0, columnspan=2, pady=5)
entry = tk.Entry(root, width=40)
entry.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

tk.Label(root, text="Bestandsnaam (bijv. qr_code.png):").grid(row=3, column=0, columnspan=2, pady=5)
filename_entry = tk.Entry(root, width=40)
filename_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

tk.Label(root, text="Kleur voorgrond:").grid(row=5, column=0, pady=5)
color_fg = tk.StringVar(value="black")
color_button_fg = tk.Button(root, text="Kies kleur", command=choose_color_fg)
color_button_fg.grid(row=5, column=1, pady=5)

tk.Label(root, text="Kleur achtergrond:").grid(row=6, column=0, pady=5)
color_bg = tk.StringVar(value="white")
color_button_bg = tk.Button(root, text="Kies kleur", command=choose_color_bg)
color_button_bg.grid(row=6, column=1, pady=5)

tk.Label(root, text="Logo toevoegen (optioneel):").grid(row=7, column=0, columnspan=2, pady=5)
logo_entry = tk.Entry(root, width=40)
logo_entry.grid(row=8, column=0, columnspan=2, padx=10, pady=5)
logo_button = tk.Button(root, text="Kies logo", command=lambda: logo_entry.insert(0, filedialog.askopenfilename()))
logo_button.grid(row=9, column=0, columnspan=2, pady=5)

# QR Code weergave label
qr_label = tk.Label(root)
qr_label.grid(row=10, column=0, columnspan=2, pady=10)

# Functieknoppen
generate_button = tk.Button(root, text="Genereer QR-code", command=generate_and_save)
generate_button.grid(row=11, column=0, pady=10)

batch_button = tk.Button(root, text="Batch QR-codes genereren", command=generate_batch)
batch_button.grid(row=11, column=1, pady=10)

# Label voor "Made by Tekkie"
footer_label = tk.Label(root, text="Made by Tekkie", font=("Arial", 8, "italic"), fg="gray")
footer_label.grid(row=12, column=0, columnspan=2, pady=5)

root.mainloop()
