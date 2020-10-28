import cv2
import numpy as np
import os
from os.path import isfile, join
pathIn_rgb= './rgb/'
pathIn_seg= './seg/'
pathOut_rgb = 'video_rgb.avi'
pathOut_seg = 'video_seg.avi'
fps = 30
frame_array = []
files1 = [f for f in os.listdir(pathIn_rgb) if isfile(join(pathIn_rgb, f))]
files2 = [f for f in os.listdir(pathIn_seg) if isfile(join(pathIn_seg, f))]
#for sorting the file names properly
files1.sort(key = str.lower)
files1.sort()
files2.sort(key = str.lower)
files2.sort()

frame_array_rgb = []
frame_array_seg = []


for i in range(len(files1)):
    filename1 = pathIn_rgb+files1[i]
    img = cv2.imread(filename1)
    frame_array_rgb.append(img)
    height, width, layers = img.shape
    size = (width,height)

for i in range(len(files1)):
    filename2 = pathIn_seg+files2[i]
    img = cv2.imread(filename2)
    frame_array_seg.append(img)
    height, width, layers = img.shape
    size = (width,height)

out_rgb = cv2.VideoWriter(pathOut_rgb,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
for i in range(len(frame_array_rgb)):
    # writing to a image array
    out_rgb.write(frame_array_rgb[i])
out_rgb.release()

out_seg = cv2.VideoWriter(pathOut_seg,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
for i in range(len(frame_array_seg)):
    # writing to a image array
    out_seg.write(frame_array_seg[i])
out_seg.release()
