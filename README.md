# 0xHunter — Telegram Bot for Bug Bounty & Reconnaissance

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED)
![Linux](https://img.shields.io/badge/Linux-Supported-8A2BE2)
![macOS](https://img.shields.io/badge/macOS-Supported-000000)
![Windows](https://img.shields.io/badge/Windows-Supported-0078D6)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)
![Contributors](https://img.shields.io/github/contributors/hidayat-tanjung/0xHunter)
![Issues](https://img.shields.io/github/issues/hidayat-tanjung/0xHunter)

> 🔥 Bot Telegram untuk bug bounty, reconnaissance, dan vulnerability scanning otomatis.  
> **Author:** Izumy

---

<img width="1536" height="1024" alt="0xHunter Demo" src="https://github.com/user-attachments/assets/d8e0e550-4a4c-44ce-8832-a2dd8665fe54" />

---

## 📖 Apa Itu 0xHunter?

0xHunter adalah bot Telegram yang dirancang khusus untuk membantu para bug bounty hunter dan security researcher dalam melakukan **reconnaissance** dan **vulnerability scanning** secara otomatis.

Lo tinggal kirim perintah ke bot, dan bot akan menjalankan tools eksternal (seperti `subfinder`, `naabu`, `nuclei`, `subzy`, `gowitness`, dll) lalu mengirimkan hasilnya langsung ke Telegram lo.

---

## ✨ Fitur Utama

### 🔍 Reconnaissance
- `/subdomainizer <domain>` — Gabungan Assetfinder + Subfinder
- `/subfinder <domain>` — Subdomain discovery (Subfinder)
- `/chaos <domain>` — Subdomain dari Chaos database (butuh API key)
- `/crtsh <domain>` — Subdomain dari crt.sh database (gratis)
- `/masscan <target>` — Port scanner cepat (Masscan)
- `/naabu <target>` — Port scanner cepat (Naabu)
- `/httpx <url>` — HTTP probe (status code, title, server, tech)
- `/dnsx <domain>` — DNS enumeration (A, MX, NS, TXT, CNAME)
- `/waybackurls <domain>` — URL historis dari Wayback Machine
- `/wayback <domain>` — Alias untuk `/waybackurls`
- `/github-subdomains <domain>` — Subdomain dari GitHub
- `/vhost <domain>` — Cek virtual host

### 🛡️ Vulnerability Scanning
- `/nuclei <target>` — Vulnerability scan dengan Nuclei (ribuan template)
- `/scan <url>` — Full scan celah (SQLi, XSS, LFI, SSRF, RCE, Open Redirect)
- `/detect <url>` — Scan cepat (XSS, SQLi, LFI, Open Redirect)
- `/sqli <url>` — Khusus uji SQL Injection
- `/xss <url>` — Khusus uji Cross-Site Scripting
- `/lfi <url>` — Khusus uji Local File Inclusion
- `/ssrf <url>` — Khusus uji Server-Side Request Forgery
- `/rce <url>` — Khusus uji Remote Code Execution
- `/openredirect <url>` — Khusus uji Open Redirect

### 🎯 Actionable Intelligence
- `/takeover <domain>` — Cek subdomain takeover (pakai Subzy)
- `/js <url>` — Cari file JavaScript dan secret (simulasi)
- `/cors <url>` — Cek konfigurasi CORS
- `/s3 <domain>` — Cek S3 bucket publik
- `/cloud <domain>` — Cek cloud provider & metadata
- `/waf <url>` — Cek Web Application Firewall
- `/archive <url>` — Cek arsip Wayback Machine

### 📸 Screenshot & Report
- `/screenshot <url>` — Ambil screenshot website (pakai Gowitness)
- `/report <url>` — Generate laporan lengkap bug bounty
- `/export <url>` — Export laporan ke file `.txt`

---

## 📁 Struktur Folder

```
0xHunter-Docker/
├── 0xhunter.py                # Bot utama
├── config.py                  # Konfigurasi token & API key
├── Dockerfile                 # Dockerfile untuk build image
├── docker-compose.yml         # Docker Compose untuk menjalankan bot
├── .dockerignore              # Mengabaikan file saat build
├── .env.example               # Template environment variable
├── README.md                  # Dokumentasi
├── github-subdomains/         # Folder clone (dari gwen001/github-subdomains)
│   ├── github-subdomains.py
│   └── requirements.txt
├── reports/                   # Folder hasil laporan export
├── logs/                      # Folder log bot
└── payloads/                  # Folder penyimpanan payload
```

---

## 📦 Dependensi

Semua dependensi diinstall **otomatis** di dalam Docker image.  
Lo tidak perlu menginstall apa pun secara manual.

---

## 🛠️ Instalasi & Menjalankan Bot (Docker)

### 1. Persiapkan Lingkungan
- Pastikan Docker sudah terinstall di sistem lo (Linux, macOS, atau Windows)
- Koneksi internet stabil

### 2. Clone Repository

```bash
git clone https://github.com/hidayat-tanjung/0xHunter-Docker.git
cd 0xHunter-Docker
```

### 3. Konfigurasi Token Bot

Buat file `.env` dari template:

```bash
cp .env.example .env
```

Edit file `.env` dan isi token bot lo:

```env
TOKEN=isi_token_bot_lo_di_sini
CHAOS_API_KEY=isi_api_key_chaos_lo_di_sini  # Opsional
```

### 4. Build Docker Image

```bash
docker build -t 0xhunter-bot .
```

### 5. Jalankan Bot dengan Docker Compose

```bash
docker-compose up -d
```

Bot akan berjalan di background dan otomatis restart jika crash.

---

## 🐧 Instalasi Docker di Linux (Ubuntu/Debian)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Docker dan Docker Compose
sudo apt install docker.io docker-compose -y

# 3. Mulai Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 🍏 Instalasi Docker di macOS

```bash
# 1. Install Docker Desktop via Homebrew
brew install --cask docker

# 2. Start Docker
open /Applications/Docker.app
```

---

## 🪟 Instalasi Docker di Windows

1. Download Docker Desktop dari: https://www.docker.com/products/docker-desktop/
2. Jalankan installer dan ikuti petunjuk
3. Buka PowerShell sebagai Administrator
4. Lanjutkan ke langkah **Clone Repository**

---

## 🤖 Cara Membuat Bot di Telegram (BotFather)

### 1. Buka BotFather di Telegram

Buka Telegram, cari kontak `@BotFather`, lalu kirim `/start`.

### 2. Buat Bot Baru

Kirim perintah:

```
/newbot
```

BotFather akan meminta:
- **Nama bot** (contoh: `0xHunter`)
- **Username bot** (contoh: `@ZeroXHunterBot` atau nama lain yang belum dipakai)

### 3. Salin Token Bot

Setelah lo memberikan nama dan username, BotFather akan mengirim token seperti ini:

```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Salin token tersebut** — ini adalah kunci akses bot lo.

### 4. Masukkan Token ke `.env`

Buka file `.env` yang sudah dibuat:

```bash
nano .env
```

Isi dengan token lo:

```env
TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CHAOS_API_KEY=isi_api_key_chaos_lo_di_sini  # Optional
```

Simpan dengan `Ctrl+X`, lalu `Y`, lalu `Enter`.

---

## 📱 Cara Pakai di Telegram

1. Buka Telegram, cari bot lo (misal: `@ZeroXHunterBot`)
2. Kirim perintah `/start` atau `/help`
3. Gunakan perintah sesuai kebutuhan

### Contoh Penggunaan

| Perintah | Output yang Diharapkan |
|----------|------------------------|
| `/subdomainizer example.com` | Daftar subdomain target |
| `/naabu example.com` | Port terbuka (22, 80, 443, dll) |
| `/nuclei https://example.com` | Laporan celah keamanan (jika ada) |
| `/takeover example.com` | Subdomain takeover yang rentan |
| `/screenshot https://example.com` | Gambar screenshot website |
| `/report example.com` | Laporan lengkap bug bounty |

---

## 📋 Daftar Lengkap Perintah

### 🔍 Reconnaissance
```
/subdomainizer <domain>
/subfinder <domain>
/chaos <domain>
/crtsh <domain>
/masscan <target>
/naabu <target>
/httpx <url>
/dnsx <domain>
/waybackurls <domain>
/wayback <domain>
/github-subdomains <domain>
/vhost <domain>
```

### 🛡️ Vulnerability Scanning
```
/nuclei <target>
/scan <url>
/detect <url>
/sqli <url>
/xss <url>
/lfi <url>
/ssrf <url>
/rce <url>
/openredirect <url>
```

### 🎯 Actionable Intelligence
```
/takeover <domain>
/js <url>
/cors <url>
/s3 <domain>
/cloud <domain>
/waf <url>
/archive <url>
```

### 📸 Screenshot & Report
```
/screenshot <url>
/report <url>
/export <url>
```

> 📌 **Gunakan hanya untuk target yang diizinkan**

---

## 🛡️ Vulnerability yang Bisa Discan

| Vulnerability | Perintah di Bot |
|---|---|
| SQL Injection | `/sqli <url>` atau `/scan <url>` |
| Cross-Site Scripting (XSS) | `/xss <url>` atau `/scan <url>` |
| Local File Inclusion (LFI) | `/lfi <url>` atau `/scan <url>` |
| Server-Side Request Forgery (SSRF) | `/ssrf <url>` atau `/scan <url>` |
| Remote Code Execution (RCE) | `/rce <url>` atau `/scan <url>` |
| Open Redirect | `/openredirect <url>` atau `/scan <url>` |
| CORS Misconfiguration | `/cors <url>` |
| Subdomain Takeover | `/takeover <domain>` |
| S3 Bucket Publik | `/s3 <domain>` |
| Cloud Metadata Exposure | `/cloud <domain>` |
| WAF Detection | `/waf <url>` |
| Wayback Machine Archive | `/archive <url>` |

---

## 🐳 Manajemen Docker

| Perintah | Keterangan |
|---|---|
| `docker-compose up -d` | Jalankan bot di background |
| `docker-compose logs bot` | Lihat log bot |
| `docker-compose restart bot` | Restart bot |
| `docker-compose down` | Hentikan dan hapus container |

---

## ⚠️ Troubleshooting & Error Umum

### 1. Bot tidak merespon di Telegram

**Penyebab:** Token salah atau bot belum jalan.

**Solusi:**
- Cek log dengan: `docker-compose logs bot`
- Pastikan `TOKEN` di `.env` benar
- Restart bot: `docker-compose restart`

### 2. `/chaos` gagal atau tidak ada output

**Penyebab:** API key Chaos tidak valid atau tidak ada.

**Solusi:**
- Daftarkan di https://chaos.projectdiscovery.io/
- Pastikan `CHAOS_API_KEY` di `.env` benar

### 3. Build image gagal

**Penyebab:** Dockerfile error atau koneksi internet lambat.

**Solusi:**
- Cek koneksi internet
- Ulangi: `docker build -t 0xhunter-bot .`

---

## 🤝 Contributing

Kontribusi sangat diterima! Jika lo ingin mengembangkan 0xHunter, ikuti langkah berikut:

### 1. Fork Repository
Klik tombol **Fork** di GitHub untuk membuat salinan repo lo sendiri.

### 2. Clone Repository
```bash
git clone https://github.com/username/0xHunter-Docker.git
cd 0xHunter-Docker
```

### 3. Buat Branch
```bash
git checkout -b fitur-baru
```

### 4. Buat Perubahan & Commit
```bash
git add .
git commit -m "Tambah fitur baru atau perbaikan"
```

### 5. Push ke Repository
```bash
git push origin fitur-baru
```

### 6. Buat Pull Request
1. Buka repository asli di GitHub
2. Klik **Compare & Pull Request**
3. Isi deskripsi perubahan
4. Klik **Create Pull Request**

### 📌 Pedoman Kontribusi
- Gunakan kode yang rapi dan mudah dibaca
- Tambahkan komentar untuk kode yang kompleks
- Pastikan bot tetap berjalan setelah perubahan
- Jangan menghapus kredit penulis
- Ikuti style code yang sudah ada

### 💬 Catatan dari Penulis

> "Saya sangat menghargai setiap kontribusi, sekecil apa pun. Jika ada yang kurang jelas, jangan ragu untuk bertanya lewat Issues atau Discussion."  
> — Izumy

---

## ⚠️ Disclaimer

**Gunakan bot ini hanya pada:**
- Program Bug Bounty (dengan izin)
- Target yang memiliki explicit authorization
- Laboratorium pribadi
- CTF (Capture The Flag)

**Jangan gunakan terhadap sistem tanpa izin.**  
Seluruh tanggung jawab penggunaan berada pada pengguna. Penulis tidak bertanggung jawab atas segala bentuk penyalahgunaan.

---

## 📜 License

MIT License — Free for personal and commercial use.

Lihat file [LICENSE](LICENSE) untuk detail lengkap.

---

Made with 🔥 by Izumy
