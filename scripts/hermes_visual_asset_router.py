#!/usr/bin/env python3
import argparse, subprocess
def main():
    ap=argparse.ArgumentParser(description='Route visual asset generation by quality tier.'); ap.add_argument('--label',required=True); ap.add_argument('--topic',default=''); ap.add_argument('--output',required=True); ap.add_argument('--quality-tier',default='local_cartoon_scene'); ap.add_argument('--allow-local-fallback',action='store_true'); ap.add_argument('--model',default='gpt-image-1'); ap.add_argument('--size',default='1024x1024'); ap.add_argument('--quality',default='low'); a=ap.parse_args()
    if a.quality_tier in ['ai_cartoon_image','ai_3d_image']:
        cmd=['/usr/bin/python3','/root/.hermes/scripts/hermes_ai_image_generator.py','--label',a.label,'--topic',a.topic,'--output',a.output,'--style',a.quality_tier,'--model',a.model,'--size',a.size,'--quality',a.quality]
        if a.allow_local_fallback: cmd.append('--allow-local-fallback')
    else:
        cmd=['/usr/bin/python3','/root/.hermes/scripts/hermes_visual_asset_generator.py','--label',a.label,'--topic',a.topic,'--output',a.output,'--style','local_cartoon_scene','--quality-tier','local_cartoon_scene']
    proc=subprocess.run(cmd,text=True,capture_output=True); print(proc.stdout.strip())
    if proc.stderr.strip(): print(proc.stderr.strip())
    return proc.returncode
if __name__=='__main__': raise SystemExit(main())
