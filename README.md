# Chatbot Interativo com Questionário e Relatórios

Este é um projeto de um chatbot interativo construído com Streamlit, que permite aos usuários responderem a um questionário e fornece recursos adicionais, como autenticação de usuários, geração de relatórios e análise de dados. O aplicativo foi projetado para oferecer uma experiência única de interface de chat utilizando o componente st.chat_message.

## Funcionalidades Principais

1. Autenticação de Usuários

- Login seguro com verificação de credenciais.

- Registro de novos usuários.

- Acesso administrativo para visualizar relatórios.

2. Upload de Questionários

- Permite o upload de arquivos JSON contendo perguntas e opções.

- Valida a estrutura do JSON para evitar erros.

3. Exibição Interativa de Perguntas

- Utiliza o st.chat_message para exibir perguntas e capturar respostas do usuário em um formato de chat.

4. Geração de Relatórios

- Gera estatísticas sobre o desempenho dos usuários.

- Exibe gráficos de distribuição de pontuações.

- Mostra o histórico de respostas em uma tabela interativa.

5. Segurança

- Respostas criptografadas antes de serem armazenadas no banco de dados.

## Estrutura do Projeto

### Principais Arquivos

- app.py: Arquivo principal que executa o chatbot.

- quiz.db: Banco de dados SQLite utilizado para armazenar perguntas, respostas e usuários.

- encryption.key: Chave para criptografia de respostas.

1. Tabelas no Banco de Dados

- questions: Armazena as perguntas do questionário.

- id: Identificador único da pergunta.

- text: Texto da pergunta.

- type: Tipo de pergunta ("aberta", "verdadeiro_falso", "multipla_escolha").

- options: Opções de resposta (JSON).

- correct_answer: Resposta correta.

2. responses: Armazena as respostas dos usuários.

- id: Identificador único da resposta.

- user: Nome do usuário.

- score: Pontuação do usuário.

- total_questions: Total de perguntas do questionário.

- responses: Respostas do usuário (criptografadas).

- timestamp: Data e hora da resposta.

3. users: Armazena as credenciais dos usuários.

- username: Nome de usuário (chave primária).

- password: Senha do usuário.

## Configuração e Execução

### Requisitos

1. Python 3.8 ou superior

2. Bibliotecas:

- streamlit

- cryptography

- sqlite3 (nativo do Python)

- pandas

- matplotlib

## Instalação

1. Crie um ambiente virtual:

python -m venv venv

source venv/bin/activate  # No Windows: venv\Scripts\activate 

2. Instale as dependências:

pip install -r requirements.txt 

3. Execute o aplicativo:

streamlit run app.py

## Formato do Arquivo JSON

O arquivo JSON para o upload do questionário deve seguir este formato:

```json
{
  "perguntas": [
    {
      "id": 1,
      "texto": "Qual é a capital da França?",
      "tipo": "aberta",
      "resposta_correta": "Paris"
    },
    {
      "id": 2,
      "texto": "Quem pintou a 'Mona Lisa'?",
      "tipo": "aberta",
      "resposta_correta": "Leonardo Da Vinci"
    },
    {
      "id": 3,
      "texto": "Em que ano o homem pisou na Lua pela primeira vez?",
      "tipo": "aberta",
      "resposta_correta": "1969"
    },
    {
      "id": 4,
      "texto": "Qual é o resultado de 3 + 2?",
      "tipo": "aberta",
      "resposta_correta": "5"
    },
    {
      "id": 5,
      "texto": "Java é uma linguagem de programação.",
      "tipo": "verdadeiro_falso",
      "resposta_correta": "verdadeiro"
    },
    {
      "id": 6,
      "texto": "Qual é a maior cidade do Brasil?",
      "tipo": "multipla_escolha",
      "opcoes": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília"],
      "resposta_correta": "São Paulo"
    }
  ]
}

```


## Funções Principais

1. Login

- Usuário: Insira seu nome de usuário e senha para acessar.

- Registro: Registre um novo usuário diretamente na interface.

2. Questionário

- Perguntas exibidas em formato de chat.

- Avanço automático após o envio de cada resposta.

3. Estatísticas (Acesso Administrador)

- Visualize métricas de uso e desempenho.

- Exiba histórico de respostas e gráficos.

## Possíveis Melhorias Futuras

- Adicionar suporte a temas customizáveis.

- Implementar métodos de autenticação mais robustos, como OAuth.

- Permitir exportação de relatórios em diferentes formatos (CSV, Excel).

- Melhorar o design da interface com estilos mais personalizados.

## Contribuições

Contribuições são bem-vindas! Por favor, envie um pull request ou abra uma issue com sugestões e melhorias.
