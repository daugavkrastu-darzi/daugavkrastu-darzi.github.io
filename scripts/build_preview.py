from __future__ import annotations

import html
import shutil
from pathlib import Path

import jinja2
import mistune
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview'


def read_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return {}, text
    _, front, body = text.split('---\n', 2)
    return yaml.safe_load(front) or {}, body


def asset(path: str) -> str:
    return '/' + path.lstrip('/')


config = yaml.safe_load((ROOT / '_config.yml').read_text(encoding='utf-8'))
gallery = yaml.safe_load((ROOT / '_data/gallery.yml').read_text(encoding='utf-8'))
markdown = mistune.create_markdown(escape=False)
news: list[dict] = []
for path in (ROOT / '_news').glob('*.md'):
    meta, body = read_front_matter(path)
    meta['html'] = markdown(body)
    news.append(meta)
news.sort(key=lambda item: str(item['date']), reverse=True)

ENV = jinja2.Environment(autoescape=True)

HEADER = r'''
<header class="site-header">
  <div class="shell header-inner">
    <a class="brand" href="/" aria-label="Daugavkrastu dārzi — sākumlapa">
      <img class="brand-wordmark" src="{{ header_logo }}" data-fallback="/assets/images/logo-placeholder.svg" onerror="this.onerror=null;this.src=this.dataset.fallback" alt="Daugavkrastu dārzi">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation"><span class="sr-only">Atvērt izvēlni</span><span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span></button>
    <nav id="primary-navigation" class="primary-nav" aria-label="Galvenā izvēlne">
      <a href="/"{% if nav == 'home' %} aria-current="page"{% endif %}>Sākums</a>
      <a href="/jaunumi/"{% if nav == 'news' %} aria-current="page"{% endif %}>Jaunumi</a>
      <a href="/galerija/"{% if nav == 'gallery' %} aria-current="page"{% endif %}>Galerija</a>
      <a href="/par-mums/"{% if nav == 'about' %} aria-current="page"{% endif %}>Par mums</a>
      <a class="nav-contact" href="/kontakti/"{% if nav == 'contact' %} aria-current="page"{% endif %}>Kontakti</a>
    </nav>
  </div>
</header>
'''

FOOTER = r'''
<footer class="site-footer">
  <div class="shell footer-grid">
    <div><a class="footer-brand" href="/">Daugavkrastu dārzi</a><p>Mazdārziņu kopiena Lucavsalā, Rīgas sirdī.</p></div>
    <div><h2>Ātrās saites</h2><a href="/jaunumi/">Jaunumi</a><a href="/galerija/">Galerija</a><a href="/kontakti/">Kontakti</a></div>
    <div><h2>Rekvizīti</h2><p>Reģ. Nr. 40008244382<br>Tālavas gatve 3–10, Rīga, LV-1029</p></div>
  </div>
  <div class="shell footer-bottom"><span>© 2026 Biedrība “Daugavkrastu dārzi”</span><span>Vienkārša statiska vietne</span></div>
</footer>
'''


def render_page(title: str, nav: str, content: str) -> str:
    header = ENV.from_string(HEADER).render(nav=nav, header_logo=config['header_logo'])
    footer = FOOTER
    draft = ''
    if config.get('draft_banner'):
        draft = f'<div class="draft-banner" role="status"><div class="shell">{html.escape(config["draft_banner"])}</div></div>'
    return f'''<!doctype html><html lang="lv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#56372c"><title>{html.escape(title)} · Daugavkrastu dārzi</title><link rel="icon" href="/assets/images/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/css/main.css"></head><body><a class="skip-link" href="#main-content">Pāriet uz saturu</a>{header}{draft}<main id="main-content">{content}</main>{footer}<script src="/assets/js/main.js" defer></script></body></html>'''


def image_tag(src: str, alt: str = '', *, loading: bool = True) -> str:
    loading_attr = ' loading="lazy"' if loading else ''
    return f'<img src="{html.escape(src, quote=True)}" data-fallback="/assets/images/photo-placeholder.svg" onerror="this.onerror=null;this.src=this.dataset.fallback" alt="{html.escape(alt, quote=True)}"{loading_attr}>'


