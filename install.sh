#!/bin/bash
# Auto Installer & Updater untuk 0xHunter Tools & Dependencies
# Author: Izumy

GITHUB_SUBDOMAINS_DIR="github-subdomains"

install_tools() {
    echo "🚀 Memulai instalasi tools dan dependencies untuk 0xHunter..."

    pkg update && pkg upgrade -y
    pkg install golang git python python-pip -y

    export PATH=$PATH:$HOME/go/bin
    echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc

    echo "🛠️ Menginstall Subfinder..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

    echo "🛠️ Menginstall Assetfinder..."
    go install -v github.com/tomnomnom/assetfinder@latest

    echo "🛠️ Menginstall Naabu..."
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

    echo "🛠️ Menginstall Nuclei..."
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

    echo "🛠️ Menginstall httpx..."
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

    echo "🛠️ Menginstall dnsx..."
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

    echo "🛠️ Menginstall Subzy..."
    go install -v github.com/LukaSikic/subzy@latest

    echo "🛠️ Menginstall Gowitness..."
    go install -v github.com/sensepost/gowitness@latest

    echo "🛠️ Menginstall Waybackurls..."
    go install github.com/tomnomnom/waybackurls@latest

    echo "🐍 Menginstall Python dependencies..."
    pip install python-telegram-bot requests beautifulsoup4

    echo "📂 Mengclone github-subdomains..."
    if [ ! -d "$GITHUB_SUBDOMAINS_DIR" ]; then
        git clone https://github.com/gwen001/github-subdomains.git
    else
        echo "✅ Folder github-subdomains sudah ada, melewati clone..."
    fi
    cd $GITHUB_SUBDOMAINS_DIR
    pip install -r requirements.txt
    cd ..

    echo "✅ Semua tools dan dependencies berhasil diinstall!"
    echo "📌 Sekarang lo bisa jalanin: python3 0xhunter.py"
}

update_tools() {
    echo "🔄 Memulai update tools ke versi terbaru..."

    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install -v github.com/tomnomnom/assetfinder@latest
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
    go install -v github.com/LukaSikic/subzy@latest
    go install -v github.com/sensepost/gowitness@latest
    go install github.com/tomnomnom/waybackurls@latest

    pip install --upgrade python-telegram-bot requests beautifulsoup4

    if [ -d "$GITHUB_SUBDOMAINS_DIR" ]; then
        cd $GITHUB_SUBDOMAINS_DIR
        git pull
        pip install -r requirements.txt
        cd ..
    fi

    echo "✅ Semua tools berhasil diupdate ke versi terbaru!"
}

if [ "$1" == "update" ]; then
    update_tools
else
    install_tools
fi
