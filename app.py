from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

QUIZ_FILE = 'quizzes.json'

# ------------------------
# Funções auxiliares
# ------------------------
def ler_quizzes():
    if not os.path.exists(QUIZ_FILE):
        return []
    with open(QUIZ_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_quizzes(quizzes):
    with open(QUIZ_FILE, 'w', encoding='utf-8') as f:
        json.dump(quizzes, f, indent=4, ensure_ascii=False)

# ------------------------
# Rotas principais
# ------------------------

@app.route('/')
def index():
    return render_template('home.html')

# Criar quiz
@app.route('/criar_quiz', methods=['GET', 'POST'])
def criar_quiz():
    if request.method == 'POST':
        titulo = request.form.get("titulo")
        perguntas = []

        # Vamos assumir 5 perguntas fixas (como no HTML que te mandei)
        for i in range(1, 6):
            texto = request.form.get(f"pergunta{i}")
            if not texto:  # se não preencher, pula
                continue

            opcoes = [
                request.form.get(f"pergunta{i}_opcao1"),
                request.form.get(f"pergunta{i}_opcao2"),
                request.form.get(f"pergunta{i}_opcao3"),
                request.form.get(f"pergunta{i}_opcao4"),
            ]
            correta = request.form.get(f"pergunta{i}_correta")

            perguntas.append({
                "pergunta": texto,
                "opcoes": opcoes,
                "correta": int(correta) if correta is not None else 0
            })

        # Salvar no JSON
        quizzes = ler_quizzes()
        quizzes.append({
            "titulo": titulo,
            "perguntas": perguntas,
            "respostas_alunos": []
        })
        salvar_quizzes(quizzes)

        return redirect(url_for('index'))

    return render_template('criar_quiz.html')

# Listar quizzes para escolher
@app.route('/responder')
def responder():
    quizzes = ler_quizzes()
    return render_template('responder_lista.html', quizzes=quizzes)

# Responder quiz específico
@app.route('/responder/<int:quiz_index>')
def responder_quiz(quiz_index):
    quizzes = ler_quizzes()
    if quiz_index >= len(quizzes):
        return "Quiz não encontrado", 404
    quiz = quizzes[quiz_index]
    return render_template('responder_quiz.html', quiz=quiz, quiz_index=quiz_index)

# Enviar respostas de um quiz
@app.route('/enviar_resposta/<int:quiz_index>', methods=['POST'])
def enviar_resposta(quiz_index):
    nick = request.form.get("nick")
    quizzes = ler_quizzes()

    if quiz_index >= len(quizzes):
        return "Quiz não encontrado", 404

    quiz = quizzes[quiz_index]
    perguntas = quiz["perguntas"]

    acertos = 0
    respostas_usuario = []

    for i, pergunta in enumerate(perguntas):
        chave = f"resposta[{i}]"
        resposta_usuario = request.form.get(chave)

        if resposta_usuario is not None:
            resposta_usuario = int(resposta_usuario)
            respostas_usuario.append(resposta_usuario)
            if resposta_usuario == pergunta["correta"]:
                acertos += 1

    quiz["respostas_alunos"].append({"nick": nick, "acertos": acertos})
    salvar_quizzes(quizzes)

    return render_template(
        "resultado.html",
        nick=nick,
        quiz=quiz,
        total=len(perguntas),
        acertos=acertos
    )

# Dashboard para ver desempenho dos alunos
@app.route('/dashboard')
def dashboard():
    quizzes = ler_quizzes()
    return render_template('dashboard.html', quizzes=quizzes)

# ------------------------
# Inicialização
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)
