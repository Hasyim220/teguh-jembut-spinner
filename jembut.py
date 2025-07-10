#!/usr/bin/env python3
import requests
import time
import pyfiglet
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tampilkan ASCII art
ascii_art = pyfiglet.figlet_format("TEGUH JEMBUT")
print(ascii_art)

# Endpoint API
url_spin = "https://api.jtmkbot.click/roulette/spin"
url_balance = "https://api.jtmkbot.click/wallet/balance"

# Header dasar
base_headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    'Accept': "application/json, text/plain, */*",
    'Accept-Encoding': "identity",
    'origin': "https://v2.jtmkbot.click",
    'referer': "https://v2.jtmkbot.click/",
    'accept-language': "en-US,en;q=0.9",
}

def read_query_from_file():
    """Baca file query.txt dan ambil nama + query_id."""
    try:
        with open("query.txt", "r") as file:
            queries = file.readlines()
        return [query.strip().split(" ", 1) for query in queries]
    except Exception as e:
        print(f"[ERROR] Gagal membaca file query.txt: {e}")
        return []

def get_balance(headers):
    """Ambil saldo (balance) akun dari API."""
    try:
        response = requests.get(url_balance, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get("balance", "N/A")
        else:
            print(f"⚠️ Gagal ambil balance: {response.status_code}")
            return "N/A"
    except Exception as e:
        print(f"⚠️ Error saat ambil balance: {e}")
        return "N/A"

def single_spin(telegram_name, headers):
    """Spin 1x dan ambil jumlah tiket jika dapat."""
    try:
        response = requests.post(url_spin, headers=headers)
        if response.status_code == 401:
            print(f"[{telegram_name}] ❌ Unauthorized (401). Cek query ID atau header.")
            return 0
        elif response.status_code != 200:
            print(f"[{telegram_name}] ❌ Gagal spin, status: {response.status_code}")
            return 0

        json_data = response.json()
        prize = json_data.get("secondLine", {}).get("prize", {}).get("tickets", 0)
        balance_points = get_balance(headers)

        if prize > 0:
            print(f"[{telegram_name}] 🎯 Tiket didapat: {prize} | 💰 Total points: {balance_points}")
        else:
            print(f"[{telegram_name}] ❌ Tidak dapat tiket. | 💰 Total points: {balance_points}")

        return prize

    except Exception as e:
        print(f"[{telegram_name}] ⚠️ Error saat spin: {e}")
        return 0

def process_account(telegram_name, query_id):
    """Spin berkali-kali untuk 1 akun sampai tidak dapat tiket lagi."""
    print(f"\n🚀 Memulai spin untuk: {telegram_name}")
    headers = base_headers.copy()
    headers['secure-header'] = query_id  # Tambahkan query_id ke header

    while True:
        with ThreadPoolExecutor(max_workers=3) as executor:  # Optimized for Termux
            futures = [executor.submit(single_spin, telegram_name, headers) for _ in range(5)]
            results = [f.result() for f in as_completed(futures)]

        if all(result == 0 for result in results):
            print(f"[{telegram_name}] ✅ Spin habis. Lanjut akun berikutnya.\n")
            break

        time.sleep(1)

def main():
    """Proses semua akun dalam query.txt"""
    queries = read_query_from_file()
    for query in queries:
        try:
            telegram_name, query_id = query
            process_account(telegram_name, query_id)
        except ValueError:
            print(f"[ERROR] Format query tidak sesuai: {query}")
            continue

    print("✅ Semua akun telah diproses.")

# Jalankan script
if __name__ == "__main__":
    main()
