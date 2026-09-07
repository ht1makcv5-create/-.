"""Dependency-free static renderer. Content and connection facts live in content/*.json.

All internal URLs are relative so this exact output works on Sites and GitHub Pages.
No payment, registration or server administration is performed by this website.
"""
from pathlib import Path
from html import escape
import json
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
C = json.loads((ROOT / 'content/site.json').read_text())
G = json.loads((ROOT / 'content/guide.json').read_text())
BASE = os.environ.get('SITE_ORIGIN', C['canonicalBase']).rstrip('/')
ROUTE = ''
e = lambda s: escape(str(s), quote=True)


def url(path=''):
    return ('../' * len(ROUTE.strip('/').split('/')) if ROUTE else './') + path


def icon(name='arrow'):
    paths = {
        'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
        'external': '<path d="M14 4h6v6m0-6-10 10M10 4H4v16h16v-6"/>',
        'copy': '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M15 8V4H4v11h4"/>',
        'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
        'close': '<path d="m6 6 12 12M6 18 18 6"/>',
        'play': '<path d="m8 4 13 8-13 8Z"/>',
        'shield': '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Zm-4 9 3 3 5-6"/>',
        'map': '<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2Zm6-2v16m6-14v16"/>',
        'people': '<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m1-17a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 5v2"/>',
        'heart': '<path d="M20 5c-3-3-8 0-8 0s-5-3-8 0c-5 5 8 15 8 15S25 10 20 5Z"/>',
        'search': '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
        'monitor': '<rect x="3" y="3" width="18" height="13" rx="2"/><path d="M8 21h8m-4-5v5"/>',
        'phone': '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/>',
        'check': '<path d="m4 12 5 5L20 6"/>',
        'chevron': '<path d="m6 9 6 6 6-6"/>',
        'refresh': '<path d="M20 7V2l-3 3a8 8 0 1 0 3 12M20 7h-5"/>',
        'compass': '<circle cx="12" cy="12" r="9"/><path d="m16 8-3 5-5 3 3-5Z"/>'
    }
    return f'<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def link(path, label, cls='text-link', external=False, glyph='arrow'):
    href = path if external else url(path)
    extra = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return f'<a class="{cls}" href="{e(href)}"{extra}>{e(label)}{icon("external" if external else glyph)}{("<span class=\"sr-only\"> (нова вкладка)</span>" if external else "")}</a>'


def ext(key, label, cls='text-link'):
    return link(C['links'][key], label, cls, True)


def image(name, alt='', cls='', priority=False):
    load = 'fetchpriority="high"' if priority else 'loading="lazy"'
    return f'<img class="{cls}" src="{url("assets/"+name+".webp")}" srcset="{url("assets/"+name+"-640.webp")} 640w, {url("assets/"+name+".webp")} 1536w" sizes="(max-width: 640px) 100vw, (max-width: 1024px) 90vw, 65vw" alt="{e(alt)}" width="1536" height="1024" {load} decoding="async">'


def copy(value=None, label='Скопіювати IP', cls='button primary'):
    return f'<button type="button" class="{cls}" data-copy="{e(value or C["ip"])}">{icon("copy")}<span>{e(label)}</span></button>'


def ip_panel():
    return f'<div class="ip-panel"><div class="ip-label">АДРЕСА СЕРВЕРА</div><div class="ip-value"><code>{e(C["ip"])}</code>{copy(cls="icon-button",label="Копіювати IP")}</div><div class="ip-ports"><span>Java <b>{C["ports"]["java"]}</b></span><span>Bedrock <b>{C["ports"]["bedrock"]}</b></span></div></div>'


def status():
    return '<span class="status" data-status aria-live="polite"><span class="status-symbol" aria-hidden="true"></span><span data-status-label>Статус не перевірено</span></span>'


def notice(text, kind='info'):
    return f'<aside class="notice {kind}">{icon("shield")}<p>{e(text)}</p></aside>'


def intro(label, title, desc, action=''):
    return f'<div class="section-heading reveal"><div><p class="eyebrow">{e(label)}</p><h2>{title}</h2>{f"<p>{e(desc)}</p>" if desc else ""}</div>{action}</div>'


