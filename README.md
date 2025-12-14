# Computer-Vision---Gesture-controlled-mouse

A python application that lets the user control their mouse via camera captured hand gestures. This project is built using Python 3.10, OpenCV for image capturing, and MediaPipe for hand landmark handling.

## Technologies and tools used

Python 3.10.x

OpenCV (opencv-python) 4.8.x

MediaPipe 0.10.x

NumPy 1.24.x

PyAutoGUI 0.9.54

OS: Windows 10 / 11

Webcam: Built-in / USB (real-time capture)

## Features

So far, the folowing features are accomplished:
- Left click
- Right click
- Double click
- Drag mouse
    
## Results & Observations

- Cursor control is smooth and responsive under normal lighting conditions.
- Gesture stability required state-based logic to prevent repeated clicks.
- Direct mapping from camera space to screen space caused jitter; smoothing and padding significantly improved usability.
- Performance is real-time on a standard laptop webcam (~30 FPS).

## Limitations

- Performance depends on lighting and camera quality.
- Hand tracking degrades near camera edges.
- Prolonged use can cause hand fatigue.
- Gestures are rule-based and may require per-user tuning.

## Future Improvements

- Train a gesture classifier instead of rule-based thresholds.
- Add scroll and zoom gestures.
- Support multi-hand interaction.
- Combine with voice commands for accessibility.

## Demo:

demo/Gesture_control.mp4
