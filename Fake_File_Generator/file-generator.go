package main

import (
	"errors"
	"fmt"
	"image/color"
	"math/rand"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

// --- CYBERPUNK THEME ---
type CyberpunkTheme struct{}

func (m CyberpunkTheme) Color(name fyne.ThemeColorName, variant fyne.ThemeVariant) color.Color {
	switch name {
	case theme.ColorNameBackground:
		return color.RGBA{R: 10, G: 10, B: 15, A: 255} // Deep Space Black
	case theme.ColorNameButton:
		return color.RGBA{R: 255, G: 0, B: 85, A: 255} // Neon Pink
	case theme.ColorNamePrimary:
		return color.RGBA{R: 0, G: 255, B: 255, A: 255} // Cyan Accent
	case theme.ColorNameInputBackground:
		return color.RGBA{R: 20, G: 20, B: 30, A: 255}
	case theme.ColorNameForeground:
		return color.RGBA{R: 0, G: 255, B: 255, A: 255} // Cyan Text
	}
	return theme.DefaultTheme().Color(name, variant)
}

func (m CyberpunkTheme) Icon(name fyne.ThemeIconName) fyne.Resource { return theme.DefaultTheme().Icon(name) }
func (m CyberpunkTheme) Font(style fyne.TextStyle) fyne.Resource    { return theme.DefaultTheme().Font(style) }
func (m CyberpunkTheme) Size(name fyne.ThemeSizeName) float32       { return theme.DefaultTheme().Size(name) }

// --- LOGIC ---
var targetDir string

func generateFiles(count int) {
	for i := 1; i <= count; i++ {
		name := fmt.Sprintf("CORP_LEAK_%04d.txt", i)
		path := filepath.Join(targetDir, name)
		content := fmt.Sprintf("ID: %X\nTOKEN: %d\nSTATUS: COMPROMISED\n", rand.Intn(0xFFFFFF), rand.Int63())
		os.WriteFile(path, []byte(content), 0644)
	}
}

func main() {
	rand.Seed(time.Now().UnixNano())
	a := app.NewWithID("com.ghostshot.generator")
	a.Settings().SetTheme(&CyberpunkTheme{})
	
	w := a.NewWindow("GHOSTSHOT // OS-INT")
	w.Resize(fyne.NewSize(700, 400))

	// Title with a "Glow" effect using a Canvas Text
	title := canvas.NewText("GHOSTSHOT // one shot. no trace. no mercy.", color.RGBA{R: 0, G: 255, B: 255, A: 255})
	title.TextSize = 24
	title.TextStyle = fyne.TextStyle{Bold: true, Monospace: true}
	title.Alignment = fyne.TextAlignCenter

	dirLabel := widget.NewLabelWithStyle("> SYSTEM_READY", fyne.TextAlignLeading, fyne.TextStyle{Monospace: true})
	countEntry := widget.NewEntry()
	countEntry.SetPlaceHolder("QUANTITY...")

	startBtn := widget.NewButton("INITIALIZE GENERATION", func() {
	    n, err := strconv.Atoi(countEntry.Text)
	    if err != nil {
	        dialog.ShowError(errors.New("INVALID PACKET COUNT"), w)
	        return
	    }
	    generateFiles(n)
	    d := dialog.NewInformation("SUCCESS", "FILES are Generated\n Time to Encrypt", w)
	    d.SetOnClosed(func() {
	        a.Quit()
	    })
	    d.Show()
	})

	browseBtn := widget.NewButton("SELECT TARGET DIR", func() {
		dialog.ShowFolderOpen(func(uri fyne.ListableURI, err error) {
			if uri != nil {
				targetDir = uri.Path()
				dirLabel.SetText("> TARGET: " + targetDir)
			}
		}, w)
	})

	// Layout with some padding and visual separation
	content := container.NewVBox(
		title,
		canvas.NewLine(color.RGBA{R: 0, G: 255, B: 255, A: 255}), // Cyan separator
		container.NewPadded(dirLabel),
		browseBtn,
		widget.NewSeparator(),
		widget.NewLabelWithStyle("FILE_COUNT:", fyne.TextAlignLeading, fyne.TextStyle{Monospace: true}),
		countEntry,
		startBtn,
	)

	w.SetContent(container.NewPadded(content))
	w.ShowAndRun()
}