def cards(features):
    return '<div class="feature-grid">' + ''.join(f'<article class="feature reveal"><span class="index">0{i+1}</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i,(t,d) in enumerate(features)) + '</div>'


def breadcrumbs(title):
    return f'<nav class="breadcrumbs" aria-label="Навігаційний шлях"><a href="{url()}">Головна</a><span aria-hidden="true">/</span><span aria-current="page">{e(title)}</span></nav>'


def page_hero(label, title, desc, asset='hero', action=None, color='green'):
    return f'<section class="page-hero {color}"><div class="page-hero-image">{image(asset,"",priority=True)}</div><div class="wrap">{breadcrumbs(title)}<div class="page-hero-copy"><p class="eyebrow">{e(label)}</p><h1>{e(title)}</h1><p class="lead">{e(desc)}</p><div class="actions">{action or link("play/","Почати грати","button primary")}{link("servers/","Усі сервери","button ghost")}</div></div></div></section>'


def mode_cards():
    result = '<div class="mode-grid">'
    for i,m in enumerate(C['modes']):
        result += f'<article class="mode-card reveal {m["color"]} {"featured" if m["featured"] else ""}" data-tilt><a class="mode-art" href="{url(m["slug"]+"/")}" aria-label="Про режим {e(m["name"])}">{image(m["image"],m["tagline"])}<span class="mode-number">0{i+1} / {e(m["label"])}</span></a><div class="mode-content"><div class="mode-title"><h3><a href="{url(m["slug"]+"/")}">{e(m["name"])}</a></h3>{icon("arrow")}</div><p>{e(m["description"])}</p><div class="tags">'+''.join(f'<span>{e(t)}</span>' for t in m['tags'])+f'</div><div class="mode-actions">{link(m["slug"]+"/","Дізнатися більше")}{link("play/" if m["available"] else "offline/","Грати зараз" if m["available"] else "Тимчасово недоступний","small-link")}</div></div></article>'
    return result+'</div>'


def faq_list(limit=None):
    items = G['faq'][:limit] if limit else G['faq']
    return '<div class="faq-list">'+''.join(f'<details class="faq-item reveal"><summary>{e(x["question"])}{icon("chevron")}</summary><div><p>{e(x["answer"])}</p>{link(x["link"],x["label"])}</div></details>' for x in items)+'</div>'


def split_panel(asset, label, title, desc, action, extra='', flip=False, tone=''):
    return f'<section class="split-panel reveal {"flip" if flip else ""} {tone}"><div class="split-image">{image(asset,"")}</div><div class="split-copy"><p class="eyebrow">{e(label)}</p><h2>{title}</h2><p>{e(desc)}</p>{extra}<div class="actions">{action}</div></div></section>'


def home():
    hero=f'<section class="hero"><div class="hero-art">{image("hero","Нічне voxel-поселення з сяйливим порталом серед гір",priority=True)}</div><div class="particles" aria-hidden="true">'+''.join(f'<i style="--i:{i}"></i>' for i in range(14))+f'</div><div class="wrap hero-wrap"><div class="hero-copy"><p class="eyebrow"><span class="ua-flag" aria-hidden="true"></span> УКРАЇНСЬКИЙ MINECRAFT-СЕРВЕР</p><h1>ЧАС МАЙНИТИ<br>ТА <em>КРАФТИТИ.</em></h1><p class="lead">Від першого блоку до великих пригод.<br>Знаходь своїх. Будуй своє.</p><div class="actions">{link("play/","Почати грати","button primary",glyph="play")}{link("servers/","Переглянути сервери","button ghost")}</div><div class="hero-discord">{ext("discord","Приєднатися до Discord")}</div>{ip_panel()}<div class="hero-platforms"><span>{icon("monitor")} JAVA EDITION</span><span>{icon("phone")} BEDROCK EDITION</span></div></div><div class="hero-caption"><span>ТВОЯ НАСТУПНА ПРИГОДА</span><b>Починається тут.</b></div></div><div class="hero-bottom wrap">{status()}<a href="#worlds">ДОСЛІДЖУЙ СВІТИ {icon("chevron")}</a><span>PC + MOBILE</span></div></section>'
    worlds=f'<section id="worlds" class="section wrap">{intro("01 / ОБЕРИ СВІЙ ШЛЯХ","Один сервер.<br><em>Різні світи.</em>","Затишне виживання, масштабні будівлі чи повна невідомість — з чого почнеш ти?",link("servers/","Усі режими"))}{mode_cards()}</section>'
    features=f'<section class="section section-lined"><div class="wrap">{intro("02 / МІСЦЕ ДЛЯ СВОЇХ","Більше, ніж блоки.","")}{cards([("Грай на своєму пристрої","Спільна адреса для Java на ПК та Bedrock на телефоні або планшеті."),("Будуй разом","Знайомся, знаходь команду й берись за проєкт, який давно хотів створити."),("Знай, куди звернутися","Правила, інструкції та зв’язок із командою завжди під рукою.")])}</div></section>'
    explore='<div class="wrap section">'+split_panel('map','03 / СВІТ БЕЗ КРАЮ','Зазирни за<br><em>горизонт.</em>','Переглядай біоми, знаходь координати та плануй подорожі на карті ВаніллаПлюс.',ext('map','Відкрити карту','button ghost'),'<p class="caption">Ілюстрація світу. Актуальна карта відкриється в новій вкладці.</p>')+split_panel('discord','04 / НАШІ ЛЮДИ','Пригоди кращі,<br><em>коли разом.</em>','Знайди напарника, обговори свою будівлю, прочитай оголошення або звернися по допомогу.',ext('discord','Приєднатися до Discord','button purple'),'<div class="tags"><span>Спілкування</span><span>Оголошення</span><span>Підтримка</span></div>',True,'violet')+'</div>'
    play=f'<section class="section section-lined"><div class="wrap">{intro("05 / ПЕРШИЙ КРОК","Твій світ чекає.","Усе потрібне для першого входу — в одній інструкції.",link("play/","Як почати грати"))}<ol class="steps compact"><li><span>01</span><h3>Відкрий Minecraft</h3><p>Java на ПК або Bedrock на мобільному.</p></li><li><span>02</span><h3>Додай сервер</h3><p><code>{e(C["ip"])}</code></p></li><li><span>03</span><h3>Заходь у гру</h3><p>Пройди реєстрацію за підказкою в чаті.</p></li></ol></div></section>'
    donate='<div class="wrap section">'+split_panel('donate','06 / ПІДТРИМКА ПРОЄКТУ','Допоможи світу<br><em>жити далі.</em>','Добровільна підтримка допомагає утримувати сервер. Умови й доступні можливості — на офіційній сторінці.',link('donate/','Про підтримку','button gold'),tone='gold-tone')+'</div>'
    faq=f'<section class="section wrap faq-section">{intro("07 / КОРОТКО ПРО ГОЛОВНЕ","Залишились питання?","",link("faq/","Усі відповіді"))}{faq_list(4)}</section>'
    return hero+worlds+features+explore+play+donate+faq


def servers():
    return page_hero('СЕРВЕРИ','Знайди свій світ.','Чотири різні способи провести вечір. Почни з того, що ближче тобі.','creative')+f'<section class="wrap section"><h2 class="sr-only">Режими гри</h2>{mode_cards()}<div class="notice"><p>Інші режими й повний перелік серверів дивись у меню офіційного сайту.</p>{link(C["officialUrl"],"Офіційний сайт",external=True)}</div></section>'


def mode_page(m):
    cta = ext('discord','Подати заявку у Discord','button primary') if m['slug']=='whitelist' else link('play/','Почати грати','button primary')
    features='<h2 class="sr-only">Можливості режиму</h2>'+cards(m['features'])
    extra=''
    if m['slug']=='creative':
        extra='<h2>Перші команди будівельника</h2><div class="command-mini">'+''.join(f'<div><code>{cmd}</code><span>{desc}</span>{copy(cmd,"Копіювати команду","icon-button")}</div>' for cmd,desc in [('/plot auto','Отримати вільну ділянку'),('/plot home','Повернутися на ділянку'),('/plot info','Дані твоєї ділянки')])+'</div>'
    if m['slug']=='whitelist':
        extra=f'<h2>Як подати заявку</h2><ol class="steps"><li><span>01</span><h3>Зайди у Discord</h3><p>Відкрий спільноту Minecrafter.</p></li><li><span>02</span><h3>Заповни форму</h3><p>Канал «вайтлист-вхід».</p></li><li><span>03</span><h3>Дочекайся відповіді</h3><p>Команда розгляне заявку в Discord.</p></li></ol>{ext("whitelistRules","Повні правила ВайтЛиста")}'
    if m['slug']=='anarchy':
        extra=f'<h2>Перехід з хабу</h2><div class="command-mini"><div><code>/server anarchy</code>{copy("/server anarchy","Копіювати команду","icon-button")}</div></div>'
    return page_hero(m['label'],m['name'],m['tagline'],m['image'],cta,m['color'])+f'<section class="section wrap"><p class="big-intro">{e(m["description"])}</p>{features}<div class="detail-layout"><article class="prose">{extra}<h2>Перед тим як вирушити</h2>{notice(m["note"])}<p>Повний опис, актуальні можливості та додаткові умови публікує команда режиму.</p>{link(m["source"],"Офіційний опис режиму",external=True)}<div class="actions">{link("rules/","Правила гри","button ghost")}{link("commands/","Корисні команди","button ghost")}{link("private/","Захист території","button ghost")}</div></article><aside class="side-card"><p class="eyebrow">ПІДКЛЮЧЕННЯ</p>{ip_panel()}<p>{e(C["versionNote"])}</p>{cta}</aside></div></section>'


def guide_steps(edition):
    java=edition=='java'
    steps=[('Запусти гру','Відкрий Minecraft Java Edition у своєму лаунчері.' if java else 'Відкрий Minecraft Bedrock Edition на телефоні або планшеті.'),('Відкрий список серверів','Обери «Гра в мережі» (Multiplayer), потім «Додати сервер» (Add Server).' if java else 'Обери «Грати» → «Сервери» → «Додати сервер».'),('Впиши адресу',C['ip']+('. Стандартний порт Java можна не вказувати.' if java else f'. У полі порту вкажи {C["ports"]["bedrock"]}.')),('Приєднайся','Збережи сервер і відкрий його. Далі виконай підказку реєстрації в чаті.')]
    return '<ol class="steps guide-steps">'+''.join(f'<li><span>0{i+1}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i,(t,d) in enumerate(steps))+'</ol>'


def play(edition=None):
    title={'java':'Почни грати на ПК.','bedrock':'Світ у твоїй кишені.'}.get(edition,'До пригод — кілька кроків.')
    body=page_hero('ЯК ПОЧАТИ ГРАТИ',title,'Вибери свою версію гри та додай адресу сервера.','howtoplay',copy())
    tabs=''
    if not edition:
        tabs=f'<div class="edition-tabs" aria-label="Версія Minecraft"><a href="{url("play/java/")}" class="button ghost" data-edition="java">{icon("monitor")}Java Edition · ПК</a><a href="{url("play/bedrock/")}" class="button ghost" data-edition="bedrock">{icon("phone")}Bedrock · мобільний</a></div>'
    steps=''.join(f'<section id="guide-{ed}" data-guide="{ed}"><h2>{"Java Edition" if ed=="java" else "Bedrock Edition"}</h2>{guide_steps(ed)}</section>' for ed in ([edition] if edition else ['java','bedrock']))
    return body+f'<section class="section wrap"><div class="detail-layout"><div>{tabs}{steps}<article class="prose"><h2>Перший вхід</h2><p>Введи команду, яку просить ігровий чат. Заміни слово ПАРОЛЬ своїм паролем.</p><div class="code-block"><span>РЕЄСТРАЦІЯ</span><code>/reg ПАРОЛЬ ПАРОЛЬ</code></div><div class="code-block"><span>НАСТУПНИЙ ВХІД</span><code>/login ПАРОЛЬ</code></div>{notice("Створи окремий складний пароль для гри. Не використовуй пароль від пошти та не надсилай його іншим гравцям.")}<div class="actions">{link("faq/","Допомога з підключенням","button ghost")}{ext("discord","Запитати у Discord","button ghost")}</div></article></div><aside class="side-card">{ip_panel()}<h2>Версія гри</h2><p>{e(C["versionNote"])}</p>{link(C['officialUrl']+'play/',"Оригінальна інструкція",external=True)}</aside></div></section>'


def commands():
    categories=list(dict.fromkeys(x[2] for x in G['commands']))
    filters='<div class="filter-bar" aria-label="Категорія команд">'+''.join(f'<button class="filter-chip" type="button" data-category="{e(c)}" aria-pressed="{str(c=="Усі").lower()}">{e(c)}</button>' for c in ['Усі']+categories)+'</div>'
    rows=''.join(f'<tr data-command data-category-name="{e(cat)}"><td><code>{e(cmd)}</code></td><td>{e(desc)}</td><td><span class="tag">{e(cat)}</span></td><td>{copy(cmd,"Копіювати команду","icon-button")}</td></tr>' for cmd,desc,cat in G['commands'])
    return page_hero('ДОВІДНИК','Команда знайдеться.','Пошук і короткі пояснення основних команд ВаніллаПлюс.','rules')+f'<section class="section wrap"><div class="search-box">{icon("search")}<label class="sr-only" for="command-search">Знайти команду або дію</label><input id="command-search" type="search" placeholder="Спробуй «дім», «приват» або /spawn" autocomplete="off"></div>{filters}<p class="caption" id="command-count" aria-live="polite">{len(G["commands"])} команд</p><div class="table-scroll"><table class="command-table"><caption class="sr-only">Команди сервера ВаніллаПлюс</caption><thead><tr><th scope="col">Команда</th><th scope="col">Що робить</th><th scope="col">Категорія</th><th scope="col"><span class="sr-only">Копіювання</span></th></tr></thead><tbody>{rows}</tbody></table></div><div class="empty-state" id="command-empty" hidden><h2>Такої команди не знайшли.</h2><p>Спробуй інше слово або вибери «Усі».</p><button type="button" class="button ghost" data-reset-search>Скинути пошук</button></div><div class="notice"><p>Доступність команд залежить від режиму та прав гравця. Скопійовані параметри «назва» й «нік» потрібно замінити своїми.</p>{ext("commands","Повний довідник")}</div></section>'


def private():
    steps=[('Візьми інструмент','Отримай дерев’яну сокиру командою //wand.'),('Виділи територію','ЛКМ і ПКМ познач два протилежні кути об’єму. На Bedrock зручно використовувати //pos1 та //pos2.'),('Збережи регіон','Введи /rg claim назва. Обери назву латиницею без пробілів.'),('Перевір захист','Стань усередині та введи /rg i. Переконайся, що регіон належить тобі.')]
    return page_hero('ЗАХИСТ ТЕРИТОРІЇ','Спочатку приват.<br>Потім великий дім.'.replace('<br>',' '),'Захисти свою працю перед тим, як поставиш першу скриню.','rules')+f'<section class="section wrap"><ol class="steps guide-steps">'+''.join(f'<li><span>0{i+1}</span><h2>{e(t)}</h2><p>{e(d)}</p></li>' for i,(t,d) in enumerate(steps))+f'</ol><div class="prose"><h2>Твій дім — твоя відповідальність</h2><p>Приват — це об’єм, тому врахуй підвал і дах. Не додавай випадкових гравців до учасників.</p>{notice("Якщо регіон не створюється, не залишай цінні речі без захисту. Збережи текст помилки й звернися до команди.")}<div class="actions">{ext("private","Повна інструкція з приватів","button primary")}{link("contact/","Потрібна допомога","button ghost")}</div></div></section>'


def rules():
    return page_hero('ПРАВИЛА СПІЛЬНОТИ','Поважай світ.<br>Поважай інших.'.replace('<br>',' '),'Короткий орієнтир перед грою. Повні правила та умови режиму мають пріоритет.','rules',ext('rules','Читати повні правила','button primary'))+f'<section class="section wrap"><h2 class="sr-only">Основні принципи</h2>{cards(G["rules"])}<div class="actions">{ext("rules","Основні правила","button ghost")}{ext("whitelistRules","Правила ВайтЛиста","button ghost")}{link("bans/","Бани та мути","button ghost")}</div></section>'


def map_page():
    return page_hero('КАРТА ВАНІЛЛАПЛЮС','Куди вирушимо?','Плануй маршрут, шукай біоми й орієнтуйся у світі.','map',ext('map','Відкрити живу карту','button primary'))+f'<section class="section wrap">{intro("ІНТЕРАКТИВНА КАРТА","Світ ближче, ніж здається.","Актуальні координати та доступні шари показує окремий сервіс карти.")}<figure class="map-preview">{image("map","Художня ілюстрація кубічного світу з різними біомами")}<figcaption>Художня ілюстрація — не знімок поточного ігрового світу.</figcaption></figure><div class="actions">{ext("map","Перейти до інтерактивної карти","button primary")}{link("contact/","Карта не відкривається?","button ghost")}</div></section>'


def donate(auto=False):
    title='Підтримка без зайвих кроків.' if auto else 'Світ, який ми будуємо разом.'
    return page_hero('АВТО-ДОНАТ' if auto else 'ПІДТРИМКА ПРОЄКТУ',title,'Добровільна підтримка розвитку й утримання Minecrafter.','donate',ext('donate','Офіційна сторінка донату','button gold'),'gold-tone')+f'<section class="section wrap"><div class="detail-layout"><article class="prose"><h2>Як це працює</h2><ol class="steps guide-steps"><li><span>01</span><h3>Перевір умови</h3><p>На офіційній сторінці уточни режим і доступні можливості.</p></li><li><span>02</span><h3>Вкажи ігровий нік</h3><p>Для автоматичного зарахування в коментарі до платежу має бути лише твій нік.</p></li><li><span>03</span><h3>Перевір зарахування</h3><p>У грі відкрий /donate_money. Меню можливостей — /donate.</p></li></ol>{notice("Помилка в ніку або зайві слова в коментарі можуть затримати зарахування. Якщо це сталося, збережи підтвердження платежу і звернися до адміністрації.")}<h2>Умови підтримки</h2><p>Пожертва добровільна. Актуальну оферту, правила зарахування та умови повернення прочитай на офіційному сайті перед платежем.</p><div class="actions">{ext("donateTerms","Оферта та правила донату","button ghost")}{link("terms/","Про умови підтримки","button ghost")}</div></article><aside class="side-card"><p class="eyebrow">ПЕРЕД ПЕРЕХОДОМ</p><h2>Перевір свій нік.</h2><p>Платіжні дані вводяться тільки на офіційній сторінці.</p>{ext("donate","Перейти до донату","button gold")}{link("contact/","Питання щодо платежу")}</aside></div></section>'


def discord():
    return page_hero('DISCORD СПІЛЬНОТА','Твої люди вже тут.','Поговорити, зібрати команду, поділитися ідеєю. Навіть коли ти поза грою.','discord',ext('discord','Приєднатися до Discord','button purple'),'violet')+f'<section class="section wrap"><h2 class="sr-only">Можливості спільноти</h2>{cards([("Знайди напарника","Обговори спільну пригоду або познайомся з майбутніми сусідами."),("Не пропусти оголошення","Стеж за новинами та інформацією про події."),("Отримай відповідь","Запитай спільноту або створи звернення до адміністрації.")])}<div class="actions">{ext("discord","Відкрити спільноту","button purple")}{ext("support","Запит до адміністрації","button ghost")}</div></section>'


def contact(team=False):
    members=''.join(f'<article class="team-card reveal"><div class="avatar" aria-hidden="true">{e(m["name"][0].upper())}</div><p class="caption">{e(m["role"])}</p><h3>{e(m["name"])}</h3><code>{e(m["nickname"])}</code>{link(m["url"],"Discord",external=True) if m["url"] else ext("support","Через запит до команди")}</article>' for m in C['team'])
    return page_hero('КОМАНДА' if team else 'КОНТАКТИ','Команда на зв’язку.','Знайдемо відповідь, допоможемо з підключенням і розберемо звернення.','contacts',ext('support','Створити запит','button primary'))+f'<section class="section wrap"><div class="contact-callout"><div><p class="eyebrow">НАЙЗРУЧНІШИЙ СПОСІБ</p><h2>Запит до адміністрації</h2><p>Вкажи свій нік, режим, час і суть проблеми. Додай скриншоти, якщо вони допоможуть.</p></div>{ext("support","Відкрити канал запитів","button primary")}</div>{intro("ЛЮДИ ПРОЄКТУ","Хто допомагає спільноті.","Контакти з офіційної сторінки проєкту.")}<div class="team-grid">{members}</div><p class="caption">Склад команди може змінюватися. Перевірено {e(C["checkedOn"])}.</p>{ext("contact","Актуальні контакти")}</section>'


def news(events=False):
    entries=C['events' if events else 'news']
    title='Наступна пригода — спільна.' if events else 'Що нового у світі?'
    body=page_hero('ІВЕНТИ' if events else 'НОВИНИ',title,'Анонси, оновлення та важливі повідомлення публікує команда в Discord.','discord',ext('discord','Переглянути оголошення','button purple'),'violet')
    if entries:
        content='<div class="feature-grid">'+''.join(f'<article class="feature"><time datetime="{e(x["date"])}">{e(x["date"])}</time><h2>{e(x["title"])}</h2><p>{e(x["description"])}</p>{link(x["url"],"Переглянути",external=True)}</article>' for x in entries)+'</div>'
    else:
        content=f'<div class="empty-state"><p class="eyebrow">ОГОЛОШЕННЯ У DISCORD</p><h2>{"Перевір розклад у спільноті." if events else "Останні повідомлення — від команди."}</h2><p>{"Дати й умови найближчих подій дивись у каналах оголошень." if events else "Відкрий Discord, щоб прочитати актуальні новини без затримки."}</p>{ext("discord","Перейти до Discord","button purple")}</div>'
    return body+f'<section class="section wrap">{content}</section>'


def faq():
    return page_hero('FAQ','Відповіді перед пригодою.','Підключення, версії, привати та допомога.','howtoplay',link('contact/','Поставити запитання','button primary'))+f'<section class="section wrap reading">{faq_list()}<div class="actions">{ext("faq","Офіційна база відповідей","button ghost")}</div></section>'


def bans():
    return page_hero('МОДЕРАЦІЯ','Бани та мути.','Переглянь чинний список покарань або звернися до команди щодо свого випадку.','rules',ext('bans','Відкрити список покарань','button primary'))+f'<section class="section wrap reading"><h2>Є питання щодо рішення?</h2><p>У зверненні вкажи нік, сервер і причину звернення. Не публікуй пароль або особисті дані.</p><div class="actions">{ext("support","Звернутися до адміністрації","button primary")}{link("rules/","Прочитати правила","button ghost")}</div></section>'


def offline(loading=False):
    return page_hero('СТАТУС ПІДКЛЮЧЕННЯ','Перевіримо зв’язок.' if loading else 'Не вдається зайти?','Перевір адресу й версію гри. Якщо проблема залишається — зазирни до оголошень.','lost',copy())+f'<section class="section wrap reading"><div class="status-card">{status()}<p class="caption" data-status-time>Дані отримуються із зовнішнього сервісу перевірки.</p><button class="button ghost" type="button" data-refresh-status>{icon("refresh")}Перевірити статус</button></div>{notice("Відсутність відповіді сервісу перевірки не завжди означає, що ігровий сервер вимкнений.")}<div class="actions">{link("play/","Перевірити підключення","button primary")}{ext("discord","Оголошення команди","button ghost")}</div></section>'


def terms():
    return page_hero('УМОВИ ПІДТРИМКИ','Спочатку прочитай умови.','Важлива інформація перед добровільною підтримкою проєкту.','donate',ext('donateTerms','Читати офіційну оферту','button gold'))+f'<section class="section wrap reading prose"><h2>Офіційна оферта</h2><p>Актуальний текст умов розміщений на сторінці авто-донату Minecrafter. Там описані призначення пожертв, зарахування на акаунт і обмеження повернення.</p><p>Ця сторінка допомагає знайти оригінальні умови. Перед переказом прочитай їх повністю та уточни незрозумілі питання в адміністрації.</p><div class="actions">{ext("donateTerms","Відкрити повний текст","button gold")}{link("contact/","Запитати про умови","button ghost")}</div></section>'


def lost():
    return page_hero('404 / НЕВІДОМИЙ БІОМ','Здається, ми заблукали.','Цієї сторінки немає. Повернімося туди, де починаються пригоди.','lost',link('','На головну','button primary'))


NAV=[('servers/','Сервери'),('play/','Як грати'),('commands/','Довідник'),('map/','Карта'),('discord/','Спільнота')]


def shell(content,title,description,noindex=False):
    nav=''.join(f'<a href="{url(path)}" {"aria-current=\"page\"" if ROUTE==path else ""}>{e(label)}</a>' for path,label in NAV)
    brand=f'<a class="brand" href="{url()}" aria-label="Minecrafter — головна"><span class="brand-mark" aria-hidden="true">M</span><span>MINECRAFTER<small>IN.UA</small></span></a>'
    footer_links=[('servers/','Сервери'),('play/','Як почати грати'),('commands/','Команди'),('private/','Привати'),('rules/','Правила'),('faq/','FAQ'),('map/','Карта'),('donate/','Підтримка'),('autodonate/','Авто-донат'),('discord/','Discord'),('news/','Новини'),('events/','Івенти'),('team/','Команда'),('bans/','Бани та мути'),('contact/','Контакти'),('offline/','Проблеми з входом')]
    canonical=BASE+'/'+ROUTE
    preview_asset=next((m['image'] for m in C['modes'] if ROUTE==m['slug']+'/'),'hero')
    social=f'<meta property="og:image" content="{e(BASE+"/assets/"+preview_asset+".webp")}"><meta property="og:image:alt" content="Оригінальна voxel-ілюстрація Minecrafter"><meta name="twitter:image" content="{e(BASE+"/assets/"+preview_asset+".webp")}">'
    jsonld=json.dumps({'@context':'https://schema.org','@type':'WebSite','name':C['name'],'url':BASE+'/'},ensure_ascii=False).replace('<','\\u003c')
    runtime=json.dumps({'ip':C['ip'],'status':C['status']},ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090f12"><title>{e(title)} — Minecrafter</title><meta name="description" content="{e(description)}"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow'}"><link rel="canonical" href="{e(canonical)}"><meta property="og:title" content="{e(title)} — Minecrafter"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:locale" content="uk_UA"><meta property="og:url" content="{e(canonical)}"><meta name="twitter:card" content="summary_large_image">{social}<link rel="icon" href="{url('assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{url('assets/site.css')}"><script type="application/ld+json">{jsonld}</script><script type="application/json" id="site-config">{runtime}</script><script src="{url('assets/site.js')}" defer></script></head>
<body><a class="skip-link" href="#main">Перейти до вмісту</a><div class="scroll-progress" aria-hidden="true"></div><header class="header"><div class="header-inner">{brand}<nav class="desktop-nav" aria-label="Головна навігація">{nav}</nav><div class="header-actions">{link('play/','Грати зараз','button primary small')}<button type="button" class="icon-button menu-toggle" data-open-menu aria-label="Відкрити меню" aria-controls="mobile-menu" aria-expanded="false">{icon('menu')}</button></div></div></header>
<dialog id="mobile-menu" class="mobile-menu" aria-label="Навігація"><div class="mobile-menu-head">{brand}<button type="button" class="icon-button" data-close-menu aria-label="Закрити меню">{icon('close')}</button></div><nav aria-label="Мобільна навігація">{nav}{link('rules/','Правила')}{link('donate/','Підтримка')}</nav>{ip_panel()}</dialog>
<main id="main">{content}</main><section class="final-cta wrap"><div><p class="eyebrow">ПОБАЧИМОСЬ У ГРІ</p><h2>Твоя історія починається<br><em>з одного блоку.</em></h2></div><div>{link('play/','Почати грати','button primary')}{link('contact/','Зв’язатися з командою')}</div></section><footer class="footer"><div class="wrap"><div class="footer-top"><div>{brand}<p>Український Minecraft-сервер.<br>Знаходь своїх. Будуй своє.</p>{copy(cls='button ghost',label='Скопіювати IP')}</div><nav aria-label="Усі сторінки">{''.join(f'<a href="{url(p)}">{e(l)}</a>' for p,l in footer_links)}</nav></div><div class="footer-bottom"><span>Minecrafter · Українська спільнота</span><span>Не є офіційним продуктом Mojang або Microsoft.</span>{link('terms/','Умови підтримки','small-link')}{link(C['officialUrl'],'Офіційний сайт',external=True,cls='small-link')}</div></div></footer><div class="mobile-bottom"><div><span>JAVA + BEDROCK</span><code>{e(C['ip'])}</code></div>{copy(label='Копіювати',cls='button primary small')}</div><div class="toast" id="toast" role="status" aria-live="polite"></div><dialog id="copy-fallback" class="copy-dialog" aria-labelledby="copy-title"><button type="button" class="icon-button dialog-close" data-close-copy aria-label="Закрити">{icon('close')}</button><h2 id="copy-title">Скопіюй вручну</h2><p>Виділи текст і скористайся копіюванням на своєму пристрої.</p><label for="copy-value">Текст для копіювання</label><input id="copy-value" readonly></dialog><noscript><div class="noscript-note">Адреса для ручного копіювання: {e(C['ip'])}. Навігація та інструкції доступні без JavaScript.</div></noscript></body></html>'''


PAGES=[
 ('',home,'Час майнити та крафтити','Український Minecraft-сервер: виживання, Креатив, ВайтЛист та Анархія. Грай на Java і Bedrock.'),
 ('servers/',servers,'Сервери','Обери режим Minecraft: ВаніллаПлюс, Креатив, ВайтЛист або Анархія.'),
 *[(m['slug']+'/',lambda m=m:mode_page(m),m['name'],m['description']) for m in C['modes']],
 ('play/',play,'Як почати грати','Покрокове підключення до українського Minecraft-сервера з Java та Bedrock.'),
 ('play/java/',lambda:play('java'),'Minecraft Java: підключення з ПК','Інструкція для Minecraft Java Edition: адреса сервера, порт, реєстрація.'),
 ('play/bedrock/',lambda:play('bedrock'),'Minecraft Bedrock: підключення з телефона','Як додати Minecrafter у Minecraft Bedrock на телефоні або планшеті.'),
 ('commands/',commands,'Команди ВаніллаПлюс','Знайди та скопіюй команду: дім, телепортація, привати, магазин, клан.'),
 ('private/',private,'Як створити приват','Захист території: виділення регіону, створення та перевірка привату.'),
 ('rules/',rules,'Правила сервера','Короткий огляд правил Minecrafter і посилання на повні умови режимів.'),
 ('faq/',faq,'Часті запитання','Відповіді щодо входу, версій гри, ВайтЛиста, приватів та допомоги.'),
 ('map/',map_page,'Інтерактивна карта','Відкрий живу карту світу ВаніллаПлюс і сплануй наступну подорож.'),
 ('donate/',donate,'Підтримати проєкт','Як добровільно підтримати Minecrafter та перевірити умови донату.'),
 ('autodonate/',lambda:donate(True),'Авто-донат','Інструкція автоматичного зарахування донату на ігровий нік.'),
 ('discord/',discord,'Discord спільнота','Спілкування, оголошення, пошук напарників і допомога у Discord Minecrafter.'),
 ('contact/',contact,'Контакти адміністрації','Звернення до команди та офіційні контакти адміністраторів, модераторів і хелперів.'),
 ('team/',lambda:contact(True),'Команда проєкту','Люди, які допомагають спільноті Minecrafter, та їхні контакти.'),
 ('news/',news,'Новини','Останні оголошення й новини Minecrafter в офіційній спільноті.'),
 ('events/',lambda:news(True),'Івенти','Де знайти актуальні анонси подій та розклад івентів Minecrafter.'),
 ('bans/',bans,'Бани та мути','Офіційний список покарань та спосіб звернутися до адміністрації.'),
 ('offline/',offline,'Допомога з підключенням','Перевірка статусу сервера та допомога, коли Minecraft не підключається.'),
 ('loading/',lambda:offline(True),'Перевірка зв’язку','Дізнайся, чи відповідає ігровий сервер Minecrafter.'),
 ('terms/',terms,'Умови підтримки','Де прочитати офіційну оферту та уточнити умови добровільної підтримки.'),
]


def build():
    global ROUTE
    for route,render,title,desc in PAGES:
        ROUTE=route
        destination=OUT/route/'index.html'
        destination.parent.mkdir(parents=True,exist_ok=True)
        rendered=shell(render(),title,desc,noindex=route in ['loading/','offline/'])
        destination.write_text(rendered)
    ROUTE=''
    missing=shell(lost(),'Сторінку не знайдено','Повернися на головну Minecrafter.',True)
    # A 404 is served at an arbitrary URL depth. Absolute links remain correct there.
    for attribute in ['href','src','srcset']:
        missing=missing.replace(attribute+'="./',attribute+'="'+BASE+'/')
    missing=missing.replace(', ./',', '+BASE+'/')
    (OUT/'404.html').write_text(missing)
    (OUT/'.nojekyll').touch()
    routes=[r for r,_,_,_ in PAGES if r not in ['offline/','loading/']]
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(BASE+"/"+r)}</loc></url>' for r in routes)+'</urlset>')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    print(f'Rendered {len(PAGES)} pages plus 404, sitemap and robots.txt.')


if __name__=='__main__':
    build()
