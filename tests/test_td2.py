import csv
import sqlite3
import unittest
from datetime import date
from contextlib import closing
from types import SimpleNamespace

import analyse as a


class VoteTests(unittest.TestCase):
    def setUp(self):
        self.vote = a.load_vote()

    def proposals(self, values):
        return [SimpleNamespace(provider='test', model_requested=str(i), value=v,
                                verdict='executed' if v is not None else 'error')
                for i, v in enumerate(values)]

    def test_four_official_examples(self):
        for values, consensus, value, count in [([100,100,120],True,100,2),
                 ([100,110,120],False,None,1), ([100,None,None],False,None,1),
                 ([0,0,100],True,0,2)]:
            with self.subTest(values=values):
                got=self.vote(self.proposals(values),2)
                self.assertEqual((got['consensus'],got['value'],got['votes']),(consensus,value,count))

    def test_invalid_thresholds(self):
        for k in [0,1,4,2.0,True]:
            with self.subTest(k=k), self.assertRaises(ValueError):
                self.vote(self.proposals([1,1,1]),k)
        with self.assertRaises(ValueError): self.vote([],1)

    def test_duplicate_even_if_unavailable(self):
        rows=self.proposals([None,None,100])
        rows[1].model_requested=rows[0].model_requested
        with self.assertRaises(ValueError): self.vote(rows,2)

    def test_errors_do_not_vote_or_reduce_n(self):
        rows=self.proposals([7,7,9,None,None])
        self.assertFalse(self.vote(rows,3)['consensus'])
        rows[0].verdict='error'
        self.assertEqual(self.vote(rows,3)['votes'],1)
        result=self.vote(self.proposals([None,None,None]),2)
        self.assertEqual(result,dict(consensus=False,value=None,votes=0,models=[]))

    def test_winning_models_and_integer_cents(self):
        result=self.vote(self.proposals([7,7,8,7,None]),3)
        self.assertEqual(result['models'],['test:0','test:1','test:3'])
        with self.assertRaises(ValueError): self.vote(self.proposals([7.1,7.1,8]),2)


class CaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=a.read_csv(a.ROOT/'traces-td1.csv')
        cls.latest=a.latest_rows(cls.rows)
        cls.refs={r['case_id']:int(r['revenue_cents']) for r in a.read_csv(a.ROOT/'reference-td1.csv')}

    def test_inputs_and_last_attempts(self):
        a.verify_inputs()
        self.assertEqual(len(self.rows),106)
        self.assertEqual(len(self.latest),100)
        # Le classement TD1 (attempts, date, ordre) retrouve les mêmes lignes que l'atelier.
        for key,last in self.latest.items():
            candidates=[(i,r) for i,r in enumerate(self.rows,1)
                        if (r['provider'],r['model_requested'],r['case_id'])==key]
            best=max(candidates,key=lambda ir:(int(ir[1]['attempts']),ir[1]['date_utc'],ir[0]))
            self.assertEqual(last['csv_record'],best[0])

    def test_real_shared_case_and_hand_count(self):
        found=a.shared_wrong_values(self.latest,self.refs)
        self.assertEqual([(r['case_id'],r['value'],len(r['models'])) for r in found],[('C02',0,2)])
        vote=a.load_vote()
        three=vote(a.proposals_for(self.latest,'C02',a.PANEL),2)
        five=vote(a.proposals_for(self.latest,'C02',a.MODELS),3)
        self.assertEqual((three['value'],three['votes']),(590320,2))
        self.assertEqual(five,dict(consensus=False,value=None,votes=2,models=[]))

    def test_queries_delta_and_independent_csv(self):
        for name, expected in [('m1-gpt20b.sql',0),('m2-dots.sql',0),('reference-c02.sql',590320)]:
            self.assertEqual(a.sql_result((a.ROOT/'sql'/name).read_text(encoding='utf-8'))['value'],expected)
        result=a.sql_result((a.ROOT/'sql/delta-c02.sql').read_text(encoding='utf-8'))
        delta=[dict(zip(result['columns'],r)) for r in result['rows']]
        independent,lines=a.independent_csv()
        self.assertEqual({r['customer_id']:r['reference_cents'] for r in delta},
                         {r['customer_id']:r['revenue_cents'] for r in independent})
        self.assertEqual(sum(r['delta_m1_cents'] for r in delta),590320)
        self.assertEqual(sum(r['delta_m2_cents'] for r in delta),590320)
        self.assertEqual(sum(r['amount_cents'] for r in lines),590320)

    def test_age_boundaries_with_synthetic_dates(self):
        # Données construites, distinctes des résultats réels des modèles.
        day=date(2026,9,25)
        for birth,age in [('2000-09-25',26),('2000-09-26',25),('2001-09-25',25),('2001-09-26',24)]:
            self.assertEqual(a.age_on(date.fromisoformat(birth),day),age)
            self.assertEqual('2000-09-25'<birth<='2001-09-25',age==25)

    def test_delta_identifies_wrong_additions_too(self):
        # Test de la requête delta sur une base synthétique séparée, en mémoire.
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript((a.ROOT/'sources/schema.sql').read_text(encoding='utf-8'))
            db.execute("INSERT INTO product VALUES ('a', 100)")
            db.executemany('INSERT INTO customers VALUES (?, ?, ?)',[
                ('ok','2025-01-01','2000-09-26'),('extra','2026-01-01','2025-10-01')])
            db.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?)',[
                ('2026-01-05','O1','ok','a',2),('2026-01-05','O2','extra','a',3)])
            cursor=db.execute((a.ROOT/'sql/delta-c02.sql').read_text(encoding='utf-8'))
            rows=[dict(zip([c[0] for c in cursor.description],r)) for r in cursor]
        self.assertEqual({r['customer_id']:r['delta_m1_cents'] for r in rows},{'ok':200,'extra':-300})

    def test_unavailable_attempt_not_replaced_by_old_success(self):
        rows=a.proposals_for(self.latest,'C20',a.PANEL)
        qwen=rows[2]
        self.assertIsNone(qwen.value)
        self.assertEqual(qwen.verdict,'error')


if __name__=='__main__':
    unittest.main()
