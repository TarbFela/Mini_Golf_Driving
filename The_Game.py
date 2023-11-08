import pygame
import math
import random
import csv
import sys
import time
from sys import argv
import importlib


import Main_Menu_UI
print(Main_Menu_UI.menuOutputInfo)
current_level = Main_Menu_UI.menuOutputInfo["level"]
time.sleep(1)


'''importlib.reload(Main_Menu_UI)
current_level = Main_Menu_UI.menuOutputInfo["level"]'''

print(argv[0])
folder_file_path_as_list = argv[0].split("/")
print(folder_file_path_as_list)
folder_file_path = ""
for word in folder_file_path_as_list[:-1]:
    folder_file_path += word + "/"
print(folder_file_path)

LEVEL_SELECTOR_MAP = 0
t = time.localtime()
current_sec = int(time.strftime("%S", t)) + 60*int(time.strftime("%M", t)) + 3600*int(time.strftime("%H", t))

t = time.localtime()
new_sec = int(time.strftime("%S", t)) + 60*int(time.strftime("%M", t)) + 3600*int(time.strftime("%H", t))
print(new_sec-current_sec)

game_clock = pygame.time.Clock()
phys_clock = pygame.time.Clock()
perf_const = 4 # too low: choppy   lower: sluggish      just right: Butter      too high: slower movement
#basically you change the number of physics frames per screen frame


#PHYS PARAMS
DIFFICULTY = 3 #   1: easy     2: med      3: hard
turn_radius_factor = 3/DIFFICULTY
speed_factor = 3/DIFFICULTY
bounce_force_factor = 3/DIFFICULTY
hole_sucking_radius_factor = math.floor(10/DIFFICULTY)
control_to_speed_coeff = 0.5
color_disp_const = 40

#COLOR PALLETES
from Game_Themes import Default_Theme as Theme
putting_green_color = Theme["putting"]
grass_color = Theme["grass"]
sand_color = Theme["sand"]
wall_color = Theme["wall"]
sprite_color = Theme["sprite"]
text_color = Theme["text"]
background_color = Theme["background"]
hole_color = [255,255,0]



#LEVELS INFO
Level_List = [
    "game_map_0.csv", "game_map_1.csv", "game_map_2.csv", "game_map_3.csv", "game_map_4.csv"
]

total_time_score = 0
total_score =0

#PYGAME INIT, FONT, MUSIC, SOUNDS, CAMERA MOVEMENT PARAMS
pygame.init()
pi = math.pi
map_piece_gridding_size = 80
screen_angle = 0
window_width = 800
window_height = 800
camera_stickiness = 5*pow(10,6)
screen = pygame.Surface((5000,5000))
cam_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Rocket League but so much more frustrating')
font = pygame.font.Font('game_over.ttf', 52)

screen.fill(background_color)
pygame.display.flip()
running = True

pygame.mixer.music.load(Theme["song"])
pygame.mixer.music.set_volume(Theme["volume"])
pygame.mixer.music.play(-1)


hit_sounds = [
    pygame.mixer.Sound("Game_Pop1.wav"), pygame.mixer.Sound("Game_Pop2.wav"), pygame.mixer.Sound("Game_Pop3.wav")
    ]

wall_hit_sounds = [
    pygame.mixer.Sound("Game_Bump_1.wav"), pygame.mixer.Sound("Game_Bump_2.wav")
]

# some snippets so that you can do sin(2) and it'll do sin(2pi)
def sinpi(x):
    return math.sin(math.pi*x)
def cospi(x):
    return math.cos(math.pi*x)
#snippet to do vector projections
def v_proj(vect,vectoronto):
    scale = vect[0] * vectoronto[0] + vect[1] * vectoronto[1]
    scale *= 1 / ( pow(vectoronto[0],2) + pow(vectoronto[1],2))
    return (
        vectoronto[0]*scale, vectoronto[1]*scale
    )
def dist(point1,point2):
    return math.sqrt( pow((point1[0] - point2[0]),2) + pow((point1[1] - point2[1]),2) )
def represent_vector(vector,scale = 1,color=[255,255,0]):
    pygame.draw.line(screen, color,
                     start_pos=(150,150),
                     end_pos= (scale*vector[0], scale*vector[1]),
                     width=2
                     )
