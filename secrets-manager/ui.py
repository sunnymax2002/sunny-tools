import tkinter as tk
from tkinter import ttk, messagebox
import json

# Assuming FamilySecretsManager, SecretModel, DecryptedSecretPayload are in the same scope
from core import FamilySecretsManager, DecryptedSecretPayload

class DarkModeFamilyVaultUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Family Secrets Vault Manager (Encrypted)")
        # self.root.geometry("950://580")
        self.root.geometry("950x600")
        self.root.minsize(900, 550)
        
        # Configure root window background for Dark Mode
        self.root.configure(bg="#121212")
        
        # Initialize backend connection
        self.manager = FamilySecretsManager("./family_vault")
        
        # --- STATE VARIABLES ---
        self.current_user = tk.StringVar()
        self.selected_service = tk.StringVar()
        self.hint_description_text = tk.StringVar(value="Select a service to see its hint.")
        self.raw_menu_data = []

        self._setup_dark_styles()
        self._build_main_layout()

    def _setup_dark_styles(self):
        """Injects a comprehensive dark mode theme map into the UI components."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Define Dark Mode Palette
        bg_darker = "#121212"    # Root window background
        bg_card = "#1e1e1e"      # Frames and panels
        bg_input = "#2d2d2d"     # Entries, dropdowns, text areas
        fg_primary = "#e0e0e0"   # Main text color
        fg_muted = "#aaaaaa"     # Hints and secondary text
        accent_blue = "#3700b3"  # Primary buttons
        accent_red = "#b00020"   # Danger button
        
        # Global Style Configurations
        self.style.configure(".", background=bg_card, foreground=fg_primary)
        
        # Main Window / TFrame mapping
        self.style.configure("TFrame", background=bg_darker)
        self.style.configure("Panel.TFrame", background=bg_card)
        
        # Labels
        self.style.configure("TLabel", background=bg_card, foreground=fg_primary, font=("Arial", 10))
        self.style.configure("Header.TLabel", background=bg_darker, foreground="#ffffff", font=("Arial", 12, "bold"))
        self.style.configure("Hint.TLabel", background=bg_card, foreground=fg_muted, font=("Arial", 9, "italic"))
        
        # LabelFrames (Panels)
        self.style.configure("TLabelframe", background=bg_card, foreground=fg_primary, bordercolor="#333333", borderwidth=1)
        self.style.configure("TLabelframe.Label", background=bg_card, foreground="#ffffff", font=("Arial", 10, "bold"))
        
        # Input Entries
        self.style.configure("TEntry", fieldbackground=bg_input, foreground=fg_primary, bordercolor="#444444", insertcolor="white")
        self.style.map("TEntry", fieldbackground=[("focus", "#3d3d3d")], bordercolor=[("focus", "#6200ee")])
        
        # Combobox (Dropdown) Dropdown styling map
        self.style.configure("TCombobox", fieldbackground=bg_input, background=bg_input, foreground=fg_primary, bordercolor="#444444")
        self.style.map("TCombobox", fieldbackground=[("readonly", bg_input)], foreground=[("readonly", fg_primary)])
        self.root.option_add("*TCombobox*Listbox.background", bg_input)
        self.root.option_add("*TCombobox*Listbox.foreground", fg_primary)
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#6200ee")
        
        # Buttons
        self.style.configure("TButton", background=bg_input, foreground=fg_primary, bordercolor="#444444", font=("Arial", 10, "bold"), padding=6)
        self.style.map("TButton", background=[("active", "#3d3d3d"), ("pressed", "#555555")])
        
        self.style.configure("Primary.TButton", background="#6200ee", foreground="white", font=("Arial", 10, "bold"))
        self.style.map("Primary.TButton", background=[("active", "#7711ff"), ("pressed", "#3700b3")])
        
        self.style.configure("Danger.TButton", background=accent_red, foreground="white", font=("Arial", 10, "bold"))
        self.style.map("Danger.TButton", background=[("active", "#cf6679"), ("pressed", "#7f0010")])
        
        # Separators
        self.style.configure("TSeparator", background="#333333")

    def _build_main_layout(self):
        # Top Global User Login Banner
        top_frame = ttk.Frame(self.root, padding=15, style="TFrame")
        top_frame.pack(fill="x")
        
        ttk.Label(top_frame, text="Active Family Profile:", style="Header.TLabel").pack(side="left", padx=5)
        self.user_entry = ttk.Entry(top_frame, textvariable=self.current_user, font=("Arial", 11), width=18)
        self.user_entry.pack(side="left", padx=5)
        
        load_btn = ttk.Button(top_frame, text="Load Vault", command=self._load_user_menu)
        load_btn.pack(side="left", padx=5)

        # Separator line
        ttk.Separator(self.root, orient="horizontal").pack(fill="x")

        # Container Frame splitting Left and Right panels
        body_frame = ttk.Frame(self.root, padding=15, style="TFrame")
        body_frame.pack(fill="both", expand=True)
        
        self._build_left_read_panel(body_frame)
        self._build_right_manage_panel(body_frame)

    def _build_left_read_panel(self, parent):
        left_panel = ttk.LabelFrame(parent, text=" Secure Decryption Terminal ", padding=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=8)

        ttk.Label(left_panel, text="Select Target Service:").pack(anchor="w", pady=2)
        self.service_dropdown = ttk.Combobox(
            left_panel, textvariable=self.selected_service, state="readonly", font=("Arial", 11)
        )
        self.service_dropdown.pack(fill="x", pady=5)
        self.service_dropdown.bind("<<ComboboxSelected>>", self._on_service_selected)
        
        self.hint_label = ttk.Label(left_panel, textvariable=self.hint_description_text, style="Hint.TLabel", wraplength=350)
        self.hint_label.pack(anchor="w", pady=5)

        ttk.Separator(left_panel, orient="horizontal").pack(fill="x", pady=15)

        ttk.Label(left_panel, text="Enter Master Key:").pack(anchor="w")
        self.read_master_key = ttk.Entry(left_panel, show="*", font=("Arial", 11))
        self.read_master_key.pack(fill="x", pady=5)

        ttk.Label(left_panel, text="Enter Hint Verification Value:").pack(anchor="w")
        self.read_hint_value = ttk.Entry(left_panel, show="*", font=("Arial", 11))
        self.read_hint_value.pack(fill="x", pady=5)

        decrypt_btn = ttk.Button(left_panel, text="🔓 Decrypt & Read", style="Primary.TButton", command=self._decrypt_record)
        decrypt_btn.pack(fill="x", pady=20)

    def _build_right_manage_panel(self, parent):
        right_panel = ttk.LabelFrame(parent, text=" Vault Content Management ", padding=15)
        right_panel.pack(side="right", fill="both", expand=True, padx=8)

        ttk.Label(right_panel, text="Service Name:").pack(anchor="w")
        self.form_service = ttk.Entry(right_panel, font=("Arial", 11))
        self.form_service.pack(fill="x", pady=3)

        ttk.Label(right_panel, text="App URL or Identifier:").pack(anchor="w")
        self.form_url = ttk.Entry(right_panel, font=("Arial", 11))
        self.form_url.pack(fill="x", pady=3)

        ttk.Label(right_panel, text="Credentials JSON Data Payload:").pack(anchor="w")
        
        # Native Tkinter text widget requires custom color assignment bypassing ttk styles
        self.form_payload = tk.Text(
            right_panel, height=4, font=("Courier", 10),
            bg="#2d2d2d", fg="#e0e0e0", insertbackground="white", 
            relief="flat", highlightthickness=1, highlightbackground="#444444", highlightcolor="#6200ee"
        )
        self.form_payload.pack(fill="x", pady=3)
        self.form_payload.insert("1.0", '{\n  "username": "user@mail.com",\n  "password": "Password123!"\n}')

        ttk.Label(right_panel, text="Hint Clue Description (Plaintext):").pack(anchor="w")
        self.form_hint_desc = ttk.Entry(right_panel, font=("Arial", 11))
        self.form_hint_desc.pack(fill="x", pady=3)

        ttk.Label(right_panel, text="Secret Hint Answer (Used to encrypt data):").pack(anchor="w")
        self.form_hint_val = ttk.Entry(right_panel, show="*", font=("Arial", 11))
        self.form_hint_val.pack(fill="x", pady=3)

        ttk.Label(right_panel, text="Master Encryption Key:").pack(anchor="w")
        self.form_master_key = ttk.Entry(right_panel, show="*", font=("Arial", 11))
        self.form_master_key.pack(fill="x", pady=3)

        btn_frame = ttk.Frame(right_panel, style="Panel.TFrame")
        btn_frame.pack(fill="x", pady=15)

        save_btn = ttk.Button(btn_frame, text="💾 Save / Update", command=self._save_or_update_record)
        save_btn.pack(side="left", fill="x", expand=True, padx=2)

        delete_btn = ttk.Button(btn_frame, text="🗑️ Delete Secret", style="Danger.TButton", command=self._delete_record)
        delete_btn.pack(side="right", fill="x", expand=True, padx=2)

    # ----------------------------------------------------
    # API INTEGRATION GATEWAYS
    # ----------------------------------------------------

    def _load_user_menu(self):
        user = self.current_user.get().strip()
        if not user:
            messagebox.showwarning("Input Required", "Please fill in an Active Family Member profile name.")
            return
            
        self.raw_menu_data = self.manager.get_dynamic_menu(user)
        
        if not self.raw_menu_data:
            self.service_dropdown.config(values=[])
            self.selected_service.set("")
            self.hint_description_text.set("No encrypted records discovered for this user.")
            return
            
        service_names = [item["service_name"] for item in self.raw_menu_data]
        self.service_dropdown.config(values=service_names)
        self.service_dropdown.current(0)
        self._on_service_selected(None)

    def _on_service_selected(self, event):
        selected = self.selected_service.get()
        for item in self.raw_menu_data:
            if item["service_name"] == selected:
                self.hint_description_text.set(f"Cryptographic Clue: {item['hint_clue']}")
                break

    def _decrypt_record(self):
        user = self.current_user.get().strip()
        service = self.selected_service.get()
        mk = self.read_master_key.get()
        hv = self.read_hint_value.get()
        
        if not all([user, service, mk, hv]):
            messagebox.showwarning("Incomplete Fields", "Please populate both secret variables to authenticate.")
            return

        decrypted = self.manager.decrypt_secret(user=user, service_name=service, master_key=mk, hint_value=hv)
        
        if decrypted:
            display_str = json.dumps(decrypted, indent=2)
            messagebox.showinfo(f"Decrypted: {service}", f"Credentials Discovered Safely:\n\n{display_str}")
            self.read_master_key.delete(0, tk.END)
            self.read_hint_value.delete(0, tk.END)
        else:
            messagebox.showerror("Access Denied", "Decryption failed. The master key or hint configuration answer is invalid.")

    def _save_or_update_record(self):
        user = self.current_user.get().strip()
        service = self.form_service.get().strip()
        url = self.form_url.get().strip()
        hint_desc = self.form_hint_desc.get().strip()
        hint_val = self.form_hint_val.get().strip()
        master_key = self.form_master_key.get().strip()
        
        if not all([user, service, url, hint_desc, hint_val, master_key]):
            messagebox.showwarning("Missing Data", "All configuration inputs on the entry panel form are mandatory.")
            return

        try:
            payload_dict = json.loads(self.form_payload.get("1.0", tk.END).strip())
        except Exception:
            messagebox.showerror("JSON Schema Error", "Credentials field must be formatted as valid JSON data.\nExample: {\"key\": \"value\"}")
            return

        payload_model = DecryptedSecretPayload(
            url_or_app=url,
            payload=payload_dict,
            hint_value=hint_val
        )

        self.manager.save_secret(
            user=user,
            service_name=service,
            master_key=master_key,
            decrypted_payload=payload_model,
            hint_description=hint_desc
        )

        messagebox.showinfo("Success", f"Secret file for '{service}' has been securely written.")
        self.form_hint_val.delete(0, tk.END)
        self.form_master_key.delete(0, tk.END)
        self._load_user_menu()

    def _delete_record(self):
        user = self.current_user.get().strip()
        service = self.form_service.get().strip()
        
        if not user or not service:
            messagebox.showwarning("Target Missing", "Specify both the Active Profile Name and Service Name to target deletion.")
            return
            
        confirm = messagebox.askyesno(
            "Confirm Destructive Action", 
            f"Are you sure you want to permanently delete the encrypted payload file tracking '{service}'?\nThis action cannot be undone."
        )
        
        if confirm:
            success = self.manager.delete_secret(user=user, service_name=service)
            if success:
                messagebox.showinfo("Purged", f"Storage token matching '{service}' has been erased from disk.")
                self.form_service.delete(0, tk.END)
                self._load_user_menu()
            else:
                messagebox.showerror("Error", "Could not find an active file matching that user-service hash fingerprint.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkModeFamilyVaultUI(root)
    root.mainloop()