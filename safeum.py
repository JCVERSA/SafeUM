import os
import sys
import time
import json
import random
import threading
from ssl import CERT_NONE
from gzip import decompress
from concurrent.futures import ThreadPoolExecutor

# Vérification et installation automatique des dépendances pour Termux 32-bit
try:
    import pyfiglet
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from websocket import create_connection
except ImportError:
    print("[*] Installation des paquets requis pour Termux 32-bit...")
    os.system("pip install websocket-client rich pyfiglet requests")
    import pyfiglet
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from websocket import create_connection

console = Console()

# Verrou de thread pour sécuriser les compteurs globaux et les fichiers
lock = threading.Lock()

SUCCESS_COUNT = 0
FAILED_COUNT = 0
RETRY_COUNT = 0
ACCOUNTS = []

def print_banner():
    banner = pyfiglet.figlet_format("SafeUm", font="slant")
    rich_text = Text(banner)
    length = len(rich_text)
    if length > 0:
        half = length // 2
        rich_text.stylize("bold bright_magenta", 0, half)
        rich_text.stylize("bold bright_cyan", half, length)
    console.print(rich_text)

def print_device_info():
    info = Text()
    info.append("🔹 Device:     ", style="bold cyan")
    info.append("Tecno Pop 7 (BF6) 32-bit\n", style="bold white")
    info.append("🔹 Creator:    ", style="bold cyan")
    info.append("@Abdullah\n", style="bold magenta")
    info.append("🔹 Status:     ", style="bold cyan")
    info.append("Optimized, Secured & Free\n", style="bold green")

    panel = Panel(info, title="[bold bright_blue]SECURE MOBILE ENGINE[/]", border_style="bright_blue", width=50)
    console.print(panel)

def load_proxies():
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

PROXIES = load_proxies()

def work():
    global SUCCESS_COUNT, FAILED_COUNT, RETRY_COUNT
    
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
                # Support des proxys avec authentification (user:pass)
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
                acc_info = f"{username}:mmmm"
                ACCOUNTS.append(acc_info)
                console.print(f"[bold green][+] SUCCÈS : {acc_info}[/bold green]")
                with open("safeum-Accounts.txt", "a", encoding="utf-8") as f:
                    f.write(f"{acc_info} | AM : @Abdullah\n")
            else:
                FAILED_COUNT += 1
    except Exception:
        with lock:
            RETRY_COUNT += 1
    finally:
        if con:
            try:
                con.close()
            except:
                pass

def main():
    print_banner()
    print_device_info()
    
    WORKERS = 3 
    console.print(f"\n[bold green][*] Moteur lancé avec {WORKERS} threads stabilisés (Tecno Pop 7 BF6)...[/bold green]\n")
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        try:
            while True:
                futures = [executor.submit(work) for _ in range(WORKERS)]
                for future in futures:
                    future.result()
                
                with lock:
                    console.print(
                        f"[dim]Stats -> Succès: [green]{SUCCESS_COUNT}[/] | Échecs: [red]{FAILED_COUNT}[/] | Retry: [yellow]{RETRY_COUNT}[/][/dim]"
                    )
                time.sleep(0.4)
        except KeyboardInterrupt:
            console.print("\n[bold red][!] Script arrêté par l'utilisateur.[/bold red]")

if __name__ == "__main__":
    main()
