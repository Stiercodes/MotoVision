# 🏍️ MotoVision

> Control your motorcycle in racing games using only your body movements and a webcam.

MotoVision is an AI-powered computer vision controller that converts natural riding gestures into real-time keyboard inputs. Using **MediaPipe**, **OpenCV**, and **Python**, it tracks body posture and hand movements to create an immersive, controller-free motorcycle riding experience.

---

## ✨ Features

- 🎥 Real-time webcam tracking
- 🧍 AI-powered body pose detection
- ✋ Hand gesture recognition
- 🏍️ Natural motorcycle lean steering
- ⚡ Adaptive pulse steering system
- 🏁 Throttle gesture detection
- 🎮 Keyboard emulation for PC games
- 📊 Live HUD with movement feedback
- ⚙️ Calibration system
- 🖥️ Lightweight and real-time performance

---

## 🛠️ Tech Stack

- Python 3.11
- OpenCV
- MediaPipe
- NumPy
- pynput
- Tkinter (if used)
- macOS / Windows Compatible

---

## 📂 Project Structure

```
MotoVision/
│
├── main.py
├── camera.py
├── pose_tracker.py
├── body_analyzer.py
├── steering_controller.py
├── throttle_controller.py
├── keyboard_output.py
├── calibration.py
├── tuning.py
│
├── assets/
│   ├── logo.png
│   ├── demo.gif
│   └── screenshots/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/Stiercodes/MotoVision.git
```

### Enter the project

```bash
cd MotoVision
```

### Create a virtual environment

macOS / Linux

```bash
python3.11 -m venv venv
source venv/bin/activate
```

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running MotoVision

```bash
python main.py
```

---

## 🎮 Controls

| Action | Gesture |
|---------|----------|
| Throttle | Rotate right hand downward |
| Steer Left | Lean left |
| Steer Right | Lean right |
| Calibrate | Press **C** |
| Exit | Press **Q** |

---

## 🧠 How It Works

1. Webcam captures live video.
2. MediaPipe detects body and hand landmarks.
3. Motion analysis calculates body lean and hand rotation.
4. Steering and throttle values are generated.
5. Keyboard inputs are simulated.
6. Racing game receives keyboard controls in real time.

---

## 📈 Current Features

- ✅ Pose Detection
- ✅ Hand Tracking
- ✅ Lean Steering
- ✅ Adaptive Pulse Steering
- ✅ Throttle Detection
- ✅ Keyboard Output
- ✅ Live Debug HUD
- ✅ Calibration

---

## 🚧 Planned Features

- Haptic feedback gloves
- Vibration module support
- Gear shifting gestures
- Brake gesture
- Clutch support
- Head tracking
- Multi-camera support
- Telemetry integration
- VR compatibility
- Controller emulation (XInput / ViGEm)

---

## 📸 Demo

Add screenshots or GIFs here.

```
assets/demo.gif
```

---

## 📋 Requirements

- Python 3.11
- Webcam
- Good lighting
- 720p or higher camera recommended

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch.

```bash
git checkout -b feature-name
```

3. Commit your changes.

```bash
git commit -m "Add awesome feature"
```

4. Push.

```bash
git push origin feature-name
```

5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Pranav Phanse**

GitHub: https://github.com/Stiercodes

---

## ⭐ Support

If you found this project interesting, consider giving it a ⭐ on GitHub.

It helps the project grow and motivates future development.

---

## 🏁 MotoVision

*"Ride with your body. Control with AI."*
