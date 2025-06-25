# 🎨 PiLively - Live 3D Wallpapers for Raspberry Pi

Transform your Raspberry Pi desktop with stunning **True 3D animated wallpapers**! PiLively brings the power of Lively Wallpaper to Raspberry Pi with optimized 3D effects.

## ✨ Features

- 🚀 **True 3D Ae Plexus** - Stunning particle network animations
- ⚡ **Optimized for Pi 5** - Smooth 60fps performance  
- 🎛️ **GUI Configuration** - Easy setup and customization
- 🔧 **systemd Integration** - Auto-start on boot
- 💾 **Minimal Package** - Only 7.2MB download

## 🎥 Demo

*3D Ae Plexus effect running on Raspberry Pi*

## 🚀 Quick Install

### Download Latest Release:
1. Go to [**Releases**](https://github.com/bobster316/pilively/releases)
2. Download `pilively-3d-final-v1.2.0.tar.gz`
3. Follow installation steps below:

```bash
# Extract and install
tar -xzf pilively-3d-final-v1.2.0.tar.gz
cd pilively_project
chmod +x install.sh
./install.sh

# Start True 3D wallpaper
pilively
```

## 📋 Requirements

- **Raspberry Pi 4/5** (recommended)
- Raspberry Pi OS with desktop
- Python 3.7+
- 128MB GPU memory split
- OpenGL support

## 🛠️ Manual Installation

If the automated installer doesn't work:

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-pygame
pip3 install --user pygame psutil watchdog

# Install PiLively
python3 pilively.py
```

## ⚙️ Configuration

Run the GUI configuration tool:
```bash
pilively-config.py
```

### Performance Tuning
Edit `~/.config/pilively/pilively.json`:
```json
{
  "performance": {
    "target_fps": 60,
    "particle_count": 500,
    "use_gpu_acceleration": true,
    "quality_preset": "high"
  }
}
```

## 🎯 Supported Pi Models

| Model | Performance | Recommended Settings |
|-------|-------------|---------------------|
| Pi 5 | Excellent | High quality, 60fps |
| Pi 4 (4GB+) | Good | Medium quality, 30fps |
| Pi 4 (2GB) | Fair | Low quality, 30fps |
| Pi 3B+ | Limited | Low quality, 15fps |

## 🐛 Troubleshooting

**Performance Issues:**
- Reduce particle count in config
- Lower target FPS
- Increase GPU memory split: `sudo raspi-config` → Advanced → Memory Split → 128

**Service Won't Start:**
```bash
# Check service status
sudo systemctl status pilively@$USER.service

# View logs
journalctl -u pilively@$USER.service
```

## 🤝 Contributing

Feel free to submit issues and pull requests! Ideas for contributions:
- New 3D wallpaper effects
- Performance optimizations
- Additional Pi model support
- Documentation improvements

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⭐ Star This Project

If PiLively enhances your Pi desktop experience, please give it a star! ⭐
