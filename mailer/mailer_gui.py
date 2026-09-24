#!/usr/bin/env python3
"""Десктопная версия рассылки: окно на tkinter поверх mailer.py.

Запуск: python3 mailer_gui.py  (или готовый .exe / .app из GitHub Actions).
Настройки, журнал отправленных и список отписавшихся хранятся в папке
~/LegoBotMailer, чтобы они не терялись между запусками.
"""
import configparser
import csv
import html
import json
import os
import queue
import smtplib
import subprocess
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from mailer import build_message, connect, load_set, render

DATA_DIR = Path.home() / "LegoBotMailer"
SETTINGS = DATA_DIR / "settings.json"
SENT_LOG = DATA_DIR / "sent.log"
UNSUBSCRIBED = DATA_DIR / "unsubscribed.txt"

DEFAULT_TEXT = """Здравствуйте, $name!

Мы подготовили новые обложки для инструкций к наборам LEGO.

С уважением,
LegoBot

Чтобы отписаться от рассылки, просто ответьте на это письмо словом «отписаться».
"""

DEFAULTS = {
    "email": "", "name": "LegoBot", "reply_to": "",
    "host": "smtp.gmail.com", "port": "465",
    "password": "", "remember_password": False,
    "clients": "", "subject": "$name, новые обложки для наборов LEGO",
    "text": DEFAULT_TEXT, "html_file": "", "make_html": True,
    "delay": "5", "limit": "",
}


def text_to_html(text):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    body = "\n".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paras)
    return ('<!doctype html><html><body style="font-family: Arial, sans-serif; '
            f'line-height: 1.5">\n{body}\n</body></html>')


