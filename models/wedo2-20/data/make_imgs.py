import sys, os, subprocess, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
base=sys.argv[1]; out=os.path.join(base,'final'); os.makedirs(out,exist_ok=True)
PROG=json.loads(sys.argv[2])  # slug -> program page or null
def page_img(pdf,page):
    tmp=f'/tmp/_pi_{os.getpid()}'
    subprocess.run(['pdfimages','-f',str(page),'-l',str(page),'-j',pdf,tmp],check=True)
    f=sorted([x for x in os.listdir('/tmp') if x.startswith(os.path.basename(tmp))])[0]
    im=Image.open('/tmp/'+f).convert('RGB')
    im=im.crop((4,4,im.size[0]-4,im.size[1]-4))
    for x in os.listdir('/tmp'):
        if x.startswith(os.path.basename(tmp)): os.remove('/tmp/'+x)
    return im
def clean(im, thr=212, sat=28):
    a=np.asarray(im).astype(np.int16)
    g=a.mean(axis=2); s=a.max(axis=2)-a.min(axis=2)
    cand=(g>thr)&(s<sat)
    lab,n=ndimage.label(cand)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    b=a.copy(); b[bg]=255
    # остатки водяного знака внутри модели: тонкие светло-серые штрихи среди белого, без тёмных контуров рядом
    gb=b.mean(axis=2); sb=b.max(axis=2)-b.min(axis=2)
    mid=(gb>=200)&(gb<249)&(sb<25)
    white=(gb>=250).astype(float); dark=(gb<170).astype(float)
    wf=ndimage.uniform_filter(white,11); df=ndimage.maximum_filter(dark,7)
    wm=mid&(wf>0.42)&(df==0)
    b[wm]=255
    return Image.fromarray(b.astype(np.uint8)), bg
def bbox(mask_fg, margin):
    ys,xs=np.where(mask_fg)
    return max(0,xs.min()-margin), max(0,ys.min()-margin), xs.max()+margin, ys.max()+margin
for slug in sorted(os.listdir(os.path.join(base,'lo'))):
    pdf=os.path.join(base,'pdf',slug+'.pdf')
    im=page_img(pdf,1); W,H=im.size
    c,bg=clean(im)
    fg=~bg
    # ignore title (top) and author line (bottom) and side bars
    top=0.21 if slug in ('idushchiy-chelovek','rybak','rytsar','uborshchik','vratar') else 0.16
    fg[:int(H*top)]=False; fg[int(H*0.855):]=False
    # drop tiny specks
    lab,n=ndimage.label(fg); sizes=ndimage.sum(fg,lab,range(1,n+1))
    keep=np.isin(lab, [i+1 for i,s in enumerate(sizes) if s>150])
    x0,y0,x1,y1=bbox(keep,8)
    crop=c.crop((x0,y0,x1,y1))
    # also whiten anything outside kept components inside crop? keep as is
    cw,ch=crop.size
    scale=min(1080/cw, 800/ch)
    crop=crop.resize((int(cw*scale),int(ch*scale)),Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2,percent=60,threshold=2))
    canvas=Image.new('RGB',(1200,900),'white')
    canvas.paste(crop,((1200-crop.size[0])//2,(900-crop.size[1])//2))
    canvas.save(os.path.join(out,f'{slug}-cover.jpg'),quality=88)
    p=PROG.get(slug)
    if p:
        im=page_img(pdf,p); c,bg=clean(im)
        fg=~bg; H2=im.size[1]
        fg[int(H2*0.93):]=False   # copyright line
        lab,n=ndimage.label(fg); sizes=ndimage.sum(fg,lab,range(1,n+1))
        keep=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>60])
        x0,y0,x1,y1=bbox(keep,20)
        pc=c.crop((x0,y0,x1,y1))
        if pc.size[0]>1000:
            r=1000/pc.size[0]; pc=pc.resize((1000,int(pc.size[1]*r)),Image.LANCZOS)
        pc.save(os.path.join(out,f'{slug}-program.jpg'),quality=90)
    print(slug,'cover',canvas.size,'prog',p)
