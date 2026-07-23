# -*- coding: utf-8 -*-
"""Сборка плоского ZIP для хостинга (прямые слэши, без служебных файлов)."""
import zipfile, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZPATH = os.path.join(ROOT, 'carservice01-site.zip')

include_files = ['index.html', 'favicon.ico', '.htaccess',
                 'robots.txt', 'sitemap.xml', 'site.webmanifest']
include_dirs = ['assets', 'video']
exclude = {'assets/gen_assets.py', 'assets/build_zip.py'}

if os.path.exists(ZPATH):
    os.remove(ZPATH)

z = zipfile.ZipFile(ZPATH, 'w', zipfile.ZIP_DEFLATED)
for f in include_files:
    p = os.path.join(ROOT, f)
    if os.path.exists(p):
        z.write(p, f)                      # arcname с прямыми слэшами
for d in include_dirs:
    base = os.path.join(ROOT, d)
    for dp, _, files in os.walk(base):
        for fn in files:
            full = os.path.join(dp, fn)
            arc = os.path.relpath(full, ROOT).replace(os.sep, '/')
            if arc in exclude:
                continue
            z.write(full, arc)
z.close()

zz = zipfile.ZipFile(ZPATH)
bad = zz.testzip()
print('testzip:', 'OK' if bad is None else bad)
print('entries:', len(zz.namelist()))
for n in sorted(zz.namelist()):
    print(' ', n)
print('size MB:', round(os.path.getsize(ZPATH) / 1048576, 2))
