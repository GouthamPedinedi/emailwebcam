import glob
import os
import cv2
import time
from send_email import send_email
from threading import Thread

video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
index = 1


def clean():
	print("Clean folder function started.")
	images = glob.glob("images/*.png")
	for image in images:
		os.remove(image)
	print("Clean folder function ended.")


while True:
	status = 0
	check, frame = video.read()
	gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)
	cv2.imshow("Video", frame)
	
	if first_frame is None:
		first_frame = gray_frame_gau
	
	delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
	thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
	dilated_frame = cv2.dilate(thresh_frame, None, iterations=5)
	contours, check = cv2.findContours(dilated_frame, cv2.RETR_EXTERNAL,
	                                   cv2.CHAIN_APPROX_SIMPLE)
	
	for contour in contours:
		if cv2.contourArea(contour) < 10000:
			continue
		x, y, w, h = cv2.boundingRect(contour)
		rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
		if rectangle.any():
			status = 1
			cv2.imwrite(f"images/image{index}.png", frame)
			index += 1
			all_images = glob.glob("images/*.png")
			index = int(len(all_images) / 2)
			image_with_object = all_images[index]
	
	status_list.append(status)
	status_list = status_list[-2:]
	if status_list[0] == 1 and status_list[1] == 0:
		email_thread = Thread(target=send_email, args=(
			image_with_object, "testcasepython123@gmail.com"))
		email_thread.daemon = True
		
		email_thread.start()
	
	print(status_list)
	
	cv2.imshow("Video", frame)
	key = cv2.waitKey(1)
	
	if key == ord("q"):
		break

video.release()
