#!/usr/bin/env python
# Define the background colour
# using RGB color coding.
import pygame
import math
import random
import csv

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
    ]

css_to_nums_dict = {
    "_" : 6,
    "\\": 2,
    "/" : 1,
    "[" : 7,
    "]" : 8,
    "-" : 5,
    "0":0,
    ".":0
}


map_matrix = []
#here is where we read the input CSV file for the map
with open('game_map_1.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for i,row in enumerate(spamreader):
        map_matrix.append([])
        for num in row[0].replace(",",""):
            map_matrix[i].append(css_to_nums_dict[num])




pygame.init()
pi = math.pi
map_piece_gridding_size = 70
background_colour = (40,40,40)
screen = pygame.display.set_mode((1200, 1200))
pygame.display.set_caption('SEE THE MAP')

# some snippets so that you can do sin(2) and it'll do sin(2pi)
def sinpi(x):
    return math.sin(math.pi*x)
def cospi(x):
    return math.cos(math.pi*x)

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
        49,50,51,52,53 # 1 2 3 4 5 keys
    ]
    in_switches = [
        0,0,0,0,
        0,
        0,0,0,0,0
    ]
    fwd_force = 1
    def key_logger(self,key_number,event_type):
        switch = 1- (event_type - pygame.KEYDOWN) # 1 if event is keyup, 0 if keydown
        if key_number in self.viable_ins:
            target = self.viable_ins.index(key_number)
            self.in_switches[target] = switch
        #print(self.viable_ins,self.in_switches)
    def input_actions(self,target,can_accelerate=True):
        if self.in_switches[5]:
            self.fwd_force = 1
        elif self.in_switches[6]:
            self.fwd_force = 3
        elif self.in_switches[7]:
            self.fwd_force = 5


        if self.in_switches[0] == 1: #forward thrust
            target.accelerate(force=self.fwd_force*can_accelerate)
        elif self.in_switches[1] == 1: #backward thrust
            target.accelerate(force= -2*can_accelerate)

        target.accelerate(force=0,drag=0.001,sideways_drag=0.01-self.in_switches[4]*0.002)

        target.steering(steering_resistance=100, steering_target=2*(self.in_switches[4]*0.5+1)*(self.in_switches[3] - self.in_switches[2]))

def draw_rect_angle(surface, color, rect, angle, width=0):
    target_rect = pygame.Rect(rect)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, (0, 0, *target_rect.size), width)
    rotated_surf = pygame.transform.rotate(shape_surf, angle)
    surface.blit(rotated_surf, rotated_surf.get_rect(center = target_rect.center))
class Sprite:
    shape = "square"
    w = 30
    h = 30
    vx = 0
    vy = 0#velocity vector
    mass = 10000
    posx = 40
    posy = 50
    wheel_angle = 0 #currently rendered in degrees, so trig functions beware!! times pi/180
    s_rect = pygame.Rect(posx,posy,w,h) #rectangle with position and size
    s_color = [230,230,230]
    s_angle = 0

    ball_is_bounce = 0

    bump_timer = 0
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
        #now we figure out which way we are moving (backward or forward)
        heading_radians = self.s_angle * pi / 180
        dot_product = self.vx * math.cos(heading_radians) + self.vy * math.sin(heading_radians)
        if dot_product < 0:
            speed*=-1
        self.wheel_angle += (steering_target - self.wheel_angle) / steering_resistance
        self.s_angle += self.wheel_angle * speed #in essense, "TURN X DEGREES FOR EVERY METERE TRAVELLED"
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
            rend_color = background_colour
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
            points = [
                [x + hyp * math.cos(angles[0]), y + hyp * math.sin(angles[0])],
                [x + hyp * math.cos(angles[1]), y + hyp * math.sin(angles[1])],
                [x + hyp * math.cos(angles[2]), y + hyp * math.sin(angles[2])],
                [x + hyp * math.cos(angles[3]), y + hyp * math.sin(angles[3])]
            ]
            pygame.draw.polygon(screen, rend_color, points)
    def render_as_ball(self):
        pygame.draw.circle(screen,self.s_color,(self.posx,self.posy),self.w/2,width=2)
    def bounce(self,other,bounciness,bounds = 10):
        dist = math.sqrt( pow((self.posx - other.posx),2) + pow((self.posy - other.posy),2) )
        if dist < bounds:
            self.vx += bounciness*(self.posx - other.posx)
            self.vy += bounciness * (self.posy - other.posy)
            #self.s_color[0] +=1
            if self.ball_is_bounce == 0:
                self.ball_is_bounce = 1
                return 1
            else:
                return 0
        self.ball_is_bounce = 0
        return 0
    def touching(self,other):
        dist = math.sqrt(pow((self.posx - other.posx), 2) + pow((self.posy - other.posy), 2))
        if dist < self.w and self.s_color != [0,255,0]:
            print("in!")
            self.s_color = [0,255,0]
            return 1
        else:
            self.bounce(other, -1,bounds=3000)
            return 0

    def flip_vel(self, wx, wy, elasticity_co = 1):
        vel = (self.vx,self.vy)
        proj_onto_wall = v_proj(vel, (wx,wy))
        self.vx = -1 * vel[0] + 2 * (proj_onto_wall[0])
        self.vy = -1 * vel[1] + 2 * (proj_onto_wall[1])
    def chunk(self):
        return (
            math.floor(self.posx / map_piece_gridding_size),
            math.floor(self.posy / map_piece_gridding_size),
        )



    '''def __init__(self,x,y,w,h,m,a):
        self.x = 20
        self.y = 20
        self.w = 20
        self.h = 30
        self.m = 0
        self.a = 0'''




