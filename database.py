import sqlite3
from typing import List
from pyotp import TOTP
from aes import AES

class Entry:
    def __init__(self, login: str, password: str, otp: str, site: str, id: int) -> None:
        self.login = login
        self.password = password
        self.otp = otp
        self.site = site
        self.id = id

class Database:
    def __init__(self, password: str) -> None:
        self.con = sqlite3.connect("manager.db")
        self.cur = self.con.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS logins (
            login VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            otp VARCHAR(255),
            site VARCHAR(255) NOT NULL,
            id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT
        );""")
        self.con.commit()

        self.aes = AES(password)
    
    def push(self, login: str, password: str, site: str) -> None:
        password = self.aes.b64enc(password)
        self.cur.execute(f"INSERT INTO logins (login, password, site) VALUES ('{login}', '{password}', '{site}');")
        self.con.commit()


    def push_entry(self, entry: Entry) -> None:
        login = entry.login
        password = self.aes.b64enc(entry.password)
        site = entry.site
        self.cur.execute(f"INSERT INTO logins (login, password, site) VALUES ('{login}', '{password}', '{site}');")
        self.con.commit()

    def get_entry(self, id) -> Entry:
        try:
            self.cur.execute(f"SELECT * FROM logins WHERE id = {id};")
        except:
            return None
        n = self.cur.fetchone()
        try:
            return Entry(
                n[0],
                self.aes.b64dec(n[1]),
                n[2],
                n[3],
                n[4]
            )
        except (IndexError, TypeError) as e:
            print(type(e), e)
            return None

    def del_entry(self, id) -> bool:
        if self.get_entry(id) == None:
            return False
        
        self.cur.execute(f"DELETE FROM logins WHERE id = {id};")
        return True

    def get_entries_by_site(self, site) -> List[Entry]:
        self.cur.execute(f"SELECT * FROM logins WHERE site = '{site}';")
        entries = []
        for n in self.cur.fetchall():
            try:
                entries.append(Entry(
                    n[0],
                    self.aes.b64dec(n[1]),
                    n[2],
                    n[3],
                    n[4]
                ))
            except (IndexError, TypeError):
                pass
        return entries
    
    def get_entries(self) -> List[Entry]:
        self.cur.execute(f"SELECT * FROM logins;")
        entries = []
        for n in self.cur.fetchall():
            try:
                entries.append(Entry(
                    n[0],
                    self.aes.b64dec(n[1]),
                    n[2],
                    n[3],
                    n[4]
                ))
            except (IndexError, TypeError):
                pass
        return entries
    
    def otp_update(self, id, code) -> bool:
        try:
            TOTP(code).now()
        except:
            return False

        self.cur.execute(f"UPDATE logins SET otp = '{code}' WHERE id = {id}")
        self.con.commit()
        return True
