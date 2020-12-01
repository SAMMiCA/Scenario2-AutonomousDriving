# AI-28-Python-Client

## 1. 요약

CARLA dataset 취득 시 필요한 util 파일들입니다.


**VidMaker.py:** rgb, seg 디렉토리에 있는 사진 파일들을 비디오로 만들어줍니다.

**Synchronizer.py** 가끔 rgb 파일이 프레임을 건너 뛸 때, 남는 seg 파일을 지워줍니다.

**lidar_distance_calculator** ply 파일들이 있는 디렉토리에 넣고 사용하시면, 전방 obstacle과의 distance, 상대속도를 계산합니다.

**rgb_steer_indicator** rgb 디렉토리의 상위 디렉토리에 넣고 사용하시면, 핸들과 조향각 등을 visualize해줍니다.


## 2. VidMaker.py
rgb 와 seg에 있는 사진 파일을 따로 비디오로 묶어줍니다.

현재 기본 fps는 30입니다.


## 3. lidar_distance_calculator.py
전방 obstacle 과의 거리와 상대속도를 계산합니다. ply파일들이 있는 디렉토리에 넣고 사용해주세요.

기본적으로 설정된 lidar fps(?)는 10입니다.

lidar fps 변경시에는 속도 계산 함수의 변경이 필요합니다.

## 4. synchronizer.py
rgb의 개수와 seg의 개수가 일치하지 않는 경우 사용합니다.

manual_control에 기본적으로 구현해 놓아서 사용하실 일이 거의 없습니다.

## 5. rgb_steer_indicator.py
rgb 디렉토리의 상위 디렉토리에 넣고 사용하시면 됩니다.

rgb data에 해당 프레임의 steering angle의 prediction, ground truth값을 직선으로 visualize 해줍니다.

좌측 하단의 핸들의 각도는 prediction의 각도를 나타냅니다.

같은 디렉토리 내에 **car-steering-wheel.png, prediction.txt, ground_truth.txt**가 필요합니다.

다음과 같은 사진이 output으로 나옵니다.
![3910 png](https://user-images.githubusercontent.com/62361339/100780189-c445ce00-344c-11eb-825e-3deba80b4070.png)
