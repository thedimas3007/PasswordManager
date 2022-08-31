from database import Database
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED as box

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
        table.add_column("Site", style="blue underline")
        if entry == None:
            entries = db.get_entries_by_site(args[0])
            if len(entries) == 0:
                console.print("Entry not found!", style="red")
                continue

            for en in entries:
                table.add_row(
                    str(en.id),
                    en.login,
                    en.password,
                    en.site
                )
        else:
            table.add_row(
                str(entry.id),
                entry.login,
                entry.password,
                entry.site
            )

        console.print(table)

    elif cmd in ["list", "ls"]:
        entries = db.get_entries()
        table = Table(title="Passwords", box=box)
        table.add_column("ID", style="purple")
        table.add_column("Login", style="yellow")
        table.add_column("Password", style="green")
        table.add_column("Site", style="blue underline")
        for entry in entries:
            password = entry.password[0] + "*"*(len(entry.password)-2) + entry.password[-1]
            table.add_row(
                str(entry.id),
                entry.login,
                password,
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

    elif cmd in ["help"]:
        for command, decription in commands.items():
            console.print(f"[yellow]{command}[/] - {decription}", highlight=False)

    elif cmd in ["exit", "q", "quit"]:
        console.print("Bye ^_^", style="bold blue")
        db.con.close()
        exit()

    else:
        color = "red"

