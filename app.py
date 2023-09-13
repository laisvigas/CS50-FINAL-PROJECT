import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
import re
import bcrypt
import os
import random
from flask_wtf import FlaskForm
from wtforms import HiddenField


app = Flask(__name__)

app.secret_key = '12345*#'

def conectar_db():
    return sqlite3.connect('diario_classe.db')

# Criar o banco de dados e as tabelas
def initialize_database():
    if not os.path.exists('diario_classe.db'):
        conn = sqlite3.connect('diario_classe.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_aluno TEXT NOT NULL,
                genero TEXT NOT NULL   
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_aluno INTEGER NOT NULL,
                nota_portugues REAL NOT NULL,
                nota_matematica REAL NOT NULL,
                nota_historia REAL NOT NULL,
                nota_geografia REAL NOT NULL,
                nota_ciencias REAL NOT NULL,
                FOREIGN KEY (id_aluno) REFERENCES alunos (id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_aluno INTEGER NOT NULL,
                nota_portugues REAL NOT NULL,
                nota_matematica REAL NOT NULL,
                nota_historia REAL NOT NULL,
                nota_geografia REAL NOT NULL,
                nota_ciencias REAL NOT NULL,
                FOREIGN KEY (id_aluno) REFERENCES alunos (id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas3 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_aluno INTEGER NOT NULL,
                nota_portugues REAL NOT NULL,
                nota_matematica REAL NOT NULL,
                nota_historia REAL NOT NULL,
                nota_geografia REAL NOT NULL,
                nota_ciencias REAL NOT NULL,
                FOREIGN KEY (id_aluno) REFERENCES alunos (id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')


        conn.commit()
        conn.close()

# Chamando a função para criar o banco de dados e as tabelas, se necessário
initialize_database()

class DeleteForm(FlaskForm):
    _method = HiddenField()

@app.route('/excluir_aluno/<int:aluno_id>', methods=['POST'])
def excluir_aluno(aluno_id):
    conn = sqlite3.connect('diario_classe.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
    conn.commit()
    conn.close()
    
    flash("Exclusão de aluno realizada com sucesso.", "success")
    return redirect(url_for('cadastrar_aluno'))


# Página de Login
@app.route('/', methods=['GET', 'POST'])
def login():
    conn = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('diario_classe.db')
        cursor = conn.cursor()

        # Procura um registro com o email fornecido pelo usuário
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        user = cursor.fetchone()

        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user[2]):
            # Redireciona de volta para a página de login com um parâmetro de consulta indicando erro
            flash('Senha ou e-mail incorreto, ou usuário inexistente. Por favor, tente novamente ou realize o cadastro abaixo.', 'error')
            return redirect(url_for('login', error='true'))
        else:
            # Armazena o email do usuário na sessão
            session['email'] = email
            return redirect(url_for('pagina_inicial'))

    if conn:
        conn.close()

    return render_template('index.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verifica se a senha atende aos requisitos
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            flash("A senha deve conter pelo menos oito caracteres com pelo menos uma letra maiúscula, uma letra minúscula, um número e um símbolo.", "error")
            return redirect('/cadastro')
        
        elif password != confirm_password:
            flash("As senhas não coincidem. Por favor, verifique e tente novamente.", "error")
            return redirect('/cadastro')
        else:
            # Realiza o hash da senha antes de armazená-la no banco de dados
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insere o novo usuário no banco de dados com a senha criptografada
            conn = sqlite3.connect('diario_classe.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO usuarios (email, senha) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            conn.close()

            # Define a mensagem de sucesso e redireciona para a página de login
            flash("Cadastro realizado com sucesso! Realize o login abaixo.", "success")
            return redirect(url_for('login'))
    
    # Caso seja um método GET ou houver algum erro, continua exibindo a página de cadastro
    return render_template('cadastro.html')


@app.route('/pagina_inicial', methods=['GET', 'POST'])
def pagina_inicial():
    # Obtém o email do usuário da sessão
    email = session.get('email', None)

    # Obtém uma frase motivacional aleatória
    motivational_phrase = get_random_motivational_phrase()

    return render_template('pagina_inicial.html', email=email, motivational_phrase=motivational_phrase)

def insert_zero_notas(con, tabela, aluno_id):
    con.execute(f'''
        INSERT INTO {tabela} (id_aluno, nota_portugues, nota_matematica, nota_historia, nota_geografia, nota_ciencias)
        VALUES (?, 0.0, 0.0, 0.0, 0.0, 0.0)
    ''', (aluno_id,))



@app.route('/cadastrar_aluno', methods=['GET', 'POST'])
def cadastrar_aluno():
    if request.method == 'POST':
        nome_aluno = request.form['nome_aluno']
        genero = request.form['genero']

        try:
            conn = sqlite3.connect('diario_classe.db')
            cursor = conn.cursor()

            # Insere os dados do aluno na tabela "alunos"
            cursor.execute('INSERT INTO alunos (nome_aluno, genero) VALUES (?, ?)',
                           (nome_aluno, genero))

            # Obtém o ID do aluno recém-cadastrado
            aluno_id = cursor.lastrowid

            # Adiciona notas zero para o aluno em todas as unidades (tabelas de notas)
            insert_zero_notas(conn, 'notas', aluno_id)
            insert_zero_notas(conn, 'notas2', aluno_id)
            insert_zero_notas(conn, 'notas3', aluno_id)

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            # Em caso de erro ao adicionar aluno, exibe a mensagem de erro para o professor
            flash(f'Erro ao adicionar aluno: {e}', 'error')
            return redirect('/cadastrar_aluno')

    conn = sqlite3.connect('diario_classe.db')
    cursor = conn.cursor()

    # Obtém a lista de alunos cadastrados na tabela "alunos" e ordena pelo nome do aluno
    cursor.execute('SELECT * FROM alunos ORDER BY nome_aluno')
    alunos = cursor.fetchall()

    conn.close()

    # Renderiza a página cadastrar_aluno.html e passa a lista de alunos para ser exibida
    return render_template('cadastrar_aluno.html', alunos=alunos, flash_messages=get_flashed_messages())



@app.route('/adicionar_notas', methods=['GET', 'POST'])
def adicionar_notas():
    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('SELECT * FROM notas')
        notas_rows = cur.fetchall()
        notas_alunos = {}

        for row in notas_rows:
            aluno_id = row[1]
            notas_alunos[aluno_id] = {
                'portugues': row[2],
                'matematica': row[3],
                'historia': row[4],
                'geografia': row[5],
                'ciencias': row[6],
            }

    if request.method == 'POST':
        with sqlite3.connect('diario_classe.db') as con:
            cur = con.execute('SELECT id FROM alunos')
            aluno_ids = [row[0] for row in cur.fetchall()]

            for aluno_id in aluno_ids:
                notas_aluno = {}
                portugues = request.form.get(f'notas_{aluno_id}_portugues', '')
                matematica = request.form.get(f'notas_{aluno_id}_matematica', '')
                historia = request.form.get(f'notas_{aluno_id}_historia', '')
                geografia = request.form.get(f'notas_{aluno_id}_geografia', '')
                ciencias = request.form.get(f'notas_{aluno_id}_ciencias', '')

                if not all(valor.replace('.', '').isdigit() or valor == '' for valor in [portugues, matematica, historia, geografia, ciencias]):
                    return redirect(url_for('adicionar_notas'))

                notas_aluno['portugues'] = float(portugues) if portugues else 0.0
                notas_aluno['matematica'] = float(matematica) if matematica else 0.0
                notas_aluno['historia'] = float(historia) if historia else 0.0
                notas_aluno['geografia'] = float(geografia) if geografia else 0.0
                notas_aluno['ciencias'] = float(ciencias) if ciencias else 0.0
                
                notas_alunos[aluno_id] = notas_aluno

            for aluno_id, notas_aluno in notas_alunos.items():
                cur = con.execute('SELECT id_aluno FROM notas WHERE id_aluno = ?', (aluno_id,))
                existing_aluno = cur.fetchone()

                if existing_aluno:
                    con.execute("""
                        UPDATE notas SET 
                        nota_portugues = ?, nota_matematica = ?, nota_historia = ?, nota_geografia = ?, nota_ciencias = ?
                        WHERE id_aluno = ?
                    """, (notas_aluno['portugues'], notas_aluno['matematica'], notas_aluno['historia'], notas_aluno['geografia'], notas_aluno['ciencias'], aluno_id))
                else:
                    con.execute("""
                        INSERT INTO notas (id_aluno, nota_portugues, nota_matematica, nota_historia, nota_geografia, nota_ciencias)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (aluno_id, notas_aluno['portugues'], notas_aluno['matematica'], notas_aluno['historia'], notas_aluno['geografia'], notas_aluno['ciencias']))

            con.commit()

        return redirect(url_for('adicionar_notas'))

    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('SELECT * FROM alunos')
        alunos = cur.fetchall()

    # Ordenar a lista de alunos em ordem alfabética pelo nome
    alunos_sorted = sorted(alunos, key=lambda aluno: aluno[1])

    # Garantir que os dicionários notas_alunos mantenham as notas correspondentes após a ordenação
    notas_alunos_sorted = {aluno[0]: notas_alunos.get(aluno[0], {}) for aluno in alunos_sorted}

    return render_template('adicionar_notas.html', alunos=alunos_sorted, notas_alunos=notas_alunos_sorted)


def insert_or_update_notas(con, tabela, aluno_id, notas_aluno):
    cur = con.execute(f'SELECT id_aluno FROM {tabela} WHERE id_aluno = ?', (aluno_id,))
    existing_aluno = cur.fetchone()

    if existing_aluno:
        con.execute(f'''
            UPDATE {tabela} SET 
            nota_portugues = ?, nota_matematica = ?, nota_historia = ?, nota_geografia = ?, nota_ciencias = ?
            WHERE id_aluno = ?
        ''', (notas_aluno['portugues'], notas_aluno['matematica'], notas_aluno['historia'], notas_aluno['geografia'], notas_aluno['ciencias'], aluno_id))
    else:
        con.execute(f'''
            INSERT INTO {tabela} (id_aluno, nota_portugues, nota_matematica, nota_historia, nota_geografia, nota_ciencias)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (aluno_id, notas_aluno['portugues'], notas_aluno['matematica'], notas_aluno['historia'], notas_aluno['geografia'], notas_aluno['ciencias']))

    con.commit()


@app.route('/adicionar_notas_uni2', methods=['GET', 'POST'])
def adicionar_notas_uni2():
    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('SELECT * FROM notas2')
        notas2_rows = cur.fetchall()
        notas2_alunos = {}

        for row in notas2_rows:
            aluno_id = row[1]
            notas2_alunos[aluno_id] = {
                'portugues': row[2],
                'matematica': row[3],
                'historia': row[4],
                'geografia': row[5],
                'ciencias': row[6],
            }

    if request.method == 'POST':
        with sqlite3.connect('diario_classe.db') as con:
            cur = con.execute('SELECT id FROM alunos')
            aluno_ids = [row[0] for row in cur.fetchall()]

            for aluno_id in aluno_ids:
                notas_aluno = {}
                portugues = request.form.get(f'notas2_{aluno_id}_portugues', '')
                matematica = request.form.get(f'notas2_{aluno_id}_matematica', '')
                historia = request.form.get(f'notas2_{aluno_id}_historia', '')
                geografia = request.form.get(f'notas2_{aluno_id}_geografia', '')
                ciencias = request.form.get(f'notas2_{aluno_id}_ciencias', '')

                if not all(valor.replace('.', '').isdigit() or valor == '' for valor in [portugues, matematica, historia, geografia, ciencias]):
                    return redirect(url_for('adicionar_notas_uni2'))

                notas_aluno['portugues'] = float(portugues) if portugues else 0.0
                notas_aluno['matematica'] = float(matematica) if matematica else 0.0
                notas_aluno['historia'] = float(historia) if historia else 0.0
                notas_aluno['geografia'] = float(geografia) if geografia else 0.0
                notas_aluno['ciencias'] = float(ciencias) if ciencias else 0.0
                
                insert_or_update_notas(con, 'notas2', aluno_id, notas_aluno)

        return redirect(url_for('adicionar_notas_uni2'))

    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('SELECT * FROM alunos')
        alunos = cur.fetchall()

    # Ordenar a lista de alunos em ordem alfabética pelo nome
    alunos_sorted = sorted(alunos, key=lambda aluno: aluno[1])

    # Garantir que os dicionários notas2_alunos mantenham as notas correspondentes após a ordenação
    notas2_alunos_sorted = {aluno[0]: notas2_alunos.get(aluno[0], {}) for aluno in alunos_sorted}

    return render_template('adicionar_notas_uni2.html', alunos=alunos_sorted, notas2_alunos=notas2_alunos_sorted)


@app.route('/adicionar_notas_uni3', methods=['GET', 'POST'])
def adicionar_notas_uni3():
    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('SELECT * FROM notas3')
        notas3_rows = cur.fetchall()
        notas3_alunos = {}

        for row in notas3_rows:
            aluno_id = row[1]
            notas3_alunos[aluno_id] = {
                'portugues': row[2],
                'matematica': row[3],
                'historia': row[4],
                'geografia': row[5],
                'ciencias': row[6],
            }

    if request.method == 'POST':
        with sqlite3.connect('diario_classe.db') as con:
            cur = con.execute('SELECT id FROM alunos')
            aluno_ids = [row[0] for row in cur.fetchall()]

            for aluno_id in aluno_ids:
                notas_aluno = {}
                portugues = request.form.get(f'notas3_{aluno_id}_portugues', '')
                matematica = request.form.get(f'notas3_{aluno_id}_matematica', '')
                historia = request.form.get(f'notas3_{aluno_id}_historia', '')
                geografia = request.form.get(f'notas3_{aluno_id}_geografia', '')
                ciencias = request.form.get(f'notas3_{aluno_id}_ciencias', '')

                if not all(valor.replace('.', '').isdigit() or valor == '' for valor in [portugues, matematica, historia, geografia, ciencias]):
                    return redirect(url_for('adicionar_notas_uni3'))

                notas_aluno['portugues'] = float(portugues) if portugues else 0.0
                notas_aluno['matematica'] = float(matematica) if matematica else 0.0
                notas_aluno['historia'] = float(historia) if historia else 0.0
                notas_aluno['geografia'] = float(geografia) if geografia else 0.0
                notas_aluno['ciencias'] = float(ciencias) if ciencias else 0.0
                
                insert_or_update_notas(con, 'notas3', aluno_id, notas_aluno)

        return redirect(url_for('adicionar_notas_uni3'))

    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('SELECT * FROM alunos')
        alunos = cur.fetchall()

    # Ordenar a lista de alunos em ordem alfabética pelo nome
    alunos_sorted = sorted(alunos, key=lambda aluno: aluno[1])

    # Garantir que os dicionários notas3_alunos mantenham as notas correspondentes após a ordenação
    notas3_alunos_sorted = {aluno[0]: notas3_alunos.get(aluno[0], {}) for aluno in alunos_sorted}

    return render_template('adicionar_notas_uni3.html', alunos=alunos_sorted, notas3_alunos=notas3_alunos_sorted)


@app.route('/media', methods=['GET', 'POST'])
def media():
    with sqlite3.connect('diario_classe.db') as con:
        cur = con.execute('''
            SELECT alunos.id, alunos.nome_aluno,
                   ROUND(COALESCE((notas.nota_portugues + notas2.nota_portugues + notas3.nota_portugues) / 3, 0), 1) AS media_portugues,
                   ROUND(COALESCE((notas.nota_matematica + notas2.nota_matematica + notas3.nota_matematica) / 3, 0), 1) AS media_matematica,
                   ROUND(COALESCE((notas.nota_historia + notas2.nota_historia + notas3.nota_historia) / 3, 0), 1) AS media_historia,
                   ROUND(COALESCE((notas.nota_geografia + notas2.nota_geografia + notas3.nota_geografia) / 3, 0), 1) AS media_geografia,
                   ROUND(COALESCE((notas.nota_ciencias + notas2.nota_ciencias + notas3.nota_ciencias) / 3, 0), 1) AS media_ciencias
            FROM alunos
            LEFT JOIN notas ON alunos.id = notas.id_aluno
            LEFT JOIN notas2 ON alunos.id = notas2.id_aluno
            LEFT JOIN notas3 ON alunos.id = notas3.id_aluno
        ''')
        media_rows = cur.fetchall()

    media_rows_sorted = sorted(media_rows, key=lambda aluno: aluno[1])

    return render_template('media.html', media_rows=media_rows_sorted)

def get_random_motivational_phrase():
    return random.choice(motivational_phrases)

motivational_phrases = [
    "A mente que se abre a uma nova ideia jamais voltará ao seu tamanho original. - Albert Einstein",
    "O verdadeiro sinal de inteligência não é o conhecimento, mas a imaginação. - Albert Einstein",
    "A educação é a arma mais poderosa que você pode usar para mudar o mundo. - Nelson Mandela",
    "O objetivo da educação é a virtude e o desejo de se tornar um bom cidadão. - Plato",
    "A educação é a melhor provisão para a velhice. - Aristóteles",
    "O único conhecimento que pode realmente influenciar o comportamento é o conhecimento que passou pelo coração. - Howard Thurman",
    "Educar a mente sem educar o coração não é educação de forma alguma. - Aristóteles",
    "O verdadeiro professor defende seus alunos contra sua própria influência. - Amos Bronson Alcott",
    "A educação é a luz da infância, a beleza da juventude e a segurança da velhice. - Aristóteles",
    "Educar a mente sem educar o coração não é educação de forma alguma. - Aristóteles",
    "A função do professor é criar as condições para a invenção ao invés de fornecer o conhecimento. - Albert Einstein",
    "A coisa mais importante é não parar de questionar. - Albert Einstein",
    "Não é suficiente ter uma boa mente; a principal coisa é usá-la bem. - René Descartes",
    "O coração tem razões que a própria razão desconhece. - Blaise Pascal",
    "A sabedoria começa na reflexão. - Sócrates",
    "A única coisa que sei é que nada sei. - Sócrates",
    "Conhece-te a ti mesmo. - Sócrates",
    "O conhecimento fala, mas a sabedoria escuta. - Jimi Hendrix",
    "A mente é um bom servo, mas um péssimo mestre. - A.W. Tozer",
    "A vida é realmente simples, mas insistimos em torná-la complicada. - Confúcio",
    "Não é o homem que tem pouco, mas sim aquele que anseia por mais, que é pobre. - Sêneca",
    "A adversidade é um espelho que reflete o verdadeiro eu. - Sêneca",
    "Não somos apenas o que pensamos ser. Somos mais; somos também o que lembramos e aquilo de que nos esquecemos. - Sigmund Freud",
    "Você não pode ensinar nada a um homem. Você só pode ajudá-lo a encontrar a resposta dentro dele mesmo. - Galileu Galilei",
    "Onde reina o amor, sobra a paz. - Mahatma Gandhi",
    "A verdadeira educação consiste em pôr a descoberto ou fazer atualizar o melhor de uma pessoa. - William Ellery Channing",
    "A educação é a arma mais poderosa que você pode usar para mudar o mundo. - Nelson Mandela",
    "A educação é o que sobrevive quando o que foi aprendido é esquecido. - B.F. Skinner",
    "A educação é a capacidade de ouvir quase qualquer coisa sem perder a paciência ou a autoconfiança. - Robert Frost",
    "Ensinar é um exercício de imortalidade. - Mark Van Doren",
    "O verdadeiro professor defende seus alunos contra sua própria influência. - Amos Bronson Alcott",
    "A função do educador é agir nos pontos sensíveis, trazendo-os à luz. - Sigmund Freud",
    "A educação é a passagem do sombrio ao claro. - Allan Bloom",
    "A educação é a arte de ajudar a descobrir o que é possível. - Albert Einstein",
    "Educar é acender uma chama, não encher um recipiente. - Sócrates",
    "A verdadeira educação é aquela que extrai o melhor de si mesmo. - Mahatma Gandhi",
    "O professor tem que ser capaz de despertar alegria na expressão criativa e no conhecimento. - Albert Einstein",
    "O verdadeiro professor defende seus alunos contra sua própria influência. - Amos Bronson Alcott",
    "Ensinar é um exercício de imortalidade. - Mark Van Doren",
    "A função do educador é agir nos pontos sensíveis, trazendo-os à luz. - Sigmund Freud",
    "A educação é a passagem do sombrio ao claro. - Allan Bloom",
    "A educação é a arte de ajudar a descobrir o que é possível. - Albert Einstein",
    "Educar é acender uma chama, não encher um recipiente. - Sócrates",
    "A verdadeira educação é aquela que extrai o melhor de si mesmo. - Mahatma Gandhi",
    "O professor tem que ser capaz de despertar alegria na expressão criativa e no conhecimento. - Albert Einstein",
    "A educação é a arma mais poderosa que você pode usar para mudar o mundo. - Nelson Mandela",
    "A educação é o que sobrevive quando o que foi aprendido é esquecido. - B.F. Skinner",
    "A educação é a capacidade de ouvir quase qualquer coisa sem perder a paciência ou a autoconfiança. - Robert Frost",
    "Ensinar é um exercício de imortalidade. - Mark Van Doren",
    "O verdadeiro professor defende seus alunos contra sua própria influência. - Amos Bronson Alcott",
    "A função do educador é agir nos pontos sensíveis, trazendo-os à luz. - Sigmund Freud",
    "A educação é a passagem do sombrio ao claro. - Allan Bloom",
    "A educação é a arte de ajudar a descobrir o que é possível. - Albert Einstein",
    "Educar é acender uma chama, não encher um recipiente. - Sócrates",
    "A verdadeira educação é aquela que extrai o melhor de si mesmo. - Mahatma Gandhi",
    "O professor tem que ser capaz de despertar alegria na expressão criativa e no conhecimento. - Albert Einstein"
]

if __name__ == '__main__':
    app.run(debug=True)
    