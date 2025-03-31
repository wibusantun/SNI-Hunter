## ASNI-Hunter

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
git clone https://github.com/wibusantun/SNI-Hunter
```

## Usage 📌
 
```shell
cd SNI-Hunter
```
# Install requirements
```shell
bash install.sh
```
# Run program by bash 
```shell
bash run.sh
```

