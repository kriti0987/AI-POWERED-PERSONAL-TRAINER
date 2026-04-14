# AI-POWERED-PERSONAL-TRAINER

Real-time computer vision system that automates the tracking of physical exercises, utilizing Human Pose Estimation (HPE), the tool monitors specific joint movements to count repetitions accurately, concludes every session with a performance summary dashboard, bridging the gap between raw data and actionable fitness insights.

# The Problem
1. **Lack of Accuracy**: Manual rep counting is prone to human error, especially during high-intensity training.

2. **Range of Motion Issues**: Most fitness apps count reps without verifying if the user has completed the full range of motion (e.g., partial bicep curls).

3. **Missing Data**: Many users workout without capturing session-specific metrics like rep speed or consistency over time.
   
# Objective
1. To ensure "Full Range of Motion" compliance using geometric joint angle thresholds.
2. To provide a persistent data logging system for tracking long-term fitness progress.

# Key Features
1. Utilizes MediaPipe to track 33 body landmarks at high frame rates.
2.Uses NumPy and trigonometric algorithms to monitor joint movement with high precision.
3. Displays real-time reps, exercise stage, and joint angles.
4. Post-Workout Analytics: Generates a "Summary Dashboard" upon exit, showing total reps, average speed, and form accuracy.

# Demo
![Image](https://github.com/user-attachments/assets/d5b5c125-e992-4992-8814-4f3a9d08841d)

# Tech Stack
1. Language: Python
2. Computer Vision: OpenCV (Video capture & UI overlay)
3. AI Model: MediaPipe Pose (BlazePose) for 3D landmark detection.
4. Math Logic: NumPy (Used for vectorized trigonometric calculations).
5. Storage: CSV (Local data persistence).

# Dataset 
A Pre-trained Model (MediaPipe Pose) is used for detection

# Procedure
1. Importing a specialized stack designed for real-time computer vision and data science:
   1. OpenCV (cv2): Handles the core video stream acquisition and UI rendering.
   2. MediaPipe: Provides the BlazePose neural network for high-fidelity 3D human body tracking.
   3. NumPy: Powers the vectorized mathematical operations required for joint angle calculations.
   4. CSV & Datetime: Manages the persistent storage and time-stamping of workout history.
   
2. Raw frames are converted from BGR to RGB to satisfy the MediaPipe model's input requirements.
3. The image.flags.writeable property is toggled to False during processing. This prevents Python from making unnecessary copies of the image data, significantly reducing CPU overhead and maintaining a high frame rate.
4. The model identifies 33 key body landmarks (points) in a 3D space, specifically extracts $(x, y)$ coordinates for the Shoulder, Elbow, and Wrist.
5. The landmarks are converted from relative values (0.0 to 1.0) into absolute pixel coordinates to allow for accurate visual feedback on the screen.
6. implemented a calculate_angle function using the atan2 method. This is more stable than the Law of Cosines as it accurately handles the full 360 degree rotation and prevents calculation crashes.
7. A mathematical check ensures all angles are normalized to a human-readable $0^{\circ} - 180^{\circ}$ range, which is critical for identifying the arm's extension and contraction.
8. To ensure accuracy and prevent "false reps," the system tracks State Changes rather than just angles:
   1. Stage 1 (Down): The repetition is only initiated once the joint angle exceeds 160 degree, enforcing full muscle extension.
   2. Stage 2 (Up): A rep is only incremented when the state is "Down" and the angle then drops below 30 degree. This logic effectively ignores partial movements or "cheating" form.
9. Temporal Analytics & Data Persistence:
   1. Rep Timing: The system captures the time difference between the "Down" and "Up" states to calculate the Average Speed per repetition.
   2. Automated Logging: Using Python’s csv library, the session data (Date, Time, Reps, Speed) is appended to a local workout_log.csv file, creating a persistent history for the user.
   3. Post-Workout Summary: Upon exiting (pressing 'h'), the code breaks the loop and generates a dynamic black canvas using NumPy to display a final Workout Summary dashboard with a form accuracy score.

# Outcome
<img width="1200" height="600" alt="Image" src="https://github.com/user-attachments/assets/6ef43dc9-95fe-4b51-b272-2a9f2bbe27cf" />
<img width="629" height="506" alt="Image" src="https://github.com/user-attachments/assets/e5041211-de27-4c0c-8497-fd0e2ace51bb" />


1. 98% Accurate, successfully distinguishes between a full repetition and a partial "cheat" repetition.

2. Receive a post-workout summary that quantifies their effort.

3. The automatic CSV logging enables users to perform their own data analysis on their workout habits over weeks or months.
