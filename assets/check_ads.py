# -*- coding: utf-8 -*-
"""Проверка лимитов Google Ads по текстам из ADS-PLAN.md."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
txt = io.open(os.path.join(ROOT, 'ADS-PLAN.md'), encoding='utf-8').read()

LIM = {'Заголовки': 30, 'Описания': 90}
problems = []
checked = 0

# --- заголовки и описания RSA ---
for m in re.finditer(r'\*\*(Заголовки|Описания)[^*]*\*\*\s*\n```\n(.*?)```', txt, re.S):
    kind, block = m.group(1), m.group(2)
    limit = LIM[kind]
    for line in [l.strip() for l in block.strip().split('\n') if l.strip()]:
        checked += 1
        if len(line) > limit:
            problems.append('%s (%d>%d): %s' % (kind, len(line), limit, line))

# --- сайтлинки: таблица в §7 ---
for line in txt.split('\n'):
    if line.startswith('| ') and 'carservice01.kz/#' in line:
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) >= 4:
            text, _url, d1, d2 = cells[0], cells[1], cells[2], cells[3]
            checked += 3
            if len(text) > 25:
                problems.append('Сайтлинк текст (%d>25): %s' % (len(text), text))
            for d in (d1, d2):
                if len(d) > 35:
                    problems.append('Сайтлинк описание (%d>35): %s' % (len(d), d))

# --- уточнения (callouts) ---
m = re.search(r'### Уточнения[^\n]*\n```\n(.*?)```', txt, re.S)
if m:
    for line in [l.strip() for l in m.group(1).strip().split('\n') if l.strip()]:
        checked += 1
        if len(line) > 25:
            problems.append('Уточнение (%d>25): %s' % (len(line), line))

# --- структурированные описания ---
m = re.search(r'Тип заголовка: \*\*Услуги\*\*\n```\n(.*?)```', txt, re.S)
if m:
    for v in [v.strip() for v in m.group(1).replace('\n', ' ').split('·') if v.strip()]:
        checked += 1
        if len(v) > 25:
            problems.append('Структ. описание (%d>25): %s' % (len(v), v))

print('Проверено строк:', checked)
if problems:
    print('\nПРЕВЫШЕНИЯ ЛИМИТОВ (%d):' % len(problems))
    for p in problems:
        print('  -', p)
    sys.exit(1)
print('OK — все тексты в лимитах Google Ads')