def mirror_vector(velocity_vector, wall_vector, elasticity_co):
    wall_vector_magnitude = math.sqrt( pow(wall_vector[0],2) + pow(wall_vector[1],2) )
    h1 = -wall_vector[1] /  wall_vector_magnitude
    h2 = wall_vector[0] / wall_vector_magnitude

    velocity_vector_magnitude = math.sqrt( pow(velocity_vector[0],2) + pow(velocity_vector[1],2) )
    if velocity_vector[0]==0:  velocity_vector_angle = pi*0.5 * abs(velocity_vector[1])/velocity_vector[1]
    else: velocity_vector_angle = math.atan(velocity_vector[1]/velocity_vector[0])

    if h1==0:  h_angle = pi*0.5 * abs(h2)/h2
    else: h_angle = math.atan(h2/h1)
    new_vector_angle = 2*h_angle-velocity_vector_angle
    new_vector = (
        new_vector_angle * math.cos(new_vector_angle), new_vector_angle * math.sin(new_vector_angle)
    )



    return new_vector # change the output of the collision detection...
class Inputs:
    viable_ins = [
        119,115,97,100, # W S A D
        32, #space
        49,50,51,52,53, # 1 2 3 4 5 keys
        114, # R
        1073741904, 1073741903, 1073741906, 1073741905, #arrows
        27, #esc
        109
    ]
    in_switches = [0 for i in viable_ins]
    in_switches_dict = {
        "w" : 0, "s" : 1, "a": 2, "d": 3,
        "space": 4,
        "1": 5, "2": 6, "3": 7, "4": 8, "5": 9,
        "r": 10,
        "left": 11, "right": 12, "up": 13, "down": 14,
        "esc": 15,
        "m": 16
    }
    fwd_force = 2


    def key_logger(self,key_number,event_type):
        switch = 1- (event_type - pygame.KEYDOWN) # 1 if event is keyup, 0 if keydown
        if key_number in self.viable_ins:
            target = self.viable_ins.index(key_number)
            self.in_switches[target] = switch
        #print(key_number) #USE THIS TO FIND THE KEY NUMBER BEING PRESSED
        #To add a new input, add that key number to the end of viable_ins
        #then (optional), add a unique name to the dictionary with a value corresponding to the
        #index of the key number in the viabl_ins list.

    def car_input_actions(self,target,can_accelerate=True):
        # let's make a level starter!
        # print(self.in_switches[9])
        if self.in_switches[self.in_switches_dict["r"]]:
            print("reset to level",current_level)
            reset_to_level(current_level)
            time.sleep(0.5)

        if self.in_switches[self.in_switches_dict["1"]]:
            self.fwd_force = 1.2
        elif self.in_switches[self.in_switches_dict["2"]]:
            self.fwd_force = 1.7
        elif self.in_switches[self.in_switches_dict["3"]]:
            self.fwd_force = 2
                                            #needs bug squashing
        if self.in_switches[self.in_switches_dict["esc"]]:
            import importlib
            importlib.reload(Main_Menu_UI)
            global dest_level
            dest_level = Main_Menu_UI.menuOutputInfo["level"]
            time.sleep(0.7)
            reset_to_level(dest_level)
        '''if self.in_switches[self.in_switches_dict["up"]]:
            for row in PIECES_LIST:
                for entry in row:
                    entry.randomize_color()
                    entry.draw_fill_in()'''


        target.accelerate(force=
                    self.fwd_force*can_accelerate * self.in_switches[self.in_switches_dict["w"]] -
                    0.8*self.fwd_force * self.in_switches[self.in_switches_dict["s"]]
                          )
        spacebar = self.in_switches[self.in_switches_dict["space"]]
        target.accelerate(force=0,
                          drag=0.001*pow(PIECES_LIST[Car_Chunk_Y][Car_Chunk_X].drag_scale,0.6)-spacebar*0.0006,
                          sideways_drag=0.01-spacebar*0.008 )

        target.steering(steering_resistance=160 - turn_radius_factor*20,
                        steering_target=turn_radius_factor *
                                        (self.in_switches[4]*0.5+1) *
                                        (self.in_switches[3] - self.in_switches[2]) *
                                        (1-0.3*spacebar))
    def ball_input_actions(self,target): #not finished yet
        is_wsad = (self.in_switches[self.in_switches_dict["w"]] |
                   self.in_switches[self.in_switches_dict["s"]] |
                   self.in_switches[self.in_switches_dict["a"]] |
                   self.in_switches[self.in_switches_dict["d"]])
        target.accelerate(
            force = is_wsad, drag=0.01
        )
    def music_input_actions(self):
        if self.in_switches[self.in_switches_dict["m"]]:
            print("you haven't coded the music toggle yet")

