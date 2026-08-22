"""
Questao 2 - Gerador de Schema (DDL)

Regras da questao:
- Apenas bibliotecas padrao do Python 3 (csv, os, zipfile, re, datetime)
- Le todos os CSVs e gera um schema.sql com CREATE TABLE para cada um
- Banco de destino: PostgreSQL
- Camada de destino: bronze (dado bruto, tipos inferidos de forma permissiva)

Uso:
    python src/q2_schema_generator.py
"""

# --- Importacoes: todas fazem parte da biblioteca padrao do Python (exigencia da Q2) ---
import csv      # ler arquivos CSV linha por linha, sem precisar interpretar o texto na mao
import os       # manipular caminhos de arquivos/pastas e listar diretorios
import re       # trabalhar com expressoes regulares (padroes de texto), usado na inferencia de tipo
import zipfile  # abrir e extrair arquivos .zip

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------
# Constantes (valores fixos) usadas em varios pontos do script.
# Centralizar aqui facilita alterar caminhos/nomes sem procurar no meio do codigo.

ZIP_PATH = "data/raw/1-lh_nautical_csv.zip"  # onde esta o zip original com os CSVs
RAW_DIR = "data/raw"                          # pasta onde os CSVs extraidos ficarao
DB_SQL_PATH = "sql/db.sql"                    # arquivo de saida: comando para criar o banco
SCHEMAS_SQL_PATH = "sql/schemas.sql"          # arquivo de saida: comandos para criar os schemas (camadas)
TABLES_SQL_PATH = "sql/tables.sql"            # arquivo de saida: comandos CREATE TABLE (uma por CSV)
DB_NAME = "db_desafio"                        # nome do banco de dados a ser criado
TARGET_SCHEMA = "bronze"                      # schema (camada) onde as tabelas serao criadas

# Expressoes regulares (re.compile) definem "padroes de texto" que serao testados
# contra cada valor da coluna, para decidir o tipo de dado mais adequado.

INT_RE = re.compile(r"^-?\d+$")
# ^-?\d+$ -> comeca (^) com um sinal de menos opcional (-?),
# seguido de um ou mais digitos (\d+), e termina ($) ali. Ex: "123", "-45"

FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
# Igual ao de cima, mas exige um ponto decimal no meio. Ex: "12.5", "-3.0"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Data no formato AAAA-MM-DD, ex: "2024-01-31"

TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
# Data + hora, separadas por espaco ou "T", ex: "2024-01-31 10:00:00" ou "2024-01-31T10:00:00"

# Limite maximo do tipo INTEGER no PostgreSQL (2^31 - 1).
# Numeros maiores que isso precisam ser BIGINT, senao o banco recusa o dado.
INT32_MAX = 2_147_483_647


# ---------------------------------------------------------------------------
# Etapa 1: extracao do ZIP
# ---------------------------------------------------------------------------

def extract_zip(zip_path: str, dest_dir: str) -> None:
    # Se o arquivo zip nao existir no caminho esperado, avisa e segue em frente
    # (assumindo que os CSVs ja foram extraidos manualmente antes).
    if not os.path.exists(zip_path):
        print(f"[aviso] ZIP nao encontrado em '{zip_path}'. "
              f"Assumindo que os CSVs ja estao em '{dest_dir}'.")
        return  # encerra a funcao aqui, sem tentar extrair

    # Garante que a pasta de destino existe; se ja existir, nao faz nada (exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)

    # Abre o arquivo .zip em modo leitura ("r")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)  # extrai todo o conteudo do zip para a pasta destino

    print(f"[ok] CSVs extraidos em '{dest_dir}'")


# ---------------------------------------------------------------------------
# Etapa 2: inferencia de tipos (regras simples, conforme decisoes_tecnicas.md)
# ---------------------------------------------------------------------------

