The project is a subtle amalgamation of robotics, AI and computer vision as it seeks to examine the position of every coin on a carrom board and consequently, play the 
most optimal shot.
The repository contains the following elements:
i) **carrom_serialcomm**: Handles serial communication between the bot's hardware, i.e. Arduino and software components.The bot commands the Arduino to position the striker and 
                      execute the calculated shot by driving the stepper and servo motors accordingly.
ii)**image_processing.py**: The Python code contains functions from the openCV library to process images of the carrom board to identify coin positions. 
iii)**shot_calculations-AI.py**: Implements algorithms to determine the most effective shots based on the current board state. Based on the identified positions of the coins, 
                              the AI module calculates the optimal shot. It considers various shot types(such as direct, cut and side), angles, and required power to maximize 
                              the chances of success.
iv)**carrom_bot.py**: Blend of ii) and iii)

**Brief Working:**
-A camera captures an image of the carrom board.
-The bot processes the image using OpenCV to detect the striker, coins, and board boundaries.
-It classifies coins based on color(Red, Black and White) and position.
-The bot analyzes the positions of coins and pockets.
-Using predefined shot types (direct shots, cut shots and side shots), it determines the optimal shot based on angles and power required.
-The algorithm selects the best move to maximize scoring chances.
-The calculated shot parameters (position, angle, power) are sent to an Arduino-controlled mechanism via serial communication.
-The bot positions the striker using stepper motors. The stepper motor moves the striker left or right along the striker line to align with the best calculated position.
-The servo motor rotates the striker mechanism to align it with the computed angle before striking.
-The striker moves to the computed position, aligns to the calculated angle, and shoots with precise power.
-The board is re-scanned, and the process repeats until the game concludes.
