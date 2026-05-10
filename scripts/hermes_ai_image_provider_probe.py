#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
PROVIDERS_ENV=Path('/root/.hermes/model_routing/providers.env')
OUT=Path('/root/.hermes/model_routing/image_probe/newcoin_image_probe.json')
def load_env_file(path):
    env={}
    if not path.exists(): return env
    for line in path.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    return env
def main():
    env=load_env_file(PROVIDERS_ENV); base=env.get('NEWCOIN_BASE_URL') or env.get('NEWCOIN_API_BASE') or env.get('NEWCOIN_BASE'); key=env.get('NEWCOIN_API_KEY') or env.get('NEWCOIN_KEY')
    result={'provider':'newcoin','base_url_found':bool(base),'key_found':bool(key),'models_status':None,'total_models':0,'candidate_image_models':[],'image_endpoint_guess':None,'newcoin_image_available':False,'reason':''}
    if not base or not key:
        result['reason']='NEWCOIN_BASE_OR_KEY_MISSING'; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2)); return 0
    base=base.rstrip('/'); cmd=['curl','-sS','-m','20','-H',f'Authorization: Bearer {key}',f'{base}/models']
    proc=subprocess.run(cmd,text=True,capture_output=True); result['models_status']=proc.returncode
    try: data=json.loads(proc.stdout)
    except Exception: data={}
    models=data.get('data',data if isinstance(data,list) else []); result['total_models']=len(models) if isinstance(models,list) else 0
    kws=['image','img','draw','dall','gpt-image','flux','sdxl','stable-diffusion','midjourney','jimeng','wanxiang','kolors','text-to-image','tti']
    c=[]
    if isinstance(models,list):
        for m in models:
            mid=str(m.get('id') or m.get('model') or m.get('name') or '') if isinstance(m,dict) else str(m)
            caps=json.dumps(m,ensure_ascii=False).lower()
            if any(k in mid.lower() or k in caps for k in kws): c.append(mid)
    result['candidate_image_models']=sorted(set([x for x in c if x])); result['newcoin_image_available']=bool(result['candidate_image_models'])
    if result['newcoin_image_available']:
        result['reason']='IMAGE_MODEL_CANDIDATES_FOUND_IN_MODELS'; result['image_endpoint_guess']=(f'{base}/images/generations' if base.endswith('/v1') else f'{base}/v1/images/generations')
    else: result['reason']='NO_IMAGE_MODEL_CANDIDATES_FOUND'
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
