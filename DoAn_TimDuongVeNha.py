import sys
import pygame
import queue
import pygame_menu

pygame.init()
pygame. display. set_caption('Do An Nhom 14')
width, height = 750,450
screen = pygame.display.set_mode((width, height))

font = pygame.font.SysFont('Arial', 40)

objects =[]
level = 0
wall = pygame.image.load('images/wall.png')
way = pygame.image.load('images/way.png')
floor = pygame.image.load('images/floor.png')
worker = pygame.image.load('images/worker.png')
worker_docked = pygame.image.load('images/worker_dock.png')
docker = pygame.image.load('images/dock.png')

class LeoDoi:
    def __init__(self, map,H): # truyền map , truyền trọng số map
        self.map = map
        self.H=H
        
    def dinhKe(self, v):# tìm đỉnh lận cận của đỉnh truyền dô
        try:
            return self.map[v]
        except:
            return '';
    
    def LeoDoc_Dung(self, start, end):# từ start đến end
        open = [start] # chưa các đỉnh có thể xét
        close = set([]) # chứa các đỉnh đã xét

        parent = {}

        parent[start] = start # gắn đỉnh bắt đầu
        current = None # Khởi tạo
        while len(open) > 0: # current đỉnh hiện tại

            for v in open:
                if current == None or ( self.H[current] > self.H[v] ): # có đỉnh để xét thì chị vòng quay
                    current = v; # lấy trọng số nhỏ nhất 

            if current == None:# nếu đỉnh hiện tại ko có trả về null
                return None

            if current == end:# nếu đỉnh htai = đích đến tạo đường
                distance = []

                while parent[current] != current:
                    distance.append(current)
                    current = parent[current]

                distance.append(start)

                distance.reverse() # đảo mảng , trả về

                return distance


            for (i) in self.dinhKe(current):
                    if i not in open and i not in close: 
                        open.append(i)
                        parent[i] = current    
            if current in open:
                open.remove(current)
            close.add(current)

        return None

class Button():
    def __init__(self, x, y, width, height, buttonText='Button', id=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = buttonText
        self.id = id

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

        objects.append(self)
        
    def process(self):
        global level

        mousePos = pygame.mouse.get_pos()
        
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.id == -2:
                    display_levels(screen)
                
                else:
                    start_game(level)

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2])
        screen.blit(self.buttonSurface, self.buttonRect)
        
