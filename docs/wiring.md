# Wiring and diagrams

~~~mermaid
flowchart LR
  PHONE[Phone/laptop browser] -- HTTP port 5000 over Wi-Fi --> PI[Raspberry Pi 3 A+]
  CAM[CSI camera] -- ribbon --> PI
  PI -- I2C bus 1: SDA/SCL --> PCA[PCA9685 at 0x40]
  PI -- physical pin 1: 3.3 V --> PCA
  PI_GND[Pi physical pin 6 GND] --- PCA_GND[PCA GND]
  SUPPLY[Servo supply, voltage per servo rating] -- positive to V+ / negative GND --> PCA
  PCA -- PWM channels 0-7 --> SERVOS[4 hip + 4 knee servos]
  PI -- RTP video port 5004 --> VLC[Laptop VLC]
~~~

## Pi physical pin mapping

| Physical pin | Signal | PCA9685 |
|---:|---|---|
| 1 | 3.3 V | VCC logic |
| 3 | GPIO2 / SDA1 | SDA |
| 5 | GPIO3 / SCL1 | SCL |
| 6 | Ground | GND |

Enable I2C in raspi-config. Confirm address 0x40 with sudo i2cdetect -y 1.

## Power

Servo supply positive to PCA9685 V+. Servo supply negative to PCA GND. Join Pi ground, PCA ground, and servo supply ground. PCA VCC receives Pi 3.3 V logic. Never feed servo V+ to the Pi's 3.3 V or 5 V pins. Choose the supply voltage for the specific servo and size it for all servos under load. Verify polarity before powering on.

## Servo channels

| Channel | Leg/joint | Channel | Leg/joint |
|---:|---|---:|---|
| 0 | Front-right hip | 1 | Front-right knee |
| 2 | Front-left hip | 3 | Front-left knee |
| 4 | Back-right hip | 5 | Back-right knee |
| 6 | Back-left hip | 7 | Back-left knee |

## Camera and network

Connect the CSI ribbon to the Pi and camera following orientation marks; do not force the latch. The browser sends control requests to the Pi on port 5000. The Pi camera helper sends H.264/RTP video to VLC on the laptop at port 5004.

~~~text
Browser --Wi-Fi--> Pi Flask controller:5000
CSI camera --> rpicam-vid --> FFmpeg --> RTP over Wi-Fi --> VLC:5004
Pi I2C --> PCA9685 --> PWM channels 0-7 --> leg servos
Separate servo supply --> PCA V+; common ground with Pi
~~~

