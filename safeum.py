import os
import sys
import time
import json
import csv
import random
import threading
from datetime import datetime
from ssl import CERT_NONE
from gzip import decompress
from concurrent.futures import ThreadPoolExecutor

# Dépendances avec installation auto
try:
    import pyfiglet
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from websocket import create_connection
except ImportError:
    print("[*] Installation des dépendances...")
    os.system("pip install websocket-client rich pyfiglet requests")
    import pyfiglet
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from websocket import create_connection

console = Console()
lock = threading.Lock()

# Compteurs globaux
SUCCESS_COUNT = 0
FAILED_COUNT = 0
RETRY_COUNT = 0
CONSECUTIVE_FAILURES = 0
ACCOUNTS = []

def print_banner():
    console.clear()
    banner = pyfiglet.figlet_format("SafeUm V2", font="slant")
    rich_text = Text(banner)
    length = len(rich_text)
    if length > 0:
        half = length // 2
        rich_text.stylize("bold bright_magenta", 0, half)
        rich_text.stylize("bold bright_cyan", half, length)
    console.print(rich_text)

def load_proxies():
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

PROXIES = load_proxies()

def save_account(username, password):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acc_data = {"username": username, "password": password, "created_at": now}
    
    # 1. Sauvegarde TXT classique
    with open("safeum-Accounts.txt", "a", encoding="utf-8") as f:
        f.write(f"{username}:{password} | Date: {now}\n")
        
    # 2. Sauvegarde CSV
    file_exists = os.path.exists("accounts.csv")
    with open("accounts.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password", "created_at"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(acc_data)
        
    # 3. Sauvegarde JSON
    json_data = []
    if os.path.exists("accounts.json"):
        try:
            with open("accounts.json", "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception:
            json_data = []
    json_data.append(acc_data)
    with open("accounts.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

def check_ip_rotation():
    global CONSECUTIVE_FAILURES
    if CONSECUTIVE_FAILURES >= 15:
        console.print("[bold yellow][!] Alerte : Trop d'échecs consécutifs. Votre IP est probablement bloquée ![/bold yellow]")
        CONSECUTIVE_FAILURES = 0
        time.sleep(3)

def test_proxies_menu():
    print_banner()
    if not PROXIES:
        console.print("[red][!] Aucun proxy trouvé dans 'proxies.txt'.[/red]")
    else:
        console.print(f"[cyan][*] Test de {len(PROXIES)} proxies en cours...[/cyan]\n")
        valid = 0
        for p in PROXIES[:10]:
            try:
                parts = p.split(":")
                kw = {"http_proxy_host": parts[0], "http_proxy_port": int(parts[1])}
                con = create_connection("wss://195.13.182.217/Auth", timeout=3, sslopt={"cert_reqs": CERT_NONE}, **kw)
                con.close()
                console.print(f"[green][✓] Proxy Fonctionnel : {p}[/green]")
                valid += 1
            except Exception:
                console.print(f"[red][✗] Proxy Invalide / HS : {p}[/red]")
        console.print(f"\n[bold green]Résultat : {valid}/{len(PROXIES[:10])} proxies actifs.[/bold green]")
    input("\nAppuyez sur Entrée pour revenir au menu...")

def show_accounts_menu():
    print_banner()
    if not os.path.exists("accounts.json"):
        console.print("[yellow][!] Aucun compte généré pour le moment.[/yellow]")
    else:
        with open("accounts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        table = Table(title="Comptes SafeUm Générés")
        table.add_column("Username", style="cyan")
        table.add_column("Password", style="green")
        table.add_column("Date de Création", style="magenta")
        
        for item in data[-10:]:
            table.add_row(item["username"], item["password"], item["created_at"])
        
        console.print(table)
        console.print(f"\n[dim]Total des comptes dans la base : {len(data)}[/dim]")
    input("\nAppuyez sur Entrée pour revenir au menu...")

def work():
    global SUCCESS_COUNT, FAILED_COUNT, RETRY_COUNT, CONSECUTIVE_FAILURES
    
    username = random.choice("qwertyuioplkjhgfdsazxcvbnm") + "".join(
        random.choices("qwertyuioplkjhgfdsazxcvbnm1234567890", k=13)
    )
    
    proxy_kwargs = {}
    if PROXIES:
        proxy = random.choice(PROXIES)
        try:
            parts = proxy.split(":")
            if len(parts) >= 2:
                proxy_kwargs["http_proxy_host"] = parts[0]
                proxy_kwargs["http_proxy_port"] = int(parts[1])
                if len(parts) == 4:
                    proxy_kwargs["http_proxy_auth"] = (parts[2], parts[3])
        except Exception:
            pass

    con = None
    try:
        con = create_connection(
            "wss://195.13.182.217/Auth",
            timeout=6,
            sslopt={"cert_reqs": CERT_NONE},
            header={
                "app": "com.safeum.android",
                "host": None,
                "remoteIp": "195.13.182.217",
                "remotePort": "8080",
                "sessionId": "b6cbb22d-06ca-41ff-8fda-c0ddeb148195",
                "time": "2023-04-30 12:13:32",
                "url": "wss://51.79.208.190/Auth",
            },
            **proxy_kwargs
        )
        
        payload = {
            "action": "Register",
            "subaction": "Desktop",
            "locale": "en_IN",
            "gmt": "+05",
            "password": {
                "m1x": "1a07f431a68b4fb69a5c96349137476cca613f019b1016e63a27e022ef09805c",
                "m1y": "ba83a1300f777ada673afb9bc4d507da3000ea2fabaaa35a6616a0af666a4bb7",
                "m2": "43c58959c91b494e05a47cad7bca5b5f52e5204d393e06829c34884fa807954b",
                "iv": "140c409aba2f6c7050518a826e6f2810",
                "message": "5080dc99f8e226891ee1f4b52a480e1d0278ff1c211e5107a5de2ceb6a646d407084bd88f05438f6f671e2574239abbe68b401980a9336947e0b47c5e56bbcf05ad345cd46958d090bdd9110fdd33b08",
            },
            "magicword": {
                "m1x": "e90328d307cc09e8efb4bc307b93711c30ddc8dd2c81a4375a8c6f56cc491b6c",
                "m1y": "c10d0ea9f845ede4e3bddabd688b5a5df39e0542a9f7e3d3e634a0c947eb7cef",
                "m2": "0743248643a4ce7fe349e117aadc8bf6b98361410d9ee87b4a8b7519ddf421d5",
                "iv": "186e765c4b10803fc9a6a9d6ae08549b",
                "message": "76f4c2466364ccf3bd38882471fc30c3",
            },
            "magicwordhint": "0000",
            "login": username,
            "devicename": "Xiaomi 220733SPH",
            "softwareversion": "1.1.0.1548",
            "nickname": "jsjkkm822mmsm",
            "os": "AND",
            "deviceuid": "3933b21c103ad7a8",
            "devicepushuid": "*fC4qytGbRgCLyGKiZRfh5n:APA91bFXieRxcxPxIyxknU-MNLUyrao13YgiKV_tthXzXVLToRz8-t6LkU2Zol8cW7jhcfQp10h0n0VyZw4vOY04HWS5fIXGX-ic_1ijzt3RGbKUBCEkAg",
            "osversion": "and_12.0.0",
            "id": "1492923070",
        }
        
        con.send(json.dumps(payload))
        response = decompress(con.recv()).decode("utf-8")
        con.close()
        
        with lock:
            if '"status":"Success"' in response:
                SUCCESS_COUNT += 1
                CONSECUTIVE_FAILURES = 0
                save_account(username, "mmmm")
                console.print(f"[bold green][+] SUCCÈS : {username}:mmmm[/bold green]")
            else:
                FAILED_COUNT += 1
                CONSECUTIVE_FAILURES += 1
    except Exception as e:
        with lock:
            RETRY_COUNT += 1
            CONSECUTIVE_FAILURES += 1
            # Affiche clairement l'erreur technique pour le diagnostic
            console.print(f"[red][!] Erreur technique : {e}[/red]")
    finally:
        if con:
            try:
                con.close()
            except:
                pass

def start_generator(workers):
    print_banner()
    console.print(f"[bold green][*] Démarrage du générateur ({workers} Workers)...[/bold green]\n")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        try:
            while True:
                futures = [executor.submit(work) for _ in range(workers)]
                for future in futures:
                    future.result()
                
                with lock:
                    console.print(
                        f"[dim]Stats -> Succès: [green]{SUCCESS_COUNT}[/] | Échecs: [red]{FAILED_COUNT}[/] | Retry: [yellow]{RETRY_COUNT}[/][/dim]"
                    )
                    check_ip_rotation()
                time.sleep(0.4)
        except KeyboardInterrupt:
            console.print("\n[bold red][!] Script arrêté par l'utilisateur.[/bold red]")
            time.sleep(1)

def main_menu():
    while True:
        print_banner()
        menu_text = Text()
        menu_text.append("[1] ", style="bold cyan")
        menu_text.append("Lancer en Mode Standard (3 Workers)\n", style="bold white")
        menu_text.append("[2] ", style="bold cyan")
        menu_text.append("Lancer en Mode Rapide / VPS (10 Workers)\n", style="bold white")
        menu_text.append("[3] ", style="bold cyan")
        menu_text.append("Tester les Proxies (proxies.txt)\n", style="bold white")
        menu_text.append("[4] ", style="bold cyan")
        menu_text.append("Voir les comptes générés (Base JSON)\n", style="bold white")
        menu_text.append("[5] ", style="bold cyan")
        menu_text.append("Quitter\n", style="bold red")

        panel = Panel(menu_text, title="[bold bright_blue]MENU PRINCIPAL[/]", border_style="bright_blue", width=58)
        console.print(panel)
        
        choice = input("\nChoisissez une option (1-5) : ").strip()
        
        if choice == "1":
            start_generator(3)
        elif choice == "2":
            start_generator(10)
        elif choice == "3":
            test_proxies_menu()
        elif choice == "4":
            show_accounts_menu()
        elif choice == "5":
            console.print("[bold green]Au revoir ![/bold green]")
            sys.exit()

if __name__ == "__main__":
    main_menu()
