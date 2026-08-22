# Desafio LH Nautical

Projeto de engenharia de dados desenvolvido para o Desafio LH Nautical, simulando o cenário da empresa fictícia **LH Nautical** (varejo náutico). O objetivo é percorrer o ciclo completo de um pipeline de dados: da ingestão bruta até análises e modelos preditivos, seguindo os princípios da arquitetura medalhão (Bronze → Silver → Gold).

## Contexto

- **Empresa fictícia:** LH Nautical (lojas físicas, armazéns e e-commerce)
- **Período dos dados:** 2020-2026
- **Fonte:** 24 arquivos CSV com o schema relacional da empresa
- **Stakeholders:** Gabriel Santos (Tech Lead), Marina Costa (Negócios), Sr. Almir (Fundador)

Detalhes completos do contexto em [`docs/instrucoes_gerais_projeto.md`](docs/instrucoes_gerais_projeto.md).

## Stack

- Python 3.13+
- PostgreSQL 18 (Docker)
- Bibliotecas: stdlib (Q2), psycopg2 + python-dotenv

## Estrutura do projeto

```
prj_lhnautica_revisado/
├── data/raw/ # CSVs extraídos do ZIP de origem
├── docs/ # decisões técnicas e enunciados do desafio
├── sql/ # DDL (db.sql, schemas.sql, tables.sql) e queries
├── src/ # scripts Python de cada questão
└── output/ # resultados finais (CSVs, relatórios, dashboard)
```

## Arquitetura

Camada **Bronze** implementada: preserva o dado bruto dos CSVs, com tipos inferidos de forma permissiva (sem tratamento, sem PK/FK). Toda tabela Bronze inclui colunas de auditoria (`_source_file`, `_loaded_at`, `_line_number`) para rastreabilidade da ingestão. Camadas **Silver/Gold** (dado tratado e modelado) ficam documentadas como evolução futura da arquitetura.

## Ordem de Execução

Apesar da numeração do desafio, a ordem lógica de execução é:

1. **Q2** — Geração do schema (`schema.sql`)
2. **Q3** — Carregamento dos dados no PostgreSQL
3. **Q1** — EDA da tabela `orders`
4. **Q4** — Análise de clientes fiéis
5. **Q5** — Dimensão de calendário
6. **Q6** — Previsão de demanda
7. **Q7** — Sistema de recomendação

> Q2 e Q3 precisam vir primeiro pois criam a base de dados usada pelas demais análises.

## Progresso

| Questão | Descrição | Status |
|---|---|---|
| Q1 | EDA da tabela `orders` (SQL) | ✅ |
| Q2 | Geração do schema (DDL) a partir dos CSVs, com inferência de tipos em Python puro | ✅ |
| Q3 | Carga dos dados no PostgreSQL via `COPY` (psycopg2) | ✅ |
| Q4 | Análise de clientes fiéis | ⬜ |
| Q5 | Dimensão de calendário / vendas por dia da semana | ⬜ |
| Q6 | Previsão de demanda | ⬜ |
| Q7 | Sistema de recomendação | ⬜ |
| Dashboard | Consolidação de visualizações | ⬜ |

## Como executar

1. Extrair os CSVs e gerar o schema:
```bash
   python src/q2_schema_generator.py
```
2. Executar `sql/db.sql`, `sql/schemas.sql` e `sql/tables.sql` no PostgreSQL.
3. Configurar o `.env` (ver `.env.example`) com as credenciais de conexão.
4. Carregar os dados:
```bash
   python src/q3_data_loader.py
```

Decisões técnicas detalhadas (com justificativas) em [`docs/decisoes_tecnicas.md`](docs/decisoes_tecnicas.md).