# ESP32 motion reference carried to the Pi

The project owner supplied and tested these reference movements on an ESP32 DevKit. phone_control.py translates the values and patterns.

- Channel order: FR hip/knee, FL hip/knee, BR hip/knee, BL hip/knee.
- Stand: 65, 110, 115, 90, 115, 90, 65, 90.
- Sit: 65, 135, 115, 65, 115, 65, 65, 115.
- Pulse range: 600-2400 microseconds; PWM frequency: 50 Hz.
- Gait: 12-degree back hip offset; 28-degree forward offset; 20-degree knee lift; diagonal pairs in four 300 ms phases.
- Smoothing: 2 degrees per update; 15 ms update target.
- Wave: front-right knee 0 degrees; hip starts at 70 degrees then alternates 65/80 degrees after a 500 ms initial interval and 400 ms thereafter.
- Dance: supplied Dance A/B four-by-eight offsets; change pose every 300 ms and dance style every 5 seconds.

Linux scheduling and I2C writes can make the Pi timing differ from ESP32.

