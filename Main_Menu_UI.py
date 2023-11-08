import pygame
from Scores_And_Times_Parser import *
import math
import random
import csv
import sys
import time
from sys import argv


numberOfSelectors = 3

numberOfLevels = 5
Theme_Name_List = [
    "Defualt Theme", "Desert", "Simple Blue", "Keanu Movie", "Royal Red"
]
numberOfThemes = len(Theme_Name_List)

settingsMenuList = ["Music", "SFX (NC)", "Clear Scores", "Difficulty (NC)"]
settingsMenuStatusList = [1 for i in settingsMenuList]
numberOfSettings = len(settingsMenuList)
setting_target = 0

viable_ins = [
        1073741904, 1073741903, 1073741906, 1073741905, #arrows
        13, #enter
        109,
        32 #space
    ]
in_switches = [0 for i in viable_ins]
in_switches_dict = {
    "left": 11, "right": 12, "up": 13, "down": 14,
    "esc": 15,
    "m": 16
}

background_color = [0,0,0]
text_color = [255,255,255]

pygame.init()

window_width = 900
window_height = 400
menu_screen = pygame.display.set_mode((window_width, window_height))
menu_screen.fill(background_color)


header_font = pygame.font.Font('game_over.ttf', 152)
tiny_font = pygame.font.Font('game_over.ttf', 55)
text_font = pygame.font.Font('game_over.ttf', 77)

pygame.display.flip()
pygame.display.set_caption("Putter's Menu")
running = True



selectors = [ 0 for i in range(0,numberOfSelectors)]
#level, theme, settings
selector_target = 0
class Text():
    def __init__(self,string,posx,posy,font=text_font):
        self.font = font
        self.posx = posx
        self.posy = posy
        self.string = string
        self.text = font.render(string, True, text_color)
        self.textRect = self.text.get_rect()
        self.textRect.center = (posx, posy)
    def render(self,t_surface):
        t_surface.blit(self.text, self.textRect)


    def change_text(self,new_string):
        self.text = self.font.render(self.string, True, background_color)
        self.render(menu_screen)
        tR = self.textRect
        pygame.draw.rect(menu_screen,background_color,[tR.x, tR.y, tR.width + 50,tR.height+5] )
        self.text = self.font.render(new_string, True, text_color)
        self.textRect = self.text.get_rect()
        self.textRect.center = (self.posx, self.posy)
        self.render(menu_screen)

def DisplayStats(level,mode,x,y,surface=menu_screen,erase=False):

    stats_list = scores_and_times(level,mode=mode)
    stats_list.sort()
    stats_list.reverse()
    while 1000000 in stats_list:
        stats_list.remove(1000000)
    stat_header_text = Text( "Lvl" + str(level) + " " + str(mode), x, y, text_font)
    stat_header_text.render(surface)
    for i, stat in enumerate(stats_list):
        stat = Text( str( stat ) , x, y+17*i + 30, tiny_font)
        stat.render(surface)

Header_Text = Text("Putter's Strokes",window_width/2,window_height-350,font=header_font)
Header_Text.render(menu_screen)
Subheader_Text = Text("Rolling with misery",window_width/2,window_height-305,font=tiny_font)
Subheader_Text.render(menu_screen)

Instructions = Text("Use Arrows To Choose. Press Enter to change settings or start",window_width/2,window_height-50,font=tiny_font)
Instructions.render(menu_screen)

Level_Name_Text = Text("Choose Level",window_width/2, window_height - 250)
Level_Name_Text.render(menu_screen)

Theme_Name_Text = Text("Choose Theme",window_width/2, window_height - 200)
Theme_Name_Text.render(menu_screen)

Setting_Name_Text = Text("Settings",window_width/2, window_height - 150)
Setting_Name_Text.render(menu_screen)

while running:
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for QUIT event
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            running = False
    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        #Inputs.key_logger(Inputs,event.key,event.type)

        switch = 1 - (event.type - pygame.KEYDOWN)  # 1 if event is keyup, 0 if keydown
        if event.key in viable_ins:
            sw_target = viable_ins.index(event.key)
            #if switch: print(sw_target)
            if in_switches[sw_target] != switch and switch and (sw_target in [0,1]):
                print("left and right!")
                sel_increment = 2*sw_target - 1
                if selector_target == 0: #level
                    selectors[0] += sel_increment
                    selectors[0] = selectors[0]%numberOfLevels
                    Level_Name_Text.change_text("Level "+str(selectors[0]))
                    pygame.draw.rect(menu_screen, background_color, [ 0, 80, 150,600 ]) #cheap erase
                    DisplayStats(selectors[0],"scores",window_width/2 - 350, 100)
                    pygame.draw.rect(menu_screen, background_color, [window_width-180, 80, 250, 600])  # cheap erase
                    DisplayStats(selectors[0], "times", window_width / 2 + 350, 100)
                if selector_target == 1: #theme
                    selectors[1] += sel_increment
                    selectors[1] = selectors[1]%numberOfThemes
                    Theme_Name_Text.change_text(Theme_Name_List[selectors[1]])
                if selector_target == 2: #settings
                    setting_target += sel_increment
                    setting_target = setting_target%numberOfSettings
                    '''if settingsMenuList[setting_target] == "Clear Scores":
                        Setting_Name_Text.change_text(str(settingsMenuList[setting_target]))
                        continue'''
                    if settingsMenuStatusList[setting_target]: status_word = ": on"
                    else: status_word = ": off"
                    Setting_Name_Text.change_text( str(settingsMenuList[setting_target]) + str(status_word) )

            if in_switches[sw_target] != switch and switch and (sw_target in [2,3]):
                print("up and down!")
                sel_targ_increment = 2* ( sw_target -2) - 1
                selector_target += sel_targ_increment
                selector_target = selector_target%numberOfSelectors

            if in_switches[sw_target] != switch and switch and sw_target == 4 and selector_target == 2: #settings editing
                '''print(settingsMenuStatusList[setting_target])
                print(settingsMenuList[setting_target])
                print(setting_target)'''
                settingsMenuStatusList[setting_target] = (settingsMenuStatusList[setting_target] + 1)%2
                if settingsMenuList[setting_target] == "Clear Scores":
                    clear_scores_and_times()
                    Setting_Name_Text.change_text(str(settingsMenuList[setting_target]) + ": CLEARED")
                    continue
                if settingsMenuStatusList[setting_target]:
                    status_word = ": on"
                else:
                    status_word = ": off"
                Setting_Name_Text.change_text(str(settingsMenuList[setting_target]) + str(status_word))

            if in_switches[sw_target] != switch and switch and sw_target == 4 and selector_target != 2:
                print("esc")
                menuOutputInfo = {
                    "level": selectors[0],
                    "theme_number": selectors[1],
                }
                for i, setting in enumerate(settingsMenuList):
                    menuOutputInfo[setting] = settingsMenuStatusList[i]
                running = False
            in_switches[sw_target] = switch


    #Level_Name_Text.render(menu_screen)
    pygame.display.flip()
pygame.display.quit()