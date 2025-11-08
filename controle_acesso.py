import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import os

# Caminho do banco de dados
db_path = os.path.join("database", "acesso.db")
os.makedirs("database", exist_ok=True)

# Conexão inicial e criação das tabelas
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha TEXT,
    nivel TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    nivel TEXT,
    data_hora TEXT
)
''')

# Cria usuário admin padrão (caso não exista)
cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO usuarios (usuario, senha, nivel) VALUES (?, ?, ?)",
                   ("admin", "admin123", "admin"))
    conn.commit()

conn.close()


# Função principal de login
def fazer_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nivel FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    resultado = cursor.fetchone()

    if resultado:
        nivel = resultado[0]
        registrar_log(usuario, nivel)
        messagebox.showinfo("Acesso Permitido", f"Bem-vindo, {usuario}! (Nível: {nivel})")
        janela_login.destroy()
        abrir_sistema(usuario, nivel)
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos.")
    conn.close()


# Registra o log de acesso
def registrar_log(usuario, nivel):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (usuario, nivel, data_hora) VALUES (?, ?, ?)",
                   (usuario, nivel, data_hora))
    conn.commit()
    conn.close()


# Abre a janela principal após login
def abrir_sistema(usuario, nivel):
    janela = tk.Tk()
    janela.title("Painel do Sistema")
    janela.geometry("350x250")

    tk.Label(janela, text=f"Usuário: {usuario}", font=("Arial", 12)).pack(pady=5)
    tk.Label(janela, text=f"Nível de acesso: {nivel}", font=("Arial", 12, "bold")).pack(pady=5)

    if nivel == "admin":
        tk.Button(janela, text="Cadastrar novo usuário", command=cadastrar_usuario, width=25, bg="lightblue").pack(pady=10)
    tk.Button(janela, text="Ver registros de acesso", command=ver_logs, width=25).pack(pady=10)
    tk.Button(janela, text="Sair", command=janela.destroy, width=25, bg="lightgray").pack(pady=10)

    janela.mainloop()


# Cadastra novos usuários (somente admin)
def cadastrar_usuario():
    def salvar():
        novo_usuario = entry_novo_usuario.get()
        nova_senha = entry_nova_senha.get()
        nivel = var_nivel.get()

        if novo_usuario and nova_senha:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (usuario, senha, nivel) VALUES (?, ?, ?)",
                               (novo_usuario, nova_senha, nivel))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", f"Usuário '{novo_usuario}' cadastrado!")
                janela_cadastro.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Usuário já existe.")
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")

    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastrar Usuário")
    janela_cadastro.geometry("300x250")

    tk.Label(janela_cadastro, text="Novo Usuário:").pack()
    entry_novo_usuario = tk.Entry(janela_cadastro)
    entry_novo_usuario.pack()

    tk.Label(janela_cadastro, text="Senha:").pack()
    entry_nova_senha = tk.Entry(janela_cadastro, show="*")
    entry_nova_senha.pack()

    tk.Label(janela_cadastro, text="Nível de Acesso:").pack()
    var_nivel = tk.StringVar(value="visitante")
    tk.OptionMenu(janela_cadastro, var_nivel, "admin", "técnico", "visitante").pack()

    tk.Button(janela_cadastro, text="Salvar", command=salvar).pack(pady=10)


# Visualiza os registros de login
def ver_logs():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, nivel, data_hora FROM logs ORDER BY id DESC LIMIT 10")
    registros = cursor.fetchall()
    conn.close()

    janela_logs = tk.Toplevel()
    janela_logs.title("Registros de Acesso")
    janela_logs.geometry("400x300")

    tk.Label(janela_logs, text="Últimos Acessos:", font=("Arial", 12, "bold")).pack(pady=5)

    for r in registros:
        tk.Label(janela_logs, text=f"{r[2]} - {r[0]} ({r[1]})").pack(anchor="w")


# Interface de login
janela_login = tk.Tk()
janela_login.title("Login do Sistema")
janela_login.geometry("300x200")

tk.Label(janela_login, text="Usuário:").pack()
entry_usuario = tk.Entry(janela_login)
entry_usuario.pack()

tk.Label(janela_login, text="Senha:").pack()
entry_senha = tk.Entry(janela_login, show="*")
entry_senha.pack()

tk.Button(janela_login, text="Entrar", command=fazer_login, width=20, bg="lightblue").pack(pady=10)
tk.Button(janela_login, text="Sair", command=janela_login.destroy, width=20, bg="lightgray").pack()

janela_login.mainloop()