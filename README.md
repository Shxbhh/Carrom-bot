# Carrom‑Bot 🤖🎯

An autonomous carrom‑playing robot that sees the board, computes the best shot, and drives motors to strike.

---

## 🔍 Features

- **Real‑time coin & striker detection** via OpenCV  
- **AI‑driven shot planning** (direct, cut & side‑shots)  
- **Automated motor control** over serial (Arduino + stepper/servo)  
- **Closed‑loop operation**: sense → plan → shoot → re‑scan → repeat  
- **Configurable parameters** for camera calibration, shot scoring and motor tuning  

---

## 🎯 How It Works

1. **Board Capture & Pre‑processing**  
   - Acquire frame from webcam or USB camera.  
   - Undistort & crop to board region using corner detection.  

2. **Coin & Striker Detection**  
   - Convert to HSV and threshold for white, black & red coins.  
   - Use Hough‑Circle (or contour) detection to find coin centers.  
   - Identify striker by unique size or color marker.  

3. **Shot Calculation**  
   - For each target coin, simulate candidate shots (direct, cut, side).  
   - Compute geometry: incidence/reflection angles, collision points.  
   - Estimate required force (power) based on distance & angle.  
   - Score all shots by success probability and pick the best.  

4. **Motor Actuation**  
   - Send angle & power commands over serial to the Arduino.  
   - Arduino drives the horizontal stepper (striker position).  
   - Servo sets the strike angle.  
   - Trigger solenoid or spring mechanism to execute the shot.  

5. **Feedback Loop**  
   - After striking, pause briefly then re‑capture the board.  
   - Update coin positions and repeat until the game ends or no legal shots remain.  