def home_content() -> str:
    cards = []
    for item in news[:3]:
        cards.append(f'''<article class="news-card"><div class="news-card-body"><p class="news-date">{html.escape(item['date_label'])}</p><h3><a href="/jaunumi/#{item['slug']}">{html.escape(item['title'])}</a></h3><p>{html.escape(item['summary'])}</p><a class="card-link" href="/jaunumi/#{item['slug']}">Lasīt ierakstu <span aria-hidden="true">→</span></a></div></article>''')
    return f'''
<section class="hero"><div class="shell hero-grid"><div class="hero-copy"><p class="eyebrow">Mazdārziņi Lucavsalā</p><h1>Vieta, kur sirds sastop dabu</h1><p class="hero-lead">Mēs kopīgi veidojam un kopjam mazdārziņus Rīgas sirdī — vietu atpūtai, dārzkopībai un stiprai kopienai.</p><div class="button-row"><a class="button button-primary" href="/jaunumi/">Lasīt jaunumus</a><a class="button button-secondary" href="/kontakti/">Sazināties</a></div></div><div class="hero-visual"><img class="hero-logo" src="{html.escape(config['logo'], quote=True)}" data-fallback="/assets/images/logo-placeholder.svg" onerror="this.onerror=null;this.src=this.dataset.fallback" alt="Biedrības “Daugavkrastu dārzi” logotips"></div></div></section>
<section class="section section-soft"><div class="shell"><div class="section-heading heading-split"><div><p class="eyebrow">Aktuāli</p><h2>Jaunākie ieraksti</h2></div><a class="text-link" href="/jaunumi/">Visi jaunumi <span aria-hidden="true">→</span></a></div><div class="news-card-grid">{''.join(cards)}</div></div></section>
<section class="section"><div class="shell intro-grid"><div><p class="eyebrow">Par biedrību</p><h2>Dārzi pilsētā, ko veidojam kopā</h2></div><div class="rich-copy"><p>“Daugavkrastu dārzi” pulcē cilvēkus, kuriem interesē dārzkopība, sakopta vide un dabas tuvums. Lucavsalas mazdārziņos ikvienam ir iespēja atpūsties un izaudzēt ekoloģiski tīrus produktus.</p><p>Kopīgiem spēkiem veidojam vidi, kurā cilvēki satiekas, dalās pieredzē un rūpējas par zaļāku Rīgu.</p><a class="text-link" href="/par-mums/">Vairāk par mums <span aria-hidden="true">→</span></a></div></div></section>
<section class="section section-links"><div class="shell"><p class="eyebrow">Vietnē</p><div class="feature-grid"><a class="feature-card" href="/jaunumi/"><span class="feature-number">01</span><h2>Jaunumi</h2><p>Publiska informācija par biedrības darbiem, pasākumiem un aktualitātēm.</p><span class="feature-arrow" aria-hidden="true">→</span></a><a class="feature-card" href="/galerija/"><span class="feature-number">02</span><h2>Galerija</h2><p>Fotogrāfijas no talkām, teritorijas labiekārtošanas un kopienas dzīves.</p><span class="feature-arrow" aria-hidden="true">→</span></a><a class="feature-card" href="/kontakti/"><span class="feature-number">03</span><h2>Kontakti</h2><p>Valdes un pārvaldnieku kontakti, kā arī vienkārša saziņas forma.</p><span class="feature-arrow" aria-hidden="true">→</span></a></div></div></section>
<section class="section"><div class="shell cta-panel"><div><p class="eyebrow">Saziņa</p><h2>Jautājums par Daugavkrastu dārziem?</h2><p>Sazinieties ar biedrības pārstāvjiem vai nosūtiet ziņu kontaktu lapā.</p></div><a class="button button-light" href="/kontakti/">Atvērt kontaktus</a></div></section>'''


def news_content() -> str:
    entries = []
    for item in news:
        images = ''
        if item.get('images'):
            imgs = ''.join(f'<figure><a href="{html.escape(im["src"], quote=True)}" target="_blank" rel="noopener">{image_tag(im["src"], im["alt"])}</a></figure>' for im in item['images'])
            single = ' single-image' if len(item['images']) == 1 else ''
            images = f'<div class="post-image-grid{single}">{imgs}</div>'
        entries.append(f'''<article class="news-entry" id="{html.escape(item['slug'])}"><header class="news-entry-header"><p class="news-date">{html.escape(item['date_label'])}</p><h2>{html.escape(item['title'])}</h2></header><div class="rich-copy news-content">{item['html']}</div>{images}<a class="back-to-top" href="#main-content">Atpakaļ uz augšu ↑</a></article>''')
    return f'''<section class="page-hero page-hero-news"><div class="shell narrow"><p class="eyebrow">Aktualitātes</p><h1>Jaunumi</h1><p>Jaunākā informācija par biedrības darbiem, pasākumiem un Lucavsalas mazdārziņu dzīvi.</p></div></section><section class="section"><div class="shell news-feed">{''.join(entries)}</div></section>'''


def gallery_content() -> str:
    albums = []
    for album in gallery:
        items = ''.join(f'<a class="gallery-item" href="{html.escape(im["src"], quote=True)}" target="_blank" rel="noopener">{image_tag(im["src"], im["alt"])}</a>' for im in album['images'])
        albums.append(f'''<section class="album" id="{html.escape(album['slug'])}"><div class="album-heading"><div><p class="eyebrow">{html.escape(album['date_label'])}</p><h2>{html.escape(album['title'])}</h2></div><span>{len(album['images'])} foto</span></div><div class="gallery-grid">{items}</div></section>''')
    return f'''<section class="page-hero page-hero-gallery"><div class="shell narrow"><p class="eyebrow">Mūsu dārzi</p><h1>Galerija</h1><p>Fotogrāfijas no kopīgi paveiktā, talkām un notikumiem Lucavsalas mazdārziņos.</p></div></section><section class="section"><div class="shell"><div class="setup-note">Šajā sākotnējā versijā izmantota izlase no pašreizējās vietnes. Pirms vecās vietnes slēgšanas visi galerijas oriģināli jāsaglabā GitHub repozitorijā.</div><div class="album-stack">{''.join(albums)}</div></div></section>'''


