import streamlit as st
import json
import string
import os
from datetime import datetime
import sqlite3
from cryptography.fernet import Fernet
import pandas as pd
import matplotlib.pyplot as plt

def generate_statistics():
    """
    Gera estatísticas e análises sobre as respostas armazenadas no banco de dados SQLite.
    """
    st.title("Relatórios e Estatísticas")

    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()

    c.execute("SELECT user, score, total_questions, timestamp FROM responses")
    data = c.fetchall()
    conn.close()

    if not data:
        st.warning("Ainda não há dados disponíveis para análise.")
        return

    df = pd.DataFrame(data, columns=["Usuário", "Pontuação", "Total de Perguntas", "Data e Hora"])

    total_users = df["Usuário"].nunique()
    avg_score = df["Pontuação"].mean()
    total_responses = len(df)

    st.subheader("📊 Métricas Gerais")
    st.write(f"**Número total de usuários:** {total_users}")
    st.write(f"**Pontuação média:** {avg_score:.2f}")
    st.write(f"**Total de questionários respondidos:** {total_responses}")

    st.subheader("📈 Distribuição de Pontuações")
    fig, ax = plt.subplots()
    df["Pontuação"].plot(kind="hist", bins=10, title="Distribuição de Pontuações", ax=ax)
    ax.set_xlabel("Pontuação")
    st.pyplot(fig)

    st.subheader("📋 Histórico de Respostas")
    st.dataframe(df)


def validate_json_structure(data, error_log="error_log.json"):
    """
    Valida a estrutura do JSON de perguntas, verifica tipos de dados e salva erros em um arquivo de log.
    """
    required_keys = {"texto", "tipo", "resposta_correta"}
    errors = []

    if not isinstance(data, dict) or "perguntas" not in data or not isinstance(data["perguntas"], list):
        errors.append("O arquivo JSON deve conter uma chave 'perguntas' com uma lista de perguntas.")
    else:
        for i, question in enumerate(data["perguntas"]):
            missing_keys = required_keys - question.keys()
            if missing_keys:
                errors.append(f"Pergunta {i + 1}: Chaves ausentes - {', '.join(missing_keys)}")

            if not isinstance(question.get("texto", ""), str):
                errors.append(f"Pergunta {i + 1}: O campo 'texto' deve ser uma string.")
            if not isinstance(question.get("tipo", ""), str):
                errors.append(f"Pergunta {i + 1}: O campo 'tipo' deve ser uma string.")
            if not isinstance(question.get("resposta_correta", ""), str):
                errors.append(f"Pergunta {i + 1}: O campo 'resposta_correta' deve ser uma string.")

            if question.get("tipo") == "multipla_escolha":
                if "opcoes" not in question or not isinstance(question["opcoes"], list):
                    errors.append(f"Pergunta {i + 1}: 'multipla_escolha' requer 'opcoes' do tipo lista.")

            for key in required_keys:
                if not question.get(key):
                    errors.append(f"Pergunta {i + 1}: O valor de '{key}' está vazio.")

    if errors:
        with open(error_log, "a") as log_file:
            json.dump({"errors": errors, "timestamp": str(datetime.now())}, log_file, indent=4)
        return False, errors

    return True, ["Arquivo JSON validado com sucesso!"]


def load_questions(uploaded_file):
    try:
        file_content = uploaded_file.read()
        data = json.loads(file_content)

        is_valid, messages = validate_json_structure(data)
        if not is_valid:
            st.error("Erros detectados no arquivo JSON. Verifique o log 'error_log.json' para mais detalhes.")
            for message in messages:
                st.error(message)
            return []

        st.success("Arquivo JSON validado com sucesso!")
        return data.get("perguntas", [])

    except json.JSONDecodeError:
        st.error("Erro: O arquivo não está no formato JSON válido. Verifique a sintaxe.")
        return []
    except Exception as e:
        st.error(f"Erro inesperado ao carregar o arquivo JSON: {e}")
        return []

def normalize_answer(answer):
    translator = str.maketrans('', '', string.punctuation)
    return answer.translate(translator).strip().lower()

def evaluate_response(user_answers, correct_answers):
    score = 0
    for question_id, user_answer in user_answers.items():
        correct_answer = normalize_answer(correct_answers.get(question_id, ""))
        user_answer = normalize_answer(user_answer)
        if user_answer == correct_answer:
            score += 1
    return score

def save_results(results):
    st.download_button(
        label="Baixar Resultados",
        data=json.dumps(results, indent=4),
        file_name="resultados.json",
        mime="application/json",
    )

def log_user_responses(user_data, log_file="logs.json"):
    """
    Registra os dados do usuário em um arquivo de log (logs.json).
    Cria o arquivo se não existir.
    """
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                logs = json.load(file)
        else:
            logs = []  
            
        logs.append(user_data)
        
        with open(log_file, "w") as file:
            json.dump(logs, file, indent=4)
    except Exception as e:
        st.error(f"Erro ao registrar o log: {e}")

