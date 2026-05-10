#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from PIL import Image
ORDER={'basic_icon':1,'local_cartoon_scene':2,'ai_cartoon_image':3,'ai_3d_image':4}
def main():
    ap=argparse.ArgumentParser(description='Verify Hermes visual asset quality tier.'); ap.add_argument('--image',required=True); ap.add_argument('--min-tier',default='local_cartoon_scene'); ap.add_argument('--min-width',type=int,default=800); ap.add_argument('--min-height',type=int,default=500); a=ap.parse_args(); img=Path(a.image); man=img.with_suffix(img.suffix+'.json')
    if not img.exists(): print('VISUAL_QUALITY=FAILED'); print('REASON=IMAGE_NOT_FOUND'); return 1
    if not man.exists(): print('VISUAL_QUALITY=FAILED'); print('REASON=MANIFEST_NOT_FOUND'); return 1
    data=json.loads(man.read_text()); tier=data.get('quality_tier','basic_icon'); placeholder=bool(data.get('placeholder',True))
    with Image.open(img) as im: w,h=im.size
    if w<a.min_width or h<a.min_height: print('VISUAL_QUALITY=FAILED'); print(f'REASON=DIMENSIONS_TOO_SMALL:{w}x{h}'); return 1
    if placeholder: print('VISUAL_QUALITY=FAILED'); print('REASON=PLACEHOLDER_TRUE'); return 1
    if ORDER.get(tier,0)<ORDER.get(a.min_tier,2): print('VISUAL_QUALITY=FAILED'); print(f'REASON=QUALITY_TIER_TOO_LOW:{tier}<{a.min_tier}'); return 1
    print('VISUAL_QUALITY=PASSED'); print('IMAGE='+str(img)); print('MANIFEST='+str(man)); print('QUALITY_TIER='+tier); print('SCENE_TYPE='+str(data.get('scene_type',''))); print(f'DIMENSIONS={w}x{h}'); return 0
if __name__=='__main__': raise SystemExit(main())
