import cv2
import mediapipe as mp
import numpy as np
import csv
from datetime import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360-angle
    return angle

cap = cv2.VideoCapture(0)

# NEW TRACKING VARIABLES 
counter = 0
stage = None
start_time = time.time()
rep_times = [] # To calculate average speed
last_rep_time = time.time()
last_count_time = time.time()
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = results.pose_landmarks.landmark
            # 1. Get visibility score for the elbow
            elbow_visibility = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility

            # 2. ONLY proceed if the camera is confident it sees the joint
            if elbow_visibility > 0.7:
                shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            
           
                angle = calculate_angle(shoulder, elbow, wrist)
           
            
                cv2.putText(image, str(int(angle)), 
                        tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                #Repetition Logic 
                if angle > 160:
                    stage = "Down"
            
                if angle < 30 and stage == 'Down':
                    current_time = time.time()
                    if current_time - last_count_time > 1.5: # Only count if 1.5s have passed
                     stage = "Up"
                     counter += 1
                    
                    # Calculate speed for stats
                    rep_duration = current_time - last_count_time
                    rep_times.append(rep_duration)
                        
                    last_count_time = current_time
            else:
                cv2.putText(image, "LOW VISIBILITY", (10, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        except Exception as e:
            pass

        # Rendering
        cv2.rectangle(image, (0,0), (300, 73), (245, 117, 16), -1)
        cv2.putText(image, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(image, 'STAGE', (120,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(stage), (120,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
        cv2.imshow('Mediapipe Feed', image)
        if cv2.waitKey(10) & 0xFF == ord('h'):
            break

cap.release()
cv2.destroyAllWindows()

# STEP 1: CALCULATE STATS 
avg_speed = round(np.mean(rep_times), 2) if rep_times else 0
# Form score: Let's assume a "Perfect" rep is between 3 and 5 seconds. 
# Too fast or too slow reduces the score.
form_score = 100 if (3 <= avg_speed <= 5) else 70 


# Updated STEP 2: SAVE TO CSV (Add a manual field or prompt for actual reps)
actual_reps = int(input("How many reps did you actually do? ")) # Manual entry for ground truth

with open('workout_log.csv', mode='a', newline='') as f:
    writer = csv.writer(f)
    # Date, Predicted Reps, Actual Reps, Avg Speed
    writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), counter, actual_reps, avg_speed])

# STEP 3: SHOW SUMMARY SCREEN 
summary_img = np.zeros((480, 640, 3), dtype=np.uint8) # Black screen
cv2.putText(summary_img, 'WORKOUT SUMMARY', (150, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(summary_img, f'Total Reps: {counter}', (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(summary_img, f'Avg Speed: {avg_speed}s / rep', (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(summary_img, f'Form Score: {form_score}%', (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(summary_img, 'Press any key to close', (180, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

cv2.imshow('Workout Summary', summary_img)

# Load the data
df = pd.read_csv('workout_log.csv', names=['Timestamp', 'AI_Reps', 'Actual_Reps', 'Avg_Speed'])

# 1. Calculate Accuracy Percentage
# This calculates accuracy and prevents it from showing negative values or errors
df['Accuracy'] = (1 - abs(df['AI_Reps'] - df['Actual_Reps']) / df['Actual_Reps']) * 100
df['Accuracy'] = df['Accuracy'].clip(lower=0)

# Create the Visualization
plt.figure(figsize=(12, 6))

# Plot 1: AI vs Actual Reps
plt.subplot(1, 2, 1)
x = np.arange(len(df))
plt.bar(x - 0.2, df['Actual_Reps'], 0.4, label='Actual (Ground Truth)', color='#2ecc71')
plt.bar(x + 0.2, df['AI_Reps'], 0.4, label='AI Prediction', color='#e74c3c')
plt.xlabel('Session #')
plt.ylabel('Rep Count')
plt.title('AI Prediction vs. Reality')
plt.legend()

# Plot 2: Accuracy Trend
plt.subplot(1, 2, 2)
plt.plot(df['Accuracy'], marker='o', linestyle='-', color='#3498db', linewidth=2)
plt.axhline(y=100, color='r', linestyle='--') # 100% Accuracy line
plt.ylim(0, 110)
plt.xlabel('Session #')
plt.ylabel('Accuracy %')
plt.title('System Accuracy Over Time')

plt.tight_layout()
plt.show()


cv2.waitKey(0) # Wait for a key press to close
cv2.destroyAllWindows()