'''map_matrix = [[1,5,5,5,5,2,6,0],
              [7,0,1,0,0,0,8,0],
              [7,3,0,0,0,0,1,0],
              [7,0,0,2,0,1,0,0],
              [2,6,6,6,1,0,0,0],
              [1,1,1,1,1,1,1,1,1],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]
              ]'''


class MapPiece:
    def __init__(self,index,rx,ry):
        self.lib_index = index
        self.relx = rx
        self.rely = ry
    def draw(self,color=(150,150,150)):
        index = self.lib_index
        b_c = (self.relx*map_piece_gridding_size, self.rely*map_piece_gridding_size) # bottom corner
        for i in range(0, WallPieceLib[index][1]):
            x1 = float(WallPieceLib[index][2*i+2][0])*map_piece_gridding_size + b_c[0]
            y1 = float(WallPieceLib[index][2*i+2][1])*map_piece_gridding_size + b_c[1]
            x2 = float(WallPieceLib[index][2*i+3][0])*map_piece_gridding_size + b_c[0]
            y2 = float(WallPieceLib[index][2*i+3][1])*map_piece_gridding_size + b_c[1]
            pygame.draw.line(screen,color,
                             start_pos=(x1,y1),
                             end_pos=(x2,y2),
                             width=2
                             )
    def wall_collision(self,other,coll_thresh):
        other_x = other.posx
        other_y = other.posy
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
                other.flip_vel(wx=wx, wy=wy)

        return 0,0

screen.fill(background_colour)
pygame.display.flip()
running = True

car_angle = 0

CAR = Sprite()
CAR.w = 20
CAR.h = 12

BALL = Sprite()
BALL.shape = "circle"
BALL.w = 10
BALL.h = 10
BALL.posx += 50
BALL.posy += 50

HOLE = Sprite()
HOLE.shape = "circle"
HOLE.w = 15
HOLE.h = 15
HOLE.posx += 100
HOLE.posy += 500

recent_bump = 0

# THIS STUFF PUTS SOME SHAPES ON THE GRID. THE SIZE OF EACH SHAPE IS DETERMINED AT THE TOP IN MAP GRIDDING SHAPE,
# THE WALL PIECE LIBRARY LIST DEFINES AVAILABLE SHAPES
print("\n\n\n\t\tLINES 239 thru 244 CREATE THE CRAPPY GRID THAT WE HAVE HERE\n\n")
PIECES_LIST = [] #rows and columns
for j,k in enumerate(map_matrix):
    PIECES_LIST.append([])
    for i,l in enumerate(map_matrix[j]):
        PIECES_LIST[j].append( MapPiece(index=(map_matrix[j][i]),rx=i,ry=j))
        PIECES_LIST[j][i].draw()


Car_Chunk_X, Car_Chunk_Y = CAR.chunk()
BOUCNE_COUNTER = 0
while running:
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for QUIT event      
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            # print(event.type,event.key) #turn this on to learn what key number in being pressed down!
            Inputs.key_logger(Inputs,event.key,event.type)


    #screen.fill(background_colour)

    for row in PIECES_LIST:
        for piece in row:
            piece.draw()

    pygame.display.flip()

        #CAR.reset_bump_timer()
    #if PIECES_LIST[Ball_Chunk_Y][Ball_Chunk_X].wall_collision(BALL,4)[0] != 0:
        # print("hit")
        # BALL.accelerate(force=0,drag=0,sideways_drag=1,desired_heading_deg= (PIECES_LIST[Ball_Chunk_Y][Ball_Chunk_X].wall_collision(CAR,10)[1])*180/pi)
        # BALL.flip_vel( PIECES_LIST[Ball_Chunk_Y][Ball_Chunk_X].wall_collision(BALL,4)[1] * 180 / pi + pi)