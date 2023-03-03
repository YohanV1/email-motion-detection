import cv2
import time
import glob
from mailer import send_email
import os
from clean_directory import clean_directory
from threading import Thread


video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
c = 0

while True:

    status = 0

    # Reading original frame
    check, frame = video.read()

    # Converting to grey scale
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Adding a blur to reduce image complexity
    grey_frame_gaus = cv2.GaussianBlur(grey_frame, (21, 21), 0)

    # Assigning the first frame for comparisons
    if first_frame is None:
        first_frame = grey_frame_gaus

    # Getting the difference between current and first frame
    delta_frame = cv2.absdiff(first_frame, grey_frame_gaus)

    # Threshold for pixels above 60 to turn completely white
    thresh_frame = cv2.threshold(delta_frame, 80, 255, cv2.THRESH_BINARY)[1]

    # Diluting frame to remove noise
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Identifying the areas with a pixel difference between images
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

    # Checking for false positives in image differences
    for contour in contours:
        if cv2.contourArea(contour) < 3000:
            continue
        # Creating a rectangle around a positive difference between images
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x,y ), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{c}.png", frame)
            c += 1
            all_images = glob.glob("images/*.png")
            img_to_email = all_images[len(all_images) // 2]

    # print(img_to_email)
    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        images_to_delete = glob.glob("images/*.png")
        images_to_delete.sort()
        for image in images_to_delete:
            if image != img_to_email:
                os.remove(image)
        email_thread = Thread(target=send_email, args=(img_to_email, ))
        email_thread.daemon = True
        email_thread.start()

    # Displaying the processed frame
    cv2.imshow("My video", frame)

    # Waiting for keyboard input
    key = cv2.waitKey(1)

    # If keyboard input is 'q'
    if key == ord("q"):
        break

try:
    video.release(0)
except SystemError:
    print("Video Terminated")

clean_directory()