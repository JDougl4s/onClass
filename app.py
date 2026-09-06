from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import hashlib
import time

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
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE matricula = ? AND senha = ? AND tipo = ?",
            (identificacao, senha, tipo_usuario)
        )
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            if usuario['tipo'] == 'professor':
                return redirect(url_for('painel_professor', professor_id=usuario['id']))
            else:
                # Redireciona o aluno corretamente para o seu portal
                return redirect(url_for('portal_aluno', aluno_id=usuario['id']))
        else:
            return "<h1>Erro de Autenticação</h1><p>Credenciais incorretas. <a href='/login'>Tentar novamente</a></p>"
            
    return render_template('login.html')

@app.route('/professor/painel/<int:professor_id>')
def painel_professor(professor_id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turmas WHERE professor_id = ?", (professor_id,))
    turmas = cursor.fetchall()
    conn.close()
    
    return render_template('painel_professor.html', professor_id=professor_id, turmas=turmas)

@app.route('/professor/iniciar_sessao', methods=['POST'])
def iniciar_sessao():
    professor_id = request.form.get('professor_id')
    turma_id = request.form.get('turma_id')
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessoes (turma_id, status) VALUES (?, 'aberta')", (turma_id,))
    conn.commit()
    sessao_id = cursor.lastrowid
    
    cursor.execute("SELECT nome_disciplina FROM turmas WHERE id = ?", (turma_id,))
    turma = cursor.fetchone()
    conn.close()
    
    return render_template('sessao_ativa.html', sessao_id=sessao_id, disciplina=turma['nome_disciplina'])

@app.route('/api/token/<int:sessao_id>')
def gerar_token(sessao_id):
    bloco_tempo = int(time.time() // 10)
    string_base = f"{sessao_id}-{bloco_tempo}-ONCLASS_SECRET"
    token_hash = hashlib.sha256(string_base.encode()).hexdigest()
    
    return jsonify({"token": token_hash, "expira_em": 10})

@app.route('/aluno/portal/<int:aluno_id>')
def portal_aluno(aluno_id):
    return render_template('portal_aluno.html', aluno_id=aluno_id)

@app.route('/aluno/registrar_presenca', methods=['POST'])
def registrar_presenca():
    aluno_id = request.form.get('aluno_id')
    token_recebido = request.form.get('token_recebido').strip()
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessoes WHERE status = 'aberta'")
    sessoes_abertas = cursor.fetchall()
    
    sessao_valida = None
    tempo_atual = int(time.time() // 10)
    blocos_para_testar = [tempo_atual, tempo_atual - 1]
    
    for sessao in sessoes_abertas:
        for bloco in blocos_para_testar:
            string_teste = f"{sessao['id']}-{bloco}-ONCLASS_SECRET"
            hash_gerado = hashlib.sha256(string_teste.encode()).hexdigest()
            
            if hash_gerado == token_recebido:
                sessao_valida = sessao['id']
                break
        if sessao_valida:
            break
            
    if sessao_valida:
        cursor.execute("SELECT * FROM presencas WHERE sessao_id = ? AND aluno_id = ?", (sessao_valida, aluno_id))
        ja_registrado = cursor.fetchone()
        
        if ja_registrado:
            conn.close()
            return f"<h1>Aviso</h1><p>Sua presença já havia sido registrada nesta aula!</p><a href='/aluno/portal/{aluno_id}'>Voltar</a>"
            
        cursor.execute("INSERT INTO presencas (sessao_id, aluno_id) VALUES (?, ?)", (sessao_valida, aluno_id))
        conn.commit()
        conn.close()
        return f"<h1>Sucesso!</h1><p>Presença confirmada e registrada com segurança pelo sistema ONClass!</p><a href='/aluno/portal/{aluno_id}'>Voltar ao Portal</a>"
    else:
        conn.close()
        return "<h1>Falha na Validação</h1><p>O token informado é inválido ou já expirou (janela de segurança ultrapassada). <a href='javascript:history.back()'>Tentar novamente</a></p>"

if __name__ == '__main__':
    app.run(debug=True)