import pygame
import numpy as np
from math import sin, cos, radians

# Initialize Pygame
pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Quantum Chemistry Visualization")
clock = pygame.time.Clock()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 100, 100)
GRADIENT = [(0, 0, 50), (0, 100, 200), (255, 255, 255)]  # Background gradient

# Orbital grid setup
grid_size = 200
x = np.linspace(-5, 5, grid_size)
y = np.linspace(-5, 5, grid_size)
z = np.linspace(-5, 5, grid_size)
X, Y = np.meshgrid(x, y)

# Functions for orbitals
def s_orbital(x, y, z=0):
    """s orbital: spherical symmetry."""
    r = np.sqrt(x**2 + y**2 + z**2)
    return np.exp(-r)

def p_orbital(x, y, z=0, axis='x'):
    """p orbital: dumbbell shape along a chosen axis."""
    r = np.sqrt(x**2 + y**2 + z**2)
    if axis == 'x':
        return x * np.exp(-r)
    elif axis == 'y':
        return y * np.exp(-r)
    elif axis == 'z':
        return z * np.exp(-r)

def d_orbital(x, y, z=0, mode='dx2-y2'):
    """d orbital: four-lobed shapes."""
    r = np.sqrt(x**2 + y**2 + z**2)
    if mode == 'dx2-y2':
        return (x**2 - y**2) * np.exp(-r)
    elif mode == 'dz2':
        return (2 * z**2 - x**2 - y**2) * np.exp(-r)

def normalize(data):
    """Normalize data to range [0, 1]."""
    return (data - np.min(data)) / (np.max(data) - np.min(data))

# Function for rendering background gradient
def draw_gradient(surface, colors):
    """Draws a vertical gradient background."""
    for i in range(len(colors) - 1):
        c1 = colors[i]
        c2 = colors[i + 1]
        for y in range(height // len(colors) * i, height // len(colors) * (i + 1)):
            blend = (y - (height // len(colors) * i)) / (height // len(colors))
            r = int(c1[0] * (1 - blend) + c2[0] * blend)
            g = int(c1[1] * (1 - blend) + c2[1] * blend)
            b = int(c1[2] * (1 - blend) + c2[2] * blend)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

# 3D projection helpers
def project_3d(x, y, z, angle_x, angle_y):
    """Projects 3D coordinates into 2D space."""
    # Rotation matrices
    rx = np.array([
        [1, 0, 0],
        [0, cos(angle_x), -sin(angle_x)],
        [0, sin(angle_x), cos(angle_x)],
    ])
    ry = np.array([
        [cos(angle_y), 0, sin(angle_y)],
        [0, 1, 0],
        [-sin(angle_y), 0, cos(angle_y)],
    ])
    coords = np.dot(rx, np.dot(ry, np.array([x, y, z])))
    return int(width / 2 + coords[0] * 80), int(height / 2 - coords[1] * 80)

# Molecular vibration setup
vibration_amplitude = 1.0
vibration_speed = 0.1
vibration_angle = 0

# Main loop variables
running = True
mode = 's'  # Default orbital mode
angle_x, angle_y = 0, 0  # 3D rotation angles

while running:
    screen.fill(BLACK)
    draw_gradient(screen, GRADIENT)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                mode = 's'
            elif event.key == pygame.K_x:
                mode = 'px'
            elif event.key == pygame.K_y:
                mode = 'py'
            elif event.key == pygame.K_d:
                mode = 'dx2-y2'
            elif event.key == pygame.K_z:
                mode = 'dz2'

    # Update 3D rotation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle_y -= radians(2)
    if keys[pygame.K_RIGHT]:
        angle_y += radians(2)
    if keys[pygame.K_UP]:
        angle_x -= radians(2)
    if keys[pygame.K_DOWN]:
        angle_x += radians(2)

    # Compute molecular vibration offset
    vibration_angle += vibration_speed
    vibration_offset = vibration_amplitude * sin(vibration_angle)

    # Choose the orbital to visualize
    if mode == 's':
        Z = s_orbital(X, Y, vibration_offset)
    elif mode == 'px':
        Z = p_orbital(X, Y, vibration_offset, axis='x')
    elif mode == 'py':
        Z = p_orbital(X, Y, vibration_offset, axis='y')
    elif mode == 'dx2-y2':
        Z = d_orbital(X, Y, vibration_offset, mode='dx2-y2')
    elif mode == 'dz2':
        Z = d_orbital(X, Y, vibration_offset, mode='dz2')

    # Normalize data and map to 3D projection
    Z = normalize(Z)
    for i in range(grid_size):
        for j in range(grid_size):
            x_3d = x[i]
            y_3d = y[j]
            z_3d = Z[i, j] * 10
            color = (
                int(Z[i, j] * 255),
                int((1 - Z[i, j]) * 100),
                int(Z[i, j] * 200),
            )
            x_proj, y_proj = project_3d(x_3d, y_3d, z_3d, angle_x, angle_y)
            pygame.draw.circle(screen, color, (x_proj, y_proj), 2)

    # Render info
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Mode: {mode}-orbital (Press 's', 'x', 'y', 'd', 'z')", True, WHITE)
    screen.blit(text, (10, 10))

    # Update the display
    pygame.display.flip()
    clock.tick(3000)

pygame.quit()