def infer_column_type(values: list[str]) -> str:
    """
    Ordem de checagem: INTEGER/BIGINT -> NUMERIC -> DATE -> TIMESTAMP -> TEXT
    Regra de seguranca: qualquer valor fora do padrao -> cai para TEXT.
    Valores vazios sao ignorados na inferencia (nao definem o tipo).
    """

    # Remove valores vazios/nulos da lista antes de analisar.
    # v.strip() remove espacos em branco; se sobrar string vazia, e considerado "sem valor".
    non_empty = [v for v in values if v is not None and v.strip() != ""]

    # Se a coluna inteira estiver vazia, nao ha como inferir tipo -> assume TEXT por seguranca.
    if not non_empty:
        return "TEXT"

    # --- Teste 1: a coluna parece ser um numero inteiro? ---
    # all(...) so retorna True se TODOS os valores da lista casarem com o padrao INT_RE.
    if all(INT_RE.match(v) for v in non_empty):

        # has_leading_zero: verifica se algum valor comeca com "0" (zero a esquerda),
        # ignorando o sinal de "-" antes de checar.
        # Isso e importante porque numeros "de verdade" nao tem zero a esquerda (ex: 007 nao existe),
        # mas identificadores como CPF podem ter (ex: "00123456789").
        has_leading_zero = any(
            v.lstrip("-").startswith("0") and v.lstrip("-") != "0"
            for v in non_empty
        )

        # fixed_length: verifica se TODOS os valores tem o mesmo tamanho (mesma quantidade de digitos).
        # Isso e caracteristico de identificadores (CPF sempre 11 digitos, CNPJ sempre 14, etc.),
        # diferente de quantidades/contagens, que variam de tamanho.
        # {len(...) for v in non_empty} cria um "set" (conjunto) com os tamanhos encontrados;
        # se o conjunto tiver so 1 elemento, e porque todos os valores tem o mesmo tamanho.
        fixed_length = len({len(v.lstrip("-")) for v in non_empty}) == 1

        # Se caiu em qualquer uma das duas condicoes acima, tratamos como identificador,
        # nao como numero -> tipo TEXT (preserva zeros a esquerda e evita operacoes matematicas indevidas).
        if has_leading_zero or fixed_length:
            return "TEXT"

        # Se passou pelas checagens acima, e realmente um numero inteiro.
        # Verificamos o maior valor absoluto para decidir entre INTEGER e BIGINT.
        max_abs = max(abs(int(v)) for v in non_empty)
        return "BIGINT" if max_abs > INT32_MAX else "INTEGER"

    # --- Teste 2: a coluna parece ser um numero decimal? ---
    if all(FLOAT_RE.match(v) for v in non_empty):
        return "NUMERIC"

    # --- Teste 3: a coluna parece ser data+hora (timestamp)? ---
    # Este teste vem antes do de DATE porque um timestamp comeca igual a uma data,
    # entao precisamos checar o padrao mais especifico primeiro.
    if all(TIMESTAMP_RE.match(v) for v in non_empty):
        return "TIMESTAMP"

    # --- Teste 4: a coluna parece ser apenas uma data? ---
    if all(DATE_RE.match(v) for v in non_empty):
        return "DATE"

    # --- Se nao se encaixou em nenhum padrao acima, e tratada como texto livre. ---
    return "TEXT"


def infer_table_schema(csv_path: str) -> list[tuple[str, str]]:
    """Retorna lista de (nome_coluna, tipo_postgres) para um CSV."""

    # Abre o CSV em modo leitura. newline="" evita problemas de quebra de linha no Windows.
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)          # cria um "leitor" que devolve cada linha como uma lista de valores
        header = next(reader)           # le a primeira linha (cabecalho = nomes das colunas)

        # Cria um dicionario onde cada coluna comeca com uma lista vazia,
        # que sera preenchida com todos os valores daquela coluna.
        columns_values: dict[str, list[str]] = {col: [] for col in header}

        # Percorre o restante das linhas do CSV (dados, sem o cabecalho)
        for row in reader:
            # zip(header, row) junta cada nome de coluna com o valor correspondente na linha
            for col, val in zip(header, row):
                columns_values[col].append(val)  # guarda o valor na lista da respectiva coluna

    # Para cada coluna, chama infer_column_type() passando todos os valores coletados,
    # e monta uma lista de tuplas (nome_da_coluna, tipo_inferido).
    return [(col, infer_column_type(vals)) for col, vals in columns_values.items()]


# ---------------------------------------------------------------------------
# Etapa 3: geracao dos arquivos SQL
# ---------------------------------------------------------------------------

def quote_ident(name: str) -> str:
    """Identificador seguro (minusculo, sem caracteres especiais)."""
    # .strip() remove espacos nas pontas; .lower() converte para minusculo
    # (Postgres trata nomes sem aspas como minusculos por padrao, entao padronizamos aqui).
    return name.strip().lower()


