#!/usr/bin/env python3
"""Почтовая рассылка клиентам через SMTP (по умолчанию Gmail).

Только стандартная библиотека Python 3.8+. Настройки — в config.ini,
получатели — в clients.csv, текст письма — в templates/.
"""
import argparse
import configparser
import csv
import mimetypes
import os
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path
from string import Template

BASE = Path(__file__).resolve().parent


def load_config(path):
    cfg = configparser.ConfigParser()
    if not cfg.read(path, encoding="utf-8"):
        sys.exit(f"Не найден файл настроек: {path} (скопируйте config.example.ini)")
    return cfg


def load_clients(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if rows and "email" not in rows[0]:
        sys.exit("В clients.csv обязательна колонка 'email'")
    return rows


def load_set(path):
    if not path.exists():
        return set()
    return {l.strip().lower() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()}


def render(text, client):
    # $name, ${company} и т.д. — любые колонки из CSV; неизвестные остаются как есть
    return Template(text).safe_substitute({k: (v or "") for k, v in client.items()})


def build_message(cfg, client, subject, text_body, html_body, attachments):
    s = cfg["sender"]
    msg = EmailMessage()
    msg["From"] = formataddr((s.get("name", ""), s["email"]))
    msg["To"] = client["email"]
    msg["Subject"] = render(subject, client)
    msg["Message-ID"] = make_msgid(domain=s["email"].split("@")[-1])
    if s.get("reply_to"):
        msg["Reply-To"] = s["reply_to"]
    unsub = s.get("unsubscribe_email") or s["email"]
    msg["List-Unsubscribe"] = f"<mailto:{unsub}?subject=unsubscribe>"

    msg.set_content(render(text_body, client))
    if html_body:
        msg.add_alternative(render(html_body, client), subtype="html")

    for path in attachments:
        ctype, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype,
                           filename=path.name)
    return msg


def connect(cfg):
    s = cfg["smtp"]
    host, port = s.get("host", "smtp.gmail.com"), s.getint("port", 465)
    password = os.environ.get("MAILER_PASSWORD") or s.get("password")
    if not password:
        sys.exit("Нет пароля: задайте MAILER_PASSWORD или [smtp] password в config.ini")
    ctx = ssl.create_default_context()
    if port == 465:
        server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
    else:
        server = smtplib.SMTP(host, port, timeout=30)
        server.starttls(context=ctx)
    server.login(s.get("user") or cfg["sender"]["email"], password)
    return server


def main():
    ap = argparse.ArgumentParser(description="Рассылка писем клиентам")
    ap.add_argument("--config", default=BASE / "config.ini", type=Path)
    ap.add_argument("--clients", default=BASE / "clients.csv", type=Path)
    ap.add_argument("--subject", help="Тема письма (иначе из config.ini)")
    ap.add_argument("--text", default=BASE / "templates" / "message.txt", type=Path)
    ap.add_argument("--html", default=BASE / "templates" / "message.html", type=Path)
    ap.add_argument("--attach", nargs="*", default=[], type=Path, help="Файлы-вложения")
    ap.add_argument("--send", action="store_true",
                    help="Реально отправить. Без флага — пробный прогон (ничего не шлётся)")
    ap.add_argument("--test", metavar="EMAIL",
                    help="Отправить одно письмо (по первому клиенту) на этот адрес")
    ap.add_argument("--limit", type=int, default=0, help="Максимум писем за запуск")
    args = ap.parse_args()

    cfg = load_config(args.config)
    subject = args.subject or cfg["message"]["subject"]
    text_body = args.text.read_text(encoding="utf-8")
    html_body = args.html.read_text(encoding="utf-8") if args.html.exists() else None
    for a in args.attach:
        if not a.exists():
            sys.exit(f"Вложение не найдено: {a}")

    clients = load_clients(args.clients)
    sent_log = BASE / "sent.log"
    already = load_set(sent_log)
    blocked = load_set(BASE / "unsubscribed.txt")
    delay = cfg["sending"].getfloat("delay_seconds", 5) if cfg.has_section("sending") else 5

    if args.test:
        client = dict(clients[0]) if clients else {}
        client["email"] = args.test
        queue = [client]
    else:
        seen, queue = set(), []
        for c in clients:
            e = (c.get("email") or "").strip().lower()
            if not e or "@" not in e or e in seen or e in already or e in blocked:
                continue
            seen.add(e)
            c["email"] = e
            queue.append(c)
        if args.limit:
            queue = queue[: args.limit]

    print(f"Клиентов в файле: {len(clients)}, к отправке: {len(queue)} "
          f"(уже отправлено: {len(already)}, отписались: {len(blocked)})")

    if not (args.send or args.test):
        for c in queue[:3]:
            print("-" * 60)
            print(f"Кому: {c['email']}\nТема: {render(subject, c)}\n\n{render(text_body, c)}")
        print("-" * 60)
        print("Пробный прогон. Для отправки добавьте --send (или --test ваш@адрес).")
        return

    server = connect(cfg)
    ok = fail = 0
    try:
        for i, c in enumerate(queue, 1):
            msg = build_message(cfg, c, subject, text_body, html_body, args.attach)
            try:
                server.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                server = connect(cfg)
                server.send_message(msg)
            except smtplib.SMTPException as e:
                fail += 1
                print(f"[{i}/{len(queue)}] ОШИБКА {c['email']}: {e}")
                continue
            ok += 1
            print(f"[{i}/{len(queue)}] отправлено {c['email']}")
            if not args.test:
                with open(sent_log, "a", encoding="utf-8") as f:
                    f.write(c["email"] + "\n")
            if i < len(queue):
                time.sleep(delay)
    except KeyboardInterrupt:
        print("\nОстановлено. Повторный запуск продолжит с того же места.")
    finally:
        try:
            server.quit()
        except Exception:
            pass
    print(f"Готово: отправлено {ok}, ошибок {fail}")


if __name__ == "__main__":
    main()
