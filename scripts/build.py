"""Build complete static pages using Python 3's standard library."""
from pathlib import Path
from html import escape
import json,re,os
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'; (DIST/'meetings').mkdir(parents=True,exist_ok=True)
ORIGIN=os.environ.get('SITE_URL','https://system-group-notes.primleaf.chatgpt.site').rstrip('/')
REPO='https://github.com/haodongwang01/group_meeting'
meetings=json.loads((ROOT/'content/meetings.json').read_text(encoding='utf-8'))
def tags(m):return ''.join(f'<span class="tag">{escape(t)}</span>' for t in m['tags'])
def people(m):
 return f'<dl class="contributors"><div><dt>主讲人</dt><dd>{escape(m["speaker"])}</dd></div><div><dt>{escape(m["contribution_label"])}</dt><dd>{escape(m["contributors"])}</dd></div></dl>'
def shell(title,description,body,path='index.html'):
 prefix='/' if path=='404.html' else '../' if path.startswith('meetings/') else './'
 canonical=ORIGIN+'/'+path
 return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · 系统组研究札记</title><meta name="description" content="{escape(description,quote=True)}"><meta name="theme-color" content="#f8faf7"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:type" content="{'article' if path.startswith('meetings/') else 'website'}"><meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}"><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head>
<body id="top"><a class="skip" href="#main">跳至主要内容</a><header class="site-header"><div class="header-inner"><a class="brand" href="{prefix}index.html" aria-label="系统组研究札记首页"><span class="brand-mark" aria-hidden="true">系</span><span>系统组 <span class="brand-divider">/</span> 研究札记<small>SYSTEMS RESEARCH NOTES</small></span></a><nav aria-label="主导航"><a href="{prefix}index.html#archive">会议归档</a><a href="{prefix}index.html#about">关于</a><a class="github" href="{REPO}">GitHub <span aria-hidden="true">↗</span></a></nav></div></header>
{body}<footer class="site-footer"><div><a class="footer-brand" href="{prefix}index.html">系统组 · 研究札记</a><p>记录问题，连接思路，让讨论继续。</p></div><div><a href="{REPO}">GitHub 源码 ↗</a><p>原创代码 MIT · <a href="{prefix}credits.html">内容与图片来源</a></p></div></footer>
<dialog id="lightbox" aria-label="图片放大查看"><button class="close-dialog" type="button" autofocus aria-label="关闭放大图片">关闭 ×</button><img alt=""><p></p></dialog></body></html>'''
def write(path,text):(DIST/path).write_bytes(text.encode('utf-8'))
cards=[]
for m in meetings:
 cards.append(f'''<article class="meeting-card" data-tags="{escape(' '.join(m['tags']),quote=True)}"><div class="card-copy"><div class="card-meta"><span class="issue">札记 {m['issue']}</span><time datetime="{m['date']}">{m['date'].replace('-',' / ')}</time></div><h3><a href="meetings/{m['date']}.html">{m['title']}</a></h3><p>{m['summary']}</p><p class="card-people">主讲 <strong>{escape(m['speaker'])}</strong></p><div class="tags">{tags(m)}</div><a class="read-link" href="meetings/{m['date']}.html" aria-label="阅读 {m['title']}">阅读本期 <span aria-hidden="true">↗</span></a></div><a class="card-image" href="meetings/{m['date']}.html" tabindex="-1" aria-hidden="true"><img src="assets/images/{m['cover']}" alt="" loading="lazy"><span>{m['type']}</span></a></article>''')
home=f'''<main id="main"><section class="hero wrap"><div class="hero-copy"><p class="eyebrow"><span class="dot"></span> SYSTEMS GROUP / RESEARCH JOURNAL</p><h1>从一个问题，<br>到下一次<span>探索。</span></h1><p class="hero-description">系统组的小组会研究札记。<br>在论文、实验与讨论之间，记录正在生长的研究思路。</p><a class="primary-link" href="#archive">翻阅会议记录 <span aria-hidden="true">↓</span></a></div><div class="hero-visual" aria-label="研究主题：计算、存储与调度"><div class="visual-top"><span>RESEARCH IN PROGRESS</span><span>2026 · 秋</span></div><div class="research-map"><div class="map-node node-compute"><small>01 / COMPUTE</small><strong>计算</strong><span>低比特训练 · 稀疏模型</span></div><div class="map-connector" aria-hidden="true">↓</div><div class="map-row"><div class="map-node"><small>02 / MEMORY</small><strong>存储</strong><span>权重与 KV 卸载</span></div><span class="map-cross" aria-hidden="true">↔</span><div class="map-node"><small>03 / SCHEDULING</small><strong>调度</strong><span>仿真与资源管理</span></div></div></div><div class="visual-bottom"><span class="dot"></span> 把系统问题，放回真实的工作负载。</div></div></section>
<section id="archive" class="archive wrap"><div class="section-heading"><div><p class="eyebrow">THE ARCHIVE</p><h2>会议归档<span> / {len(meetings):02d}</span></h2></div><p>2026.10 — 2026.11 <span class="muted">· 日期倒序</span></p></div><div class="filter-bar" hidden><span>研究主题</span><button type="button" data-filter="all" aria-pressed="true">全部 <small>{len(meetings)}</small></button><button type="button" data-filter="SSD 卸载">SSD 卸载</button><button type="button" data-filter="具身 RL">具身 RL</button><button type="button" data-filter="MoE">MoE</button><button type="button" data-filter="低比特训练">低比特训练</button><p id="filter-status" class="sr-only" aria-live="polite"></p></div><div class="meeting-list">{''.join(cards)}</div></section>
<section id="about" class="about wrap"><p class="eyebrow">ABOUT THESE NOTES</p><div><h2>让每一次讨论，<br>都有迹可循。</h2><p>这里整理系统组的小组会记录：论文的核心机制、实验中的观察，以及值得继续追问的研究方向。我们保留讨论的来处，也保留尚未解决的问题。</p><p>论文结果、组内初步实验与研究设想分别标明。主讲人与 idea 贡献分别标注，论文图与数据可按需展开。</p><a href="{REPO}">查看网站源码 <span aria-hidden="true">↗</span></a></div></section></main>'''
write('index.html',shell('从一个问题，到下一次探索', '系统组小组会研究札记：低比特训练、MoE 权重卸载、具身 RL 与原生稀疏注意力的四期会议核心思想与成员 idea。',home))
for i,m in enumerate(meetings):
 body=(ROOT/'content'/f"{m['date']}.html").read_text(encoding='utf-8')
 headings=re.findall(r'<h([23])\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>',body,re.S)
 toc=''.join(f'<li class="toc-level-{level}"><a href="#{id}">{re.sub("<[^>]+>","",title)}</a></li>' for level,id,title in headings)
 nav=''
 for j,label in [(i+1,'上一期 · 更早'),(i-1,'下一期 · 更新')]:
  if 0<=j<len(meetings):
   n=meetings[j];nav+=f'<a href="{n["date"]}.html"><small>{label} / {n["date"]}</small><strong>{n["title"]}</strong><span aria-hidden="true">↗</span></a>'
 chars=len(re.sub('<[^>]+>','',body)); minutes=max(3,round(chars/450))
 article=f'''<main id="main" class="article-wrap wrap"><div class="breadcrumb"><a href="../index.html#archive">会议归档</a><span aria-hidden="true">/</span><span>札记 {m['issue']}</span></div><header class="article-header"><p class="eyebrow">MEETING NOTES / {m['issue']}</p><div class="article-meta"><time datetime="{m['date']}">{m['date'].replace('-',' 年 ',1).replace('-',' 月 ')} 日</time><span>{m['type']}</span><span>约 {minutes} 分钟</span></div><h1>{m['title']}</h1><p class="article-deck">{m['summary']}</p><div class="tags">{tags(m)}</div>{people(m)}</header><div class="article-layout"><aside class="toc"><details open><summary>本期目录 <span aria-hidden="true">⌄</span></summary><nav aria-label="本期章节"><ol>{toc}</ol></nav></details><a class="back-top" href="#top">↑ 返回顶部</a></aside><article class="prose">{body}<details class="source-note"><summary>来源与说明</summary><p>{m['source']}。网页提炼核心思想，验证步骤据讨论整理；成员归属结合原记录与补充确认。引用图版权归原作者。</p><a href="../credits.html">查看来源与使用说明 →</a></details><nav class="issue-nav" aria-label="前后期导航">{nav}</nav></article></div></main>'''
 write(f"meetings/{m['date']}.html",shell(m['title'],m['summary'],article,f"meetings/{m['date']}.html"))
credits='''<main id="main" class="wrap simple-page"><p class="eyebrow">SOURCES & CREDITS</p><h1>内容与图片来源</h1><p>网站整理用户提供的四期系统组会议材料。会议原 DOCX、PDF、TeX 和演示文稿不作为下载文件发布。</p><h2>会议内容</h2><ul>'''+''.join(f'<li><a href="meetings/{m["date"]}.html">{m["date"]} · {m["title"]}</a><p>{m["source"]}</p></li>' for m in meetings)+'''</ul><h2>引用图片</h2><p>10 月 15 日：FourTune 图 8，来自胡揚嘉汇报材料。10 月 22 日：Expert 内神经元聚类示意，来自游嘉玮汇报的会议总结。11 月 4 日：DSec 图 3、4，EBRL 图 9、10，来自所提供论文及配套图。11 月 5 日：HiSparse 图 6、2，FlatCake 图 5、4，来自会议 DOCX。所有图片均在正文相邻位置标注出处。</p><h2>使用范围</h2><p>原创网站代码采用 MIT 许可。MIT 不覆盖会议正文、第三方论文图片及其他引用材料；这些内容的权利归各自权利人所有，未另行授予开放再利用许可。需要转载、修改或用于其他用途时，应另行核对并取得相应许可。</p><p>研究设想示意依据原会议材料重排；不应解读为已实现的系统或已验证的实验结果。</p><p><a href="index.html">← 返回首页</a></p></main>'''
write('credits.html',shell('内容与图片来源','会议材料、论文插图和原创代码的来源与使用说明。',credits,'credits.html'))
write('404.html',shell('未找到页面','该页面不存在，请返回会议归档。','<main id="main" class="wrap simple-page"><p class="eyebrow">404 / PAGE NOT FOUND</p><h1>这一页，还没有记录。</h1><p>链接可能已变化，回到归档继续阅读。</p><a class="primary-link" href="/index.html#archive">返回会议归档 →</a></main>','404.html'))
urls=['index.html','credits.html']+[f'meetings/{m["date"]}.html' for m in meetings]
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}/{p}</loc></url>' for p in urls)+'</urlset>\n')
write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
print(f'Built {len(meetings)} meeting pages, home, credits, 404 and sitemap.')
