from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # To stop obnoxious advertising by pygame when imported

import pygame, sys, random
from pygame.locals import *
import subprocess

# Allow user to draw a selection box with the mouse then crops image to selection box
# Based on: https://stackoverflow.com/questions/64716266/how-can-i-make-a-rectangle-selection-tool-in-python-3
# Usage: Press iand hold left mouse button and draw out a selection box then release button, box then changes
#        from red to green
#        Press left iand hold mouse button on existing (green) top or left borders and drag to resize box then
#        release.
#        Press escape to exit, cropped image will be in "crop.jpg"

def create_box(p1, p2):
    x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
    x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
    return pygame.Rect(x1, y1, x2-x1, y2-y1)


# set up pygame
pygame.init()
mainClock = pygame.time.Clock()

infoObject = pygame.display.Info()
scrn = pygame.display.set_mode((700, 700), pygame.RESIZABLE)
pygame.display.set_caption('Selection box test')

# set up the colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BACKGROUNDCOLOR = GREEN

img = pygame.image.load("image.jpg").convert()

# Make maximum image size slightly smaller than screen size
maxWidth=infoObject.current_w-200
maxHeight=infoObject.current_h-200

width=img.get_width()
height=img.get_height()

scale1=scale2=1
print(f"Image size {width},{height}")
if (width > maxWidth):
    print(f"Width {width} too big for window, scaling")
    scale1 = maxWidth/width
    width = maxWidth
    height = height*scale1
    img=pygame.transform.scale(img, (width, height))
    print(f"Scaled size {width},{height}")
if (height > maxHeight):
    print(f"Height {height} too big for window, scaling")
    scale2 = maxHeight/height
    width = width*scale2
    height = maxHeight
    img=pygame.transform.scale(img, (width, height))
    print(f"Scaled size {width},{height}")
scale=scale1*scale2

scrn = pygame.display.set_mode((width, height), pygame.RESIZABLE)
 
draw_new_selection_box = False
selection_completed = False
resizing = False
resizeStartY=False
resizeStartX=False
resizeEndY=False
resizeEndX=False

# game loop
game_loop = True
while game_loop:
    # check for events and change variables based on events
    for event in pygame.event.get():
        # check if user has quit
        if event.type == QUIT:
            # FIXME: Output cmds for both exits
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if selection_completed:
                    # FIXME: Use PIL ISO imagemagick convert to crop image
                    cmd=["convert","-crop", f"+{box_start[0]/scale}+{box_start[1]/scale}", "-crop", f"-{(width-box_end[0])/scale}-{(height-box_end[1])/scale}", "+repage", "image.jpg", "crop.jpg"]
                    subprocess.call(cmd)
                    # FIXME: Display cropped image
                else:
                    print(f"No selection made.")
                pygame.quit()
                sys.exit()
  
        check_which_mouse_button = pygame.mouse.get_pressed()
        if event.type == MOUSEBUTTONDOWN:
            if check_which_mouse_button[0]:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (selection_completed and abs(mouse_y-box_start[1])<10):
                    print("Resizing Start Y")
                    resizing = True
                    resizeStartY=True
                elif (selection_completed and abs(mouse_x-box_start[0])<10):
                    print("Resizing Start X")
                    resizing = True
                    resizeStartX=True
                elif (selection_completed and abs(mouse_y-box_end[1])<10):
                    print("Resizing End Y")
                    resizing = True
                    resizeEndY=True
                elif (selection_completed and abs(mouse_x-box_end[0])<10):
                    print("Resizing End X")
                    resizing = True
                    resizeEndX=True
                else:
                    box_start = pygame.mouse.get_pos()
                    print(f"Start {box_start[0]},{box_start[1]}")
                    draw_new_selection_box = True
        if event.type == MOUSEBUTTONUP:
            if not check_which_mouse_button[0]:
                if resizing:
                    resizing=False
                    resizeStartY=False    
                    resizeStartX=False    
                    resizeEndY=False    
                    resizeEndX=False
                else:
                    box_end = pygame.mouse.get_pos()
                    print(f"End {box_end[0]},{box_end[1]}")
                    draw_new_selection_box = False
                    selection_completed = True
    
    current_mouse_location = pygame.mouse.get_pos()   
    if resizing:
        mouse_x, mouse_y = current_mouse_location
        if resizeStartY:
            box_start= box_start[0],mouse_y
        elif resizeStartX:
            box_start= mouse_x, box_start[1]
        elif resizeEndY:
            box_end = box_end[0],mouse_y
        elif resizeEndX:
            box_end= mouse_x, box_end[1]
        selection_box = create_box(box_start, box_end)
    elif draw_new_selection_box:
        selection_box = create_box(box_start, current_mouse_location)
    elif selection_completed:
        completed_selection_box = create_box(box_start, box_end)
                    
    scrn.blit(img, (0, 0))

    if draw_new_selection_box:
        pygame.draw.rect(scrn, RED, selection_box, 2)
    elif resizing:
        pygame.draw.rect(scrn, BLUE, selection_box, 2)
    elif selection_completed:
        pygame.draw.rect(scrn, GREEN, completed_selection_box, 4)

    # draw the scrn onto the screen
    pygame.display.update()
    mainClock.tick(60)

