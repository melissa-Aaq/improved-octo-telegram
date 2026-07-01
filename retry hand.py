import cv2
import mediapipe as mp
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Function to set system volume (Windows only)
def set_system_volume(volume_level):
    devices = AudioUtilities.GetSpeakers()
    # FIX: We bypass the .Activate bug completely by using pycaw's modern shortcut property
    volume = devices.EndpointVolume.QueryInterface(IAudioEndpointVolume)
    volume.SetMasterVolumeLevelScalar(volume_level / 100, None)

# Function to detect hand gestures and control pointer
def detect_hand_gesture(frame, volume_level):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    screen_width, screen_height = pyautogui.size()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            thumb_x = int(thumb_tip.x * frame.shape[1])
            thumb_y = int(thumb_tip.y * frame.shape[0])
            index_x = int(index_tip.x * frame.shape[1])
            index_y = int(index_tip.y * frame.shape[0])
            
            distance = ((thumb_x - index_x)**2 + (thumb_y - index_y)**2)**0.5
            
            pointer_x = int(index_tip.x * screen_width)
            pointer_y = int(index_tip.y * screen_height)
            pyautogui.moveTo(pointer_x, pointer_y)
            
            pinch_threshold = 50  
            swipe_threshold = 30  
            
            if distance < pinch_threshold:
                if thumb_x > index_x:
                    volume_level += 1
                else:
                    volume_level -= 1
                
                volume_level = max(0, min(volume_level, 100))
                set_system_volume(volume_level)
                print("Volume adjusted:", volume_level)
                pyautogui.click()
                print("Click detected.")
            
            elif thumb_y > index_y:
                pyautogui.scroll(-30)  
                print("Scroll down detected.")
                
            elif thumb_y < index_y:
                pyautogui.scroll(30)  
                print("Scroll up detected.")
                
            elif (thumb_x - index_x) > swipe_threshold and abs(thumb_y - index_y) < swipe_threshold:
                pyautogui.press('left')  
                print("Swipe left detected.")
            
            elif (index_x - thumb_x) > swipe_threshold and abs(thumb_y - index_y) < swipe_threshold:
                pyautogui.press('right')  
                print("Swipe right detected.")
    
    return frame, volume_level

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    volume_level = 50  
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame, volume_level = detect_hand_gesture(frame, volume_level)
        cv2.imshow('IncreHand', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


