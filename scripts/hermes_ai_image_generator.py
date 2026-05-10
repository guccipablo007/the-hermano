#!/usr/bin/env python3
import argparse, base64, hashlib, json, subprocess, urllib.request
from pathlib import Path
from PIL import Image
PROVIDERS_ENV=Path('/root/.hermes/model_routing/providers.env'); CACHE=Path('/root/.hermes/file_outputs/ai_image_assets')
def load_env_file(path):
    env={}
    if path.exists():
        for line in path.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    return env
def norm(s): return ' '.join((s or '').lower().split())
def cache_key(label,topic,style,quality_tier,model,size,quality):
    raw=json.dumps({'label':norm(label),'topic':norm(topic),'style':style,'quality_tier':quality_tier,'model':model,'size':size,'quality':quality},sort_keys=True,ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:28]
def make_prompt(label,topic,style):
    style_line='beautiful 3D cartoon educational illustration, soft rounded 3D characters, bright classroom colors' if style=='ai_3d_image' else 'beautiful cartoon educational illustration, bright classroom colors'
    return f'{style_line}. Scene: {label}. Topic: {topic}. Show one cheerful 6-year-old child clearly doing the activity. Age-appropriate for kindergarten/primary school lesson material. Clean simple background, warm lighting, cute expressive face, safe classroom-friendly style. Absolutely no text anywhere in the image. No words, no letters, no numbers, no captions, no signs, no labels, no readable writing, no chalkboard words, no bottle labels, no book text, no watermark, no logo, no distorted hands, no scary elements. Objects that normally have writing must be blank.'
def write_manifest(path,label,topic,style,quality_tier,provider,model,endpoint,prompt,status,key,reason='',size='',quality=''):
    man={'label':label,'topic':topic,'style':style,'quality_tier':quality_tier,'provider':provider,'provider_route':'newcoin_image' if provider=='newcoin' else provider,'model':model,'endpoint':endpoint,'prompt':prompt,'status':status,'reason':reason,'cache_key':key,'size':size,'quality':quality,'output':str(path),'placeholder':False if status=='generated' else True}
    path.with_suffix(path.suffix+'.json').write_text(json.dumps(man,indent=2),encoding='utf-8')
def validate_image(path):
    with Image.open(path) as im:
        w,h=im.size; im.verify()
    if w<512 or h<512: raise RuntimeError(f'IMAGE_TOO_SMALL:{w}x{h}')
    return w,h
def decode_response_to_file(data,out):
    if not isinstance(data,dict): raise RuntimeError('INVALID_JSON_RESPONSE')
    items=data.get('data')
    if not isinstance(items,list) or not items: raise RuntimeError('NO_IMAGE_DATA_IN_RESPONSE')
    first=items[0]
    if first.get('b64_json'): out.write_bytes(base64.b64decode(first['b64_json'])); return 'b64_json'
    if first.get('url'):
        with urllib.request.urlopen(first['url'],timeout=120) as r: out.write_bytes(r.read())
        return 'url'
    if first.get('image'): out.write_bytes(base64.b64decode(first['image'])); return 'image'
    raise RuntimeError('UNSUPPORTED_IMAGE_RESPONSE_SHAPE')
def post_json(url,key,payload,timeout=180):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.loads(r.read().decode())
def generate_newcoin_image(label,topic,out,style,model,size,quality):
    env=load_env_file(PROVIDERS_ENV); base=(env.get('NEWCOIN_BASE_URL') or env.get('NEWCOIN_API_BASE') or env.get('NEWCOIN_BASE') or '').rstrip('/'); key=env.get('NEWCOIN_API_KEY') or env.get('NEWCOIN_KEY')
    if not base or not key: raise RuntimeError('NEWCOIN_BASE_OR_KEY_MISSING')
    endpoints=[base+'/images/generations'] if base.endswith('/v1') else [base+'/v1/images/generations', base+'/images/generations']
    prompt=make_prompt(label,topic,style); payload={'model':model,'prompt':prompt,'n':1,'size':size,'quality':quality}; last=''
    for endpoint in dict.fromkeys(endpoints):
        try:
            data=post_json(endpoint,key,payload); source=decode_response_to_file(data,out); w,h=validate_image(out); return {'endpoint':endpoint,'prompt':prompt,'source':source,'width':w,'height':h}
        except Exception as exc: last=f'{type(exc).__name__}:{exc}'
    raise RuntimeError('NEWCOIN_IMAGE_GENERATION_FAILED:'+last)
def main():
    ap=argparse.ArgumentParser(description='Generate AI cartoon/3D images through NewCoin image endpoint with cache.'); ap.add_argument('--label',required=True); ap.add_argument('--topic',default=''); ap.add_argument('--output',required=True); ap.add_argument('--style',choices=['ai_cartoon_image','ai_3d_image'],default='ai_3d_image'); ap.add_argument('--model',default='gpt-image-1'); ap.add_argument('--size',default='1024x1024'); ap.add_argument('--quality',default='low'); ap.add_argument('--allow-local-fallback',action='store_true'); a=ap.parse_args()
    CACHE.mkdir(parents=True,exist_ok=True); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); key=cache_key(a.label,a.topic,a.style,a.style,a.model,a.size,a.quality); cached=CACHE/f'{key}.png'; cm=cached.with_suffix(cached.suffix+'.json')
    if cached.exists() and cm.exists(): out.write_bytes(cached.read_bytes()); out.with_suffix(out.suffix+'.json').write_text(cm.read_text(),encoding='utf-8'); print('AI_IMAGE_GENERATION=PASSED'); print('CACHE_HIT=TRUE'); print('PROVIDER=newcoin'); print('MODEL='+a.model); print('QUALITY_TIER='+a.style); print('OUTPUT_PATH='+str(out)); return 0
    try:
        result=generate_newcoin_image(a.label,a.topic,cached,a.style,a.model,a.size,a.quality)
        write_manifest(cached,a.label,a.topic,a.style,a.style,'newcoin',a.model,result['endpoint'],result['prompt'],'generated',key,size=a.size,quality=a.quality)
        out.write_bytes(cached.read_bytes()); out.with_suffix(out.suffix+'.json').write_text(cm.read_text(),encoding='utf-8')
        print('AI_IMAGE_GENERATION=PASSED'); print('CACHE_HIT=FALSE'); print('PROVIDER=newcoin'); print('PROVIDER_ROUTE=newcoin_image'); print('MODEL='+a.model); print('QUALITY_TIER='+a.style); print('SIZE='+a.size); print('QUALITY='+a.quality); print('ENDPOINT='+result['endpoint']); print('OUTPUT_PATH='+str(out)); print(f"DIMENSIONS={result['width']}x{result['height']}"); return 0
    except Exception as exc:
        if a.allow_local_fallback:
            proc=subprocess.run(['/usr/bin/python3','/root/.hermes/scripts/hermes_visual_asset_generator.py','--label',a.label,'--topic',a.topic,'--output',str(out),'--style','local_cartoon_scene','--quality-tier','local_cartoon_scene'],text=True,capture_output=True); print(proc.stdout.strip()); print('AI_IMAGE_GENERATION=FALLBACK_LOCAL_CARTOON_SCENE' if proc.returncode==0 else proc.stderr.strip()); return proc.returncode
        print('AI_IMAGE_GENERATION=NOT_VERIFIED'); print('REASON='+type(exc).__name__+':'+str(exc)); return 1
if __name__=='__main__': raise SystemExit(main())
