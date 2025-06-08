# Carrom‑Bot 🤖🎯

An autonomous carrom‑playing robot that uses computer vision and AI to analyze the board state, calculate the optimal shot, and then drive stepper/servo motors (via an Arduino) to execute the shot.

---

## 🔍 Features

- **Real‑time coin detection** using OpenCV  
- **AI‑driven shot planning** (direct, cut, side shots)  
- **Serial communication** with Arduino for precise motor control  
- **Closed‑loop**: image → plan → shoot → re‑scan → repeat  

---

🎯 How It Works
Capture

Grab a frame from the camera.

Pre‑process (blur, threshold) and detect board corners.

Detect Coins

Use color filtering and Hough/Circle detection to locate striker & coins.

Classify coin colors (white, black, red).

Plan Shot

Given coin and pocket positions, compute angles & power for direct/cut/side shots.

Score and select the shot with highest success probability.

Actuate

Send position/angle/power commands via serial to Arduino.

Stepper aligns striker horizontally; servo sets angle; spring/solenoid strikes.

Repeat

After the strike, re‑scan and plan the next move until the game ends.