def read_clients(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        rows = list(csv.DictReader(f, dialect=dialect))
    # Excel иногда пишет заголовки с пробелами и в разном регистре
    return [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in rows]


def open_folder(path):
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LegoBot — рассылка клиентам")
        self.geometry("900x720")
        self.minsize(760, 600)
        self.events = queue.Queue()
        self.stop_flag = threading.Event()
        self.worker = None
        self.vars = {}
        self.attachments = []

        s = dict(DEFAULTS)
        try:
            s.update(json.loads(SETTINGS.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
        self.build_ui(s)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self.poll_events)

    # ---------- интерфейс ----------
    def var(self, key, value, kind=tk.StringVar):
        v = kind(value=value)
        self.vars[key] = v
        return v

    def build_ui(self, s):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        # --- Письмо
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Письмо")
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(3, weight=1)

        ttk.Label(tab, text="Файл клиентов (CSV):").grid(row=0, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.var("clients", s["clients"])).grid(
            row=0, column=1, sticky="ew", padx=5)
        ttk.Button(tab, text="Выбрать…", command=self.pick_clients).grid(row=0, column=2)
        self.clients_info = ttk.Label(tab, foreground="gray")
        self.clients_info.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)

        ttk.Label(tab, text="Тема:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(tab, textvariable=self.var("subject", s["subject"])).grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=(8, 0))

        self.text = scrolledtext.ScrolledText(tab, wrap="word", height=14, undo=True)
        self.text.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=8)
        self.text.insert("1.0", s["text"])

        ttk.Label(tab, text="Подстановки: $name, $email и любые колонки из CSV, "
                            "например ${company}.", foreground="gray").grid(
            row=4, column=0, columnspan=3, sticky="w")

        ttk.Checkbutton(tab, text="Отправлять также оформленную HTML-версию письма",
                        variable=self.var("make_html", s["make_html"], tk.BooleanVar)).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Label(tab, text="Свой HTML-файл (необязательно):").grid(row=6, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.var("html_file", s["html_file"])).grid(
            row=6, column=1, sticky="ew", padx=5)
        ttk.Button(tab, text="Выбрать…", command=self.pick_html).grid(row=6, column=2)

        ttk.Label(tab, text="Вложения:").grid(row=7, column=0, sticky="w", pady=(6, 0))
        self.attach_label = ttk.Label(tab, text="нет", foreground="gray")
        self.attach_label.grid(row=7, column=1, sticky="w", padx=5, pady=(6, 0))
        af = ttk.Frame(tab)
        af.grid(row=7, column=2, pady=(6, 0))
        ttk.Button(af, text="Добавить…", command=self.add_attachments).pack(side="left")
        ttk.Button(af, text="×", width=2, command=self.clear_attachments).pack(side="left")

        # --- Настройки
        tab = ttk.Frame(nb, padding=10)
        nb.add(tab, text="Настройки почты")
        tab.columnconfigure(1, weight=1)
        rows = [
            ("Ваш e-mail:", "email"), ("Имя отправителя:", "name"),
            ("Ответы на адрес (необязательно):", "reply_to"),
            ("SMTP-сервер:", "host"), ("Порт:", "port"),
        ]
        for i, (label, key) in enumerate(rows):
            ttk.Label(tab, text=label).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Entry(tab, textvariable=self.var(key, s[key])).grid(
                row=i, column=1, sticky="ew", padx=5, pady=3)
        r = len(rows)
        ttk.Label(tab, text="Пароль приложения:").grid(row=r, column=0, sticky="w", pady=3)
        ttk.Entry(tab, show="•", textvariable=self.var("password", s["password"])).grid(
            row=r, column=1, sticky="ew", padx=5, pady=3)
        ttk.Checkbutton(tab, text="Запомнить пароль на этом компьютере (хранится в открытом виде)",
                        variable=self.var("remember_password", s["remember_password"],
                                          tk.BooleanVar)).grid(
            row=r + 1, column=1, sticky="w", padx=5)
        ttk.Label(tab, text="Пауза между письмами, сек:").grid(row=r + 2, column=0, sticky="w", pady=3)
        ttk.Entry(tab, width=8, textvariable=self.var("delay", s["delay"])).grid(
            row=r + 2, column=1, sticky="w", padx=5, pady=3)
        ttk.Label(tab, text="Не больше писем за запуск:").grid(row=r + 3, column=0, sticky="w", pady=3)
        ttk.Entry(tab, width=8, textvariable=self.var("limit", s["limit"])).grid(
            row=r + 3, column=1, sticky="w", padx=5, pady=3)

        help_text = (
            "Gmail: нужен пароль приложения, а не обычный пароль.\n"
            "1) Включите двухэтапную аутентификацию: myaccount.google.com/security\n"
            "2) Создайте пароль приложения: myaccount.google.com/apppasswords\n\n"
            "Яндекс: smtp.yandex.ru, порт 465 (пароль приложения в id.yandex.ru).\n"
            "Mail.ru: smtp.mail.ru, порт 465 (пароль для внешних приложений).\n\n"
            "Лимит Gmail — около 500 писем в сутки. Пишите только тем, кто согласился "
            "получать рассылку."
        )
        ttk.Label(tab, text=help_text, foreground="gray", justify="left", wraplength=640).grid(
            row=r + 4, column=0, columnspan=2, sticky="w", pady=(14, 0))

        df = ttk.Frame(tab)
        df.grid(row=r + 5, column=0, columnspan=2, sticky="w", pady=(14, 0))
        ttk.Button(df, text="Открыть папку данных",
                   command=lambda: open_folder(DATA_DIR)).pack(side="left")
        ttk.Button(df, text="Начать новую рассылку (сбросить журнал)",
                   command=self.reset_log).pack(side="left", padx=6)

        # --- Кнопки и журнал
        bar = ttk.Frame(self, padding=(8, 8))
        bar.pack(fill="x")
        ttk.Button(bar, text="Предпросмотр", command=self.preview).pack(side="left")
        ttk.Button(bar, text="Тест себе", command=self.send_test).pack(side="left", padx=6)
        self.send_btn = ttk.Button(bar, text="Разослать всем", command=self.send_all)
        self.send_btn.pack(side="left")
        self.stop_btn = ttk.Button(bar, text="Стоп", command=self.stop_flag.set, state="disabled")
        self.stop_btn.pack(side="left", padx=6)
        self.progress = ttk.Progressbar(bar, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=6)

        self.log = scrolledtext.ScrolledText(self, height=9, state="disabled")
        self.log.pack(fill="both", padx=8, pady=(0, 8))

        self.refresh_clients_info()
        self.vars["clients"].trace_add("write", lambda *_: self.refresh_clients_info())

    # ---------- действия ----------
    def pick_clients(self):
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Все файлы", "*.*")])
        if p:
            self.vars["clients"].set(p)

    def pick_html(self):
        p = filedialog.askopenfilename(filetypes=[("HTML", "*.html *.htm"), ("Все файлы", "*.*")])
        if p:
            self.vars["html_file"].set(p)

    def add_attachments(self):
        self.attachments += [Path(p) for p in filedialog.askopenfilenames()]
        self.attach_label.config(text=", ".join(p.name for p in self.attachments) or "нет")

    def clear_attachments(self):
        self.attachments = []
        self.attach_label.config(text="нет")

    def reset_log(self):
        if not SENT_LOG.exists():
            messagebox.showinfo("Журнал", "Журнал и так пуст.")
            return
        if messagebox.askyesno("Новая рассылка",
                               "Все клиенты снова станут получателями. Продолжить?\n"
                               "Старый журнал будет сохранён в папке данных."):
            SENT_LOG.rename(DATA_DIR / f"sent-{datetime.now():%Y%m%d-%H%M%S}.log")
            self.refresh_clients_info()

    def refresh_clients_info(self):
        try:
            total, q = self.build_queue()
            self.clients_info.config(
                text=f"Клиентов в файле: {total}, получат письмо: {len(q)}")
        except Exception:
            self.clients_info.config(text="")

    def settings(self):
        s = {k: v.get() for k, v in self.vars.items()}
        s["text"] = self.text.get("1.0", "end-1c")
        return s

    def save_settings(self):
        s = self.settings()
        if not s["remember_password"]:
            s["password"] = ""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

    def config_from_settings(self, s):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg["sender"] = {"email": s["email"].strip(), "name": s["name"],
                         "reply_to": s["reply_to"].strip()}
        cfg["smtp"] = {"host": s["host"].strip(), "port": s["port"].strip() or "465",
                       "password": s["password"].replace(" ", "")}
        return cfg

    def build_queue(self):
        path = self.vars["clients"].get().strip()
        if not path:
            return 0, []
        clients = read_clients(path)
        done, blocked = load_set(SENT_LOG), load_set(UNSUBSCRIBED)
        seen, q = set(), []
        for c in clients:
            e = c.get("email", "").lower()
            if not e or "@" not in e or e in seen or e in done or e in blocked:
                continue
            seen.add(e)
            c["email"] = e
            q.append(c)
        return len(clients), q

    def bodies(self, s):
        text_body = s["text"]
        html_body = None
        if s["html_file"].strip():
            html_body = Path(s["html_file"].strip()).read_text(encoding="utf-8")
        elif s["make_html"]:
            html_body = text_to_html(text_body)
        return text_body, html_body

    def validate(self, s, need_clients=True):
        if "@" not in s["email"]:
            return "Укажите ваш e-mail на вкладке «Настройки почты»."
        if not s["password"].strip():
            return "Укажите пароль приложения на вкладке «Настройки почты»."
        if need_clients and not s["clients"].strip():
            return "Выберите файл клиентов (CSV)."
        for a in self.attachments:
            if not a.exists():
                return f"Вложение не найдено: {a}"
        return None

    def preview(self):
        s = self.settings()
        try:
            _, q = self.build_queue()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл клиентов:\n{e}")
            return
        c = q[0] if q else {"email": "client@example.com", "name": "Иван"}
        win = tk.Toplevel(self)
        win.title(f"Предпросмотр — {c['email']}")
        win.geometry("640x480")
        t = scrolledtext.ScrolledText(win, wrap="word")
        t.pack(fill="both", expand=True)
        t.insert("1.0", f"Кому: {c['email']}\nТема: {render(s['subject'], c)}\n\n"
                        f"{render(s['text'], c)}")
        t.config(state="disabled")

    def send_test(self):
        s = self.settings()
        err = self.validate(s, need_clients=False)
        if err:
            messagebox.showwarning("Не хватает данных", err)
            return
        try:
            _, q = self.build_queue()
        except Exception:
            q = []
        client = dict(q[0]) if q else {"name": "Тест"}
        client["email"] = s["email"].strip()
        self.start(s, [client], test=True)

    def send_all(self):
        s = self.settings()
        err = self.validate(s)
        if err:
            messagebox.showwarning("Не хватает данных", err)
            return
        try:
            _, q = self.build_queue()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл клиентов:\n{e}")
            return
        if s["limit"].strip().isdigit() and int(s["limit"]) > 0:
            q = q[: int(s["limit"])]
        if not q:
            messagebox.showinfo("Рассылка", "Некому отправлять: все уже получили письмо "
                                            "или список пуст.")
            return
        if not messagebox.askyesno("Рассылка", f"Отправить письмо {len(q)} получателям?"):
            return
        self.start(s, q, test=False)

    def start(self, s, q, test):
        try:
            text_body, html_body = self.bodies(s)
            delay = float(s["delay"].replace(",", ".") or 0)
        except (OSError, ValueError) as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self.save_settings()
        self.stop_flag.clear()
        self.send_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.config(maximum=len(q), value=0)
        args = (self.config_from_settings(s), s["subject"], text_body, html_body,
                list(self.attachments), q, delay, test)
        self.worker = threading.Thread(target=self.run, args=args, daemon=True)
        self.worker.start()

    # ---------- фоновая отправка ----------
    def run(self, cfg, subject, text_body, html_body, attachments, q, delay, test):
        emit = self.events.put
        ok = fail = 0
        try:
            emit(("log", "Подключаюсь к почтовому серверу…"))
            server = connect(cfg)
        except SystemExit as e:
            emit(("error", str(e)))
            return
        except smtplib.SMTPAuthenticationError:
            emit(("error", "Сервер не принял логин или пароль. Для Gmail нужен "
                           "пароль приложения (см. вкладку «Настройки почты»)."))
            return
        except Exception as e:
            emit(("error", f"Не удалось подключиться: {e}"))
            return
        try:
            for i, c in enumerate(q, 1):
                if self.stop_flag.is_set():
                    emit(("log", "Остановлено. Следующий запуск продолжит с этого места."))
                    break
                msg = build_message(cfg, c, subject, text_body, html_body, attachments)
                try:
                    try:
                        server.send_message(msg)
                    except smtplib.SMTPServerDisconnected:
                        server = connect(cfg)
                        server.send_message(msg)
                except Exception as e:
                    fail += 1
                    emit(("log", f"[{i}/{len(q)}] ОШИБКА {c['email']}: {e}"))
                else:
                    ok += 1
                    emit(("log", f"[{i}/{len(q)}] отправлено {c['email']}"))
                    if not test:
                        DATA_DIR.mkdir(parents=True, exist_ok=True)
                        with open(SENT_LOG, "a", encoding="utf-8") as f:
                            f.write(c["email"] + "\n")
                emit(("progress", i))
                if i < len(q):
                    self.stop_flag.wait(delay)
        finally:
            try:
                server.quit()
            except Exception:
                pass
        emit(("done", f"Готово: отправлено {ok}, ошибок {fail}."))

    def poll_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "progress":
                    self.progress.config(value=value)
                    continue
                self.write_log(value)
                if kind in ("error", "done"):
                    self.send_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    self.refresh_clients_info()
                    if kind == "error":
                        messagebox.showerror("Ошибка", value)
        except queue.Empty:
            pass
        self.after(100, self.poll_events)

    def write_log(self, line):
        self.log.config(state="normal")
        self.log.insert("end", f"{time.strftime('%H:%M:%S')}  {line}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def on_close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno("Выход", "Рассылка ещё идёт. Остановить и выйти?"):
                return
            self.stop_flag.set()
        try:
            self.save_settings()
        except OSError:
            pass
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
