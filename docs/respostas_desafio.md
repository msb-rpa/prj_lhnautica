# Questão 1 - EDA

## Premissas obrigatórias:

- Utilize apenas a tabela "orders"
- Não faça limpeza nem tratamento dos dados
- Apenas observe, agregue e descreva
- O código deve ser enviado em SQL

## Questão 1.1 - SQL

Código calculando:
- Quantidade total de linhas

```
total_linhas = 48998
```

- Intervalo de datas analisado (data mínima e máxima)

```
data_minima = 2020-01-01 01:19:28	
data_maxima = 2026-12-31 23:43:09
```

- Valor mínimo
```
valor_minimo = 32.62
```
- Valor máximo
```
valor_maximo = 127262.02
```
- Valor médio
```
valor_medio = 28704.992077227642
```

**Código SQL:**
```
SELECT
    COUNT(*) AS total_linhas,
    MIN(created_at) AS data_minima,
    MAX(created_at) AS data_maxima,
    MIN(total) AS valor_minimo,
    MAX(total) AS valor_maximo,
    AVG(total) AS valor_medio
FROM bronze.orders;
```

## Questão 1.2 - Validação

- Qual é o valor médio registrado na coluna "total"?

```
28704.992077227642
```

## Respostas da Questão 1.3 - Interpretação

Com base na análise exploratória realizada, escreva um breve diagnóstico sobre a confiabilidade da tabela orders para análises futuras. Comente sobre:

**Possíveis outliers em "total":**

```
Os valores variam de R$ 32,62 a R$ 127.262,02, uma faixa ampla, mas sem zeros ou negativos. 
Aplicando o método IQR (Intervalo Interquartílico), ver `q1_eda_sql_.sql`, foram identificados registros fora do limite superior (Q3 + 1,5×IQR), indicando possíveis outliers de alto valor. Não é possível confirmar se são erros ou pedidos legítimos de maior porte sem cruzar com outras tabelas.
```

**Qualidade dos dados (nulos ou inconsistências):**

```
`total` e `customer_id` não têm valores nulos. `salesperson_id` está vazio em quase metade dos registros, possivelmente porque pedidos do canal e-commerce não têm vendedor associado, mas isso não foi confirmado. Não foram observadas outras inconsistências óbvias.
```

**A tabela orders está pronta para análises ou exige tratamento prévio ou relacionamento com demais tabelas?**

```
A tabela está íntegra isoladamente (sem nulos/erros em `total`), mas não está pronta para responder perguntas de negócio sozinha: não é possível validar se o `total` bate com os itens do pedido, nem diferenciar pedidos válidos de cancelados/rascunho sem cruzar com `order_items`, `customers` e `payments`. Recomenda-se tratamento e relacionamento com essas tabelas antes de análises conclusivas.
```
