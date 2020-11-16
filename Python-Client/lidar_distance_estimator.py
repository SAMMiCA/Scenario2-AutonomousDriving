#====================================Ver 201116======================================#
# Initial Version
# ply 파일들이 있는 디렉토리에 넣고 쓰시면 됩니다.
#====================================================================================#
import os
from os.path import isfile, join
import numpy as np
#====================================================================================#
# image_loader
# 현 디렉토리의 ply 파일을 불러와서 numpy array로 변환
#====================================================================================#
def image_loader(file_name):
    raw_data = open(file_name, 'r')
    sliced_data = raw_data.readlines()[8:]
    point_cloud = np.loadtxt(sliced_data)
    print(point_cloud[0,0])
    return point_cloud

#====================================================================================#
# point_compressor(ply data)
# return: numpy array - shape:(n,2)
# LiDAR로부터 raw_data를 받아와, z축 좌표가 bound 내에 존재하는 포인트들의 x,y 좌표 반환
#====================================================================================#
def point_compressor(ply_data):
    lower_bound = -2.1
    upper_bound = 0

    points = ply_data.reshape([-1,4])
    
    efficient_points = points[points[:,2]>lower_bound]
    efficient_points = efficient_points[efficient_points[:,2]<upper_bound]

    compressed_points = np.array(efficient_points[:, :2])
    return compressed_points

#====================================================================================#
# obstacle_detector(compressed_points)
# return: integer
# compressed_points에서 LiDAR 앞의 point 검출, 평균 15개의 distance 계산해 반환
# 15m내에 point 없으면 obstacle이 없다 판단, 0 반환
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
# main
# 디렉토리 내 모든 ply파일에 대해 실행
#====================================================================================#

def main():
    files = [f for f in os.listdir('.') if isfile(join('.', f))]
    files.sort(key = str.lower)
    files = files[0:len(files)-1]
    for i in range(len(files)):
        filename = files[i]
        print(str(filename) +' '+ str(obstacle_detector(point_compressor(image_loader(str(filename))))))



main()
