from pathlib import Path
import subprocess,os,json,urllib.request,urllib.error
root=Path(__file__).resolve().parents[1]
result={'estado':'pendente','repo':'vorneermel/a-magia-do-corredor-21','publico':True}
env=dict(os.environ,GCM_INTERACTIVE='never',GIT_TERMINAL_PROMPT='0')
try:
    p=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,env=env,timeout=25)
    cred=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
    token=cred.get('password')
    if not token: raise RuntimeError('Git local sem credencial autenticada disponível; gh não instalado e conector sem criação de repositório.')
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'Codex-book-backup'}
    def api(path,data=None):
        req=urllib.request.Request('https://api.github.com'+path,headers=headers,data=None if data is None else json.dumps(data).encode())
        with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
    profile=api('/user')
    if profile['login'].lower()!='vorneermel':raise RuntimeError('Conta da credencial Git diferente da conta confirmada pelo conector.')
    try: repo=api('/repos/'+result['repo'])
    except urllib.error.HTTPError as e:
        if e.code!=404:raise
        repo=api('/user/repos',{'name':'a-magia-do-corredor-21','description':'A Magia do Corredor 21 — Vorne Ermel. Manuscrito, preparação editorial e arquivos.','private':False,'auto_init':False})
    if repo['private']:raise RuntimeError('Remoto encontrado privado; visibilidade pública precisa ser aplicada antes de enviar.')
    remotes=subprocess.run(['git','remote'],cwd=root,text=True,capture_output=True,check=True).stdout.split()
    if 'origin' not in remotes:subprocess.run(['git','remote','add','origin',repo['clone_url']],cwd=root,check=True)
    result.update(estado='remoto criado ou reutilizado; commit final ainda não enviado',url=repo['html_url'])
except Exception as e:
    # Nunca persistir corpo HTTP ou credenciais; só causa técnica resumida.
    result['causa']=('HTTP '+str(e.code)) if isinstance(e,urllib.error.HTTPError) else str(e)
(root/'editorial/backup.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
