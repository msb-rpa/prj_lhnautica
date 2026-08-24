"""
Questao 2 - Gerador de Schema (DDL)

Le os CSVs de origem, infere o tipo de dado de cada coluna e gera os
arquivos SQL de criacao do banco, dos schemas e das tabelas (camada bronze).

Restricoes da questao:
- Apenas bibliotecas padrao do Python 3 (csv, os, re, zipfile)
- Banco de destino: PostgreSQL

Uso:
    python src/q2_schema_generator.py
"""

import csv
import os
import re
import zipfile

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------

ZIP_PATH = "data/raw/1-lh_nautical_csv.zip"
RAW_DIR = "data/raw"
DB_SQL_PATH = "sql/db.sql"
SCHEMAS_SQL_PATH = "sql/schemas.sql"
TABLES_SQL_PATH = "sql/tables.sql"
DB_NAME = "db_desafio"
TARGET_SCHEMA = "bronze"

INT_RE = re.compile(r"^-?\d+$")
FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")

INT32_MAX = 2_147_483_647


# ---------------------------------------------------------------------------
# Etapa 1: extracao do ZIP
# ---------------------------------------------------------------------------

def extract_zip(zip_path: str, dest_dir: str) -> None:
    if not os.path.exists(zip_path):
        print(f"[aviso] ZIP nao encontrado em '{zip_path}'. "
              f"Assumindo que os CSVs ja estao em '{dest_dir}'.")
        return

    os.makedirs(dest_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)

    print(f"[ok] CSVs extraidos em '{dest_dir}'")


# ---------------------------------------------------------------------------
# Etapa 2: inferencia de tipos
# ---------------------------------------------------------------------------

def infer_column_type(values: list[str]) -> str:
    """
    Ordem de checagem: INTEGER/BIGINT -> NUMERIC -> DATE -> TIMESTAMP -> TEXT
    Colunas identificadoras (zero a esquerda ou tamanho fixo) sao tratadas
    como TEXT, mesmo contendo apenas digitos (ex: CPF, CNPJ, codigo de barras).
    """

    non_empty = [v for v in values if v is not None and v.strip() != ""]

    if not non_empty:
        return "TEXT"

    if all(INT_RE.match(v) for v in non_empty):
        has_leading_zero = any(
            v.lstrip("-").startswith("0") and v.lstrip("-") != "0"
            for v in non_empty
        )
        fixed_length = len({len(v.lstrip("-")) for v in non_empty}) == 1

        if has_leading_zero or fixed_length:
            return "TEXT"

        max_abs = max(abs(int(v)) for v in non_empty)
        return "BIGINT" if max_abs > INT32_MAX else "INTEGER"

    if all(FLOAT_RE.match(v) for v in non_empty):
        return "NUMERIC"

    if all(TIMESTAMP_RE.match(v) for v in non_empty):
        return "TIMESTAMP"

    if all(DATE_RE.match(v) for v in non_empty):
        return "DATE"

    return "TEXT"


def infer_table_schema(csv_path: str) -> list[tuple[str, str]]:
    """Retorna lista de (nome_coluna, tipo_postgres) para um CSV."""

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        columns_values: dict[str, list[str]] = {col: [] for col in header}

        for row in reader:
            for col, val in zip(header, row):
                columns_values[col].append(val)

    return [(col, infer_column_type(vals)) for col, vals in columns_values.items()]


# ---------------------------------------------------------------------------
# Etapa 3: geracao dos arquivos SQL
# ---------------------------------------------------------------------------

def quote_ident(name: str) -> str:
    """Normaliza identificador (minusculo, sem espacos nas pontas)."""
    return name.strip().lower()


def write_db_sql() -> None:
    os.makedirs(os.path.dirname(DB_SQL_PATH), exist_ok=True)

    with open(DB_SQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- Questao 2 - Criacao da base de dados\n")
        f.write(f"CREATE DATABASE {DB_NAME};\n")

    print(f"[ok] {DB_SQL_PATH} gerado")


def write_schemas_sql() -> None:
    with open(SCHEMAS_SQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- Questao 2 - Criacao dos schemas (camadas da arquitetura medalhao)\n")

        for schema in ("bronze", "silver", "gold"):
            f.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n")

    print(f"[ok] {SCHEMAS_SQL_PATH} gerado")


def write_tables_sql(csv_dir: str) -> None:
    csv_files = sorted(f for f in os.listdir(csv_dir) if f.endswith(".csv"))

    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em '{csv_dir}'")

    with open(TABLES_SQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- Questao 2 - DDL das tabelas bronze (tipos inferidos a partir dos CSVs)\n\n")

        for csv_file in csv_files:
            table_name = quote_ident(os.path.splitext(csv_file)[0])
            csv_path = os.path.join(csv_dir, csv_file)

            schema = infer_table_schema(csv_path)

            f.write(f"CREATE TABLE {TARGET_SCHEMA}.{table_name} (\n")

            col_lines = [f"    {quote_ident(col)} {dtype}" for col, dtype in schema]

            # Colunas de auditoria, adicionadas a toda tabela bronze
            col_lines += [
                "    _source_file TEXT",
                "    _loaded_at TIMESTAMP",
                "    _line_number INTEGER",
            ]

            f.write(",\n".join(col_lines))
            f.write("\n);\n\n")

            print(f"[ok] {table_name}: {len(schema)} colunas mapeadas")

    print(f"[ok] {TABLES_SQL_PATH} gerado com {len(csv_files)} tabelas")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    extract_zip(ZIP_PATH, RAW_DIR)
    write_db_sql()
    write_schemas_sql()
    write_tables_sql(RAW_DIR)


if __name__ == "__main__":
    main()