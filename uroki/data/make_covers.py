# python3 make_covers.py <src_dir_or_map.tsv> <out_dir>  — RGBA png -> 1200x900 white jpg, model fitted into 1100x820
import sys, os, glob
from PIL import Image
def cover(src, dst, box=(1100,820)):
    im=Image.open(src)
    if im.mode in ('RGBA','LA','P'):
        im=im.convert('RGBA'); bb=im.split()[3].point(lambda v:255 if v>10 else 0).getbbox(); im=im.crop(bb)
        bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); im=bg.convert('RGB')
    else:
        im=im.convert('RGB')
    s=min(box[0]/im.width, box[1]/im.height); im=im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    out=Image.new('RGB',(1200,900),'white'); out.paste(im,((1200-im.width)//2,(900-im.height)//2)); out.save(dst,quality=88,optimize=True,progressive=True)
pairs=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
os.makedirs(sys.argv[2],exist_ok=True)
for src,name in pairs:
    cover(src, os.path.join(sys.argv[2], name+'.jpg')); print('ok',name)