def write_db_sql() -> None:
    # Garante que a pasta "sql/" existe antes de tentar criar o arquivo dentro dela.
    os.makedirs(os.path.dirname(DB_SQL_PATH), exist_ok=True)

    # Abre (ou cria) o arquivo db.sql em modo escrita ("w"), sobrescrevendo se ja existir.
    with open(DB_SQL_PATH, "w", encoding="utf-8") as f:
        f.write(f"-- Questao 2 - Criacao da base de dados\n")
        f.write(f"CREATE DATABASE {DB_NAME};\n")  # comando SQL para criar o banco

    print(f"[ok] {DB_SQL_PATH} gerado")


def write_schemas_sql() -> None:
    with open(SCHEMAS_SQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- Questao 2 - Criacao dos schemas (camadas da arquitetura medalhao)\n")

        # Cria um comando CREATE SCHEMA para cada uma das 3 camadas da arquitetura medalhao.
        # IF NOT EXISTS evita erro caso o schema ja exista (idempotencia).
        for schema in ("bronze", "silver", "gold"):
            f.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n")

    print(f"[ok] {SCHEMAS_SQL_PATH} gerado")


def write_tables_sql(csv_dir: str) -> None:
    # Lista todos os arquivos da pasta que terminam em ".csv", em ordem alfabetica (sorted).
    csv_files = sorted(f for f in os.listdir(csv_dir) if f.endswith(".csv"))

    # Se nao houver nenhum CSV, nao ha o que processar -> interrompe com erro claro.
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em '{csv_dir}'")

    with open(TABLES_SQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- Questao 2 - DDL das tabelas bronze (tipos inferidos a partir dos CSVs)\n\n")

        # Para cada CSV encontrado, gera um bloco CREATE TABLE correspondente.
        for csv_file in csv_files:
            # Remove a extensao ".csv" do nome do arquivo para usar como nome da tabela.
            table_name = quote_ident(os.path.splitext(csv_file)[0])
            csv_path = os.path.join(csv_dir, csv_file)  # caminho completo do arquivo

            # Chama a funcao que le o CSV e devolve (coluna, tipo) para cada coluna.
            schema = infer_table_schema(csv_path)

            # Escreve o inicio do comando CREATE TABLE, indicando o schema (bronze) e o nome da tabela.
            f.write(f"CREATE TABLE {TARGET_SCHEMA}.{table_name} (\n")

            # Monta uma linha para cada coluna, no formato "    nome_coluna TIPO"
            # # col_lines = [f"    {quote_ident(col)} {dtype}" for col, dtype in schema]
            col_lines = [f"    {quote_ident(col)} {dtype}" for col, dtype in schema]

            # Colunas de auditoria (metadados de ingestão), adicionadas a toda tabela Bronze
            # para rastrear a origem e o momento da carga de cada registro.
            col_lines += [
                "    _source_file TEXT",     # nome do arquivo CSV de origem
                "    _loaded_at TIMESTAMP",  # data/hora em que o registro foi carregado
                "    _line_number INTEGER",  # número da linha no CSV original (rastreabilidade)
            ]

            # Junta todas as linhas de coluna separadas por vírgula e quebra de linha
            f.write(",\n".join(col_lines))
            f.write("\n);\n\n")  # fecha o parenteses do CREATE TABLE e pula duas linhas

            print(f"[ok] {table_name}: {len(schema)} colunas mapeadas")

    print(f"[ok] {TABLES_SQL_PATH} gerado com {len(csv_files)} tabelas")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Ordem de execucao do script, passo a passo:
    extract_zip(ZIP_PATH, RAW_DIR)   # 1. extrai os CSVs do zip (se necessario)
    write_db_sql()                   # 2. gera o comando de criacao do banco
    write_schemas_sql()               # 3. gera os comandos de criacao dos schemas (bronze/silver/gold)
    write_tables_sql(RAW_DIR)         # 4. gera os comandos CREATE TABLE, um para cada CSV


# Este bloco so executa main() quando o arquivo e rodado diretamente
# (ex: "python q2_schema_generator.py"), e nao quando e importado por outro script.
if __name__ == "__main__":
    main()
