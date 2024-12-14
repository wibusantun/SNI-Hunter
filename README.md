## AdwanceSNI-2.0
AdwanceSNI 2.0 is the enhanced version of the original AdwanceSNI program, designed to provide a comprehensive suite for network scanning and subdomain discovery. It retains the core functionalities of finding subdomains and scanning hosts while introducing new tools for IP extraction, IP generation, and a lite scanner.

## Installation commands 🔗
```shell
termux-setup-storage
```
 ```shell
pkg update && pkg upgrade -y
```
 ```shell
pkg install golang -y
```
```shell 
pkg install python-pip -y
```
 ```shell 
pkg install zlib -y
```

```shell
pkg install git
```
```shell
 pip install aiofiles rich aiohttp pytz bs4 requests colorama psutil
```

# Add Go to PATH

```shell
echo 'PATH="$PATH:$HOME/go/bin"' >> $HOME/.bashrc
source $HOME/.bashrc
```

# Install subfinder and bughunter-go

```shell 
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

```shell
go install -v github.com/Ayanrajpoot10/bughunter-go@v1.0.2
```

# Clone the repository

 ```shell 
git clone https://github.com/SirYadav1/AdwanceSNI-2.0
```

## Usage 📌
 
```shell
cd AdwanceSNI-2.0
```

```shell
python main.py
```

## Author Information

**Author**: YADAV  
**Coded by**: YADAV  
**Design by**: Amith<br>
**Contact**: siryadav025@gamil.com<br>
**Telegram**: [@SirYadav](https://t.me/SirYadav)  
**Version**: 2.0