ABOUT = '''<section class="page-hero page-hero-about"><div class="shell narrow"><p class="eyebrow">Biedrība</p><h1>Par mums</h1><p>Kopiena, kas rūpējas par Lucavsalas mazdārziņiem un zaļu pilsētvidi.</p></div></section><section class="section"><div class="shell about-layout"><article class="rich-copy about-copy"><p class="lead-paragraph">“Daugavkrastu dārzi” ir biedrība, kas tika izveidota 2022. gada 15. septembrī un sāka apsaimniekot teritoriju no 2023. gada 1. janvāra.</p><p>Mūsu biedrība pulcē cilvēkus ar interesi par dārzkopību un dabas harmoniju, piedāvājot iespēju kopīgi veltīties dārzu radīšanai un kopšanai Daugavas malā.</p><p>“Daugavkrastu dārzi” ir ne vien biedrība, bet arī vienota kopiena, kurā dalāmies zināšanās, veidojam ilgtspējīgus dārzus un baudām skaistumu, ko piedāvā apkārtējā dabas vide.</p><p>Kopā veidojam pievilcīgus un dzīvotspējīgus dārzus, kurus ar lepnumu saucam par savējiem.</p></article><aside class="facts-card"><h2>Biedrības rekvizīti</h2><dl><div><dt>Nosaukums</dt><dd>Biedrība “Daugavkrastu dārzi”</dd></div><div><dt>Reģistrācijas Nr.</dt><dd>40008244382</dd></div><div><dt>Adrese</dt><dd>Tālavas gatve 3–10, Rīga, LV-1029</dd></div><div><dt>Konta numurs</dt><dd>LV36HABA0551053916043</dd></div></dl></aside></div></section><section class="section section-soft"><div class="shell quote-panel"><blockquote>“Vieta, kur sirds sastop dabu un kopiena kopīgi audzē bagātīgu nākotni.”</blockquote></div></section>'''

CONTACT = '''<section class="page-hero page-hero-contact"><div class="shell narrow"><p class="eyebrow">Sazinieties ar mums</p><h1>Kontakti</h1><p>Jautājumiem par biedrību un Lucavsalas mazdārziņiem sazinieties ar kādu no biedrības pārstāvjiem.</p></div></section><section class="section"><div class="shell contact-layout"><div><div class="section-heading"><p class="eyebrow">Biedrības pārstāvji</p><h2>Tālruņi</h2></div><div class="contact-list"><article class="contact-card"><h3>Aija Žvīgule</h3><p>Biedrības dibinātāja, galvenā pārvaldniece</p><a href="tel:+37129839163">+371 29 839 163</a></article><article class="contact-card"><h3>Regnārs Cīrulis</h3><p>Biedrības dibinātājs</p><a href="tel:+37129956760">+371 29 956 760</a></article><article class="contact-card"><h3>Kristīne Cīrule Miņjuka</h3><p>Valdes priekšsēdētāja</p><a href="tel:+37129590811">+371 29 590 811</a></article><article class="contact-card"><h3>Anda Sīpola</h3><p>Valdes locekle</p><a href="tel:+37129167538">+371 29 167 538</a></article></div></div><div class="form-panel"><p class="eyebrow">Rakstiet mums</p><h2>Kontaktu forma</h2><p>Norādiet savu vārdu, e-pasta adresi un jautājumu.</p><div class="setup-note">Forma vēl nav aktivizēta. Pirms publicēšanas izveidojiet bezmaksas Formspree formu un ievietojiet tās adresi failā <code>_config.yml</code>.</div><form class="contact-form" aria-disabled="true" onsubmit="return false"><label>Vārds</label><input type="text" disabled><label>Dārza Nr.</label><input type="text" disabled><label>E-pasts</label><input type="email" disabled><label>Ziņojums</label><textarea rows="7" disabled></textarea><button class="button button-primary" type="button" disabled>Nosūtīt ziņu</button></form></div></div></section>'''

if OUT.exists():
    shutil.rmtree(OUT)
(OUT / 'assets').mkdir(parents=True)
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)

pages = {
    'index.html': render_page('Sākums', 'home', home_content()),
    'jaunumi/index.html': render_page('Jaunumi', 'news', news_content()),
    'galerija/index.html': render_page('Galerija', 'gallery', gallery_content()),
    'par-mums/index.html': render_page('Par mums', 'about', ABOUT),
    'kontakti/index.html': render_page('Kontakti', 'contact', CONTACT),
}
for rel, output in pages.items():
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding='utf-8')
print(f'Built {len(pages)} pages in {OUT}')
