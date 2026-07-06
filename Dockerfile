FROM python:3.10-slim

RUN apt update && apt install -y \
    golang \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/tomnomnom/assetfinder@latest && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest && \
    go install -v github.com/LukaSikic/subzy@latest && \
    go install -v github.com/sensepost/gowitness@latest && \
    go install github.com/tomnomnom/waybackurls@latest

RUN pip install --no-cache-dir python-telegram-bot requests beautifulsoup4

RUN git clone https://github.com/gwen001/github-subdomains.git

ENV PATH=$PATH:/root/go/bin

WORKDIR /app
COPY 0xhunter.py config.py ./

CMD ["python3", "0xhunter.py"]
