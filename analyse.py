"""Analyse hors ligne du groupe B : traces conservées, SQL et contrôle CSV."""
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import sandbox_sqlite

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data/boutique.sqlite'
MODELS = [
    ('groq', 'openai/gpt-oss-120b'),
    ('groq', 'openai/gpt-oss-20b'),
    ('openrouter', 'cohere/north-mini-code:free'),
    ('groq', 'qwen/qwen3.8-27b'),
    ('openrouter', 'dots-studio/dots-3-note-preview:free'),
]
PANEL = [MODELS[0], MODELS[2], MODELS[3]]
CASES = [f'C{i:02}' for i in range(1, 21)]


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_vote():
    spec = importlib.util.spec_from_file_location('td2_skeleton', ROOT / 'skeleton-multi-llm-en.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def latest_rows(rows):
    """Dernière ligne CSV par cellule, conformément à atelier-vote.py."""
    latest = {}
    for record, row in enumerate(rows, 1):
        require(row['nature'] == 'real', 'Un seul lot réel est attendu.')
        key = (row['provider'], row['model_requested'], row['case_id'])
        previous = latest.get(key)
        if previous:
            require(row['date_utc'] >= previous['date_utc'], 'Ordre chronologique incohérent.')
            require(row['question'] == previous['question'] and
                    row['prompt_sha256'] == previous['prompt_sha256'], 'Expériences mélangées.')
        latest[key] = {**row, 'csv_record': record}
    require(set(latest) == {(p, m, c) for p, m in MODELS for c in CASES},
            'Il faut exactement les 100 cellules des cinq modèles.')
    return latest


def proposals_for(latest, case, panel):
    proposals = []
    for provider, model in panel:
        row = latest.get((provider, model, case), {})
        executed = row.get('verdict') in {'correct', 'incorrect'} and row.get('value', '') != ''
        proposals.append(SimpleNamespace(provider=provider, model_requested=model,
                         value=int(row['value']) if executed else None,
                         verdict='executed' if executed else 'error'))
    return proposals


def shared_wrong_values(latest, refs):
    """Cherche des valeurs erronées identiques, pas une majorité d'erreurs différentes."""
    found = []
    for case in CASES:
        groups = defaultdict(list)
        for provider, model in MODELS:
            row = latest[provider, model, case]
            if row['verdict'] == 'incorrect':
                value = int(row['value'])
                require(value != refs[case], 'Verdict incorrect incompatible avec la référence.')
                groups[value].append(f'{provider}:{model}')
        for value, models in sorted(groups.items()):
            if len(models) >= 2:
                found.append(dict(case_id=case, value=value, reference=refs[case], models=models))
    return found


def sql_result(sql, max_rows=1000):
    result = sandbox_sqlite.execute_query(DB, sql, max_rows=max_rows)
    require(result['ok'], f"Échec SQL : {result['reason']} / {result['detail']}")
    return result


def age_on(birth, day):
    return day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))


def independent_csv():
    """Aucun SQL : âge révolu en Python, jointures par dictionnaires, entiers."""
    day = date(2026, 9, 25)
    customers = {r['customer_id']: r for r in read_csv(ROOT / 'data/customers.csv')}
    prices = {r['product_id']: int(r['price']) for r in read_csv(ROOT / 'data/product.csv')}
    totals, counts = Counter(), Counter()
    lines = []
    for order in read_csv(ROOT / 'data/orders.csv'):
        customer = customers[order['customer_id']]
        if age_on(date.fromisoformat(customer['birth_date']), day) == 25:
            amount = int(order['quantity_product']) * prices[order['product_id']]
            totals[order['customer_id']] += amount
            counts[order['customer_id']] += 1
            lines.append({**order, 'birth_date': customer['birth_date'], 'amount_cents': amount})
    customers_out = [dict(customer_id=c, birth_date=customers[c]['birth_date'],
                         order_lines=counts[c], revenue_cents=totals[c]) for c in sorted(totals)]
    return customers_out, lines


