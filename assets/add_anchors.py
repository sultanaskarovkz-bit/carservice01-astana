# -*- coding: utf-8 -*-
"""Проставляет якоря на карточки услуг (для доп. ссылок в рекламе)."""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html')
html = io.open(p, encoding='utf-8').read()

ids = ['dvigatel', 'hodovaya', 'elektrika', 'injector', 'diagnostika']
old = '<article class="mod" data-mod>'

if 'id="dvigatel"' in html:
    print('якоря уже проставлены')
else:
    count = html.count(old)
    if count != len(ids):
        raise SystemExit('ожидалось %d карточек, найдено %d' % (len(ids), count))
    for i in ids:
        html = html.replace(old, '<article class="mod" data-mod id="%s">' % i, 1)
    io.open(p, 'w', encoding='utf-8').write(html)
    print('проставлено:', ', '.join('#' + i for i in ids))
