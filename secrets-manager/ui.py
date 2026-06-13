import tkinter as tk
from tkinter import ttk, messagebox

# Assuming the previous FamilySecretsManager class is imported or in the same file
from core import FamilySecretsManager, DecryptedSecretPayload

class FamilySecretsVaultUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Family Secrets Vault")
        self.root.geometry("500x550")
        self.root.minsize(450, 500)
        
        # Initialize the backend API
        # (Points to the './family_vault' directory we defined earlier)
        self.manager = FamilySecretsManager("./family_vault")
        
        # UI State Variables
        self.current_user = tk.StringVar()
        self.selected_service = tk.StringVar()
        self.hint_description_text = tk.StringVar(value="Select a service to see its hint.")
        
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        """Configures clean, modern padding and layout styles."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Arial", 11))
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="#2c3e50")
        self.style.configure("Hint.TLabel", font=("Arial", 10, "italic"), foreground="#7f8c8d")

    def _build_ui(self):
        """Constructs the window components divided into logical sections."""
        
        # --- SECTION 1: USER SELECTION ---
        user_frame = ttk.LabelFrame(self.root, text=" 1. Family Member Login ", padding=15)
        user_frame.pack(fill="x", padx=15, y=10)
        
        ttk.Label(user_frame, text="Who are you?").grid(row=0, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(user_frame, textvariable=self.current_user, font=("Arial", 11))
        self.user_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        login_btn = ttk.Button(user_frame, text="Load Menu", command=self._load_user_menu)
        login_btn.grid(row=0, column=2, padx=5, pady=5)
        user_frame.columnconfigure(1, weight=1)

        # --- SECTION 2: DYNAMIC SERVICE MENU ---
        menu_frame = ttk.LabelFrame(self.root, text=" 2. Available Vault Records ", padding=15)
        menu_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        ttk.Label(menu_frame, text="Select Service:").pack(anchor="w", pady=5)
        
        # Combobox handles the dynamic menu items returned by the API
        self.service_dropdown = ttk.Combobox(
            menu_frame, textvariable=self.selected_service, state="readonly", font=("Arial", 11)
        )
        self.service_dropdown.pack(fill="x", pady=5)
        self.service_dropdown.bind("<<ComboboxSelected>>", self._on_service_selected)
        
        # Label to display the plaintext hint description to the user
        hint_label = ttk.Label(menu_frame, textvariable=self.hint_description_text, style="Hint.TLabel", wraplength=400)
        hint_label.pack(anchor="w", pady=5)

        # --- SECTION 3: DECRYPTION GATE ---
        crypto_frame = ttk.LabelFrame(self.root, text=" 3. Security Credentials ", padding=15)
        crypto_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(crypto_frame, text="Master Key:").grid(row=0, column=0, sticky="w", pady=5)
        self.master_key_entry = ttk.Entry(crypto_frame, show="*", font=("Arial", 11))
        self.master_key_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ttk.Label(crypto_frame, text="Hint Answer:").grid(row=1, column=0, sticky="w", pady=5)
        self.hint_value_entry = ttk.Entry(crypto_frame, show="*", font=("Arial", 11))
        self.hint_value_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        crypto_frame.columnconfigure(1, weight=1)
        
        decrypt_btn = ttk.Button(crypto_frame, text="🔓 Decrypt & Reveal", command=self._decrypt_record)
        decrypt_btn.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

    # ----------------------------------------------------
    # API CONSUMPTION LOGIC
    # ----------------------------------------------------

    def _load_user_menu(self):
        """Consumes the `get_dynamic_menu` API filter."""
        user = self.current_user.get().strip()
        if not user:
            messagebox.showwarning("Input Required", "Please enter your family user name.")
            return
            
        # Call the API backend
        self.raw_menu_data = self.manager.get_dynamic_menu(user)
        
        if not self.raw_menu_data:
            messagebox.showinfo("Empty Vault", f"No records found on disk linked to user '{user}'.")
            self.service_dropdown.Rubric = []
            self.service_dropdown.config(values=[])
            self.selected_service.set("")
            self.hint_description_text.set("Select a service to see its hint.")
            return
            
        # Populate the dropdown with found service names
        service_names = [item["service_name"] for item in self.raw_menu_data]
        self.service_dropdown.config(values=service_names)
        self.service_dropdown.current(0)  # Auto-select the first one
        self._on_service_selected(None)

    def _on_service_selected(self, event):
        """Updates the hint UI label when a user toggles between their items."""
        selected = self.selected_service.get()
        # Find the matching dictionary in our raw menu array to extract the plaintext hint prompt
        for item in self.raw_menu_data:
            if item["service_name"] == selected:
                self.hint_description_text.set(f"Cryptographic Clue: {item['hint_clue']}")
                break

    def _decrypt_record(self):
        """Consumes the `decrypt_secret` API and securely presents the payload."""
        user = self.current_user.get().strip()
        service = self.selected_service.get()
        master_key = self.master_key_entry.get()
        hint_answer = self.hint_value_entry.get()
        
        if not all([user, service, master_key, hint_answer]):
            messagebox.showwarning("Missing Fields", "Please populate all security inputs before attempting decryption.")
            return

        # Execute API decryption call
        decrypted_payload = self.manager.decrypt_secret(
            user=user,
            service_name=service,
            master_key=master_key,
            hint_value=hint_answer
        )
        
        if decrypted_payload:
            # Format the flexible dictionary payload cleanly for a popup display
            display_text = "\n".join([f"🔒 {k}: {v}" for k, v in decrypted_payload.items()])
            messagebox.showinfo(f"Decrypted: {service}", f"Credentials Found:\n\n{display_text}")
            
            # Defensive Cleanup: Clear secret fields instantly upon completion
            self.master_key_entry.delete(0, tk.END)
            self.hint_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Access Denied", "Decryption failed.\nEither your Master Key or your Hint Answer is incorrect.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FamilySecretsVaultUI(root)
    root.mainloop()