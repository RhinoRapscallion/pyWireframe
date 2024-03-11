import pygame
from math import cos, sin, pi
import numpy as np
import struct

vertexArray = []
lineArray = []
normals = []


with open("./fox.stl", 'rb') as stl:
    stl.read(80)
    triangles = (int.from_bytes(stl.read(4), "little"))
    index = 0
    stl.seek(84)

    while (byte := stl.read(50)):
        normals.append(struct.unpack_from('fff', byte[0: 12]))
        vertexArray.append(struct.unpack_from('fff', byte[12: 24]))
        vertexArray.append(struct.unpack_from('fff', byte[24: 36]))
        vertexArray.append(struct.unpack_from('fff', byte[36: 48]))
        

        lineArray.append([index, index + 1])
        lineArray.append([index + 1, index + 2])
        lineArray.append([index + 2, index])
        
        index += 3

print(len(vertexArray) / 3)
print(vertexArray[0])
print(lineArray[0:5])


focalLength = 1
cameraPos = [0, 0, -500]
cameraRotation = [0, 0, 0]

def CameraTransform(cameraPos, cameraRotation, point, focalLength):
    xMatrix = np.array([[1, 0, 0], [0, cos(cameraRotation[0]), sin(cameraRotation[0])], [0, -sin(cameraRotation[0]), cos(cameraRotation[0])]])
    yMatrix = np.array([[cos(cameraRotation[1]), 0, -sin(cameraRotation[1])], [0, 1, 0], [sin(cameraRotation[1]), 0, cos(cameraRotation[1])]])
    zMatrix = np.array([[cos(cameraRotation[2]), sin(cameraRotation[2]), 0], [-sin(cameraRotation[2]), cos(cameraRotation[2]), 0], [0, 0, 1]])

    diffOfAC = np.array([a - c for a, c in zip(point, cameraPos)])

    return (np.matmul(np.matmul(xMatrix, yMatrix), np.matmul(zMatrix, diffOfAC)))

def CameraProject(cameraPos, cameraRotation, point, focalLength):
    CameraTransformPoint = CameraTransform(cameraPos, cameraRotation, point, focalLength)
    if CameraTransformPoint[2] < 0:
        return (1, 1)

    bx = ((focalLength * CameraTransformPoint[0]) / CameraTransformPoint[2])
    by = ((focalLength * CameraTransformPoint[1]) / CameraTransformPoint[2])

    return (bx, by)

vertexArray = [[x, z, y] for x, y, z in vertexArray]

display = pygame.display.set_mode((1500, 1200))
clock = pygame.time.Clock()

def scalePoint(point, maxdim):
    return ((point[0] * maxdim[0]) + (maxdim[0] / 2), (-point[1] * maxdim[1]) + (maxdim[1] / 2))

running = True
move = [0, 0, 0, 0, 0, 0]
movexy = [0, 0]
while running:
    display.fill((0, 0, 0))
    #for lineSet in lineArray:
    #    pygame.draw.line(display, (255, 255, 255), scalePoint(CameraProject(cameraPos, cameraRotation, vertexArray[lineSet[0]], focalLength), (1500, 1200)), scalePoint(CameraProject(cameraPos, cameraRotation, vertexArray[lineSet[1]], focalLength), (1500, 1200)), 1)
    
    for i in range(triangles):

        for lineSet in lineArray[i * 3 : i * 3 +3]:
            pygame.draw.line(display, (255, 255, 255), scalePoint(CameraProject(cameraPos, cameraRotation, vertexArray[lineSet[0]], focalLength), (1500, 1200)), scalePoint(CameraProject(cameraPos, cameraRotation, vertexArray[lineSet[1]], focalLength), (1500, 1200)), 1)

    cameraRotMatrix=[
        [cos(-cameraRotation[1]), -sin(-cameraRotation[1])],
        [sin(-cameraRotation[1]), cos(-cameraRotation[1])]
    ]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                movexy[1] = 1
            
            if event.key == pygame.K_s:
                movexy[1] = -1
            
            if event.key == pygame.K_a:
                movexy[0] = -1
            
            if event.key == pygame.K_d:
                movexy[0] = 1
            
            if event.key == pygame.K_q:
                move[2] -= 1
            
            if event.key == pygame.K_e:
                move[2] += 1
            
            if event.key == pygame.K_LEFT:
                move[4] -= pi / 180

            if event.key == pygame.K_RIGHT:
                move[4] += pi / 180
            
            if event.key == pygame.K_UP:
                move[5] -= pi / 180

            if event.key == pygame.K_DOWN:
                move[5] += pi / 180
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                movexy[1] = 0

            if event.key == pygame.K_a or event.key == pygame.K_d:
                movexy[0] = 0
            
            if event.key == pygame.K_q or event.key == pygame.K_e:
                move[2] = 0

            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                move[4] = 0
            
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                move[5] = 0
    
    print(movexy)
    move[0] = np.matmul(cameraRotMatrix, movexy)[0]
    move[1] = np.matmul(cameraRotMatrix, movexy)[1]
    cameraPos[0] += move[0]
    cameraPos[2] += move[1]
    cameraPos[1] += move[2]
    cameraRotation[1] += move[4]
    cameraRotation[0] += move[5]
    print(move)
    
    pygame.display.flip()
    clock.tick(24)


