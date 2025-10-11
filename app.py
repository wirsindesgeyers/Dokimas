from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




#tabelas
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    perguntas = db.relationship('Pergunta', backref='quiz', cascade="all, delete-orphan")
    respostas_alunos = db.relationship('RespostaAluno', backref='quiz', cascade="all, delete-orphan")

class Pergunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    pergunta = db.Column(db.String(500), nullable=False)
    opcoes = db.Column(db.PickleType, nullable=False)  # Lista de opções
    correta = db.Column(db.Integer, nullable=False)

class RespostaAluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    nick = db.Column(db.String(50), nullable=False)
    acertos = db.Column(db.Integer, nullable=False)




#Controller
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/criar_quiz', methods=['GET', 'POST'])
def criar_quiz():
    if request.method == 'POST':
        titulo = request.form.get("titulo")
        perguntas_texto = request.form.getlist("pergunta[]")
        opcoes1 = request.form.getlist("opcao1[]")
        opcoes2 = request.form.getlist("opcao2[]")
        opcoes3 = request.form.getlist("opcao3[]")
        opcoes4 = request.form.getlist("opcao4[]")

        # cria o quiz 
        quiz = Quiz(titulo=titulo)
        db.session.add(quiz)
        db.session.commit()  # gera o ID do quiz

        # agora cria as perguntas
        for i in range(len(perguntas_texto)):
            # pega o índice da resposta correta para esta pergunta
            correta = request.form.get(f"correta[{i}]")
            if correta is None:
                correta = 0  
            else:
                correta = int(correta)

            
            pergunta = Pergunta(
                quiz_id=quiz.id,
                pergunta=perguntas_texto[i],
                opcoes=[opcoes1[i], opcoes2[i], opcoes3[i], opcoes4[i]],
                correta=correta
            )
            db.session.add(pergunta)

        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('criar_quiz.html')

@app.route('/responder')
def responder():
    quizzes = Quiz.query.all()
    return render_template('responder_lista.html', quizzes=quizzes)

@app.route('/responder/<int:quiz_id>', methods=['GET'])
def responder_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('responder_quiz.html', quiz=quiz)

@app.route('/enviar_resposta/<int:quiz_id>', methods=['POST'])
def enviar_resposta(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    nick = request.form.get("nick")

    perguntas = quiz.perguntas
    acertos = 0

    for i, pergunta in enumerate(perguntas):
        chave = f"resposta[{i}]"
        resposta_usuario = request.form.get(chave)
        if resposta_usuario is not None and int(resposta_usuario) == pergunta.correta:
            acertos += 1

    resposta_aluno = RespostaAluno(quiz_id=quiz.id, nick=nick, acertos=acertos)
    db.session.add(resposta_aluno)
    db.session.commit()

    return render_template('resultado.html', nick=nick, quiz=quiz, total=len(perguntas), acertos=acertos)

@app.route('/deletar_quiz/<int:quiz_id>', methods=['POST'])
def deletar_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('dashboard'))



@app.route('/dashboard')
def dashboard():
    quizzes = Quiz.query.all()
    return render_template('dashboard.html', quizzes=quizzes)



#cria o banco de dados
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