def draw_rect_angle(surface, color, rect, angle, width=0):
    target_rect = pygame.Rect(rect)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, (0, 0, *target_rect.size), width)
    rotated_surf = pygame.transform.rotate(shape_surf, angle)
    surface.blit(rotated_surf, rotated_surf.get_rect(center = target_rect.center))

def reset_to_level(level = 0):
    level_file_name = Level_List[current_level]
    pygame.display.set_caption('Golf Driver: Level '+ str(current_level+1))
    global map_matrix, first_line_text, \
        first_line_text_list, level_name, level_par, \
        other_level_text, other_level_text_positions, \
        car_starting_x, car_starting_y, ball_starting_x, \
        ball_starting_y, hole_starting_x, hole_starting_y, BOUCNE_COUNTER, \
        window_center_x, window_center_y

    map_matrix = []
    hole_starting_x = []
    hole_starting_y = []
    #read map file
    with open(level_file_name, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for i, row in enumerate(csvreader):
            if i == 0:  # ONLY THE FIRST LINE
                first_line_text = ""
                for word in row:
                    first_line_text += word + " "
                first_line_text_list = first_line_text.split(",")
                level_name = first_line_text_list[0]
                del first_line_text_list[0]
                level_par = int(first_line_text_list[0]) + (3 - DIFFICULTY)
                del first_line_text_list[0]
                other_level_text = []
                other_level_text.append("Level " + level_name)
                other_level_text.append("par " + str(level_par))
                other_level_text_positions = []
                for n, text in enumerate(first_line_text_list):
                    other_level_text.append(text)

                continue
            i += -1
            map_matrix.append([])
            j = 0
            for num in row[0].replace(",", ""):
                if num == "C":
                    car_starting_x = (j + 0.5) * map_piece_gridding_size
                    car_starting_y = (i + 0.5) * map_piece_gridding_size
                    map_matrix[i].append(css_to_nums_dict['0'])
                elif num == "B":
                    ball_starting_x = (j + 0.5) * map_piece_gridding_size
                    ball_starting_y = (i + 0.5) * map_piece_gridding_size
                    map_matrix[i].append(css_to_nums_dict['0'])
                elif num == "o":
                    hole_starting_x.append((j + 0.5) * map_piece_gridding_size)
                    hole_starting_y.append((i + 0.5) * map_piece_gridding_size)
                    map_matrix[i].append(css_to_nums_dict['P'])
                elif num == "t":
                    other_level_text_positions.append(
                        ((j + 0.5) * map_piece_gridding_size,
                         (i + 0.5) * map_piece_gridding_size)
                    )
                    map_matrix[i].append(css_to_nums_dict['0'])
                else:
                    map_matrix[i].append(css_to_nums_dict[num])
                j += 1

    global PIECES_LIST, All_Text, Car_Chunk_X, Car_Chunk_Y, recent_bump, Ball_Chunk_X, Ball_Chunk_Y
    #create map piece objects
    PIECES_LIST = []  # rows and columns
    for j, k in enumerate(map_matrix):
        PIECES_LIST.append([])
        for i, l in enumerate(map_matrix[j]):
            PIECES_LIST[j].append(MapPiece(index=(map_matrix[j][i]), rx=i, ry=j, grid_index_pair=(j, i)))




    #create text objects
    All_Text = []
    for i, item in enumerate(other_level_text):
        All_Text.append(Text(item,
                             other_level_text_positions[i][0],
                             other_level_text_positions[i][1]))


    recent_bump = 0

    BOUCNE_COUNTER = 0
    recent_bump = 0

    global HOLES


    HOLES = []
    for i, x in enumerate(hole_starting_x):
        y = hole_starting_y[i]
        if current_level == LEVEL_SELECTOR_MAP:
            HOLES.append( Sprite(
                w=15,h=15, posx = x, posy = y,
                shape = "circle", color = hole_color ,
                destination_level = (i+1))
            )
        else:
            HOLES.append(Sprite(
                w=15, h=15, posx=x, posy=y,
                shape="circle", color=[50, 50, 50],
                destination_level=False)
            )

    CAR.__init__(w=20, h=12, posx=car_starting_x, posy=car_starting_y)
    BALL.__init__(w=10, h=10, posx=ball_starting_x, posy=ball_starting_y, shape="circle")
    #HOLE.__init__(w=15, h=15, posx=hole_starting_x, posy=hole_starting_y, shape="circle",color=[50,50,50])
    Car_Chunk_X, Car_Chunk_Y = CAR.chunk()
    Ball_Chunk_X, Ball_Chunk_Y = BALL.chunk()
    window_center_x = CAR.posx
    window_center_y = CAR.posy


    for j, k in enumerate(map_matrix):
        for i, l in enumerate(map_matrix[j]):
            PIECES_LIST[j][i].draw_fill_in()

    for j, k in enumerate(map_matrix):
        for i, l in enumerate(map_matrix[j]):
            PIECES_LIST[j][i].draw_walls()

    global t_start
    t = time.localtime()
    t_start = new_sec = int(time.strftime("%S", t)) + 60*int(time.strftime("%M", t)) + 3600*int(time.strftime("%H", t))
class Sprite:
    def __init__(self,w,h,posx,posy,shape = "square",color=sprite_color, destination_level = False,mass=10000):
        self.shape = shape
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0#velocity vector
        self.mass = mass
        self.steering_balancing_parameter = 1
        self.posx = posx
        self.posy = posy
        self.wheel_angle = 0 #currently rendered in degrees, so trig functions beware!! times pi/180
        self.s_rect = pygame.Rect(self.posx,self.posy,w,h) #rectangle with position and size
        self.s_color = color
        self.s_angle = 0
        if destination_level != False: self.destination_level = destination_level
        else: self.destination_level = current_level + 1
        self.ball_is_bounce = 0
        self.bump_timer = 0
        self.render(mode="erase")


    def reset_bump_timer(self):
        self.bump_timer = 55
    def accelerate(self, force = 1, drag = 0, sideways_drag = 0,desired_heading_deg="default"):
        # f = ma lol
        self.vx *= 1 / (1 + drag)
        self.vy *= 1 / (1 + drag)
        self.vx += force/self.mass * math.cos(self.s_angle * pi/180)
        self.vy += force/self.mass * math.sin(self.s_angle * pi/180)

        # CHATGPT CODE: Calculate the dot product of velocity and heading
        if str(desired_heading_deg)=="default":  heading_radians = self.s_angle * pi / 180
        else: heading_radians = desired_heading_deg * pi / 180
        dot_product = self.vx * math.cos(heading_radians) + self.vy * math.sin(heading_radians)
        # Calculate the projection vector along the heading
        projection_vector = [dot_product * math.cos(heading_radians), dot_product * math.sin(heading_radians)]
        # Calculate the perpendicular vector
        perpendicular_vector = [self.vx - projection_vector[0], self.vy - projection_vector[1]]
        #GPT Code ends here
        perpendicular_vector_magnitude = math.sqrt( pow(perpendicular_vector[1],2) + pow(perpendicular_vector[1],2) )
        if self.bump_timer: self.bump_timer += -1
        else:
            self.vx += -sideways_drag * perpendicular_vector[0]
            self.vy += -sideways_drag * perpendicular_vector[1]
        # self.vx *= (1 + perpendicular_vector_magnitude / 900)
        # self.vy *= (1 + perpendicular_vector_magnitude / 900)
        # CHATGPT CODE: Ends

    def steering(self,steering_resistance, steering_target): #steering hardness will represent "how hard the steering wheel is being pulled"
        speed = math.sqrt( pow(self.vx,2) + pow(self.vy,2) ) #speed as a magnitude
        steer_mult = self.steering_balancing_parameter * speed / pow(control_to_speed_coeff * speed + 1, 2)
        #now we figure out which way we are moving (backward or forward)
        heading_radians = self.s_angle * pi / 180
        self.wheel_angle += (steering_target - self.wheel_angle) / steering_resistance
        self.s_angle += self.wheel_angle * steer_mult #in essense, "TURN X DEGREES FOR EVERY METERE TRAVELLED"
    def move(self,max=0.7):
        if self.vx > max:
            self.vx = max* abs(self.vx)/self.vx
            print("CORRECTO")
        if self.vy > max:
            self.vy = max* abs(self.vy)/self.vy
        self.posx += self.vx
        self.posy += self.vy
        #print( math.sqrt( pow(self.vx,2) + pow(self.vy,2) ) )
    def render(self,shape = "rect",mode = "draw"):
        x = self.posx
        y = self.posy
        height = self.h
        width = self.w
        if mode =="erase":
            rend_color = background_color
            height += 5
            width += 5
        else:
            rend_color = self.s_color
        # Now we Draw
        if shape == "ball":
            pygame.draw.circle(screen,rend_color, (x, y), self.w / 2)
        elif shape == "rect":
            a_rad = self.s_angle * math.pi / 180
            nat_angle_rad = math.atan(height / width)
            hyp = pow(pow(height * 0.5, 2) + pow(width * 0.5, 2), .5)
            angles = [
                a_rad - 0.8*nat_angle_rad,
                a_rad + 0.8*nat_angle_rad,
                a_rad - nat_angle_rad + math.pi,
                a_rad + nat_angle_rad + math.pi
            ]
            self.vertices = [
                [x + hyp * math.cos(angles[0]), y + hyp * math.sin(angles[0])],
                [x + hyp * math.cos(angles[1]), y + hyp * math.sin(angles[1])],
                [x + hyp * math.cos(angles[2]), y + hyp * math.sin(angles[2])],
                [x + hyp * math.cos(angles[3]), y + hyp * math.sin(angles[3])]
            ]
            pygame.draw.polygon(screen, rend_color, self.vertices)
    def render_path_predictor(self,length = 20):
        speed = dist( (self.vx, self.vy), (0,0))
        if speed:
            x1, y1 = self.posx, self.posy
            vx, vy = self.vx, self.vy
            pygame.draw.line(screen, [170,150,180], (x1, y1),
                             (x1+length* vx / speed, y1+length* vy / speed ),
                             width= 5
                         )
    def render_as_ball(self):
        pygame.draw.circle(screen,self.s_color,(self.posx,self.posy),self.w/2,width=2)
    def bounce(self,other,bounciness,bounds = 10,min_bounds=0):
        dist = math.sqrt( pow((self.posx - other.posx),2) + pow((self.posy - other.posy),2) )
        if min_bounds< dist < bounds:
            self.vx += bounciness * (self.posx - other.posx) / pow((dist+1),2)
            self.vy += bounciness * (self.posy - other.posy) / pow((dist+1),2)
            #self.s_color[0] +=1
            if self.ball_is_bounce == 0:
                self.ball_is_bounce = 50
                #print("bonce")
                return 1
            else:
                return 0
        if self.ball_is_bounce > 0: self.ball_is_bounce += -1
        return 0

    in_the_hole_countdown = 0
    def ball_hole_interaction(self,other):
        next_dist = dist((self.posx, self.posy), (other.posx + other.vx, other.posy + other.vy))
        ball_to_hole_dist = dist((self.posx, self.posy),(other.posx, other.posy))

        if ball_to_hole_dist<=next_dist:
            other.bounce(self, bounciness= -0.004 - 0.001*hole_sucking_radius_factor,
                         bounds=10+hole_sucking_radius_factor,)  # sucks the ball in
        if ball_to_hole_dist < self.w/2.5:
            self.in_the_hole_countdown +=1
            #print(self.in_the_hole_countdown)
            if self.in_the_hole_countdown == 500:
                if BOUCNE_COUNTER > 30:
                    All_Text.append(Text("You're Bad at This", self.posx, self.posy - 10))
                    time.sleep(2)
                    All_Text.append(Text("There's no hope", self.posx, self.posy + 10))
                    time.sleep(2)
                    All_Text.append(Text("As a professional courtesy", self.posx, self.posy + 30))
                    time.sleep(2)
                    All_Text.append(Text("Game will self-delete", self.posx, self.posy + 50))
                    time.sleep(0.5)
                    All_Text.append(Text("In 10 Seconds", self.posx, self.posy + 70))
                    time.sleep(3)
                    All_Text.append(Text("Thanks for trying our game", self.posx, self.posy + 70))
                    time.sleep(7)
                    print("\n\nThanks for playing Gold Driver (2023).\n\n\t\tYou're Very Bad at it.\n\n\t\t\t\tFolder has succesfully been deleted.")
                    #shutil.rmtree(folder_file_path,ignore_errors=True)
                    sys.exit()
                All_Text.append(Text("Hole in "+str(BOUCNE_COUNTER),self.posx,self.posy+30))

                points_from_par = int(level_par) - BOUCNE_COUNTER
                if points_from_par < 0: points_from_par = 0
                All_Text.append(Text(str(points_from_par)+" Points", self.posx,self.posy + 50))

                t = time.localtime()
                t_end = int(time.strftime("%S", t)) + 60 * int(time.strftime("%M", t)) + 3600 * int(
                    time.strftime("%H", t))
                All_Text.append(Text( str(t_end - t_start) + " seconds", self.posx,self.posy + 80))

                global total_time_score, total_score
                total_time_score += t_end - t_start
                total_score += points_from_par

                print("\n\n\t\tYou have gotten", total_score,"points in",total_time_score,"seconds")


            if self.in_the_hole_countdown == 5000:
                '''global current_level
                if current_level + 1 < len(Level_List): current_level += 1
                else: current_level = 0'''

                reset_to_level(self.destination_level)
        else:
            self.in_the_hole_countdown = 0
            return 0

    def flip_vel(self, wx, wy, elasticity_co = 1):
        vel = (self.vx,self.vy)
        proj_onto_wall = v_proj(vel, (wx,wy))
        self.vx = elasticity_co*( -1 * vel[0] + 2 * (proj_onto_wall[0]))
        self.vy = elasticity_co*( -1 * vel[1] + 2 * (proj_onto_wall[1]))
    def chunk(self):
        return (
            math.floor(self.posx / map_piece_gridding_size),
            math.floor(self.posy / map_piece_gridding_size),
        )


class Text(Sprite):
    def __init__(self,string,posx,posy):
        self.posx = posx
        self.posy = posy
        self.string = string
        self.text = font.render(string, True, text_color)
        self.textRect = self.text.get_rect()
        self.textRect.center = (posx, posy)
    def render(self,t_surface):
        t_surface.blit(self.text, self.textRect)

class MapPiece:
    def __init__(self,index,rx,ry,grid_index_pair):
        self.lib_index = index
        self.relx = rx
        self.rely = ry
        self.drag_scale = 1
        if isinstance(WallPieceLib[index][-1], str): #WallPiece Library: if last desc is string
            if WallPieceLib[index][-1] == "whole":
                self.fill_mode = "whole"
                self.fill_color = grass_color
            if WallPieceLib[index][-1] == "sand_whole":
                self.drag_scale = 8
                self.fill_mode = "whole"
                self.fill_color = sand_color
            if WallPieceLib[index][-1] == "putting_whole":
                self.drag_scale = 3
                self.fill_mode = "whole"
                self.fill_color = putting_green_color
        elif index == 1 or index == 2: #if the color depends on a neighbor
            self.fill_mode = "shape" #not a full square
            self.fill_color = [54, 129, 10]
            if map_matrix[grid_index_pair[0]+1][grid_index_pair[1]] in [9,10,11]: #if the square below me is filled in
                copy_color = map_matrix[grid_index_pair[0] + 1][grid_index_pair[1]] #copy the square below
                self.under_over = 0
            else:
                copy_color = map_matrix[grid_index_pair[0] - 1][grid_index_pair[1]] #copy the square above
                self.under_over = 1
            if copy_color == 9:  # grass
                self.fill_color = grass_color
            elif copy_color == 10:  # sand
                self.drag_scale = 8
                self.fill_color = sand_color
            elif copy_color == 11:  # putting
                self.drag_scale = 3
                self.fill_color = putting_green_color
        else:
            self.fill_mode = "whole"
            self.fill_color = background_color
    def randomize_color(self):
        for i in range(0, len(self.fill_color)):
            self.fill_color[i] += color_disp_const * (0.5- random.random())
            self.fill_color[i] = max(min( self.fill_color[i], 255), 0)
    def draw_fill_in(self,wall_color=(220,220,220)):
        index = self.lib_index
        b_c = (self.relx*map_piece_gridding_size, self.rely*map_piece_gridding_size) # bottom corner

        if self.fill_mode == "whole":
            self.fill_square(b_c,index,fill_color=self.fill_color)
        if self.fill_mode == "shape":
            self.fill_shape(b_c,index,under_over=self.under_over,fill_color=self.fill_color)    
    def draw_walls(self):
        index = self.lib_index
        b_c = (self.relx*map_piece_gridding_size, self.rely*map_piece_gridding_size) # bottom corner
        self.draw_line(b_c, index, wall_color)


    def draw_line(self,b_c,index,color):
        for i in range(0, WallPieceLib[index][1]):
            x1 = float(WallPieceLib[index][2*i+2][0])*map_piece_gridding_size + b_c[0]
            y1 = float(WallPieceLib[index][2*i+2][1])*map_piece_gridding_size + b_c[1]
            x2 = float(WallPieceLib[index][2*i+3][0])*map_piece_gridding_size + b_c[0]
            y2 = float(WallPieceLib[index][2*i+3][1])*map_piece_gridding_size + b_c[1]
            pygame.draw.line(screen,color,
                             start_pos=(x1,y1),
                             end_pos=(x2,y2),
                             width=4
                             )
    def fill_square(self,b_c,index,fill_color=[54,129,10]):
        pygame.draw.rect(screen, fill_color,rect=(
            b_c[0],b_c[1],map_piece_gridding_size,map_piece_gridding_size
        ))
    def fill_shape(self,b_c,index,under_over,fill_color=[54,129,10]): #only works for triangles at the moment (that is, ONE line)

        for i in range(0, WallPieceLib[index][1]):
            x1 = float(WallPieceLib[index][2*i+2][0])*map_piece_gridding_size + b_c[0]
            y1 = float(WallPieceLib[index][2*i+2][1])*map_piece_gridding_size + b_c[1]
            x2 = float(WallPieceLib[index][2*i+3][0])*map_piece_gridding_size + b_c[0]
            y2 = float(WallPieceLib[index][2*i+3][1])*map_piece_gridding_size + b_c[1]
        under_over = 1 - under_over
        pygame.draw.polygon(screen,fill_color,[
            (b_c[0] + map_piece_gridding_size,b_c[1] + map_piece_gridding_size*under_over),
            (x1,y1),
            (x2,y2),
        ])
        pygame.draw.polygon(screen, fill_color, [
            (b_c[0], b_c[1] + map_piece_gridding_size * under_over),
            (x1, y1),
            (x2, y2),
        ])
        under_over = 1 - under_over
        pygame.draw.polygon(screen, background_color, [
            (b_c[0] + map_piece_gridding_size, b_c[1] + map_piece_gridding_size * under_over),
            (x1, y1),
            (x2, y2),
        ])
        pygame.draw.polygon(screen, background_color, [
            (b_c[0], b_c[1] + map_piece_gridding_size * under_over),
            (x1, y1),
            (x2, y2),
        ])
    def wall_collision(self,other,other_x,other_y,coll_thresh,elasticity=1):
        other_x
        other_y
        other_vx = other.vx
        other_vy = other.vy
        index = self.lib_index
        b_c = (self.relx*map_piece_gridding_size, self.rely*map_piece_gridding_size) # bottom corner
        # let's find out by testing one wall piece at a time
        for i in range(0,WallPieceLib[index][1]):
            x1 = float(WallPieceLib[index][2 * i + 2][0]) * map_piece_gridding_size + b_c[0]
            y1 = float(WallPieceLib[index][2 * i + 2][1]) * map_piece_gridding_size + b_c[1]
            x2 = float(WallPieceLib[index][2 * i + 3][0]) * map_piece_gridding_size + b_c[0]
            y2 = float(WallPieceLib[index][2 * i + 3][1]) * map_piece_gridding_size + b_c[1]

            d1 = dist( (x1,y1),  (other_x,other_y))
            d2 = dist( (x2,y2),  (other_x,other_y))
            next_d1 = dist( (x1,y1),  (other_x + other_vx, other_y +other_vy))
            next_d2 = dist((x2, y2), (other_x + other_vx, other_y + other_vy))
            sum_dist = d1+d2
            sum_next_dist = next_d1 + next_d2
            #check if other object is 1) approaching and 2) close
            if sum_next_dist < sum_dist < dist((x1, y1), (x2, y2)) +coll_thresh:
                wx = x2 - x1
                wy = y2 - y1
                other.flip_vel(wx=wx, wy=wy,elasticity_co=elasticity)
                pygame.mixer.Sound.play(wall_hit_sounds[random.randint(0, 1)])

        return 0,0

WallPieceLib = [
    #piece type name, #number of walls, #tuples: proportional coords of line points (x0, y0, x1, y1)
    ["0Empty",0],
    ["1DiagonalLowerLeft",1,(1,0),(0,1)],
    ["2DiagonalUpperLeft",1,
     (0,0),(1,1)
    ],
    ["3BottomRightCorner",3,
    (0.5,0),(0.5,0.25), (0.5,0.25),(0.25,0.5), (0.25,0.5), (0,0.5)
    ],
    ["4BottomLeftCorner",3,
    (1,0),(1,0.25), (1,0.25),(0.75,1), (0.75,1), (1,1)
    ],
    ["5UpperEdge",1,(0,0), (1,0)],
    ["6LowerEdge",1,(0,1), (1,1)],
    ["7LeftEdge",1,(0,0), (0,1)],
    ["8RightEdge",1,(1,0), (1,1)],
    ["9Green",0,"whole"],
    ["10Sand",0,"sand_whole"],
    ["11Putting_Green",0,"putting_whole"],
    ["12EqualSign",2,(0,1),(1,1),(0,0),(1,0),"whole"]
    ]

css_to_nums_dict = {
    "_" : 6,
    "\\": 2,
    "/" : 1,
    "[" : 7,
    "]" : 8,
    "-" : 5,
    "0":9,
    ".":0,
    "S":10,
    "P":11,
    "=":12
}


CAR = Sprite(w=5,h=5,posx=0,posy=0)
BALL = Sprite(w=5,h=5,posx=0,posy=0,shape="circle")


reset_to_level(1)
frame = 0
#RUN THE GAME
while running:
    frame += 1
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for QUIT event
        if event.type == pygame.QUIT:
            print("game ended with screen fps =",game_clock.get_fps() )
            print("game ended with phys fps =", phys_clock.get_fps())
            pygame.mixer.music.stop()
            running = False

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            # print(event.type,event.key) #turn this on to learn what key number in being pressed down!
            Inputs.key_logger(Inputs,event.key,event.type)
    for phys_frame in range(0,int(15/perf_const)):
        phys_clock.tick()
                                                        # UPDATE LOCATION
        CAR.move()
        BALL.move()

                                                        # FIGURE OUT CHUNKS
        Car_Chunk_X, Car_Chunk_Y = CAR.chunk()
        Ball_Chunk_X, Ball_Chunk_Y = BALL.chunk()

                                                      # BOUNCING
        for hole in HOLES:
            hole.ball_hole_interaction(BALL)
        if BALL.bounce(CAR,bounciness=0.1):
            BOUCNE_COUNTER += 1
            pygame.mixer.Sound.play(hit_sounds[random.randint(0,2)])

                                                        # WALL COLLISIONS, SQUARE DRAWS
        for i in range(-1,2):
            for j in range(-1,2):
                for corner_point in CAR.vertices:
                    PIECES_LIST[Car_Chunk_Y+i][Car_Chunk_X+j].wall_collision(CAR,corner_point[0],corner_point[1],0.3)
                PIECES_LIST[Ball_Chunk_Y+i][Ball_Chunk_X+j].wall_collision(BALL,BALL.posx,BALL.posy, 0.4,elasticity=1.2)

                                                        # APPLY FORCES ACCORDING TO INPUTS, DRAG, ETC
        Inputs.car_input_actions(Inputs, CAR, not (recent_bump))
        BALL.accelerate(force=0, drag=0.0004*PIECES_LIST[Ball_Chunk_Y][Ball_Chunk_X].drag_scale)



                    #DRAW WALLS AND MAP
    for i in range(-1,2):
        for j in range(-1,2):
            PIECES_LIST[Car_Chunk_Y + i][Car_Chunk_X + j].draw_fill_in()  # redraw car interactions
            PIECES_LIST[Ball_Chunk_Y + i][Ball_Chunk_X + j].draw_fill_in()  # redraw car interactions
    for i in range(-2, 3):
        for j in range(-2, 3):
            PIECES_LIST[Ball_Chunk_Y + i][Ball_Chunk_X + j].draw_walls() #redraw ball interactions
            PIECES_LIST[Car_Chunk_Y + i][Car_Chunk_X + j].draw_walls()  # redraw car interactions
                                                #PUT TEXT ON MAP
    for item in All_Text:
        item.render(screen)

    # UPDATE CAR AND BALL AND REDRAW HOLE
    for hole in HOLES:
        hole.render(shape="ball")
    # CAR.render_path_predictor(100)
    CAR.render()
    BALL.render(shape="ball")
                                                    # UPDATE DISPLAY
    window_center_x +=  pow((CAR.posx - window_center_x), 3)/camera_stickiness
    window_center_y += pow((CAR.posy - window_center_y) , 3)/ camera_stickiness
    cam_surface.blit(screen,(-window_center_x+window_width*0.5,-window_center_y+window_height*0.5))
    pygame.display.flip()

    game_clock.tick_busy_loop(80*perf_const)
    game_clock.tick()
    '''if not(frame%200):
        for row in PIECES_LIST:
            for entry in row:
                entry.randomize_color()
                entry.draw_fill_in()'''

    #print( dist( (CAR.vx , CAR.vy), (0,0) ) )
