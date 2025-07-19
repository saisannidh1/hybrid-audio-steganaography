import tkinter as tk
from tkinter import filedialog, messagebox
from hybrid_steganography import hybrid_encode_n, hybrid_decode_n
import os
from datetime import datetime

KEY_FILE = "keys.txt"
OUTPUT_DIR = "encoded_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_key_to_file(encrypted_key):
    # Append only the key, no filename or metadata
    with open(KEY_FILE, "a") as f:
        f.write(encrypted_key.strip() + "\n")


def encode_page():
    def browse_file():
        filepath.set(filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")]))
    
    def encode():
        in_file = filepath.get()
        msg = message.get("1.0", tk.END).strip()
        try:
            n_val = int(n.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for parts.")
            return
        passwd = password.get()

        if not os.path.exists(in_file):
            messagebox.showerror("File Error", "Audio file not found.")
            return

        out_filename = f"{OUTPUT_DIR}/stego_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        try:
            encrypted_key = hybrid_encode_n(in_file, out_filename, msg, n_val, password=passwd)
            write_key_to_file(encrypted_key)
            messagebox.showinfo("Success", f"Encoding complete.\nOutput: {out_filename}\nKey saved to {KEY_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Encoding failed:\n{e}")

    clear_frame()
    tk.Label(root, text="Encoding", font=("Arial", 14)).pack(pady=10)

    filepath = tk.StringVar()
    tk.Button(root, text="Select Audio File", command=browse_file).pack(pady=5)
    tk.Entry(root, textvariable=filepath, width=50).pack()

    tk.Label(root, text="Secret Message:").pack()
    message = tk.Text(root, height=5, width=50)
    message.pack()

    tk.Label(root, text="Number of Parts (n):").pack()
    n = tk.Entry(root)
    n.pack()

    tk.Label(root, text="Password:").pack()
    password = tk.Entry(root, show="*")
    password.pack()

    tk.Button(root, text="Encode", command=encode).pack(pady=10)
    tk.Button(root, text="Back", command=main_menu).pack(pady=5)

def decode_page():
    def browse_file():
        filepath.set(filedialog.askopenfilename(initialdir=OUTPUT_DIR, filetypes=[("WAV files", "*.wav")]))

    def decode():
        in_file = filepath.get()
        key_val = key.get("1.0", tk.END).strip()
        passwd = password.get()

        if not os.path.exists(in_file):
            messagebox.showerror("File Error", "Stego-audio file not found.")
            return
        if not key_val:
            messagebox.showerror("Input Error", "Please enter the encrypted key.")
            return

        try:
            result = hybrid_decode_n(in_file, key_val, password=passwd)
            messagebox.showinfo("Decoded Message", f"Message:\n{result}")
        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed:\n{e}")

    clear_frame()
    tk.Label(root, text="Decoding", font=("Arial", 14)).pack(pady=10)

    filepath = tk.StringVar()
    tk.Button(root, text="Select Stego-Audio File", command=browse_file).pack(pady=5)
    tk.Entry(root, textvariable=filepath, width=50).pack()

    tk.Label(root, text="Encrypted Key:").pack()
    key = tk.Text(root, height=4, width=50)
    key.pack()

    tk.Label(root, text="Password:").pack()
    password = tk.Entry(root, show="*")
    password.pack()

    tk.Button(root, text="Decode", command=decode).pack(pady=10)
    tk.Button(root, text="Back", command=main_menu).pack(pady=5)

def main_menu():
    clear_frame()
    tk.Label(root, text="Hybrid Audio Steganography", font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="Encode", width=20, command=encode_page).pack(pady=10)
    tk.Button(root, text="Decode", width=20, command=decode_page).pack(pady=10)

def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# --- Main Tkinter setup ---
root = tk.Tk()
root.title("Audio Steganography GUI")
root.geometry("600x500")
main_menu()
root.mainloop()
