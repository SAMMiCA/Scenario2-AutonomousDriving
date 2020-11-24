# AI-28-Python-Client

## 1. 요약

다음 디렉토리에 받아서 사용하시면 됩니다.   
```
/carla/PythonAPI/
```

**agents:** Python으로 구현된 간단한 자율주행을 위한 모듈이 있습니다.

**manual_control.py:**  Client를 실행하는 파일입니다. 대부분의 시뮬레이션은 이 파일을 통해 이뤄집니다.

**lite_control.py** 이상 상황을 발생시키기 위해 조종 가능한 차량 혹은 보행자를 생성하는 파일입니다. 

**spawn_npc.py:** npc를 spawn합니다.

**VidMaker.py:** rgb, seg 디렉토리에 있는 사진 파일들을 비디오로 만들어줍니다.

**Synchronizer.py** 가끔 rgb 파일이 프레임을 건너 뛸 때, 남는 seg 파일을 지워줍니다.

**lidar_distance_calculator** ply 파일들이 있는 디렉토리에 넣고 사용하시면, 전방 obstacle과의 distance, 상대속도를 계산합니다.

**lidar_control.py** manual_control에 lidar 기반 obstacle avoidance를 추가했습니다. 아직 버그가 많아 고치는 중입니다.

**lidar_add_on.py** lidar_control에 필요한 모듈입니다.

## 2. agents

agents에 있는 모듈을 통한 자율주행은 다음과 같은 문제점이 있어 현재 사용하지 않도록 주석처리 해두었습니다.

```

1. 고속 주행시 장애물 회피가 전혀 되지 않는다.

  가로등 등에 부딪혀 전혀 움직이지 못하는 상황이 굉장히 자주 나옵니다.
  
2. Client의 FPS 방어가 되지 않을 때, 정상적인 주행이 불가능하다.

  직진을 할 때에도 지그재그를 그리며 굉장히 불안하게 주행합니다.
  
```

이런 문제점이 있기는 하지만, carla의 재빌드 없이, 속도 등의 간단한 설정을 만질 수 있어서 남겨두었습니다.

### 2.1 navigation

자율주행을 위한 파일들입니다. 표면적으로 **manual_control.py**에서 사용할만한 파일은 basic_agent.py와 roaming_agent.py입니다.

**basic_agent.py**는 목적지가 정해져있습니다. 목적지에 다다르면 차가 멈춥니다.

**roaming_agent.py**는 목적지가 없습니다. 다만 화면에 waypoint들이 보여서 사용할 일은 거의 없을 것 같습니다.

### 2.2 tools
**navigation** 디렉토리에 있는 코드에 쓰이는 간단한 툴입니다. 속도, 차 사이의 간격 등을 계산하는 함수가 있습니다.

## 3. manual_control.py

수동, 혹은 자동으로 CARLA에서 차량을 움직이게 하는 프로그램입니다.

차량 생성과 동시에, RGB camera, semantic segmentation camera, LiDAR, semantic LiDAR 센서 생성합니다.

Unreal Engine에서 Play를 누르고 manual_control.py를 실행시킵니다.

### 자주 사용하는 키

|키|기능|
|----|----|
|**wasd**|앞뒤좌우로 움직임|
|**r**|사진, angle record 시작, 멈춤|
|**v**|record된 파일 저장|
|**p**|autopilot 시작, 멈춤|
|**~**|센서 변경|
|**c**|날씨 변경|

### 3.1 맵 변경
같은 서버 상에서 여러 클라이언트를 돌리기 위해서 맵이 바뀌는 것을 막기 위해 현재 막아 두었습니다.

