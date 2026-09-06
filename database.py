import sqlite3

def conectar():
    # Conecta ao banco (cria o arquivo database.db na raiz se ele não existir)
    conn = sqlite3.connect('database.db')
    # row_factory permite acessar as colunas pelo nome (ex: linha['nome'])
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # 1. Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL -- 'aluno' ou 'professor'
        )
    ''')

    # 2. Tabela de Turmas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_disciplina TEXT NOT NULL,
            professor_id INTEGER,
            FOREIGN KEY (professor_id) REFERENCES usuarios (id)
        )
    ''')

    # 3. Tabela de Sessões (Chamadas abertas via QR Code)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'aberta', -- 'aberta' ou 'fechada'
            FOREIGN KEY (turma_id) REFERENCES turmas (id)
        )
    ''')

    # 4. Tabela de Presenças (Onde o token validado será registrado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presencas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao_id INTEGER,
            aluno_id INTEGER,
            timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sessao_id) REFERENCES sessoes (id),
            FOREIGN KEY (aluno_id) REFERENCES usuarios (id)
        )
    ''')

    # 5. Inserir dados iniciais (Mock) apenas se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Criando o professor
        cursor.execute("INSERT INTO usuarios (nome, matricula, senha, tipo) VALUES ('Prof. Wellington', '12345', 'senha123', 'professor')")
        # Criando o seu usuário como aluno, usando os dados do TAP
        cursor.execute("INSERT INTO usuarios (nome, matricula, senha, tipo) VALUES ('João Douglas', '2026117789', 'senha123', 'aluno')")
        
        # Criando uma turma vinculada ao professor (que será o ID 1)
        cursor.execute("INSERT INTO turmas (nome_disciplina, professor_id) VALUES ('Engenharia de Software', 1)")

    conn.commit()
    conn.close()
    print("Banco de dados SQLite inicializado com sucesso!")

# Se rodarmos este arquivo direto no terminal, ele cria as tabelas
if __name__ == '__main__':
    inicializar_banco()