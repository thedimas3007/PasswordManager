import sqlite3

from aes import AES
from database import Database, Entry
from rich.console import Console
from rich.pretty import pprint as print
from rich import inspect


console = Console()
db = Database(console.input("Enter password > "))

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
        if entry == None:
            entry = db.get_entry_by_site(args[0])

        if entry == None:
            console.print("Entry not found!", style="red")
            continue

        console.print(f"Login:    [yellow]{entry.login}[/]")
        console.print(f"Password: [green]{entry.password}[/]")
        console.print(f"Site:     [blue underline]{entry.site}[/]")

    elif cmd in ["exit", "q", "quit"]:
        console.print("Bye ^_^", style="bold blue")
        exit()
    else:
        color = "red"

