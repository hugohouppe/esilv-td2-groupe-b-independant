"""Une commande pour tester et recréer les preuves, sans accès réseau."""
import json
import platform
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def run(arguments, filename):
    result=subprocess.run([sys.executable,*arguments],cwd=ROOT,capture_output=True,
                          text=True,encoding='utf-8',errors='replace')
    text='$ python '+' '.join(arguments)+'\n'+result.stdout+result.stderr
    (ROOT/'evidence'/filename).write_text(text,encoding='utf-8')
    if result.returncode:
        print(text)
        raise SystemExit(result.returncode)
    print('OK : '+' '.join(arguments))


def main():
    (ROOT/'evidence').mkdir(exist_ok=True)
    run(['-m','unittest','discover','-s','tests','-v'],'tests.txt')
    run(['analyse.py'],'analysis-run.txt')
    run(['atelier-vote.py'],'official-synthetic-votes.txt')
    run(['atelier-vote.py','--traces','traces-td1.csv','--case','C02'],'official-c02-vote.txt')
    runtime=dict(python=platform.python_version(),sqlite=sqlite3.sqlite_version,
                 platform=platform.system(),network_calls=0)
    (ROOT/'evidence/runtime.json').write_text(json.dumps(runtime,indent=2)+'\n',encoding='utf-8')
    print('Toutes les vérifications ont réussi. Preuves dans evidence/.')


if __name__=='__main__':
    main()
