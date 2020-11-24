#====================================Ver 201113======================================#
# Initial Version
#====================================Ver 201121======================================#
# 코드 정리
#====================================Ver 201124======================================#
# 실선 차선 침범 방지 기능 추가
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
        return False
    elif distance < 15:
        return distance
    else:
        return False

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
def LiDAR_safety_check(raw_data, waypoint):
    compressed_points = point_compressor(raw_data)
    #Check Left
    left_result = check_left(compressed_points)
    #Check Right
    right_result = check_right(compressed_points)
    #Check Lane
    left_lane_result = check_lane(waypoint, 'left')
    right_lane_result = check_lane(waypoint, 'right')
    
    if left_result is 0 and right_result is 0:
        return 0
    elif left_result > 0 and left_lane_result is True: #go to left
        return 1
    elif right_result > 0 and right_lane_result is True: #go to right
        return 2
    else:
        return 0
#====================================================================================#
# check_left(compressed_points)
# return: Integer (obstacle과의 longitudinal 거리 표시)
# obstacle이 20m 보다 가까우면 0 반환
#====================================================================================#
def check_left(compressed_points): #20 이상일시 safe라 판단
    left_points_ahead = compressed_points[compressed_points[:,1]< -2]
    left_points_ahead = left_points_ahead[left_points_ahead[:,1]> -4]
    left_points_ahead = left_points_ahead[left_points_ahead[:,0]>-2.5]
    points_idx = left_points_ahead[:,0].argsort(axis=0)
    left_near_points_ahead = left_points_ahead[points_idx,:].reshape(-1,2)[:1,:] # Choose the nearest points
    if left_near_points_ahead.shape[0] > 0:
        left_mean_distance = left_near_points_ahead.mean(axis=0)
        if left_mean_distance[0] > 20:
            return left_mean_distance[0]
        else:
            return 0
    else:
        return 20
#====================================================================================#
# check_right(compressed_points)
# return: Integer (obstacle과의 longitudinal 거리 표시)
# obstacle이 20m 보다 가까우면 0 반환
#====================================================================================#
def check_right(compressed_points): #20 이상일시 safe라 판단
    right_points_ahead = compressed_points[compressed_points[:,1]< 4]
    right_points_ahead = right_points_ahead[right_points_ahead[:,1]> 2]
    right_points_ahead = right_points_ahead[right_points_ahead[:,0]>-2.5]
    points_idx = right_points_ahead[:,0].argsort(axis=0)
    right_near_points_ahead = right_points_ahead[points_idx,:].reshape(-1,2)[:1,:] # Choose the nearest points
    if right_near_points_ahead.shape[0] > 0:
        right_mean_distance = right_near_points_ahead.mean(axis=0)
        if right_mean_distance[0] > 20:
            return right_mean_distance[0]
        else:
            return 0
    else:
        return 20

#====================================================================================#
# check_lane(waypoint, direction)
# 실선, 점선, 중앙선 등 감지하여 차선 변경 가능 여부 반환
# waypoint: carla상에서 차선 정보가 waypoint에 담김
# direction: 체크하고 싶은 방향
# return: Bool (가도 되면 True 안되면 False)
#====================================================================================#
def check_lane(waypoint, direction):

    if direction == 'left':
        if str(waypoint.left_lane_marking.lane_change) == 'Both':
            return True
        else:
            return False
    else:
        if str(waypoint.right_lane_marking.lane_change) == 'Both':
            return True
        else:
            return False