def verify_inputs():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    require(sha256(DB) == manifest['sqlite_file_sha256'], 'Base différente de la base officielle.')
    for name, digest in manifest['csv_sha256'].items():
        require(sha256(ROOT / 'data' / name) == digest, f'CSV modifié : {name}')
    provenance = json.loads((ROOT / 'sources/provenance.json').read_text(encoding='utf-8'))
    for item in provenance['files']:
        require(sha256(ROOT / item['path']) == item['sha256'], f"Source modifiée : {item['path']}")


def main():
    verify_inputs()
    evidence = ROOT / 'evidence'
    evidence.mkdir(exist_ok=True)
    rows = read_csv(ROOT / 'traces-td1.csv')
    references = read_csv(ROOT / 'reference-td1.csv')
    refs = {r['case_id']: int(r['revenue_cents']) for r in references}
    require(set(refs) == set(CASES) and len(references) == 20, 'Références incomplètes.')
    latest = latest_rows(rows)
    final_rows = [latest[p, m, c] for c in CASES for p, m in MODELS]
    write_csv(evidence / 'final-100-cells.csv', final_rows)
    candidates = shared_wrong_values(latest, refs)
    write_json(evidence / 'shared-wrong-values.json', candidates)
    require(any(c['case_id'] == 'C02' and c['value'] == 0 for c in candidates), 'C02 absent.')

    # Rejouer toutes les requêtes exécutées : aucune nouvelle inférence de modèle.
    replays = []
    for number, row in enumerate(rows, 1):
        if row['verdict'] not in {'correct', 'incorrect'}:
            continue
        value = sql_result(row['sql'])['value']
        require(value == int(row['value']), f'Valeur non reproduite, enregistrement {number}.')
        require(int(row['reference']) == refs[row['case_id']], 'Références contradictoires.')
        verdict = 'correct' if value == refs[row['case_id']] else 'incorrect'
        require(verdict == row['verdict'], f'Verdict non reproduit, enregistrement {number}.')
        replays.append(dict(csv_record=number, cell_id=row['cell_id'], nature='sql_replay',
                            recorded_value=int(row['value']), replayed_value=value, matches=True))
    write_csv(evidence / 'sql-replay.csv', replays)

    official_text = (ROOT / 'sources/reference-values-td1-en.md').read_text(encoding='utf-8')
    official = {m[0]: int(m[1]) for m in re.findall(r'^\| (C\d\d) \| .*? \| (\d+) \|', official_text, re.M)}
    require(set(official) == set(CASES), 'Table officielle illisible.')
    reference_checks = []
    for row in references:
        value = sql_result(row['sql'])['value']
        case = row['case_id']
        require(value == refs[case] == official[case], f'Référence erronée : {case}')
        reference_checks.append(dict(case_id=case, reference=refs[case], sql_value=value,
                                     official_value=official[case], matches=True))
    write_csv(evidence / 'reference-checks.csv', reference_checks)

    vote = load_vote()
    votes, vote_table = {}, []
    for case in CASES:
        a = vote(proposals_for(latest, case, PANEL), 2)
        b = vote(proposals_for(latest, case, MODELS), 3)
        votes[case] = {'fixed_2_of_3': a, 'all_3_of_5': b, 'reference': refs[case]}
        detail = '; '.join(f"{m}={latest[p,m,case]['value'] or 'null'} ({latest[p,m,case]['verdict']})"
                           for p, m in MODELS)
        vote_table.append(dict(case_id=case, reference=refs[case],
                               decision_2of3='consensus' if a['consensus'] else 'abstention',
                               value_2of3=a['value'], votes_2of3=a['votes'],
                               matches_2of3=a['value'] == refs[case] if a['consensus'] else '',
                               decision_3of5='consensus' if b['consensus'] else 'abstention',
                               value_3of5=b['value'], votes_3of5=b['votes'],
                               matches_3of5=b['value'] == refs[case] if b['consensus'] else '',
                               trace_detail=detail))
    write_json(evidence / 'quorums.json', votes)
    write_csv(evidence / 'quorums-20.csv', vote_table)

    c02 = [latest[p,m,'C02'] for p,m in MODELS]
    write_csv(evidence / 'c02-traces.csv', c02)
    for filename, model in [('m1-gpt20b.sql', MODELS[1]), ('m2-dots.sql', MODELS[4])]:
        require((ROOT/'sql'/filename).read_text(encoding='utf-8').strip() ==
                latest[model[0], model[1], 'C02']['sql'].strip(), 'SQL différent de la trace.')
    values = {name: sql_result((ROOT/'sql'/name).read_text(encoding='utf-8'))['value']
              for name in ['m1-gpt20b.sql', 'm2-dots.sql', 'reference-c02.sql']}
    result = sql_result((ROOT/'sql/delta-c02.sql').read_text(encoding='utf-8'))
    delta = [dict(zip(result['columns'], r)) for r in result['rows']]
    write_csv(evidence / 'delta-c02.csv', delta)
    csv_customers, csv_lines = independent_csv()
    write_csv(evidence / 'independent-csv-customers.csv', csv_customers)
    write_csv(evidence / 'independent-csv-order-lines.csv', csv_lines)
    require({r['customer_id']: r['reference_cents'] for r in delta} ==
            {r['customer_id']: r['revenue_cents'] for r in csv_customers}, 'Delta SQL / CSV différent.')
    for key, filename in [('delta_m1_cents','m1-gpt20b.sql'), ('delta_m2_cents','m2-dots.sql')]:
        require(sum(r[key] for r in delta) == refs['C02'] - values[filename], 'Écart non expliqué.')
    require(sum(r['revenue_cents'] for r in csv_customers) == refs['C02'] == values['reference-c02.sql'],
            'Contrôle indépendant incorrect.')
    predicate_result = sql_result((ROOT/'sql/diagnostic-predicates.sql').read_text(encoding='utf-8'))
    predicates = dict(zip(predicate_result['columns'], predicate_result['rows'][0]))
    ablation_result = sql_result((ROOT/'sql/diagnostic-m2.sql').read_text(encoding='utf-8'))
    ablations = dict(zip(ablation_result['columns'], ablation_result['rows'][0]))
    illustrative_panel = [MODELS[1], MODELS[4], MODELS[2]]
    illustrative_vote = vote(proposals_for(latest, 'C02', illustrative_panel), 2)
    write_json(evidence/'c02-posthoc-panel.json', {
        'nature': 'post_hoc_vote_on_stored_real_traces',
        'warning': 'Panel illustratif choisi après observation, distinct du panel officiel.',
        'panel': [':'.join(key) for key in illustrative_panel], 'k': 2, 'n': 3,
        'decision': illustrative_vote, 'reference': refs['C02']})

    prompt_checks = []
    system = (ROOT/'prompts/system.txt').read_text(encoding='utf-8')
    for case in CASES:
        user = (ROOT/'prompts'/f'{case}-user.txt').read_text(encoding='utf-8')
        digest = hashlib.sha256((system+'\n'+user).encode()).hexdigest()
        require({r['prompt_sha256'] for r in rows if r['case_id']==case} == {digest}, 'Prompt différent.')
        prompt_checks.append(dict(case_id=case, sha256=digest, matches_all_traces=True))
    write_csv(evidence/'prompt-checks.csv', prompt_checks)
    summary = dict(source_records=len(rows), final_cells=len(latest), retries=len(rows)-len(latest),
                   final_verdicts=dict(Counter(r['verdict'] for r in final_rows)),
                   shared_wrong_cases=candidates, replayed_queries=len(replays),
                   verified_references=len(reference_checks), prompt_checks=len(prompt_checks),
                   c02_values=values, c02_quorums=votes['C02'],
                   delta_customers=len(delta), delta_order_lines=len(csv_lines),
                   delta_total_cents=sum(r['delta_m1_cents'] for r in delta), predicates=predicates,
                   m2_ablations=ablations,
                   database_sha256=sha256(DB), network_calls=0)
    verify_inputs()
    write_json(evidence/'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == '__main__':
    main()
