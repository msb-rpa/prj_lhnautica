"""
Questao 3 - Carregamento dos dados (DML)

Regras da questao:
- Python 3, qualquer biblioteca necessaria (psycopg2 + python-dotenv)
- Carrega todos os CSVs respeitando o schema criado na Questao 2
- Sem tratamento de dados (nulos e caracteres especiais preservados)
- Idempotente: TRUNCATE antes de cada carga

Pre-requisitos:
- Tabelas ja criadas (sql/tables.sql executado)
- Arquivo .env na raiz do projeto com:
    DB_HOST=...
    DB_PORT=...
    DB_NAME=...
    DB_USER=...
    DB_PASSWORD=...

Uso:
    python src/q3_data_loader.py
"""

# --- Importacoes ---
import csv  # ler o cabecalho dos CSVs (nomes das colunas)
import os   # ler variaveis de ambiente e listar arquivos/pastas
import io         # cria um "arquivo em memoria" para montar as linhas com os campos extras
import datetime   # gera o timestamp de carga (_loaded_at)

import psycopg2          # biblioteca para conectar e executar comandos no PostgreSQL
from dotenv import load_dotenv  # le o arquivo .env e carrega as variaveis nele definidas

# --- Configuracao ---
RAW_DIR = "data/raw"        # pasta onde estao os CSVs a serem carregados
TARGET_SCHEMA = "bronze"    # schema (camada) onde as tabelas ja foram criadas na Q2

# Lista fixa de tabelas usadas na validacao pedida na Questao 3.2
# (soma de linhas de customers + orders + order_items + payments)
VALIDATION_TABLES = ["customers", "orders", "order_items", "payments"]


def get_connection():
    # Le o arquivo .env na raiz do projeto e injeta suas variaveis em os.environ
    load_dotenv()

    # Abre a conexao com o PostgreSQL usando as credenciais vindas do .env.
    # os.environ["NOME"] busca o valor da variavel de ambiente; se nao existir, gera erro
    # (isso e proposital: preferimos falhar cedo a rodar com credencial vazia).
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def get_csv_header(csv_path: str) -> list[str]:
    # Abre o CSV so para ler a primeira linha (cabecalho = nomes das colunas)
    with open(csv_path, newline="", encoding="utf-8") as f:
        return next(csv.reader(f))  # next() pega a primeira linha do "leitor" de CSV


def load_csv_to_table(conn, csv_path: str, table_name: str) -> None:
    # Descobre os nomes das colunas a partir do cabecalho do CSV.
    columns = get_csv_header(csv_path)

    # Adiciona as colunas de auditoria na lista de colunas do COPY,
    # pois elas nao existem no CSV e serao geradas por este script.
    col_list = ", ".join(columns + ["_source_file", "_loaded_at", "_line_number"])

    # cursor e o objeto usado para executar comandos SQL na conexao aberta.
    # "with conn.cursor() as cur" garante que o cursor sera fechado automaticamente ao final.
    with conn.cursor() as cur:
        # TRUNCATE apaga todos os dados da tabela (mas mantem a estrutura),
        # garantindo que rodar o script novamente nao duplique os dados (idempotencia).
        cur.execute(f"TRUNCATE TABLE {TARGET_SCHEMA}.{table_name};")

        # Abre o CSV novamente, agora para de fato ler e enviar os dados ao banco.
        # Nome do arquivo (sem o caminho da pasta), usado para preencher _source_file
        source_file = os.path.basename(csv_path)

        # Timestamp unico para toda a carga desta tabela (momento em que o script roda)
        loaded_at = datetime.datetime.now().isoformat()

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # pula a primeira linha (cabecalho)

            # Buffer em memoria: o COPY precisa receber os dados prontos,
            # mas o CSV original nao tem as colunas de auditoria.
            # Por isso montamos aqui uma copia de cada linha ja com os 3 campos extras.
            buffer = io.StringIO()
            writer = csv.writer(buffer)

            # enumerate(reader, start=1) numera cada linha de dados, comecando em 1
            for line_number, row in enumerate(reader, start=1):
                writer.writerow(row + [source_file, loaded_at, line_number])

            buffer.seek(0)  # volta o "cursor" do buffer para o inicio, para ser lido do zero

            copy_sql = (
                f"COPY {TARGET_SCHEMA}.{table_name} ({col_list}) "
                f"FROM STDIN WITH (FORMAT csv, NULL '')"
            )

            cur.copy_expert(copy_sql, buffer)

    # commit() confirma a transacao, gravando as alteracoes de forma definitiva no banco.
    conn.commit()


def load_all(conn, csv_dir: str) -> None:
    # Lista todos os arquivos ".csv" da pasta, em ordem alfabetica.
    csv_files = sorted(f for f in os.listdir(csv_dir) if f.endswith(".csv"))

    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em '{csv_dir}'")

    # Processa um arquivo CSV por vez.
    for csv_file in csv_files:
        # Nome da tabela = nome do arquivo sem a extensao ".csv", em minusculo.
        table_name = os.path.splitext(csv_file)[0].strip().lower()
        csv_path = os.path.join(csv_dir, csv_file)

        try:
            load_csv_to_table(conn, csv_path, table_name)
            print(f"[ok] {table_name} carregada")
        except Exception as exc:
            # Se der erro ao carregar uma tabela especifica, desfaz so aquela transacao (rollback)
            # e continua tentando carregar as demais tabelas, em vez de parar tudo.
            conn.rollback()
            print(f"[erro] {table_name}: {exc}")


def validate_row_counts(conn) -> None:
    print("\n--- Validacao (Questao 3.2) ---")
    total = 0  # acumulador da soma de linhas das 4 tabelas

    with conn.cursor() as cur:
        for table in VALIDATION_TABLES:
            # Executa um COUNT(*) para saber quantas linhas a tabela tem.
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{table};")

            # fetchone() pega o resultado da consulta (uma linha, uma coluna: a contagem).
            # [0] pega o primeiro (e unico) valor dessa linha.
            count = cur.fetchone()[0]

            total += count  # soma ao total acumulado
            print(f"{table}: {count}")

    print(f"TOTAL (customers + orders + order_items + payments): {total}")


def main() -> None:
    conn = get_connection()  # abre a conexao com o banco

    try:
        load_all(conn, RAW_DIR)       # carrega todos os CSVs nas respectivas tabelas
        validate_row_counts(conn)     # confere a contagem de linhas ao final
    finally:
        # O bloco "finally" sempre executa, mesmo se der erro no "try" acima,
        # garantindo que a conexao com o banco seja sempre fechada corretamente.
        conn.close()


# So executa main() quando o script e rodado diretamente (nao quando importado).
if __name__ == "__main__":
    main()