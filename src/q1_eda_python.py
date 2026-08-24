"""
EDA complementar - orders.csv (Python puro, stdlib apenas)
Bibliotecas: csv, datetime, statistics, collections

Observação: a Questão 1 exige entrega em SQL. Este script é um
complemento/validação cruzada, não substitui o SQL entregável.
"""

import csv
import datetime
import statistics
from collections import Counter, defaultdict

CSV_PATH = "data/raw/orders.csv"
DATA_INICIO_OPERACAO = datetime.datetime(2020, 1, 1)
DATAS_EPOCA = {"1970-01-01", "0001-01-01"}
STATUS_FINALIZADOS = {"paid", "cancelled"}


def parse_dt(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    rows = load_rows(CSV_PATH)
    total_registros = len(rows)
    colunas = rows[0].keys() if rows else []

    print(f"=== 1. Total de registros: {total_registros} ===\n")

    # --- 2. Nulos/vazios por coluna ---
    print("=== 2. Nulos/vazios por coluna ===")
    nulos_por_coluna = {}
    for col in colunas:
        qtd = sum(1 for r in rows if not r[col] or r[col].strip() == "")
        nulos_por_coluna[col] = qtd
        print(f"{col}: {qtd}")
    print()

    # --- 3. Valores únicos por coluna ---
    print("=== 3. Valores únicos por coluna ===")
    for col in colunas:
        qtd = len(set(r[col] for r in rows))
        print(f"{col}: {qtd}")
    print()

    # --- 4. Duplicidade de id / order_number ---
    print("=== 4. Duplicidade id / order_number ===")
    for campo in ("id", "order_number"):
        contagem = Counter(r[campo] for r in rows)
        duplicados = {k: v for k, v in contagem.items() if v > 1}
        print(f"{campo} duplicados: {duplicados if duplicados else 'nenhum'}")
    print()

    # --- 5. Valores distintos em status ---
    print("=== 5. Distribuição de status ===")
    status_count = Counter(r["status"] for r in rows)
    for status, qtd in status_count.most_common():
        print(f"{status}: {qtd}")
    print()

    # --- 6. Contagem por channel e location_id ---
    print("=== 6. Contagem por channel ===")
    for ch, qtd in Counter(r["channel"] for r in rows).most_common():
        print(f"{ch}: {qtd}")

    print("\n=== 6b. Contagem por location_id ===")
    for loc, qtd in Counter(r["location_id"] for r in rows).most_common():
        print(f"{loc}: {qtd}")
    print()

    # --- 7. Consistência channel x salesperson_id ---
    print("=== 7. channel x salesperson_id ===")
    channel_sales = defaultdict(lambda: {"com_vendedor": 0, "sem_vendedor": 0})
    for r in rows:
        key = "sem_vendedor" if not r["salesperson_id"].strip() else "com_vendedor"
        channel_sales[r["channel"]][key] += 1
    for ch, dados in channel_sales.items():
        print(f"{ch}: {dados}")
    print()

    # --- 8. Nulos em customer_id e location_id ---
    print("=== 8. Nulos em chaves de relacionamento ===")
    print(f"customer_id nulo/vazio: {nulos_por_coluna.get('customer_id', 0)}")
    print(f"location_id nulo/vazio: {nulos_por_coluna.get('location_id', 0)}")
    print()

    # --- 9. Positivos/negativos/zero em subtotal, discount_amount, total ---
    print("=== 9. Sinal de subtotal, discount_amount, total ===")
    for campo in ("subtotal", "discount_amount", "total"):
        neg = pos = zero = 0
        for r in rows:
            try:
                v = float(r[campo])
            except (ValueError, TypeError):
                continue
            if v < 0:
                neg += 1
            elif v == 0:
                zero += 1
            else:
                pos += 1
        print(f"{campo} -> negativos: {neg}, zerados: {zero}, positivos: {pos}")
    print()

    # --- 10. discount_amount > subtotal ---
    print("=== 10. discount_amount > subtotal (total ficaria negativo) ===")
    casos = [
        r for r in rows
        if float(r["subtotal"] or 0) < float(r["discount_amount"] or 0)
    ]
    print(f"Casos encontrados: {len(casos)}")
    for r in casos[:5]:
        print(f"  id={r['id']} subtotal={r['subtotal']} discount={r['discount_amount']}")
    print()

    # --- 11. subtotal - discount_amount == total ---
    print("=== 11. subtotal - discount_amount <> total ===")
    divergentes = []
    for r in rows:
        try:
            sub = float(r["subtotal"])
            desc = float(r["discount_amount"])
            tot = float(r["total"])
        except (ValueError, TypeError):
            continue
        if round(sub - desc, 2) != round(tot, 2):
            divergentes.append(r)
    print(f"Casos divergentes: {len(divergentes)}")
    for r in divergentes[:5]:
        print(f"  id={r['id']} subtotal={r['subtotal']} discount={r['discount_amount']} total={r['total']}")
    print()

    # --- 12. total = 0 ---
    print("=== 12. Pedidos com total = 0 ===")
    zerados = [r for r in rows if float(r["total"] or -1) == 0]
    print(f"Quantidade: {len(zerados)}")
    print()

    # --- 13. Outliers via IQR (total) ---
    print("=== 13. Outliers em total (IQR) ===")
    valores_total = sorted(float(r["total"]) for r in rows if r["total"])
    q1 = statistics.quantiles(valores_total, n=4)[0]
    q3 = statistics.quantiles(valores_total, n=4)[2]
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    outliers = [v for v in valores_total if v < lim_inf or v > lim_sup]
    print(f"Q1={q1:.2f} Q3={q3:.2f} IQR={iqr:.2f}")
    print(f"Limite inferior={lim_inf:.2f} | Limite superior={lim_sup:.2f}")
    print(f"Outliers encontrados: {len(outliers)}")
    print()

    # --- 14. Datas: parse e validações ---
    print("=== 14. Validações de datas (placed_at, created_at, updated_at) ===")
    agora = datetime.datetime.now()

    nulos_placed = nulos_created = nulos_updated = 0
    futuros = []
    inversoes = []
    epoca_ou_antigas = []
    latencia_negativa = []
    latencia_extrema = []
    finalizados_sem_etapa = []
    timestamps_placed = Counter()

    for r in rows:
        placed = parse_dt(r["placed_at"])
        created = parse_dt(r["created_at"])
        updated = parse_dt(r["updated_at"])

        if not r["placed_at"]:
            nulos_placed += 1
        if not r["created_at"]:
            nulos_created += 1
        if not r["updated_at"]:
            nulos_updated += 1

        # datas futuras
        if placed and placed > agora:
            futuros.append(("placed_at", r["id"]))
        if created and created > agora:
            futuros.append(("created_at", r["id"]))
        if updated and updated > agora:
            futuros.append(("updated_at", r["id"]))

        # inversões cronológicas
        if created and updated and created > updated:
            inversoes.append(("created>updated", r["id"]))
        if placed and created and placed > created:
            inversoes.append(("placed>created", r["id"]))
        if placed and updated and placed > updated:
            inversoes.append(("placed>updated", r["id"]))

        # datas de época / antigas
        for campo, dt in (("placed_at", placed), ("created_at", created), ("updated_at", updated)):
            if dt and (dt < DATA_INICIO_OPERACAO or r[campo][:10] in DATAS_EPOCA):
                epoca_ou_antigas.append((campo, r["id"], r[campo]))

        # latência negativa / extrema
        if placed and created:
            delta = created - placed
            if delta.total_seconds() < 0:
                latencia_negativa.append(r["id"])
            elif delta.days > 30:
                latencia_extrema.append((r["id"], delta.days))

        # finalizados sem etapa intermediária
        if r["status"] in STATUS_FINALIZADOS and created and updated and created == updated:
            finalizados_sem_etapa.append(r["id"])

        # timestamps idênticos (placed_at)
        if r["placed_at"]:
            timestamps_placed[r["placed_at"]] += 1

    print(f"Nulos -> placed_at: {nulos_placed}, created_at: {nulos_created}, updated_at: {nulos_updated}")
    print(f"Datas futuras: {len(futuros)}")
    print(f"Inversões cronológicas: {len(inversoes)}")
    print(f"Datas de época/antigas (<2020): {len(epoca_ou_antigas)}")
    print(f"Latência negativa (created < placed): {len(latencia_negativa)}")
    print(f"Latência extrema (>30 dias): {len(latencia_extrema)}")
    print(f"Finalizados (paid/cancelled) sem etapa intermediária: {len(finalizados_sem_etapa)}")

    duplicados_placed = {k: v for k, v in timestamps_placed.items() if v > 1}
    print(f"Timestamps placed_at duplicados: {len(duplicados_placed)}")


if __name__ == "__main__":
    main()