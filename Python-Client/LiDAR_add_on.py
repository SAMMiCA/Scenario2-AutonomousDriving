#====================================Ver 201113======================================#
# Initial Version
#====================================================================================#
import carla

from carla import ColorConverter as cc

import argparse
import collections
import datetime
import logging
import math
import random
import re
import weakref
import cv2
import shutil
import time
import numpy as np
from os.path import isfile, join

#====================================================================================#
# point_compressor(raw_data, lower_bound, upper_bound)
# return: numpy array - shape:(n,2)
# LiDAR로부터 raw_data를 받아와, z축 좌표가 bound 내에 존재하는 포인트들의 x,y 좌표 반환
#====================================================================================#
def point_compressor(raw_data):
    lower_bound = -2.1
    upper_bound = 0
    points = np.frombuffer(raw_data, dtype=np.dtype('f4'))
    points = np.reshape(points, (int(points.shape[0] / 4), 4))
    
    efficient_points = points[points[:,2]>lower_bound]
    efficient_points = efficient_points[efficient_points[:,2]<upper_bound]

    compressed_points = np.array(efficient_points[:, :2])
    return compressed_points

#====================================================================================#
# obstacle_detector(compressed_points)
# return: integer
# compressed_points에서 LiDAR 앞의 point 검출, 평균 distance 계산해 반환
# 15개의 points가 15m내에 없으면 obstacle이 없다 판단, 0 반환
#====================================================================================#
def obstacle_detector(compressed_points):
    points_ahead = compressed_points[compressed_points[:,1]< 1.5]
    points_ahead = points_ahead[points_ahead[:,1]> -1.5]
    points_ahead = points_ahead[points_ahead[:,0]>0]
    points_idx = points_ahead[:,0].argsort(axis=0)
    near_points_ahead = points_ahead[points_idx,:].reshape(-1,2)[:15,:] # Choose 15 nearest points
    if near_points_ahead.shape[0]>0:
        mean_distance = near_points_ahead.mean(axis=0)
        if mean_distance[0] > 15:
            return 0
        else:
            return mean_distance[0]
    else:
        return 0

#====================================================================================#
# obstacle_indicator(compressed_points)
# return: Integer or False >>> HUD에 띄울 수도??
# obstacle_detector에서 obstacle의 유무, distance를 받아 출력
#====================================================================================#
def obstacle_indicator(distance):
    if distance == 0:
        return -1
    elif distance < 15:
        return distance
    else:
        return -1

#====================================================================================#
# LiDAR_distance_calculator(raw_data)
# 실행
#====================================================================================#
def calculate_distance_LiDAR(raw_data):
    distance = obstacle_detector(point_compressor(raw_data))
    return obstacle_indicator(distance)

#====================================================================================#
# LiDAR_safety_check(raw_data)
# return: string (Left, Right, Stop)
# obstacle이 감지된 경우 피해야 할 방향 반환
#====================================================================================#
def LiDAR_safety_check(raw_data):
    compressed_points = point_compressor(raw_data)
    #Check Left
    left_result = check_left(compressed_points)
    #Check Right
    right_result = check_right(compressed_points)

    if left_result is 0 and right_result is 0:
        return 0
    elif left_result > right_result:
        return 1
    else:
        return 2

def check_left(compressed_points):
    left_points_ahead = compressed_points[compressed_points[:,1]< -1.5]
    left_points_ahead = left_points_ahead[left_points_ahead[:,1]> -6.5]
    left_points_ahead = left_points_ahead[left_points_ahead[:,0]>-1.5]
    points_idx = left_points_ahead[:,0].argsort(axis=0)
    left_near_points_ahead = left_points_ahead[points_idx,:].reshape(-1,2)[:1,:] # Choose the nearest points
    if left_near_points_ahead.shape[0] > 0:
        left_mean_distance = left_near_points_ahead.mean(axis=0)
        if left_mean_distance[0] > 40:
            return left_mean_distance[0]
        else:
            return 0
    else:
        return 20

def check_right(compressed_points):
    right_points_ahead = compressed_points[compressed_points[:,1]< 6.5]
    right_points_ahead = right_points_ahead[right_points_ahead[:,1]> 1.5]
    right_points_ahead = right_points_ahead[right_points_ahead[:,0]>-1.5]
    points_idx = right_points_ahead[:,0].argsort(axis=0)
    right_near_points_ahead = right_points_ahead[points_idx,:].reshape(-1,2)[:1,:] # Choose the nearest points
    if right_near_points_ahead.shape[0] > 0:
        right_mean_distance = right_near_points_ahead.mean(axis=0)
        if right_mean_distance[0] > 40:
            return right_mean_distance[0]
        else:
            return 0
    else:
        return 20


