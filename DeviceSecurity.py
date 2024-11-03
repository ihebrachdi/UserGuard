import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading
import os
from deepface import DeepFace


# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)




def capture_and_save_image(cap, save_path, image_directory):
    ret, frame = cap.read()

    if ret:
       
        _ = 1
        save_path = image_directory + save_path
        while os.path.exists(save_path):
            _ +=1
            # os.remove(save_path)
            save_path = image_directory + str(_) + ".jpg"

        cv2.imwrite(save_path, frame)
        print("Image captured and saved successfully.")
   


reference_images = []

for filename in os.listdir("user/"):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join("user/", filename)
        reference_images.append(cv2.imread(image_path))

face_match = False

def check_face(frame):
    global face_match
    try:
        for reference_img in reference_images:
            if DeepFace.verify(frame, reference_img.copy())['verified']:
                face_match = True
                return  
        
        face_match = False
    except ValueError:
        face_match = False




enable = False
threat_detect_count = 0
def start_security():
    global threat_detect_count 
    global enable
    threat_detect_count = 0
    enable = not enable
    button1.config(text="Stop"if enable else "Start")
    

def capture():
    capture_and_save_image(cap , "ref0.jpg","user/")


font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 2
font_thickness = 3

threshold = 150
not_match_count = 0
counter = 0
def update_video():
    global threat_detect_count
    global enable
    global threshold
    global not_match_count
    global counter
    global font
    global font_scale
    global font_thickness
    
    #Green Color For authorized user
    color = (0, 255, 0)
    ret, frame = cap.read()

    if ret:
        if enable :
            
            if counter % 5 == 0:
                try:
                    threading.Thread(target=check_face, args=(frame.copy(),)).start()
                except ValueError:
                    pass
            counter += 1
            if face_match:
                
                not_match_count = 0
                text = "USER AUTHORIZED"
            else:
                
                if not_match_count > threshold:
                    color = (0, 0, 255)
                    text = "OUTSIDER"

                    if threat_detect_count == 0:
                        capture_and_save_image(cap , "out.jpg","threat/")
                    threat_detect_count +=1
                    if os.name == 'nt':  # Windows    
                        print("unothorize access")
                        os.system('rundll32.exe user32.dll,LockWorkStation')
                    else:
                        print("TODO: Unsupported operating system ")

                else:
                    not_match_count +=1
                    text = ""
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = frame.shape[0] - 20  
            cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, font_thickness)
            

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(Image.fromarray(frame))
        video_label.config(image=photo)
        video_label.image = photo
        video_label.after(10, update_video)




# Create the main window
window = tk.Tk()
window.title("Device Security")

window.geometry("960x480")

video_label = tk.Label(window)
video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
button_frame = tk.Frame(window)
button_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")
button1 = tk.Button(button_frame, text="Start", command=start_security, width=25 , height=4)  
button2 = tk.Button(button_frame, text="Save User", command=capture, width=25, height=4)  
button1.grid(row=0, column=0, pady=10)
button2.grid(row=1, column=0, pady=10)

video_label.grid(row=0, column=1, padx=10, pady=10, sticky="n")

window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)
button_frame.grid_rowconfigure(0, weight=1)

window.grid_rowconfigure(2, minsize=video_label.winfo_height())

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(0, weight=1)



update_video()

window.mainloop()
cap.release()
