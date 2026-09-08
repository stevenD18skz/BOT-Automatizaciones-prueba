import tkinter as tk
from tkinter import messagebox
from typing import Tuple


class LoginDialog:
    """Ventana de diálogo para capturar credenciales de usuario."""

    def __init__(self):
        self.root = None
        self.username = ""
        self.password = ""
        self.result = False

    def show_login_dialog(self) -> Tuple[bool, str, str]:
        """
        Muestra la ventana de login y retorna las credenciales.

        Returns:
            Tuple[bool, str, str]: (success, username, password)
        """
        self.root = tk.Tk()
        self.root.title("Login SIIF")
        self.root.geometry("350x200")
        self.root.resizable(False, False)

        # Centrar ventana
        self.root.eval("tk::PlaceWindow . center")

        # Variables para los campos
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            main_frame, text="Credenciales SIIF", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Campo usuario
        tk.Label(main_frame, text="Usuario:", font=("Arial", 10)).pack(anchor=tk.W)
        username_entry = tk.Entry(
            main_frame, textvariable=self.username_var, font=("Arial", 10), width=30
        )
        username_entry.pack(pady=(5, 10), fill=tk.X)
        username_entry.focus()

        # Campo contraseña
        tk.Label(main_frame, text="Contraseña:", font=("Arial", 10)).pack(anchor=tk.W)
        password_entry = tk.Entry(
            main_frame,
            textvariable=self.password_var,
            show="*",
            font=("Arial", 10),
            width=30,
        )
        password_entry.pack(pady=(5, 20), fill=tk.X)

        # Frame para botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # Botones
        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            command=self._on_login,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
        )
        login_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            bg="#f44336",
            fg="white",
            font=("Arial", 10),
            width=12,
        )
        cancel_btn.pack(side=tk.RIGHT)

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self._on_login())
        password_entry.bind("<Return>", lambda e: self._on_login())

        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Hacer modal
        self.root.transient()
        self.root.grab_set()

        # Ejecutar loop
        self.root.mainloop()

        return self.result, self.username, self.password

    def _on_login(self):
        """Maneja el clic en el botón de login."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username:
            messagebox.showerror("Error", "Por favor ingrese el usuario")
            return

        if not password:
            messagebox.showerror("Error", "Por favor ingrese la contraseña")
            return

        self.username = username
        self.password = password
        self.result = True
        self.root.destroy()  # type: ignore

    def _on_cancel(self):
        """Maneja el clic en cancelar."""
        self.result = False
        self.root.destroy()  # type: ignore


def get_credentials() -> Tuple[bool, str, str]:
    """
    Función utilitaria para obtener credenciales.

    Returns:
        Tuple[bool, str, str]: (success, username, password)
    """
    dialog = LoginDialog()
    return dialog.show_login_dialog()
