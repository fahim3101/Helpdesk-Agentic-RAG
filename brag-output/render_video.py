from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, math, os
import json
import io

OUT = Path(__file__).parent
ASSET = OUT / 'composition' / 'assets'
ASSET.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080
BG = (8, 11, 16)
BG_SOFT = (12, 16, 23)
PANEL = (14, 19, 27)
PANEL2 = (19, 26, 36)
PANEL3 = (24, 32, 44)
BORDER = (30, 39, 53)
TEXT = (231, 238, 247)
TEXT2 = (179, 192, 208)
MUTED = (127, 140, 158)
FAINT = (91, 102, 117)
GREEN = (61, 220, 151)
BLUE = (88, 166, 255)
AMBER = (240, 180, 41)
FONT = '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
BOLD = '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

def f(size, bold=False, mono=False):
    return ImageFont.truetype(MONO if mono else (BOLD if bold else FONT), size)

def txt(d, xy, s, size=28, fill=TEXT2, bold=False, mono=False, anchor=None):
    d.text(xy, s, font=f(size, bold, mono), fill=fill, anchor=anchor)

def rr(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def make_base():
    im = Image.new('RGB', (W,H), BG)
    px = im.load()
    for y in range(H):
        t = y / H
        c = tuple(int(BG[i]*(1-t) + BG_SOFT[i]*t) for i in range(3))
        for x in range(W): px[x,y] = c
    glow = Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse((450,-540,1530,460), fill=(40,93,78,34))
    glow=glow.filter(ImageFilter.GaussianBlur(160))
    return Image.alpha_composite(im.convert('RGBA'),glow).convert('RGB')

def draw_mark(d, x, y, r=22):
    d.rounded_rectangle((x-r,y-r,x+r,y+r), radius=12, fill=GREEN)
    cx,cy=x,y
    for a in range(0,360,45):
        rad=math.radians(a)
        d.line((cx+math.cos(rad)*7,cy+math.sin(rad)*7,cx+math.cos(rad)*15,cy+math.sin(rad)*15),fill=(6,18,13),width=3)
    d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=(6,18,13))

