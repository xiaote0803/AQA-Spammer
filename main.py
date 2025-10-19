import random
import time
import threading
import requests
import urllib3
from typing import List, Dict, Iterable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIMEOUT_SLEEP = 20
URL = "https://aqa.link/portal/message/send"

PRINT_LOCK = threading.Lock()
COUNTER_LOCK = threading.Lock()

INVALID_PROXIES: List[str] = []
USER_AGENTS: List[str] = []
MESSAGES: List[str] = []
PROXIES: List[str] = []


def print_sync(msg: str) -> None:
    with PRINT_LOCK:
        print(msg, flush=True)


def print_colored(msg_type: str, message: str) -> None:
    colors = {
        "ERROR": "\033[1;31m",
        "SUCCESS": "\033[1;32m",
        "WARN": "\033[33m",
        "ABORT": "\033[31m",
        "MISSING": "\033[31m",
        "INFO": "\033[34m"
    }
    color = colors.get(msg_type.upper(), "")
    reset = "\033[0m"
    with PRINT_LOCK:
        print(f"{color}[{msg_type.upper()}]{reset} {message}", flush=True)


def load_file_lines(filename: str) -> List[str]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if not lines:
                print_colored("WARN", f"Empty file: {filename}")
            return lines
    except FileNotFoundError:
        print_colored("MISSING", f"File not found: {filename}")
        return []


def build_headers(user_agents: Iterable[str]) -> Dict[str, str]:
    ua_list = list(user_agents)
    if not ua_list:
        raise ValueError("No user agents available")
    return {
        "Content-Length": "110",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="141", "Not?A_Brand";v="8"',
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": random.choice(ua_list),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "Origin": "https://aqa.link",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=4, i"
    }


def proxy_worker(proxy: str, toUserId: int, messages: List[str], user_agents: List[str], counter: List[int], stop_event: threading.Event) -> None:
    session = requests.Session()
    px = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    while not stop_event.is_set():
        headers = build_headers(user_agents)
        data = {
            "toUserId": toUserId,
            "content": random.choice(messages),
            "deviceId": "".join(random.choices("0123456789abcdef", k=42)),
            "topic": 1
        }
        try:
            resp = session.post(URL, headers=headers, json=data, proxies=px, timeout=(2, 5))
            status = resp.status_code
            if status == 429:
                time.sleep(TIMEOUT_SLEEP)
                continue
            if status != 200:
                print_colored("ERROR", f"{status} | drop {proxy}")
                break
            with COUNTER_LOCK:
                counter[0] += 1
                print_colored("SUCCESS", f"Message Total: {counter[0]}")
        except requests.exceptions.Timeout:
            break
        except (requests.exceptions.ProxyError, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            with COUNTER_LOCK:
                if proxy not in INVALID_PROXIES:
                    INVALID_PROXIES.append(proxy)
            break
        except Exception as e:
            print_colored("ERROR", f"Unexpected | {proxy} | {type(e).__name__}")
            break


def send_messages(toUserId: int, messages: List[str], proxies: List[str], user_agents: List[str]) -> None:
    counter = [0]
    stop_event = threading.Event()
    threads: List[threading.Thread] = []
    for proxy in proxies:
        if proxy in INVALID_PROXIES:
            continue
        t = threading.Thread(
            target=proxy_worker,
            args=(proxy, toUserId, messages, user_agents, counter, stop_event),
            daemon=True,
        )
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def get_toUserId() -> int:
    while True:
        try:
            print_colored("INFO", "Enter the target toUserId:")
            toUserId_str = input().strip()
            if not toUserId_str:
                print_colored("WARN", "toUserId cannot be empty.")
                continue
            toUserId = int(toUserId_str)
            return toUserId
        except ValueError:
            print_colored("WARN", "toUserId must be a valid integer.")
        except KeyboardInterrupt:
            print_colored("ABORT", "Input interrupted.")
            raise


def main() -> None:
    global USER_AGENTS, MESSAGES, PROXIES
    USER_AGENTS = load_file_lines("user_agents.txt")
    MESSAGES = load_file_lines("message.txt")
    PROXIES = load_file_lines("proxy.txt")
    if not USER_AGENTS or not MESSAGES or not PROXIES:
        print_colored("ABORT", "Required files missing or empty.")
        return
    try:
        toUserId = get_toUserId()
    except KeyboardInterrupt:
        return
    send_messages(toUserId, MESSAGES, PROXIES, USER_AGENTS)


if __name__ == "__main__":
    main()