def init_db():
    """
    Inicializa o banco de dados SQLite, criando tabelas se necessário.
    """
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            score INTEGER,
            total_questions INTEGER,
            responses TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_questions_to_db(questions):
    """
    Salva perguntas no banco de dados SQLite.
    """
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    
    for question in questions:
        options = json.dumps(question.get("opcoes", None))
        c.execute('''
            INSERT INTO questions (text, type, options, correct_answer)
            VALUES (?, ?, ?, ?)
        ''', (question["texto"], question["tipo"], options, question["resposta_correta"]))
    
    conn.commit()
    conn.close()

def save_responses_to_db(user, score, total_questions, responses):
    """
    Salva respostas e resultados no banco de dados SQLite.
    Criptografa as respostas antes de armazená-las.
    """
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()

    encrypted_responses = {
        question_id: encrypt_response(response)
        for question_id, response in responses.items()
    }

    responses_json = json.dumps(encrypted_responses)
    c.execute('''
        INSERT INTO responses (user, score, total_questions, responses)
        VALUES (?, ?, ?, ?)
    ''', (user, score, total_questions, responses_json))

    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """
    Autentica um usuário verificando suas credenciais no banco de dados.
    """
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == password:
        return True
    return False

def register_user(username, password):
    """
    Registra um novo usuário no banco de dados.
    """
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

init_db()

if "questions" not in st.session_state:
    st.session_state["questions"] = []
if "current_question" not in st.session_state:
    st.session_state["current_question"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = {}
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "completed" not in st.session_state:
    st.session_state["completed"] = False
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def load_encryption_key():
    """
    Carrega a chave de criptografia de um arquivo ou cria uma nova.
    """
    key_file = "encryption.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        return key

encryption_key = load_encryption_key()
fernet = Fernet(encryption_key)

def encrypt_response(response):
    """
    Criptografa uma resposta usando Fernet.
    """
    return fernet.encrypt(response.encode()).decode()

def decrypt_response(encrypted_response):
    """
    Descriptografa uma resposta criptografada.
    """
    return fernet.decrypt(encrypted_response.encode()).decode()

def login_screen():
    st.title("Login do Chatbot")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos. Por favor, tente novamente.")

    if st.button("Registrar"):
        if register_user(username, password):
            st.success("Usuário registrado com sucesso. Agora você pode fazer login.")
        else:
            st.error("Nome de usuário já existe. Escolha outro.")

def chatbot_app():
    if not st.session_state.get("authenticated", False):
        login_screen()
        return

    if st.session_state["username"] == "admin":
        st.sidebar.title("Administração")
        if st.sidebar.button("Ver Estatísticas"):
            generate_statistics()
            return

    if not st.session_state.get("questions"):
        st.title("Upload do Questionário")
        uploaded_file = st.file_uploader("Envie o arquivo JSON do questionário", type="json")
        
        if uploaded_file:
            questions = load_questions(uploaded_file)
            if questions:
                st.session_state["questions"] = questions
                st.success("Perguntas carregadas com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao carregar as perguntas.")
        else:
            st.info("Por favor, envie um arquivo JSON para continuar.")
            return  
        
    if st.session_state["questions"] and not st.session_state["completed"]:
        questions = st.session_state["questions"]
        current_question = st.session_state["current_question"]
        question = questions[current_question]

        with st.chat_message("assistant"):
            st.write(f"**Pergunta {current_question + 1}:** {question['texto']}")

        with st.chat_message("user"):
            response = None
            widget_key = f"input_{current_question}"  
            if question["tipo"] == "aberta":
                response = st.text_input("Sua resposta:", key=widget_key)
            elif question["tipo"] == "verdadeiro_falso":
                response = st.radio("Escolha uma opção:", ["verdadeiro", "falso"], key=widget_key)
            elif question["tipo"] == "multipla_escolha":
                response = st.selectbox("Escolha uma opção:", question["opcoes"], key=widget_key)
            else:
                st.error("Tipo de pergunta desconhecido.")
                return
            
        if response and st.button("Enviar Resposta"):
            st.session_state["responses"][current_question] = normalize_answer(response)

            if current_question + 1 < len(questions):
                st.session_state["current_question"] += 1
                st.rerun()
            else:
                st.session_state["completed"] = True
                st.rerun()

    if st.session_state["completed"]:
        with st.chat_message("assistant"):
            st.success("Você concluiu o questionário!")
            correct_answers = {i: q["resposta_correta"] for i, q in enumerate(st.session_state["questions"])}
            st.session_state["score"] = evaluate_response(st.session_state["responses"], correct_answers)
            st.write(f"**Pontuação final:** {st.session_state['score']} / {len(st.session_state['questions'])}")

        save_responses_to_db(st.session_state["username"], st.session_state["score"], len(st.session_state["questions"]), st.session_state["responses"])
        results = {
            "score": st.session_state["score"],
            "responses": st.session_state["responses"],
            "total_questions": len(st.session_state["questions"]),
        }
        save_results(results)

        if st.button("Reiniciar"):
            username = st.session_state["username"]
            st.session_state.clear()
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()

if __name__ == "__main__":
    chatbot_app()
