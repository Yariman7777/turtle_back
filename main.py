import pygame
import numpy as np
from pygame.locals import *
import math

# Инициализация pygame
pygame.init()
pygame.mouse.set_visible(False)  # Скрываем курсор
pygame.event.set_grab(True)  # Захватываем мышь в окне

# Параметры окна
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D пространство от первого лица")


# Настройки камеры
class Camera:
    def __init__(self):
        self.pos = np.array([0.0, 0.0, 0.0])  # Позиция [x, y, z]
        self.yaw = 0.0  # Поворот по горизонтали (влево/вправо)
        self.pitch = 0.0  # Поворот по вертикали (вверх/вниз)
        self.speed = 0.1
        self.sensitivity = 0.1

    def rotate(self, dx, dy):
        self.yaw += dx * self.sensitivity
        self.pitch += dy * self.sensitivity

        # Ограничение наклона камеры
        self.pitch = max(-89.0, min(89.0, self.pitch))

    def move(self, direction):
        # Преобразование углов в направление движения
        yaw_rad = math.radians(self.yaw)

        if direction == 'forward':
            self.pos[0] += math.sin(yaw_rad) * self.speed
            self.pos[2] += math.cos(yaw_rad) * self.speed
        elif direction == 'backward':
            self.pos[0] -= math.sin(yaw_rad) * self.speed
            self.pos[2] -= math.cos(yaw_rad) * self.speed
        elif direction == 'left':
            self.pos[0] += math.sin(yaw_rad - math.pi / 2) * self.speed
            self.pos[2] += math.cos(yaw_rad - math.pi / 2) * self.speed
        elif direction == 'right':
            self.pos[0] += math.sin(yaw_rad + math.pi / 2) * self.speed
            self.pos[2] += math.cos(yaw_rad + math.pi / 2) * self.speed


