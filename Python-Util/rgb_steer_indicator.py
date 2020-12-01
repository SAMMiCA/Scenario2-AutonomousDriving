import cv2
import numpy as np
import os
import imutils
from os.path import isfile, join
import math

pathIn_rgb= './rgb/'
pathOut_rgb = './rgb_with_steer/'
if not os.path.isdir(pathOut_rgb):
    os.mkdir(pathOut_rgb)

frame_array = []
files1 = [f for f in os.listdir(pathIn_rgb) if isfile(join(pathIn_rgb, f))]
#for sorting the file names properly
files1.sort(key = str.lower)
files1.sort()


pred_txt = './prediction.txt'
f = open(pred_txt)
gt_txt = './ground_truth.txt'
g = open(gt_txt)

for i in range(len(files1)):

    filename1 = pathIn_rgb+files1[i]
    img = cv2.imread(filename1)
    height = img.shape[0]
    width = img.shape[1]
    print(img.shape)
    ############################Angle 읽어오기##########################
    pred_line = f.readline()
    pred_angle = -1*float(pred_line[pred_line.index(' '):])

    gt_line = g.readline()
    gt_angle = -1*float(gt_line[gt_line.index(' '):])
    ############################핸들 그림 삽입###########################
    vpos = height-160  #핸들 위치
    hpos = 100

    handle_img = cv2.imread('car-steering-wheel.png')
    handle_img = imutils.rotate(handle_img,pred_angle)
    handle_gray = cv2.cvtColor(handle_img, cv2.COLOR_BGR2GRAY)
    handle_gray = 255-handle_gray
    handle_gray[handle_gray>254] = 0

    rows, cols, channels = handle_img.shape
    roi = img[vpos:rows+vpos, hpos:cols+hpos]
    ret, mask = cv2.threshold(handle_gray, 100, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    img_bg = cv2.bitwise_and(roi, roi, mask = mask_inv)
    handle_fg = cv2.bitwise_and(handle_img, handle_img, mask = mask)
    dist = cv2.add(img_bg, handle_fg)
    img[vpos:rows+vpos, hpos:cols+hpos] = dist
    ##############################Line 그리기############################
    line_length = 100

    pred_dest_y = round(height-line_length*math.cos(pred_angle*math.pi/180))
    pred_dest_x = round(width//2-line_length*math.sin(pred_angle*math.pi/180))
    cv2.line(img, (width//2, height),(pred_dest_x, pred_dest_y), (255,0,0), 5)

    gt_dest_y = round(height-line_length*math.cos(gt_angle*math.pi/180))
    gt_dest_x = round(width//2-line_length*math.sin(gt_angle*math.pi/180))
    cv2.line(img, (width//2, height),(gt_dest_x, gt_dest_y), (0,255,0), 5)
    ##############################텍스트 표시###############################
    label_string_gt = "Green: Ground Truth"
    label_string_pred = "Blue: Prediction"
    cv2.putText(img, label_string_gt, (0, 30), cv2.FONT_ITALIC, 1, (0, 255, 0),2)
    cv2.putText(img, label_string_pred, (0, 70), cv2.FONT_ITALIC, 1, (255, 0, 0),2)
    cv2.putText(img, "Error: %.4f(rad)" %(abs(gt_angle-pred_angle)*math.pi/180), (0, 110), cv2.FONT_ITALIC, 1, (0, 0, 255),2)




    cv2.imwrite(pathOut_rgb+str(files1[i])+'.png', img)

f.close()

