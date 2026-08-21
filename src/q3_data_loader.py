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

import csv
import os

import psycopg2
from dotenv import load_dotenv

RAW_DIR = "data/raw"
TARGET_SCHEMA = "bronze"

# Tabelas usadas na validacao da Questao 3.2
VALIDATION_TABLES = ["customers", "orders", "order_items", "payments"]


def get_connection():
    load_dotenv()
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def get_csv_header(csv_path: str) -> list[str]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def load_csv_to_table(conn, csv_path: str, table_name: str) -> None:
    columns = get_csv_header(csv_path)
    col_list = ", ".join(columns)

    with conn.cursor() as cur:
        # Idempotencia: garante que reexecucoes nao dupliquem dados
        cur.execute(f"TRUNCATE TABLE {TARGET_SCHEMA}.{table_name};")

        with open(csv_path, "r", encoding="utf-8") as f:
            next(f)  # pula o header, ja usado em col_list
            copy_sql = (
                f"COPY {TARGET_SCHEMA}.{table_name} ({col_list}) "
                f"FROM STDIN WITH (FORMAT csv, NULL '')"
            )
            cur.copy_expert(copy_sql, f)

    conn.commit()


def load_all(conn, csv_dir: str) -> None:
    csv_files = sorted(f for f in os.listdir(csv_dir) if f.endswith(".csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em '{csv_dir}'")

    for csv_file in csv_files:
        table_name = os.path.splitext(csv_file)[0].strip().lower()
        csv_path = os.path.join(csv_dir, csv_file)
        try:
            load_csv_to_table(conn, csv_path, table_name)
            print(f"[ok] {table_name} carregada")
        except Exception as exc:
            conn.rollback()
            print(f"[erro] {table_name}: {exc}")


def validate_row_counts(conn) -> None:
    print("\n--- Validacao (Questao 3.2) ---")
    total = 0
    with conn.cursor() as cur:
        for table in VALIDATION_TABLES:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{table};")
            count = cur.fetchone()[0]
            total += count
            print(f"{table}: {count}")
    print(f"TOTAL (customers + orders + order_items + payments): {total}")


def main() -> None:
    conn = get_connection()
    try:
        load_all(conn, RAW_DIR)
        validate_row_counts(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