def pill(d, x,y,label,color=GREEN, bg=None, size=18):
    bg=bg or (color[0]//7,color[1]//7,color[2]//7)
    box=d.textbbox((0,0),label,font=f(size,True))
    w=box[2]+24; h=size+18
    rr(d,(x,y,x+w,y+h),h//2,bg,outline=color,width=2)
    txt(d,(x+12,y+7),label,size,color,True)
    return w

def pipeline(d, active=0, status='idle', source='—'):
    x0,y0=1372,220
    rr(d,(1344,174,1818,934),22,(14,19,27),BORDER,2)
    txt(d,(1380,207),'Agent Pipeline',29,TEXT,True)
    pill(d,1650,194,status.upper(), GREEN if status=='done' else (AMBER if status=='weak' else MUTED), size=15)
    steps=[('Route','Decide: company knowledge or casual chat'),('Retrieve','Search private FAISS knowledge base'),('Grade','Is retrieved evidence good enough?'),('Web Fallback','Only when private evidence is weak'),('Rewrite & Retry','Improve the query, retry with a guard'),('Generate','Grounded answer with citations')]
    for i,(name,detail) in enumerate(steps):
        y=y0+i*94
        color=GREEN if i<active or (i==active and status=='done') else (AMBER if i==active and status=='weak' else (BLUE if i==active else FAINT))
        if i<5:
            d.line((1391,y+34,1391,y+92),fill=BORDER,width=3)
        d.ellipse((1382,y+24,1400,y+42),fill=color)
        if i==active and status in ('working','weak'):
            d.ellipse((1377,y+19,1405,y+47),outline=color,width=2)
        title_color=TEXT if i==active or i<active else TEXT2
        txt(d,(1422,y+13),name,23,title_color,True)
        state='done' if i<active or (i==active and status=='done') else ('weak' if i==active and status=='weak' else ('active' if i==active and status=='working' else 'idle'))
        txt(d,(1748,y+16),state.upper(),14,color,True,anchor='ra')
        txt(d,(1422,y+48),detail,15,MUTED)
    d.line((1374,798,1788,798),fill=BORDER,width=2)
    txt(d,(1380,824),'FINAL SOURCE',14,FAINT,True)
    txt(d,(1380,854),source,24,TEXT,True)
    txt(d,(1380,890),'Answer source is visible in the trace.',15,MUTED)

def frame(stage):
    im=make_base(); d=ImageDraw.Draw(im)
    if stage==5:
        # End card keeps the actual product lockup and color language.
        draw_mark(d,960,300,35)
        txt(d,(960,390),'Agentic RAG',60,TEXT,True,anchor='mm')
        txt(d,(960,466),'IT Support Copilot',34,MUTED,anchor='mm')
        d.line((720,540,1200,540),fill=BORDER,width=2)
        txt(d,(960,620),'Private knowledge first.',48,TEXT,True,anchor='mm')
        txt(d,(960,688),'Web when evidence is weak.',35,GREEN,True,anchor='mm')
        pill(d,790,790,'ASK AN IT SUPPORT QUESTION',GREEN,(9,34,25),22)
        txt(d,(960,930),'LangGraph  ·  FAISS  ·  Gemini  ·  DuckDuckGo',19,MUTED,mono=True,anchor='mm')
        return im

    # The actual product uses a three-panel desktop layout.
    x,y,r,b=72,70,1848,1010
    rr(d,(x,y,r,b),22,(12,16,23),BORDER,2)
    d.rectangle((x+2,y+2,r-2,y+81),fill=(14,19,27))
    d.line((x,y+82,r,y+82),fill=(25,33,45),width=2)
    # header
    d.ellipse((102,98,120,116),fill=GREEN)
    txt(d,(142,94),'Enterprise Knowledge Copilot',26,TEXT,True)
    pill(d,590,91,'PRIVATE KNOWLEDGE FIRST',GREEN,(9,34,25),16)
    pill(d,1668,91,'AGENTIC RAG',GREEN,(9,34,25),16)
    # column dividers
    d.line((438,152,438,1009),fill=BORDER,width=2)
    d.line((1334,152,1334,1009),fill=BORDER,width=2)
    # left rail
    draw_mark(d,122,191,24)
    txt(d,(165,173),'Agentic RAG',25,TEXT,True)
    txt(d,(165,204),'IT Support Copilot',19,MUTED)
    txt(d,(102,254),'Private company knowledge first.',17,MUTED)
    txt(d,(102,282),'Public web only when evidence is weak.',17,MUTED)
    txt(d,(102,352),'ARCHITECTURE',15,FAINT,True)
    arch=[('Agentic loop','LangGraph',GREEN),('Reasoning LLM','Gemini',GREEN),('Private KB','FAISS',BLUE),('Web fallback','DuckDuckGo',BLUE),('Failover','Groq',AMBER)]
    for i,(a,v,c) in enumerate(arch):
        yy=397+i*54
        d.ellipse((104,yy+8,116,yy+20),fill=c)
        txt(d,(132,yy),a,18,TEXT2)
        txt(d,(412,yy),v,16,FAINT,anchor='ra')
    txt(d,(102,715),'BEHAVIOUR',15,FAINT,True)
    txt(d,(102,752),'Ground answers in retrieved',17,MUTED)
    txt(d,(102,781),'company documents. Show each',17,MUTED)
    txt(d,(102,810),'decision in the live trace.',17,MUTED)
    rr(d,(101,914,409,973),12,(19,26,36),BORDER,2)
    txt(d,(255,934),'＋  Add Company Document',17,TEXT2,True,anchor='mm')
    # center panel
    txt(d,(482,178),'IT SUPPORT',15,FAINT,True)
    if stage==0:
        rr(d,(500,254,1264,437),18,(19,26,36),BORDER,2)
        txt(d,(530,280),'How can I help with IT support?',27,TEXT,True)
        txt(d,(530,328),'Ask about company IT policy, devices, access',19,TEXT2)
        txt(d,(530,360),'or troubleshooting. Vendor questions can use',19,TEXT2)
        txt(d,(530,392),'the public web when internal evidence is weak.',19,TEXT2)
        txt(d,(502,535),'Ask an IT support question…',22,FAINT)
        rr(d,(502,508,1280,577),15,(19,26,36),BORDER,2)
        txt(d,(536,531),'Ask an IT support question…',21,FAINT)
        d.ellipse((1214,523,1260,569),fill=GREEN)
        d.polygon([(1231,535),(1248,546),(1231,557)],fill=(6,18,13))
        txt(d,(502,632),'Private knowledge first. Evidence decides what comes next.',20,GREEN,True)
    else:
        q = 'How do I connect to the company VPN?' if stage in (1,2) else 'What is the latest Microsoft Teams outage guidance?'
        rr(d,(638,214,1280,294),18,(22,36,31), (35,68,58),2)
        txt(d,(674,239),q,21,TEXT,True)
        txt(d,(482,335),'AI',16,(6,18,13),True)
        d.ellipse((488,330,524,366),fill=GREEN)
        txt(d,(506,341),'AI',14,(6,18,13),True,anchor='mm')
        if stage==1:
            rr(d,(538,324,1295,520),18,(19,26,36),BORDER,2)
            txt(d,(570,350),'Searching private knowledge',23,TEXT,True)
            txt(d,(570,399),'Retrieving evidence from the company FAISS',19,TEXT2)
            txt(d,(570,431),'knowledge base before answering.',19,TEXT2)
            pill(d,570,468,'PRIVATE KB',GREEN,(9,34,25),16)
        elif stage==2:
            rr(d,(538,324,1295,542),18,(19,26,36),BORDER,2)
            txt(d,(570,350),'Grounded in the company knowledge base',23,TEXT,True)
            txt(d,(570,399),'The answer is generated from retrieved internal',19,TEXT2)
            txt(d,(570,431),'documents and includes source citations.',19,TEXT2)
            pill(d,570,472,'PRIVATE KB',GREEN,(9,34,25),16)
            pill(d,702,472,'CITATIONS',BLUE,(10,24,39),16)
        elif stage==3:
            rr(d,(538,324,1295,542),18,(19,26,36),BORDER,2)
            txt(d,(570,350),'Private evidence is weak',23,TEXT,True)
            txt(d,(570,399),'The current vendor question needs information',19,TEXT2)
            txt(d,(570,431),'the company knowledge base may not contain.',19,TEXT2)
            pill(d,570,472,'GRADE: WEAK',AMBER,(38,30,10),16)
            pill(d,738,472,'WEB FALLBACK',BLUE,(10,24,39),16)
        else:
            rr(d,(538,324,1295,607),18,(19,26,36),BORDER,2)
            txt(d,(570,350),'External information',23,TEXT,True)
            txt(d,(570,399),'The private KB was insufficient. Web evidence',19,TEXT2)
            txt(d,(570,431),'may need IT validation before changing',19,TEXT2)
            txt(d,(570,463),'company-managed systems.',19,TEXT2)
            pill(d,570,518,'WEB SEARCH',BLUE,(10,24,39),16)
            pill(d,738,518,'VALIDATE WITH IT',AMBER,(38,30,10),16)
        # input field remains true to the project UI
        rr(d,(502,857,1280,923),15,(19,26,36),BORDER,2)
        txt(d,(536,879),'Ask an IT support question…',19,FAINT)
        d.ellipse((1216,866,1260,910),fill=GREEN)
        d.polygon([(1231,878),(1247,888),(1231,898)],fill=(6,18,13))
        # trace footer
        txt(d,(502,741),'DECISION TRACE',14,FAINT,True)
        txt(d,(502,777),'Route  →  Retrieve  →  Grade  →  Generate',19,TEXT2,mono=True)

    # pipeline from project UI
    if stage==0:
        pipeline(d,active=0,status='idle',source='—')
    elif stage==1:
        pipeline(d,active=1,status='working',source='IN PROGRESS')
    elif stage==2:
        pipeline(d,active=5,status='done',source='PRIVATE KB')
    elif stage==3:
        pipeline(d,active=2,status='weak',source='WEB FALLBACK')
    else:
        pipeline(d,active=5,status='done',source='WEB SEARCH')
    # small footer, matching the source product's support-first voice
    txt(d,(482,968),'Answers are grounded in retrieved evidence.',15,FAINT)
    return im

for i in range(6):
    frame(i).save(ASSET / f'scene-{i+1:02d}.png', optimize=True)

# Build the 20-second preview-quality film from source-matched UI frames.
# HyperFrames composition remains beside this script as the editable project.
ffmpeg = '/usr/bin/ffmpeg'
inputs=[]
segment_durations = [2.12, 3.90, 3.92, 3.90, 4.95, 2.31]
for i, duration in enumerate(segment_durations):
    inputs += ['-loop','1','-framerate','30','-t',str(duration),'-i',str(ASSET/f'scene-{i+1:02d}.png')]
# Music starts on the bundled 1.60s cue; SFX are quiet and tied to visible actions.
inputs += ['-i',str(ASSET/'music/music-bed.mp3')]
inputs += ['-i',str(ASSET/'sfx/interface/click_003.ogg'),'-i',str(ASSET/'sfx/interface/click_003.ogg'),'-i',str(ASSET/'sfx/impact/impactSoft_medium_001.ogg')]
filters=[]
for i in range(6):
    filters.append(f'[{i}:v]zoompan=z=1+0.00043*on:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=1:s=1920x1080:fps=30,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]')
filters.append('[v0][v1]xfade=transition=wipeleft:duration=0.22:offset=1.90[x1]')
filters.append('[x1][v2]xfade=transition=smoothleft:duration=0.22:offset=5.58[x2]')
filters.append('[x2][v3]xfade=transition=wipeleft:duration=0.22:offset=9.28[x3]')
filters.append('[x3][v4]xfade=transition=smoothleft:duration=0.22:offset=12.96[x4]')
filters.append('[x4][v5]xfade=transition=wipeleft:duration=0.22:offset=17.69,fade=t=in:st=0:d=0.25,fade=t=out:st=19.65:d=0.35,tpad=stop_mode=clone:stop_duration=0.1,trim=duration=20[vout]')
filters.append('[6:a]volume=1.0,afade=t=in:st=0:d=0.6,afade=t=out:st=18.2:d=1.8,atrim=0:20[bgm]')
filters.append('[7:a]volume=0.34,adelay=2400|2400,atrim=0:20[click1]')
filters.append('[8:a]volume=0.28,adelay=9500|9500,atrim=0:20[click2]')
filters.append('[9:a]volume=0.25,adelay=17900|17900,atrim=0:20[impact]')
filters.append('[bgm][click1][click2][impact]amix=inputs=4:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.0:LRA=7[aout]')
cmd=[ffmpeg,'-y',*inputs,'-filter_complex',';'.join(filters),'-map','[vout]','-map','[aout]','-t','20','-r','30','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(OUT/'brag.mp4')]
subprocess.run(cmd,check=True)
# Modulate a restrained green halo from extracted bass energy, frame by frame.
# This keeps the music response visual and subtle without animating readable text.
source_video = OUT / 'brag.mp4'
glow_video = OUT / 'brag.glow.mp4'
audio_data = json.loads((ASSET/'music/audio-data.json').read_text())
mask = Image.new('L',(W,H),0)
md = ImageDraw.Draw(mask)
md.ellipse((440,-370,1480,540),fill=96)
mask = mask.filter(ImageFilter.GaussianBlur(150))
decoder = subprocess.Popen([ffmpeg,'-hide_banner','-loglevel','error','-i',str(source_video),'-map','0:v:0','-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
encoder = subprocess.Popen([ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','30','-i','pipe:0','-i',str(source_video),'-map','0:v:0','-map','1:a?','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(glow_video)],stdin=subprocess.PIPE)
frame_bytes = W*H*3
try:
    for frame_no in range(600):
        raw = decoder.stdout.read(frame_bytes)
        if len(raw) != frame_bytes:
            raise RuntimeError(f'video ended at frame {frame_no}')
        energy = audio_data['frames'][frame_no]['bands'][0]
        alpha = mask.point(lambda value: int(value*(0.08+min(energy,1.0)*0.30)))
        glow = Image.new('RGBA',(W,H),(61,220,151,0)); glow.putalpha(alpha)
        image = Image.frombytes('RGB',(W,H),raw).convert('RGBA')
        image = Image.alpha_composite(image,glow).convert('RGB')
        encoder.stdin.write(image.tobytes())
finally:
    decoder.stdout.close()
    decoder.wait()
    encoder.stdin.close()
    encoder.wait()
os.replace(glow_video,source_video)
# Best poster: the settled private-KB proof frame.
subprocess.run([ffmpeg,'-y','-ss','7.2','-i',str(OUT/'brag.mp4'),'-frames:v','1','-q:v','2',str(OUT/'brag.jpg')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
# Make the selected poster the first frame, preserving the remaining timing and audio.
poster=OUT/'brag.poster.mp4'
subprocess.run([ffmpeg,'-y','-i',str(OUT/'brag.mp4'),'-i',str(OUT/'brag.jpg'),'-filter_complex',"[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",'-map','[v]','-map','0:a?','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(poster)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
os.replace(poster,OUT/'brag.mp4')
print(OUT/'brag.mp4')
