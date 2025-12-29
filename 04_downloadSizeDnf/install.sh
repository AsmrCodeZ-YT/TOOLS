#!/usr/bin/env bash
set -e

INSTALL_DIR="$HOME/.local/bin"
BIN_NAME="dnff"

mkdir -p "$INSTALL_DIR"

cat ./dnff.sh > "$INSTALL_DIR/$BIN_NAME"
chmod +x "$INSTALL_DIR/$BIN_NAME"

if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "⚠️  Added ~/.local/bin to PATH. Reload your shell or run: source ~/.bashrc"
fi

echo "✅ $BIN_NAME installed successfully!"
echo "Run: $BIN_NAME"
