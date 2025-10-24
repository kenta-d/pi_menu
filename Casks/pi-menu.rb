cask "pi-menu" do
  version "2.0.0"
  sha256 :no_check

  url "https://github.com/kenta-d/pi-menu/releases/download/v#{version}/Pi_Menu_v#{version}_macOS.zip"
  name "Pi Menu"
  desc "Modern circular application launcher for macOS with Glassmorphism UI"
  homepage "https://github.com/kenta-d/pi-menu"

  depends_on macos: ">= :catalina"
  depends_on formula: "python@3.13"

  app "Pi Menu.app"

  zap trash: [
    "~/Library/Preferences/com.kenta-d.pi-menu.plist",
    "~/Library/Application Support/Pi Menu",
    "~/.pi-menu",
  ]

  caveats <<~EOS
    Pi Menu requires PyQt6 to be installed. You can install it with:
      brew install pyqt@6
    
    Or using pip:
      pip3 install PyQt6
  EOS
end