Unreal Engine 화면 아래 부분에 보이는 *Carla/Maps/* 디렉토리에서 찾아 쓸 수 있습니다.

PythonAPI로 구현하려면 **game_loop** 함수 내의
```
world = World(client.get_world(), hud, args)
```
부분을 다음 코드로 고치시면 됩니다.
```
world = World(client.load_world('Town01'), hud, args)
```

### 3.2 Player 설정
안정적인 시야 각도를 뽑기 위해서 player를 AUDI A2로 고정시켜 두었습니다.

backspace를 누르면 player를 변경할 수 있습니다.

blueprint filter를 'walker.pedestrian.*'로 설정한다면 보행자로도 플레이가 가능합니다.

보행자 player를 생성하면 차와 충돌이 나지 않는데, blueprint 코드 몇줄 밑의 invincible을 true로 설정해주면 충돌이 가능합니다.

### 3.3 Record

**R**을 누르면 RGB, semantic segmentation, LiDAR point cloud, Semantic LiDAR point cloud, steering angle log가 동시에 저장됩니다.

각 센서 class의 **_parse_image** 함수를 참고하시면 됩니다.

**Record가 끝나면 V 키를 꼭 눌러서 백업을 해두셔야합니다.**

### 3.4 화면 조절

**Camera** class의 self.sensors를 보시면 exposure를 통해 밝기를 조절하실 수 있습니다. #CARLA 0.9.10 사용시, 쓸 일이 거의 없습니다.


**main** 함수의 argparser 부분에서 해상도 기본 값을 조절하실 수 있습니다.

```
python manual_control.py --res 'WIDTHxHEIGHT'
```

이렇게도 조절 가능합니다.

### 3.3 자율 주행 설정
현재 자율주행을 위해 사용하는 알고리즘은 carla에서 기본 제공하는 알고리즘입니다.

실험 결과 장애물을 만났을 때 멈추지만, 회피해서 목적지로 가지는 않는다는 문제가 있습니다.

대안으로는 **agents** 디렉토리에 있는 모듈이 있지만, 위 문제점은 똑같이 일어납니다.

다만 속도 등의 기본적인 특성을 쉽게 만질 수 있다는 메리트가 있습니다.

BasicAgent를 사용하기 위해서는 game_loop 함수의 주석을 참고해주세요.

**LiDAR 센서를 통해 Obstacle avoidance도 구현하고 있습니다.**


### 3.4 FPS
client fps와 server fps가 있습니다. 

client fps는 **game_loop** 함수의 **clock.tick()** 을 이용하여 설정이 가능합니다.

server fps는 carla에서 make launch 하신 이후에 상단바의 *settings - project settings - Engine - general settings - Default Time Mode Frame Rate*에서 설정 가능합니다.

Fixed Frame Rate을 30정도로 사용하는 편이 좋아 보입니다.

### 3. LiDAR

기본 LiDAR와 semantic LiDAR가 있습니다.

LiDAR는 x,y,z,intensity가 포함된 ply파일을,

semantic LiDAR는 x,y,z,intensity,static/dynamic,label 정보가 포함된 ply 파일을 저장합니다.

LiDAR sensor 사용시에는 client fps와 LiDAR fps를 맞춰주는 것이 필수적입니다. (아닐시에는 한 프레임 안에 특정 방향만 감지 가능)

다음과 같이 fps를 설정해주시면 됩니다.

```
cd ~/carla/PythonAPI/util
python3 config.py --fps=10
```


## 6. lite_control.py

차량을 움직이는 것 외에 모든 기능을 뺀 manual_control입니다.

연산량을 줄여, manual_control.py를 두 개 켜는 것과 비교해 대략 초당 5프레임정도 이득이 있습니다.

인자로 --w를 줄 경우 보행자가, 주지 않을 경우 차량이 생성됩니다.


## 5. spawn_npc.py
npc를 spawn 합니다.

실행시 argument로 --n 으로는 차량 대수, --w 로는 보행자수를 설정 가능합니다.

## 6. VidMaker.py
rgb 와 seg에 있는 사진 파일을 따로 비디오로 묶어줍니다.

현재 기본 fps는 30입니다.


## 7. lidar_distance_calculator.py
전방 obstacle 과의 거리와 상대속도를 계산합니다. ply파일들이 있는 디렉토리에 넣고 사용해주세요.

기본적으로 설정된 lidar fps(?)는 10입니다.

lidar fps 변경시에는 속도 계산 함수의 변경이 필요합니다.

## 8. lidar_control.py
manual_control.py와 기본적으로 비슷하지만, 전방의 obstacle과 거리가 가까워질때, 회피하는 기능을 넣었습니다.

LiDAR sensor 사용시에는 client fps와 LiDAR fps를 맞춰주는 것이 필수적입니다. (아닐시에는 한 프레임 안에 특정 방향만 감지 가능)

다음과 같이 fps를 설정해주시면 됩니다.

```
cd ~/carla/PythonAPI/util
python3 config.py --fps=10
```

L버튼을 누르시면 lidar controller가 활성화 됩니다. lidar controller 활성화를 시키지 않으면, manual_control과 기능이 같습니다.

LiDAR sensor만으로는 실선, 점선의 구분이 어려워, 차선 유지(중앙선 침범 금지 등)는 carla map의 ground truth 값을 restriction으로 사용하고 있습니다.

자세한 알고리즘은 다음 링크를 참고해주세요.

https://drive.google.com/file/d/1xlqQSHlE9xqsv9OkMZ6fsIy01o5cg8KT/view?usp=sharing

이전 버전의 segmentation fault는 완화되었지만,
현재 pygame과 thread 관련 client가 꺼지는 버그, 연속한 장애물을 제대로 피하지 못하는 버그 등이 있습니다.

장기적으로 사용에 어려움이 없어졌을 때 manual_control.py와 합치는 것을 목표로 하고 있습니다.
