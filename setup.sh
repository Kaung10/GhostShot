sudo apt update
python3 -m venv venv 
. ./venv/bin/activate
pip install -r requirements.txt

# -- GoLang Setup ---
sudo apt install golang
# mine ---> go version go1.24.6 linux/amd64 

# --- To use fyne-cross, we need docker to simulate windows --
sudo apt install docker.io -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# -- Install Fyne for GUI and Fyne-cross for exe ---
go install fyne.io/fyne/v2/cmd/fyne@latest			# mine --> fyne cli version: v1.7.0
go install fyne.io/tools/cmd/fyne@latest
go install github.com/fyne-io/fyne-cross@latest		# mine --> fyne-cross version v1.6.1
sudo apt install libx11-dev libxcursor-dev libxrandr-dev libxinerama-dev libxi-dev build-essential libgl1-mesa-dev libglu1-mesa-dev libxxf86vm-dev libxrender-dev

# -- Enable to fyne-cross in shell

case "$SHELL" in
    */zsh)
        echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.zshrc
        source ~/.zshrc
        echo "[+] Injected into ~/.zshrc"
        ;;
    */bash)
        echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
        source ~/.bashrc
        echo "[+] Injected into ~/.bashrc"
        ;;
    *)
        echo "[!] Unknown shell: $SHELL"
        ;;
esac

# -- go project setup ----
cd ransomware
go mod init Ghostshot
go get fyne.io/fyne/v2
go get fyne.io/fyne/v2/app
go get fyne.io/fyne/v2/container
go get fyne.io/fyne/v2/canvas
go get fyne.io/fyne/v2/dialog
go get fyne.io/fyne/v2/widget
go get fyne.io/fyne/v2/layout
go get fyne.io/fyne/v2/theme
fyne bundle Creepster-Regular.ttf > bundled.go
cd ..

cd Fake_File_Generator
go mod init generator
go get fyne.io/fyne/v2
go get fyne.io/fyne/v2/app
go get fyne.io/fyne/v2/container
go get fyne.io/fyne/v2/canvas
go get fyne.io/fyne/v2/dialog
go get fyne.io/fyne/v2/widget
go get fyne.io/fyne/v2/theme
go mod tidy
cd ..



