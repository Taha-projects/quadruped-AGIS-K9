# Quadruped AGIS-K9

A Raspberry Pi 3 Model A+ quadruped prototype using eight hobby servos, a PCA9685 PWM driver, a local phone/laptop control page, and an optional CSI camera stream to VLC.

## Aim and purpose

Translate the project owner's ESP32-tested stand, gait, sit, wave, and dance movements to Raspberry Pi. The project supports robotics education, embedded Linux, gait programming, camera streaming, and human-operated remote inspection.

Potential uses include indoor infrastructure checks, education, and observation where direct access is inconvenient or hazardous. In military or security settings it could be explored as an unarmed defensive observation or infrastructure inspection prototype. It is not a validated military system and includes no autonomous navigation, person identification, targeting, or weapon control. Operate only with human supervision and where camera use is authorized.

Benefits: off-the-shelf components, remote viewing, reusable motion patterns, and the option to keep an operator farther from a hazardous area. Performance depends on the frame, servo torque, supply, network, lighting, and terrain.

## Architecture

~~~mermaid
flowchart LR
  OP[Phone or laptop] -- Wi-Fi HTTP commands :5000 --> PI[Raspberry Pi 3 A+]
  CAM[CSI camera] -- ribbon cable --> PI
  PI -- I2C SDA/SCL --> PCA[PCA9685 at 0x40]
  PSU[Regulated servo supply] -- V+ and GND --> PCA
  PCA -- PWM 0-7 --> MOT[4 hip + 4 knee servos]
  PI -- H.264 RTP video :5004 --> VLC[Laptop VLC]
~~~

See docs/wiring.md, docs/wiring.svg, and docs/system-architecture.svg.

## Parts and wiring

Parts: Pi 3 Model A+, Raspberry Pi OS Lite (32-bit), microSD, stable 5 V Pi supply, PCA9685 at I2C 0x40, eight servos, separate regulated supply sized for the servos, CSI camera, frame, phone/laptop, and VLC.

| Pi physical pin | Signal | PCA9685 |
|---:|---|---|
| 1 | 3.3 V | VCC logic |
| 3 | GPIO2 / SDA1 | SDA |
| 5 | GPIO3 / SCL1 | SCL |
| 6 | Ground | GND |

Servo supply positive goes to PCA V+; negative goes to PCA GND. Pi ground, PCA ground, and servo supply ground must be common. Never connect servo V+ to Pi 3.3 V or 5 V. Use a supply voltage within the servo rating, sized for combined load/stall current.

| Channel | Servo | Channel | Servo |
|---:|---|---:|---|
| 0 | Front-right hip | 1 | Front-right knee |
| 2 | Front-left hip | 3 | Front-left knee |
| 4 | Back-right hip | 5 | Back-right knee |
| 6 | Back-left hip | 7 | Back-left knee |

Enable I2C in raspi-config and verify with sudo i2cdetect -y 1; the board should appear at 40. Connect the CSI ribbon following its orientation marks.

## Install the Pi software

1. Raspberry Pi Imager: choose Raspberry Pi OS Lite (32-bit); set hostname taha, username pipi, Wi-Fi, and enable SSH with password authentication. Write and verify.
2.  Connect from PowerShell, replacing these placeholders with the username and hostname set in Raspberry Pi Imager:
   ``powershell
   ssh YOUR_USERNAME@YOUR_HOSTNAME.local
   
3. Enable I2C: sudo raspi-config → Interface Options → I2C; finish and reboot.
4. Install packages:
   ~~~bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip i2c-tools ffmpeg
   sudo i2cdetect -y 1
   mkdir -p ~/quad
   python3 -m venv ~/quad/venv
   ~/quad/venv/bin/pip install adafruit-circuitpython-servokit Flask
   ~~~
5. Copy phone_control.py and the templates folder into ~/quad, keeping index.html inside ~/quad/templates. Run:
   ~~~bash
   ~/quad/venv/bin/python ~/quad/phone_control.py
   ~~~
6. Find the Pi address with hostname -I. Open http://PI_IP:5000 from a phone/laptop on the same Wi-Fi.

Keep the robot supported and legs clear during first movement checks.

## Motion reference

The channel order is FR hip/knee, FL hip/knee, BR hip/knee, BL hip/knee. Stand is [65,110,115,90,115,90,65,90]; sit is [65,135,115,65,115,65,65,115]. Gait uses hip offsets 12 degrees back, 28 degrees forward, knee lift 20 degrees, four phases of 300 ms, a 15 ms update target, and 2-degree steps. Dance alternates the supplied A/B offset arrays, changing pose every 300 ms and style every 5 seconds. Wave uses front-right knee 0 degrees and hip 70 degrees, then alternates 65/80 degrees. Full reference values are in firmware-reference/README.md.

The Pi translation preserves angles and sequence patterns. Linux scheduling and I2C writes can make the timing differ from ESP32. Left/right use the supplied turning-style patterns; they do not provide true sideways strafing with only hip/knee joints.

## Camera to VLC

Copy camera/stream-to-laptop.sh to ~/quad/camera on the Pi. Start VLC on the laptop first: Media → Open Network Stream → rtp://@:5004. Then run on the Pi, replacing LAPTOP_IP with its Wi-Fi IPv4 address:
~~~bash
chmod +x ~/quad/camera/stream-to-laptop.sh
~/quad/camera/stream-to-laptop.sh LAPTOP_IP
~~~
Stop camera with Ctrl+C in its SSH window. Camera and movement use separate SSH windows.

## Stop, security, limitations

Press Stop/Stand, stop camera and controller windows with Ctrl+C, then switch off servo power before handling wiring. The web page has no login and uses plain HTTP: keep it on trusted Wi-Fi, do not expose port 5000 to the internet, and do not commit Wi-Fi passwords, SSH keys, tokens, or private IPs. The prototype has no hardware emergency stop, fall/obstacle sensing, encrypted control, or weather protection. Keep a human operator in control.

If the OS reports read-only filesystem or I/O errors, stop and inspect SD card and power before installing more software. Keep Pi and servo supplies separate with a shared ground.

## Files

- phone_control.py: Flask backend and PCA9685 motion program
- templates/index.html: mobile-friendly control website
- camera/stream-to-laptop.sh: H.264/RTP camera helper
- docs/: wiring instructions and diagrams
- firmware-reference/: ESP32-tested motion values