# Создание текстур
def create_texture_grid(size, color1, color2):
    texture = pygame.Surface((size, size))
    for y in range(size):
        for x in range(size):
            if (x // 16 + y // 16) % 2 == 0:
                texture.set_at((x, y), color1)
            else:
                texture.set_at((x, y), color2)
    return texture


# Создание текстур для пола и стен
floor_texture = create_texture_grid(128, (50, 50, 50), (70, 70, 70))
wall_texture_red = create_texture_grid(128, (100, 30, 30), (150, 50, 50))
wall_texture_blue = create_texture_grid(128, (30, 30, 100), (50, 50, 150))
wall_texture_green = create_texture_grid(128, (30, 100, 30), (50, 150, 50))
wall_texture_yellow = create_texture_grid(128, (100, 100, 30), (150, 150, 50))


# Класс для стены
class Wall:
    def __init__(self, x1, y1, x2, y2, height, texture):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.height = height
        self.texture = texture

    def draw(self, screen, camera):
        # Преобразование координат стены относительно камеры
        points = [
            (self.x1 - camera.pos[0], self.y1 - camera.pos[2]),
            (self.x2 - camera.pos[0], self.y2 - camera.pos[2])
        ]

        # Поворот точек относительно камеры
        rotated = []
        for x, y in points:
            dist = math.sqrt(x * x + y * y)
            angle = math.degrees(math.atan2(y, x)) - camera.yaw
            rad = math.radians(angle)
            rotated.append((
                dist * math.sin(rad),
                dist * math.cos(rad)
            ))

        # Если стена позади камеры, не рисуем
        if rotated[0][1] < 0.1 and rotated[1][1] < 0.1:
            return

        # Проекция на экран
        def project(x, y):
            if y == 0:
                y = 0.001
            screen_x = WIDTH / 2 + (x / y) * 400
            scale = 1000 / y
            return screen_x, scale

        x1, scale1 = project(rotated[0][0], rotated[0][1])
        x2, scale2 = project(rotated[1][0], rotated[1][1])

        # Вычисление высоты стены на экране
        h1 = self.height * scale1
        h2 = self.height * scale2

        # Рисование стены (упрощённое)
        if abs(x2 - x1) > 1:
            pygame.draw.polygon(screen, (100, 100, 100), [
                (x1, HEIGHT / 2 - h1 / 2),
                (x2, HEIGHT / 2 - h2 / 2),
                (x2, HEIGHT / 2 + h2 / 2),
                (x1, HEIGHT / 2 + h1 / 2)
            ])


# Создание уровня
def create_level():
    walls = []
    size = 10

    # Создание квадратной комнаты
    walls.append(Wall(-size, -size, size, -size, 3, wall_texture_red))  # Северная стена
    walls.append(Wall(size, -size, size, size, 3, wall_texture_blue))  # Восточная стена
    walls.append(Wall(size, size, -size, size, 3, wall_texture_green))  # Южная стена
    walls.append(Wall(-size, size, -size, -size, 3, wall_texture_yellow))  # Западная стена

    # Внутренние стены для интереса
    walls.append(Wall(-3, -3, 3, -3, 2, wall_texture_red))
    walls.append(Wall(3, -3, 3, 3, 2, wall_texture_blue))
    walls.append(Wall(-3, 3, 3, 3, 2, wall_texture_green))
    walls.append(Wall(-3, -3, -3, 3, 2, wall_texture_yellow))

    return walls


# Основной цикл
def main():
    clock = pygame.time.Clock()
    camera = Camera()
    walls = create_level()
    running = True

    # Создание текстуры пола
    floor_surface = pygame.Surface((WIDTH, HEIGHT // 2))
    floor_surface.fill((60, 60, 60))

    while running:
        dt = clock.tick(60)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Выход по нажатию ESC или закрытию окна
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    running = False

            # Обработка движения мыши для поворота камеры
            if event.type == MOUSEMOTION:
                camera.rotate(event.rel[0], event.rel[1])

        # Получение состояния клавиш для движения
        keys = pygame.key.get_pressed()
        if keys[K_w] or keys[K_UP]:
            camera.move('forward')
        if keys[K_s] or keys[K_DOWN]:
            camera.move('backward')
        if keys[K_a] or keys[K_LEFT]:
            camera.move('left')
        if keys[K_d] or keys[K_RIGHT]:
            camera.move('right')
        if keys[K_SPACE]:
            camera.pos[1] += camera.speed  # Прыжок
        if keys[K_LCTRL]:
            camera.pos[1] -= camera.speed  # Присесть

        # Очистка экрана
        screen.fill((135, 206, 235))  # Голубой цвет неба

        # Рисование пола (нижняя половина экрана)
        screen.blit(floor_surface, (0, HEIGHT // 2))

        # Рисование стен
        for wall in walls:
            wall.draw(screen, camera)

        # Рисование прицела (перекрестия)
        crosshair_size = 15
        crosshair_color = (255, 255, 0)
        pygame.draw.line(screen, crosshair_color,
                         (WIDTH // 2 - crosshair_size, HEIGHT // 2),
                         (WIDTH // 2 + crosshair_size, HEIGHT // 2), 2)
        pygame.draw.line(screen, crosshair_color,
                         (WIDTH // 2, HEIGHT // 2 - crosshair_size),
                         (WIDTH // 2, HEIGHT // 2 + crosshair_size), 2)

        # Отображение информации о позиции и угле камеры
        font = pygame.font.Font(None, 24)
        pos_text = font.render(f"Позиция: ({camera.pos[0]:.1f}, {camera.pos[1]:.1f}, {camera.pos[2]:.1f})", True,
                               (255, 255, 255))
        angle_text = font.render(f"Угол: {camera.yaw:.1f}°", True, (255, 255, 255))
        fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (255, 255, 255))

        screen.blit(pos_text, (10, 10))
        screen.blit(angle_text, (10, 35))
        screen.blit(fps_text, (10, 60))

        # Обновление экрана
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()