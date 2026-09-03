#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WEBCOPY.PY — полная офлайн-копия любой веб-страницы.

  1. python webcopy.py
  2. вставляешь ссылку в консоль
  3. получаешь папку copy_домен/ с рабочим index.html

Зависимости:  pip install requests beautifulsoup4
"""

import os
import re
import sys
import time
import hashlib
import webbrowser
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

# ─────────────────────── настройки ───────────────────────

TIMEOUT = 30                  # секунд на один файл
MAX_SIZE = 80 * 1024 * 1024   # файлы больше 80 МБ не тянем
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")

# ANSI-цвета для красивой консоли
C = {"ok": "\033[92m", "dim": "\033[90m", "warn": "\033[93m",
     "err": "\033[91m", "acc": "\033[96m", "end": "\033[0m"}

try:
    sys.stdout.reconfigure(encoding="utf-8")   # чиним юникод в Windows
except Exception:
    pass


def log(msg, kind="ok"):
    print(f"{C[kind]}{msg}{C['end']}")


def short(url, n=58):
    return url if len(url) <= n else url[: n - 1] + "…"


def banner():
    log("┌──────────────────────────────────────────────┐", "acc")
    log("│   WEBCOPY.PY — клонирую страницы целиком     │", "acc")
    log("└──────────────────────────────────────────────┘", "acc")


# расширение → тип ассета (папка в assets/)
EXT_KIND = {
    "css": "css", "js": "js", "mjs": "js",
    "png": "img", "jpg": "img", "jpeg": "img", "gif": "img",
    "webp": "img", "svg": "img", "ico": "img", "avif": "img",
    "woff": "fonts", "woff2": "fonts", "ttf": "fonts",
    "otf": "fonts", "eot": "fonts",
    "mp4": "media", "webm": "media", "mp3": "media",
    "wav": "media", "ogg": "media", "mov": "media",
}

# content-type → расширение (если в имени файла его нет)
MIME_EXT = {
    "text/css": "css", "javascript": "js", "ecmascript": "js",
    "font/woff2": "woff2", "font/woff": "woff",
    "font/ttf": "ttf", "font/otf": "otf",
    "image/svg+xml": "svg", "image/png": "png",
    "image/jpeg": "jpg", "image/webp": "webp",
    "image/gif": "gif", "image/avif": "avif",
    "video/mp4": "mp4", "audio/mpeg": "mp3",
}

# такие ссылки не скачиваем — они и так локальные/не файлы
SKIP_SCHEMES = ("data:", "mailto:", "javascript:", "tel:", "blob:", "#")


class PageCloner:
    """Скачивает страницу и всё, к чему она обращается."""

    def __init__(self, url):
        if "://" not in url:
            url = "https://" + url
        parsed = urlparse(url)
        if not parsed.netloc:
            log("Некорректный URL. Нужен вида https://site.com/page", "err")
            sys.exit(1)

        self.url = url
        self.host = parsed.netloc

        # папка copy_домен/, а если занята — copy_домен_2, _3 ...
        slug = re.sub(r"[^a-z0-9-]+", "-", parsed.netloc.lower()).strip("-")
        self.root = os.path.abspath(f"copy_{slug}")
        n = 2
        while os.path.exists(self.root):
            self.root = os.path.abspath(f"copy_{slug}_{n}")
            n += 1

        self.assets = {}       # абсолютный url -> локальный путь
        self.total_bytes = 0
        self.errors = 0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept": "*/*"})

        for sub in ("assets/css", "assets/js", "assets/img",
                    "assets/fonts", "assets/media", "assets/other"):
            os.makedirs(os.path.join(self.root, sub), exist_ok=True)

    # ─────────────────────── сеть ───────────────────────

    def fetch(self, url):
        try:
            r = self.session.get(url, timeout=TIMEOUT, stream=True)
            r.raise_for_status()
            size = int(r.headers.get("content-length", 0) or 0)
            if size > MAX_SIZE:
                log(f"  skip (>80 МБ)  {short(url)}", "warn")
                return None
            return r.content, r.headers.get("content-type", "").lower()
        except Exception as e:
            self.errors += 1
            log(f"  ! не скачал: {short(url)} ({type(e).__name__})", "warn")
            return None

    # ──────────────────── сохранение ────────────────────

    def save_asset(self, raw_url, base=None):
        if not raw_url:
            return None
        raw_url = raw_url.strip().strip("'").strip('"')
        if not raw_url or raw_url.lower().startswith(SKIP_SCHEMES):
            return None

        abs_url = urljoin(base or self.url, raw_url)

        if abs_url in self.assets:          # уже скачан — не тянем второй раз
            return self.assets[abs_url]

        got = self.fetch(abs_url)
        if got is None:
            return None                     # оставим ссылкой в сеть
        data, ctype = got

        # красивое имя файла по адресу
        path = unquote(urlparse(abs_url).path)
        name = os.path.basename(path.rstrip("/")) or "file"
        name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name)

        if "." not in name:                 # добиваем расширение по mime
            for key, ext in MIME_EXT.items():
                if key in ctype:
                    name += "." + ext
                    break
            else:
                name += ".bin"

        ext = name.rsplit(".", 1)[-1].lower()
        kind = EXT_KIND.get(ext, "other")

        final = os.path.join(self.root, "assets", kind, name)
        if os.path.exists(final):           # хэш против коллизий имён
            digest = hashlib.md5(abs_url.encode()).hexdigest()[:8]
            name = digest + "-" + name
            final = os.path.join(self.root, "assets", kind, name)

        if kind == "css":                   # css сначала переписываем
            css = data.decode("utf-8", errors="replace")
            rel = f"assets/{kind}/{name}"
            self.assets[abs_url] = rel      # до рекурсии — защита от циклов
            data = self.rewrite_css(css, abs_url, rel).encode("utf-8")
        else:
            rel = f"assets/{kind}/{name}"
            self.assets[abs_url] = rel

        with open(final, "wb") as f:
            f.write(data)

        self.total_bytes += len(data)
        log(f"  ✓ {rel:<46} {len(data) / 1024:8.1f} КБ")
        return rel

    # ─────────────── css: url() и @import ───────────────

    def rewrite_css(self, css, css_abs, css_rel):
        def rel_from(local):                # путь от css-файла до ассета
            start = os.path.dirname(css_rel) or "."
            return os.path.relpath(local, start).replace(os.sep, "/")

        def repl_url(m):
            q, target = m.group(1) or "", m.group(2).strip()
            if target.lower().startswith(SKIP_SCHEMES):
                return m.group(0)
            local = self.save_asset(target, base=css_abs)
            if not local:
                return f"url({q}{urljoin(css_abs, target)}{q})"
            return f"url({q}{rel_from(local)}{q})"

        def repl_import(m):
            q, target = m.group(1) or "", m.group(2).strip()
            local = self.save_asset(target, base=css_abs)
            if not local:
                return f"@import {q}{urljoin(css_abs, target)}{q}"
            return f"@import {q}{rel_from(local)}{q}"

        css = re.sub(r"url\(\s*([\"']?)([^)\"']+)\1\s*\)", repl_url, css)
        css = re.sub(r"@import\s+(?:url\()?\s*([\"'])([^\"']+)\1\s*\)?",
                     repl_import, css)
        return css

    # ─────────────── переписываем сам HTML ───────────────

    def rewrite_html(self, html):
        soup = BeautifulSoup(html, "html.parser")

        for b in soup.find_all("base"):     # <base> ломает локальные пути
            b.decompose()

        replaced = 0

        def grab(tag, attr):
            nonlocal replaced
            for el in soup.find_all(tag):
                val = el.get(attr)
                if not val:
                    continue
                if tag == "link":           # берём только css/иконки/шрифты
                    rels = " ".join(el.get("rel", [])).lower()
                    if rels and not any(k in rels for k in
                                        ("stylesheet", "icon", "preload")):
                        continue
                    if el.get("as") and el.get("as") not in ("style", "font", "image"):
                        continue
                local = self.save_asset(val)
                if local:
                    el[attr] = local
                    el.attrs.pop("integrity", None)   # иначе файл заблокируется
                    el.attrs.pop("crossorigin", None)
                    replaced += 1
                else:
                    el[attr] = urljoin(self.url, val)

        for tag, attr in (("link", "href"), ("script", "src"),
                          ("img", "src"), ("source", "src"),
                          ("video", "src"), ("video", "poster"),
                          ("audio", "src"), ("input", "src"),
                          ("embed", "src"), ("track", "src")):
            grab(tag, attr)
            # iframe src не трогаем: это чужие страницы, пусть грузятся из сети

        def grab_srcset():                  # srcset="кандидат 1x, кандидат 2x"
            nonlocal replaced
            for el in soup.find_all(True):
                ss = el.get("srcset")
                if not ss:
                    continue
                out = []
                for cand in ss.split(","):
                    cand = cand.strip()
                    if not cand:
                        continue
                    url_part, _, desc = cand.partition(" ")
                    local = self.save_asset(url_part)
                    out.append((local or urljoin(self.url, url_part))
                               + (" " + desc.strip() if desc.strip() else ""))
                    if local:
                        replaced += 1
                el["srcset"] = ", ".join(out)

        grab_srcset()

        for el in soup.find_all(style=True):            # style="...url(...) "
            el["style"] = self.rewrite_css(el["style"], self.url, "index.html")

        for st in soup.find_all("style"):               # <style> ... </style>
            if st.string:
                st.string.replace_with(
                    self.rewrite_css(st.string, self.url, "index.html"))

        return str(soup), replaced

    # ─────────────────────── запуск ───────────────────────

    def run(self):
        log(f"→ Цель:  {self.url}", "acc")
        log(f"→ Папка: {self.root}", "dim")

        got = self.fetch(self.url)
        if not got:
            log("Страница не скачалась — проверь ссылку и интернет.", "err")
            sys.exit(1)

        data, _ = got
        html = data.decode("utf-8", errors="replace")
        log(f"→ HTML получен ({len(html) / 1024:.1f} КБ), ищу ресурсы…", "acc")

        final_html, replaced = self.rewrite_html(html)

        index = os.path.join(self.root, "index.html")
        with open(index, "w", encoding="utf-8") as f:
            f.write(final_html)

        log(f"→ переписано ссылок: {replaced}", "acc")
        self.summary()
        return index

    def summary(self):
        kinds = {}
        for rel in self.assets.values():
            k = rel.split("/")[1]
            kinds[k] = kinds.get(k, 0) + 1

        print()
        log("─" * 54, "dim")
        log(f"  ГОТОВО: {self.host} склонирован", "acc")

        order = ("css", "js", "img", "fonts", "media", "other")
        items = [k for k in order if k in kinds]
        for i, k in enumerate(items):
            branch = "└──" if i == len(items) - 1 else "├──"
            log(f"  {branch} assets/{k:<7} ×{kinds[k]}", "dim")

        mb = self.total_bytes / 1024 / 1024
        log(f"  файлов: {len(self.assets):>4}   "
            f"размер: {mb:6.2f} МБ   ошибок: {self.errors}")
        log(f"  папка:  {self.root}", "dim")
        log("─" * 54, "dim")


def main():
    banner()
    try:
        url = input(f"\n{C['acc']}  Вставь ссылку на страницу → {C['end']}").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)

    if not url:
        log("Пусто. Нужен URL, например: https://example.com", "warn")
        sys.exit(1)

    t0 = time.time()
    try:
        index = PageCloner(url).run()
    except KeyboardInterrupt:
        log("\nОтменено пользователем.", "warn")
        sys.exit(130)

    log(f"⏱ {time.time() - t0:.1f} сек — открываю в браузере…", "acc")
    webbrowser.open("file://" + index)      # index.html откроется сам


if __name__ == "__main__":
    main()
