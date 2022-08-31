import sqlite3

from base64 import b64decode
from pyotp import TOTP
from rich import inspect
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED as box

from database import Database

console = Console()
db = None
while True:
    db = Database(console.input("Enter password > "))
    try:
        db.get_entries()
        break
    except UnicodeDecodeError:
        console.print("Invalid password!", style="red")

commands = {
    "create <site>": "create new entry",
    "get <id/site>": "get entry by id/site",
    "remove <id>": "remove entry by id",
    "list": "list of current entries",
    "otp <id>": "setup otp for account",
    "help": "help message",
    "exit": "bye :3",
}

color = "blue"
while True:
    raw = console.input(f"[{color}]>[/] ")

    if len(raw.strip()) == 0: 
        continue

    cmd = raw.split()[0]
    args = raw.split()[1:]

    if cmd in ["create", "insert", "new"]:
        if len(args) == 0:
            console.print("Not enough arguments!", style="red")
            color = "red"
            continue
        
        site = args[0]
        login = console.input("Login > ")
        password = console.input("Password > ", password=True)

        db.push(login, password, site)
        color = "blue"
    elif cmd in ["open", "read", "get"]:
        if len(args) == 0:
            console.print("Not enough arguments!", style="red")
            color = "red"
            continue
        entry = db.get_entry(args[0])
        table = Table(title="Passwords", box=box)
        table.add_column("ID", style="purple")
        table.add_column("Login", style="yellow")
        table.add_column("Password", style="green")
        table.add_column("OTP", style="red")
        table.add_column("Site", style="blue underline")
        if entry == None:
            entries = db.get_entries_by_site(args[0])
            if len(entries) == 0:
                console.print("Entry not found!", style="red")
                continue

            for en in entries:
                code = None
                if en.otp != None:
                    code = TOTP(entry.otp).now()
                table.add_row(
                    str(en.id),
                    en.login,
                    en.password,
                    code,
                    en.site
                )
        else:
            code = None
            if entry.otp != None:
                code = TOTP(entry.otp).now()
            table.add_row(
                str(entry.id),
                entry.login,
                entry.password,
                code,
                entry.site
            )

        console.print(table)

    elif cmd in ["list", "ls"]:
        entries = db.get_entries()
        table = Table(title="Passwords", box=box)
        table.add_column("ID", style="purple")
        table.add_column("Login", style="yellow")
        table.add_column("Password", style="green")
        table.add_column("OTP", style="red")
        table.add_column("Site", style="blue underline")
        for entry in entries:
            password = entry.password[0] + "*"*(len(entry.password)-2) + entry.password[-1]
            code = None
            if entry.otp != None:
                code = TOTP(entry.otp).now()
            table.add_row(
                str(entry.id),
                entry.login,
                password,
                code,
                entry.site
            )
        console.print(table)

    elif cmd in ["remove", "rem", "delete", "del"]:
        if len(args) == 0:
            console.print("Not enough arguments!", style="red")
            color = "red"
            continue

        if db.del_entry(args[0]):
            console.print(f"Successfully removed entry with ID {args[0]}")
        else:
            console.print("Entry not found!", style="red")

    elif cmd in ["otp", "2fa"]:
        if len(args) == 0:
            console.print("Not enough arguments!", style="red")
            color = "red"
            continue
        if db.get_entry(args[0]) == None:
            console.print("Entry not found!", style="red")
            continue

        try:
            code = console.input("Enter code > ")
            TOTP(code).now()
            db.otp_update(args[0], code)
        except Exception as e:
            console.print("Invalid code!", style="red")
            continue
    
    elif cmd in ["exec", "sql"]:
        if len(args) == 0:
            console.print("Not enough arguments!", style="red")
            color = "red"
            continue
        try:
            db.cur.execute(" ".join(args))
            console.print(db.cur.fetchall())
        except sqlite3.OperationalError as e:
            console.print(f"SQLite error: {e}", style="red")

    elif cmd in ["help"]:
        for command, decription in commands.items():
            console.print(f"[yellow]{command}[/] - {decription}", highlight=False)

    elif cmd in ["exit", "q", "quit"]:
        console.print("Bye ^_^", style="bold blue")
        db.con.close()
        exit()

    else:
        color = "red"

