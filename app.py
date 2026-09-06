from flask import Flask, render_template, request, redirect

# Inicializa o servidor Flask
app = Flask(__name__)

# Rota 1: A raiz do site
@app.route('/')
def index():
    # Se a pessoa acessar o site sem digitar /login, nós a redirecionamos
    return redirect('/login')

# Rota 2: A tela de Login (Aceita acessar a tela e enviar o formulário)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Quando o usuário clica no botão do formulário, os dados chegam aqui
        identificacao = request.form.get('identificacao')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo_usuario')
        
        # Por enquanto, vamos apenas imprimir no terminal para ver funcionando
        print(f"Tentativa de login -> Usuário: {identificacao} | Tipo: {tipo_usuario}")
        
        # E devolver uma mensagem simples na tela
        return f"<h1>Sucesso!</h1> <p>O servidor Python recebeu os dados do {tipo_usuario}: {identificacao}.</p>"
        
    # Se o método for GET (apenas acessar a URL), renderizamos o seu HTML
    return render_template('login.html')

# Inicia o servidor apenas se este arquivo for executado diretamente
if __name__ == '__main__':
    # debug=True faz o servidor reiniciar sozinho sempre que você salvar o código
    app.run(debug=True)