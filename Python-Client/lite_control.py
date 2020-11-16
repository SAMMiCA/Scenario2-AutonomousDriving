#!/usr/bin/env python

# Copyright (c) 2019 Aptiv
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

#====================================Ver 201023======================================#
# 돌발 상황을 위한 차량 생성
# 차량 조작 이외의 기능 간소화
#====================================Ver 201026======================================#
# 보행자 생성 기능 추가
# 실행 시 --w 인자를 주면 보행자 생성
# 보행자 회전시 (A,D) W를 동시에 누르면 오류
#====================================================================================#
"""
An example of client-side bounding boxes with basic car controls.

Controls:

	W			 : throttle
	S			 : brake
	AD			 : steer
	Space		 : hand-brake

	ESC			 : quit
"""

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
import argparse

try:
	sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
		sys.version_info.major,
		sys.version_info.minor,
		'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
	pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================
import time
start = time.time()
import carla
import weakref
import random
import cv2

try:
	import pygame
	from pygame.locals import K_ESCAPE
	from pygame.locals import K_SPACE
	from pygame.locals import K_a
	from pygame.locals import K_d
	from pygame.locals import K_s
	from pygame.locals import K_w
	from pygame.locals import K_m
except ImportError:
	raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
	import numpy as np
except ImportError:
	raise RuntimeError('cannot import numpy, make sure numpy package is installed')

VIEW_WIDTH = 1280
VIEW_HEIGHT = 720
VIEW_FOV = 90





# ==============================================================================
# -- BasicSynchronousClient ----------------------------------------------------
# ==============================================================================


class BasicSynchronousClient(object):
	"""
	Basic implementation of a synchronous client.
	"""

	def __init__(self):
		self.client = None
		self.world = None
		self.camera = None
		self.depth_camera = None
		self.car = None
		self.display = None
		self.depth_display = None
		self.image = None
		self.depth_image = None
		self.capture = True
		self.depth_capture = True
		self.counter = 0
		self.depth = None
		self.pose = []		


	def camera_blueprint(self):
		"""
		Returns camera blueprint.
		"""

		camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
		camera_bp.set_attribute('image_size_x', str(VIEW_WIDTH))
		camera_bp.set_attribute('image_size_y', str(VIEW_HEIGHT))
		camera_bp.set_attribute('fov', str(VIEW_FOV))
		return camera_bp
		

	def set_synchronous_mode(self, synchronous_mode):
		"""
		Sets synchronous mode.
		"""

		settings = self.world.get_settings()
		settings.synchronous_mode = synchronous_mode
		self.world.apply_settings(settings)

	def setup_car(self, walker):
		"""
		Spawns actor-vehicle to be controled.
		"""
		if walker == False:
			car_bp = self.world.get_blueprint_library().filter('model3')[0]
		else:
			car_bp = self.world.get_blueprint_library().filter('walker.pedestrian.*')[0]
		location = random.choice(self.world.get_map().get_spawn_points())
		self.car = self.world.spawn_actor(car_bp, location)

	def setup_camera(self):
		"""
		Spawns actor-camera to be used to render view.
		Sets calibration for client-side boxes rendering.
		"""

		camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15))
		self.camera = self.world.spawn_actor(self.camera_blueprint(), camera_transform, attach_to=self.car)
		weak_self = weakref.ref(self)
		self.camera.listen(lambda image: weak_self().set_image(weak_self, image))

		calibration = np.identity(3)
		calibration[0, 2] = VIEW_WIDTH / 2.0
		calibration[1, 2] = VIEW_HEIGHT / 2.0
		calibration[0, 0] = calibration[1, 1] = VIEW_WIDTH / (2.0 * np.tan(VIEW_FOV * np.pi / 360.0))
		self.camera.calibration = calibration
		

	def control(self, car, ms):
		"""
		Applies control to main car based on pygame pressed keys.
		Will return True If ESCAPE is hit, otherwise False to end main loop.
		"""

		keys = pygame.key.get_pressed()
		control = car.get_control()

		if isinstance(car, carla.Vehicle):
			if keys[K_ESCAPE]:
				return True
			control.throttle = 0
			
			if keys[K_w]:
				control.throttle = 1
				control.reverse = False
			elif keys[K_s]:
				control.throttle = 1
				control.reverse = True
			if keys[K_a]:
				control.steer = max(-1., min(control.steer - 0.05, 0))
			elif keys[K_d]:
				control.steer = min(1., max(control.steer + 0.05, 0))
			else:
				control.steer = 0
			control.hand_brake = keys[K_SPACE]
			car.apply_control(control)

		elif isinstance(car, carla.Walker):
			pedestrian_heading = 0
			control.speed = 0.0
			car.rotation = car.get_transform().rotation
			if keys[K_s]:
				control.speed = 0.0
			if keys[K_a]:
				control.speed = .01
				car.rotation.yaw -=0.08*ms
			if keys[K_d]:
				control.speed = .01
				car.rotation.yaw += 0.08*ms
			if keys[K_w]:
				control.speed = 3.713
			control.jump = keys[K_SPACE]
			car.rotation.yaw = round(car.rotation.yaw, 1)
			control.direction = car.rotation.get_forward_vector()
			car.apply_control(control)


		return False

	@staticmethod
	def set_image(weak_self, img):
		"""
		Sets image coming from camera sensor.
		The self.capture flag is a mean of synchronization - once the flag is
		set, next coming image will be stored.
		"""

		self = weak_self()
		if self.capture:
			self.image = img
			self.capture = False


	def render(self, display):
		"""
		Transforms image from camera sensor and blits it to main pygame display.
		"""

		if self.image is not None:
			array = np.frombuffer(self.image.raw_data, dtype=np.dtype("uint8"))
			array = np.reshape(array, (self.image.height, self.image.width, 4))
			array = array[:, :, :3]
			array = array[:, :, ::-1]
			surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
			display.blit(surface, (0, 0))
		

	def game_loop(self, walker):
		"""
		Main program loop.
		"""

		try:
			pygame.init()

			self.client = carla.Client('127.0.0.1', 2000)
			self.client.set_timeout(2.0)
			self.world = self.client.get_world()

			self.setup_car(walker)
			self.setup_camera()
			self.display = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)

			pygame_clock = pygame.time.Clock()

			self.set_synchronous_mode(False)
			vehicles = self.world.get_actors().filter('vehicle.*')

			while True:
				self.world.tick()
				self.capture = True
				pygame_clock.tick(60)
				self.render(self.display)
				pygame.display.flip()
				pygame.event.pump()
				cv2.waitKey(1)
				if self.control(self.car, pygame_clock.get_time()):
					return
				
		#except Exception as e: print(e)
		finally:

			self.set_synchronous_mode(False)
			self.camera.destroy()
			self.car.destroy()
			pygame.quit()
			cv2.destroyAllWindows()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
	"""
	Initializes the client-side bounding box demo.
	"""
	parser = argparse.ArgumentParser(description='Lite_Controller')
	parser.add_argument(
		'--w', '-w',
        action='store_true',
        help='spawn walker?')
	args = parser.parse_args()

	try:
		client = BasicSynchronousClient()
		client.game_loop(args.w)
	finally:
		print('EXIT')


if __name__ == '__main__':
	main()
