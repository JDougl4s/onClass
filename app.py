from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def conectar_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identificacao = request.form.get('identificacao')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo_usuario')
        
        # Conecta ao banco de dados SQLite
        conn = conectar_db()
        cursor = conn.cursor()
        
        # Consulta o usuário na tabela filtrando por matrícula, senha e tipo
        cursor.execute(
            "SELECT * FROM usuarios WHERE matricula = ? AND senha = ? AND tipo = ?",
            (identificacao, senha, tipo_usuario)
        )
        usuario = cursor.fetchone()
        conn.close()
        
        # Valida se o usuário foi encontrado
        if usuario:
            print(f"Login bem-sucedido para: {usuario['nome']} ({usuario['tipo']})")
            return f"<h1>Bem-vindo, {usuario['nome']}!</h1><p>Login efetuado com sucesso no perfil de {usuario['tipo']}.</p>"
        else:
            return "<h1>Erro de Autenticação</h1><p>Matrícula, senha ou tipo de usuário incorretos. <a href='/login'>Tentar novamente</a></p>"
            
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)