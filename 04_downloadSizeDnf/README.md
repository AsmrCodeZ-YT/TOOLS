# dnf-upgrade-size

A small but handy tool for **Fedora** that helps you quickly see **which packages are bigger and more important** before updating.  
If you're like me and sometimes get lost when updating packages, this tool is here to save you! 😎

---

## Features
- Lists all available updates along with their download sizes
- Color-coded and neatly formatted for quickly spotting large (important) packages
- No extra dependencies; only requires `dnf`, `awk`, `numfmt`, `sort`
- Open-source and ready for use or further development

---

## Installation

### Easy one-line install with curl:
```bash
curl -fsSL https://raw.githubusercontent.com/USERNAME/dnf-upgrade-size/main/install.sh | bash
````

### Manual installation:

```bash
git clone https://github.com/asmrcodez-yt/dnf-upgrade-size
cd dnf-upgrade-size
./install.sh
```

> After installation, simply run:

```bash
dnff
```

---

## Usage

* To see the full list of updates with their sizes:

```bash
dnff
```

* To see only the top 10 largest packages:

```bash
dnff | head -n 10
```

## Pro Tips

* Bigger packages usually mean **more important updates**.
* You can pipe the output to `less -R` to preserve colors:

```bash
dnff| less -R
```

---

## Contributing

This project is open-source. Feel free to submit a Pull Request if you have ideas or improvements! 🎉

---

## License

MIT License


