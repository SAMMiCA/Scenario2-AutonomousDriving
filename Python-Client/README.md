# AI-28-Python-Client

## 1. 요약

다음 디렉토리에 받아서 사용하시면 됩니다.   
```
/carla/PythonAPI/
```

**agents:** Python으로 구현된 간단한 자율주행을 위한 모듈이 있습니다.

**rgb:** Client에서 찍은 RGB Camera 사진들이 저장되는 디렉토리입니다.

**seg:** Client에서 찍은 Semantic Segmentation 사진들이 저장되는 디렉토리입니다.

**manual_control.py:**  Client를 실행하는 파일입니다. 대부분의 시뮬레이션은 이 파일을 통해 이뤄집니다.

**lite_control.py** 이상 상황을 발생시키기 위해 조종 가능한 차량 혹은 보행자를 생성하는 파일입니다. 

**spawn_npc.py:** npc를 spawn합니다.

**VidMaker.py:** rgb, seg 디렉토리에 있는 사진 파일들을 비디오로 만들어줍니다.

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

**simple_agent.py**도 사용할 수 있을 것 같은데 추후 추가하겠습니다.

### 2.2 tools
**navigation** 디렉토리에 있는 코드에 쓰이는 간단한 툴입니다. 속도, 차 사이의 간격 등을 계산하는 함수가 있습니다.

## 3. manual_control.py

Unreal Engine에서 Play를 누르고 manual_control.py를 실행시킵니다.

### 자주 사용하는 키

|키|기능|
|----|----|
|**wasd**|앞뒤좌우로 움직임|
|**r**|사진, angle record 시작, 멈춤|
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

class **World**의 **restart**함수를 참고하여 player를 변경할 수 있습니다.

blueprint filter를 'walker.pedestrian.*'로 설정한다면 보행자로도 플레이가 가능합니다.

보행자 player를 생성하면 차와 충돌이 나지 않는데, blueprint 코드 몇줄 밑의 invincible을 true로 설정해주면 충돌이 가능합니다.

### 3.3 Record

**R**을 누르면 사진과 steering angle이 기록됩니다.

**Camera** class의 **_parse_image** 함수를 참고하시면 됩니다.
**Record를 시작하면 기존의 사진들은 삭제됩니다. 백업을 미리 해두셔야합니다.**

### 3.4 화면 조절

**Camera** class의 self.sensors를 보시면 exposure를 통해 밝기를 조절하실 수 있습니다.

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

### 3.4 Semantic Segmentation
**~!!현재 막아둔 기능입니다!!~**

**ver 0.9.10에서 성능 저하와 튕김 현상이 완화되어 사용 가능합니다.**

Ground truth를 얻기 위해 RGB로 찍히는 화면과 Semantic Segmentation으로 찍히는 화면을 동시에 기록하는 코드를 작성했습니다.

~RGB image를 Segmentation으로 convert하는 것을 시도해 보았는데, (Camera class의 사용하지 마세요! 부분입니다)~

~우리가 원하는 그림이 나오지 않고 이상하게 나옵니다.~

~깔끔한 Semantic Segmentation image를 얻기 위해서는 센서를 하나 추가해야하는데,~

~연산량이 많아서 그런지 thread 관련 오류가 나면서 1분 내외로 Unreal Engine이 계속 꺼집니다.~

~synchronous mode를 통해 해결하려 했으나, 이를 사용한 코드를 돌려보아도 에러가 나는 것을 확인했습니다.~

**사용법**

manual_control.py의 다음 코드 부분입니다. 필요가 없으시다면 주석 처리 하시는 게 연산량이 훨씬 적어서 좋습니다.

```
# self.semantic_manager = Semantic_Camera(self.player, self.hud, False)
# self.semantic_manager.transform_index = cam_pos_index
# self.semantic_manager.set_sensor(cam_index, notify=False)    
```

```
# self.semantic_manager.render(display2)
```

```
# world.semantic_manager.toggle_recording()
```

### 3.5 FPS
client fps와 server fps가 있습니다. 

client fps는 **game_loop** 함수의 **clock.tick()** 을 이용하여 설정이 가능합니다.

server fps는 carla에서 make launch 하신 이후에 상단바의 *settings - project settings - Engine - general settings - Default Time Mode Frame Rate*에서 설정 가능합니다.

Fixed Frame Rate을 30정도로 사용하는 편이 좋아 보입니다.


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