class Game:
    def __init__(self,filename,level):
        self.queue = queue.LifoQueue()
        self.matrix = []
        self.matrix.append([])
        self.matrix.append([])
        file = open(filename,'r')
        level_found = False
        for line in file:
            row = []
            if not level_found:
                x= "Level "+str(level)
                y =line.strip()
                if  "Level "+str(level) == line.strip():
                    level_found = True
            else:
                if line.strip() != "":
                    row = []
                    for c in line:
                        if c != '\n' and self.is_valid_value(c):
                            row.append(c)
                        elif c == '\n':
                            continue
                        else:
                            print("ERROR: Level "+str(level)+" has invalid value "+c)
                            sys.exit()
                    self.matrix.append(row)
                else:
                    break
    
    def is_valid_value(self,char):
        if (char == ' ' or #floor
            char == '~' or #way
            char == '#' or #wall
            char == '@' or #worker on floor
            char == '.' or #dock   
            char == '+' ): #worker on dock
            return True
        else:
            return False

    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self):
        return self.matrix

    def get_content(self,x,y):
        return self.matrix[y][x]

    def set_content(self,x,y,content):
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print("ERROR: Value '"+content+"' to be added is not valid")

    def worker(self):
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def can_move(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y) not in ['#']

    def next(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == '+':
                    return True
        return False

    def unmove(self):
        if not self.queue.empty():
            movement = self.queue.get()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def move(self,x,y,save):
        if self.can_move(x,y):
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
                if save: self.queue.put((x,y,False))
            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
                if save: self.queue.put((x,y,False))
            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
                if save: self.queue.put((x,y,False))
            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
                if save: self.queue.put((x,y,False))
        
def map_numbered(matrix):
    temp_map = []
    temp = 1

    for index in range(len(matrix)):
        row = []
        for cell in range(len(matrix[index])):
            row.append(matrix[index][cell])
        temp_map.append(row)
    
    for index in range(3,len(temp_map)-1):
        for cell in range(1,len(temp_map[index])):
            if temp_map[index][cell] == ' ':
                temp_map[index][cell] = temp
                temp+=1
    return temp_map

def getMap(matrix):
    map = {}
    temp_map = map_numbered(matrix)

    for i in range(3, len(temp_map)-1):
        for j in range(1, len(temp_map[i])-1):
            if temp_map[i][j] != '#':
                map[temp_map[i][j]] = []

                if temp_map[i][j-1] != '#':
                    map[temp_map[i][j]].append(temp_map[i][j-1])
                if temp_map[i][j+1] != '#':
                    map[temp_map[i][j]].append(temp_map[i][j+1])
                if temp_map[i-1][j] != '#':
                    map[temp_map[i][j]].append(temp_map[i-1][j])
                if temp_map[i+1][j] != '#':
                    map[temp_map[i][j]].append(temp_map[i+1][j])

    return map

def calculate_Start(h, row, column):
    if h[row+1][column] != '#' and h[row+1][column] != ' ' and h[row+1][column] != '~':
        if h[row+1][column] == '.':
            h[row][column] = 1
            return
        elif h[row][column] == '@' or h[row][column] > h[row+1][column]+1:
            h[row][column] = h[row+1][column]+1
            return

    if h[row-1][column] != '#' and h[row-1][column] != ' ' and h[row-1][column] != '~':
        if h[row-1][column] == '.':
            h[row][column] = 1
            return
        elif h[row][column] == '@' or h[row][column] > h[row-1][column]+1:
            h[row][column] = h[row-1][column]+1
            return


    if h[row][column+1] != '#' and h[row][column+1] != ' ' and h[row][column+1] != '~':
        if h[row][column+1] == '.':
            h[row][column] = 1
            return
        elif h[row][column] == '@' or h[row][column] > h[row][column+1]+1:
            h[row][column] = h[row][column+1]+1
            return

    if h[row][column-1] != '#' and h[row][column-1] != ' ' and h[row][column-1] != '~':
        if h[row][column-1] == '.':
            h[row][column-1] = 1
            return
        elif h[row][column] == '@' or h[row][column] > h[row][column-1]+1:
            h[row][column] = h[row][column-1]+1
        
            return
    
def calculate(h, start_row, start_column):
    # Tính điểm hàng chứa đích theo chiều trái -> phải từ đích
    for col in range(start_column+1, len(h[start_row])):
        if h[start_row][col] == '#' or h[start_row][col] == '.' or h[start_row][col] == '@' or h[start_row][col-1] == '#':
            break
        if h[start_row][col-1] == '.':
            h[start_row][col] = 1
        elif h[start_row][col] == ' ' or h[start_row][col] == '~' or h[start_row][col] > (h[start_row][col-1] + 1):
            h[start_row][col] = h[start_row][col-1] + 1

    # Tính điểm hàng chứa đích theo chiều phải -> trái từ đích
    col = start_column -1
    while col > 0:
        if h[start_row][col] == '#' or h[start_row][col] == '.' or h[start_row][col] == '@' or h[start_row][col+1] == '#':
            break
        if h[start_row][col+1] == '.':
            h[start_row][col] = 1
        elif h[start_row][col] == ' ' or h[start_row][col] == '~' or h[start_row][col] > (h[start_row][col+1] + 1):
            h[start_row][col] = h[start_row][col+1] + 1

        col -= 1
        
    # Tính điểm dọc lên và dọc xuống từng cell trong start_row
    # Duyệt Xuống
    row = start_row
    col = start_column
    while h[row+1][col] != '#' and h[row+1][col] != '.' and h[row+1][col] != '@':
            if h[row][col] == '#' or h[row][col] == ' ' or h[row][col] == '@' or h[row+1][col] == '@' or h[row][col] == '~':
                break
            if h[row][col] == '.':
                h[row+1][col] = 1
            elif h[row+1][col] == ' '  or h[row+1][col] == '~' or h[row+1][col] > h[row][col]+1:
                h[row+1][col] = h[row][col]+1
            
            row += 1


    row = start_row
    # Duyệt lên
    while h[row-1][col] != '#' and h[row-1][col] != '.' and row > 2:
        if h[row][col] == '#' or h[row][col] == ' ' or h[row][col] == '@' or h[row-1][col] == '@' or h[row][col] == '~':
            break
        if h[row][col] == '.':
            h[row-1][col] = 1
        elif h[row-1][col] == ' ' or h[row-1][col] == '~' or h[row-1][col] > h[row][col]+1:
            h[row-1][col] = h[row][col]+1

        row -= 1
    
    return h

def getH(matrix):
    h = []
    H = {}
    H['.'] = 0
    end_row = 0
    end_column = 0
    start_row = 0
    start_column = 0
    for index in range(len(matrix)):
        row = []
        for cell in range(len(matrix[index])):
            row.append(matrix[index][cell])
        h.append(row)

    for i in range(3,len(h)-1): 
        for j in range(1, len(h[i])-1):
            if h[i][j] == '.':
                end_row = i
                end_column = j
                break

    for i in range(3,len(h)-1): 
        for j in range(1, len(h[i])-1):
            if h[i][j] == '@':
                start_row = i
                start_column = j
                break
    
    # Tính điểm hàng chứa đích theo chiều trái -> phải từ đích
    for j in range(end_column+1, len(h[end_row])):
        if h[end_row][j] == '#' or h[end_row][j] == '@' or h[end_row][j] == '.':
            break
        if h[end_row][j-1] == '.':
            h[end_row][j] = 1
        elif h[end_row][j] == ' ' or h[end_row][j] == '~' or h[end_row][j] > (h[end_row][j-1] + 1):
            h[end_row][j] = h[end_row][j-1] + 1

    # Tính điểm hàng chứa đích theo chiều phải -> trái từ đích
    col = end_column -1
    while col > 0:
        if h[end_row][col] == '#' or h[end_row][col] == '@' or h[end_row][col] == '.':
            break
        if h[end_row][col+1] == '.':
            h[end_row][col] = 1
        elif h[end_row][col] == ' ' or h[end_row][col] == '~' or h[end_row][col] > (h[end_row][col+1] + 1):
            h[end_row][col] = h[end_row][col+1] + 1

        col -= 1
        
    # Tính điểm dọc lên và dọc xuống từng cell trong end_row
    row = end_row
    for cell in range(1,len(h[end_row])):
        # Duyệt xuống
        a = h[row+1][cell]
        while h[row+1][cell] != '#' and h[row+1][cell] != '.':
            if h[row][cell] == '#' or h[row][cell] == ' ' or h[row][cell] == '@' or h[row][cell] == '~':
                break
            if h[row][cell] == '.':
                h[row+1][cell] = 1
            elif h[row+1][cell] == ' ' or h[row+1][cell] == '~':
                h[row+1][cell] = h[row][cell]+1
            elif h[row+1][cell] != '@' and h[row+1][cell] > h[row][cell]+1:
                h[row+1][cell] = h[row][cell]+1
            row += 1
        
        # Duyệt lên 
        row = end_row
        b =h[row-1][cell]
        while h[row-1][cell] != '#' and h[row-1][cell] != '.':
            if h[row][cell] == '#' or h[row][cell] == ' ' or h[row][cell] == '@' or h[row][cell] == '~':
                break
            if h[row][cell] == '.':
                h[row-1][cell] = 1
            elif h[row-1][cell] == ' ' or h[row-1][cell] == '~':
                h[row-1][cell] = h[row][cell]+1
            elif h[row-1][cell] != '@' and h[row-1][cell] > h[row][cell]+1:
                h[row-1][cell] = h[row][cell]+1
            row -= 1
    
    # Tính điểm từng hàng lấy tâm là hàng đích đích
    flag = True
    while flag:
        for r in range(3,len(h)-2):
            for c in h[r]:
                if c == ' ':
                    flag = False
                    break
        if flag:
            break

        row = end_row - 1
        while row > 2:
            for col in range(len(h[row])):
                if h[row][col] != ' ' and h[row][col] != '~' and h[row][col] != '#' and h[row][col] != '.' and h[row][col] != '@':
                      h = calculate(h,row,col)
            row -= 1

        for row in range(end_row, len(h)-1):
           for col in range(len(h[row])):
                if h[row][col] != ' ' and h[row][col] != '~' and h[row][col] != '#' and h[row][col] != '.' and h[row][col] != '@':
                      h = calculate(h,row,col)
        
        calculate_Start(h,start_row, start_column)
        flag = True


    map_num = map_numbered(matrix)
    
    for i in range(3, len(h)):
        for j in range(1, len(h[i])):
            if h[i][j] != '#' and h[i][j] != '.':
                H[map_num[i][j]] = h[i][j] 
    return H

def support(matrix):
    map = getMap(matrix)
    H = getH(matrix)
    dt = LeoDoi(map,H)
    distance =  dt.LeoDoc_Dung('@', '.')
    matrix = map_numbered(matrix)
    for index in range(3,len(matrix)):
        for cell in range(1,len(matrix[index])):
            if matrix[index][cell] == '#' or matrix[index][cell] == '@' or matrix[index][cell] == '.':
                continue

            if matrix[index][cell] not in distance:
                matrix[index][cell] = ' '
            else:
                matrix[index][cell] = '~'

    return matrix
    
def button_support(action=None, values=None):
    global screen
    screen.blit(font.render("Click on the screen to be supported", 1, (255,255,255)), (0,0))
    click = pygame.mouse.get_pressed()
    if click[0] == True and action != None:
        matrix = action(values)
        return matrix

def print_game(matrix):
    global screen
    sp = button_support(support,matrix)
    if sp != None:
        matrix = sp
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == ' ': #floor
                screen.blit(floor,(x,y))
            elif char == '#': #wall
                screen.blit(wall,(x,y))
            elif char == '~': #way
                screen.blit(way,(x,y))
            elif char == '@': #worker on floor
                screen.blit(worker,(x,y))
            elif char == '.': #dock
                screen.blit(docker,(x,y))
            elif char == '+': #worker on dock
                screen.blit(worker_docked,(x,y))
            x = x + 32
        x = 0
        y = y + 32

def setLevel(id):
    global level
    level = id
    start_game(level)

def display_levels(screen):
    menu = pygame_menu.Menu('Level', width, height,
                       theme=pygame_menu.themes.THEME_BLUE,
                       center_content=True,
                       columns=2,
                       rows=5)
    

    menu.add.button('Level 1', setLevel,1)
    menu.add.button('Level 2', setLevel,2)
    menu.add.button('Level 3', setLevel,3)
    menu.add.button('Level 4', setLevel,4)
    menu.add.button('Level 5', setLevel,5)
    menu.add.button('Level 6', setLevel,6)
    menu.add.button('Level 7', setLevel,7)
    menu.add.button('Level 8', setLevel,8)
    menu.add.button('Level 9', setLevel,9)
    menu.add.button('Level 10', setLevel,10)
    menu.mainloop(screen)
    
def display_end(screen):
    global level
    level_cu = level
    level = level +1
    screen = pygame.display.set_mode((width, height))
    
    screen.fill((0, 0, 0))
    
    if level<10:
        screen.blit(font.render("Hoan Thanh Level "+str(level_cu), 1, (255,255,255)),
                ((screen.get_width() / 2)-150, 50))
        Button(100, 200, 150, 100, 'Quay Lai',-2)
        Button(450, 200, 250, 100, 'Man Tiep Theo',0)
    else:
        screen.blit(font.render("END", 1, (255,255,255)),
                ((screen.get_width() / 2)-30, 50))
        Button(300, 200, 150, 100, 'Quay Lai',-2)
    pygame.display.flip()
    pygame.display.update()
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        if(level-1!=level_cu):
            break
        for object in objects:
            object.process()

        pygame.display.flip()

def start_game(level):
    global screen
    
    game = Game('Levels.txt',level)
    size = game.load_size()
    screen = pygame.display.set_mode(size)
    while 1:
        if game.is_completed(): 
            display_end(screen)
        print_game(game.get_matrix())
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: game.move(0,-1, True)
                elif event.key == pygame.K_DOWN: game.move(0,1, True)
                elif event.key == pygame.K_LEFT: game.move(-1,0, True)
                elif event.key == pygame.K_RIGHT: game.move(1,0, True)
                elif event.key == pygame.K_q: sys.exit(0)
                elif event.key == pygame.K_d: game.unmove()
        pygame.display.update()

menu = pygame_menu.Menu('Nhóm 14', 600, 300,
                       theme=pygame_menu.themes.THEME_BLUE)

menu.add.label('Tìm đường về nhà')
menu.add.button('Play', display_levels,screen)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(screen)