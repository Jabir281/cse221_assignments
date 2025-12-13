import pygame, random, math, sys                        # import pygame for graphics, random for randomness, math for math funcs, sys for exit
from collections import deque                            # import deque for efficient waypoint rotation/management

# ---------- Parameters ----------
WIDTH, HEIGHT = 900, 600                                # set window width and height in pixels
GRID_ROWS, GRID_COLS = 12, 18                           # number of rows and columns in the coverage grid
NUM_UAVS = 8                                            # number of UAV agents to spawn
NUM_VICTIMS = 12                                        # number of victims to randomly place
UAV_SPEED = 80.0                                        # movement speed of UAVs in pixels per second
SENSOR_RADIUS = 40                                      # radius in pixels within which UAV can detect a victim
DETECTION_PROB = 0.9                                    # probability of successful detection when in range
CELL_MARGIN = 2                                         # visual margin inside each grid cell for drawing
FPS = 60                                                # frames per second target for main loop

# ---------- NEW: Collision + communication parameters ----------
COMM_RANGE = 150                                        # communication range in pixels (UAVs share detections within this distance)
COLLISION_DIST = 20                                     # minimum distance to avoid collisions between UAVs
AVOID_STRENGTH = 1.0                                    # strength coefficient for avoidance heading adjustment

# ---------- NEW: Pheromone parameters ----------
PHEROMONE_DECAY = 0.995                                 # multiplicative decay factor applied to pheromone each frame
PHEROMONE_DEPOSIT = 5.0                                 # amount of pheromone deposited by UAV per step
STEER_ANGLE = math.radians(40)                          # angle offset used for sampling left/right pheromone (converted to radians)
SAMPLE_DIST = max(WIDTH/GRID_COLS, HEIGHT/GRID_ROWS) * 0.9  # distance at which UAV samples pheromone ahead (approx cell size)
ROTATION_SPEED = math.radians(120)                      # maximum rotation speed in radians per second
RANDOMNESS = 0.2                                        # amount of random noise added when sampling pheromone

# Colors
BG = (30, 30, 30)                                       # background color RGB
GRID_COLOR = (50, 50, 50)                               # grid line color RGB
UAV_COLOR = (50, 150, 240)                              # default UAV color RGB
UAV_FOUND_COLOR = (0, 220, 0)                           # UAV color when it has found victims RGB
RUBBLE_COLOR = (120, 110, 100)                          # color for undetected rubble (victim placeholder)
VICTIM_COLOR = (220, 40, 40)                            # color for detected victims
TEXT_COLOR = (230, 230, 230)                            # UI text color

pygame.init()                                           # initialize pygame modules
screen = pygame.display.set_mode((WIDTH, HEIGHT))       # create the display window with WIDTH x HEIGHT
clock = pygame.time.Clock()                             # create a clock to cap FPS and measure dt
font = pygame.font.SysFont(None, 22)                    # choose a system font for small UI text

# ---------- Derived ----------
cell_w = WIDTH / GRID_COLS                              # compute width of a grid cell in pixels
cell_h = HEIGHT / GRID_ROWS                             # compute height of a grid cell in pixels

# ---------- Victim class ----------
class Victim:                                          # define a simple Victim class
    def __init__(self, x, y):                          # constructor takes x,y position
        self.pos = (x, y)                              # store position as tuple
        self.detected = False                          # boolean flag whether victim is detected

# ---------- NEW: pheromone grid ----------
pheromone = [[0.0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]  # 2D list of pheromone values initialized to 0

# ---------- UAV class ----------
class UAV:                                             # define UAV agent class
    def __init__(self, uid, waypoints):                # constructor: unique id and list of waypoint positions
        self.id = uid                                   # store UAV id
        self.pos = list(waypoints[0])                   # set current position to the first waypoint (as a mutable list)
        self.waypoints = deque(waypoints)               # store waypoints as a deque for rotation/iteration
        self.speed = UAV_SPEED                          # travel speed in pixels/sec
        self.found_count = 0                            # number of victims this UAV directly found

        self.heading = random.uniform(0, 2 * math.pi)  # initial heading angle in radians chosen randomly

        # NEW: communication memory
        self.known_detections = set()                   # set of victim ids (id(v)) this UAV knows about

    # NEW
    def _cell_index(self, px, py):                      # helper to map pixel coordinates to grid indexes
        cx = int(px // cell_w)                          # compute column index by integer division
        cy = int(py // cell_h)                          # compute row index by integer division
        cx = max(0, min(GRID_COLS - 1, cx))             # clamp column index to valid range
        cy = max(0, min(GRID_ROWS - 1, cy))             # clamp row index to valid range
        return cy, cx                                   # return (row, column)

    # NEW
    def sample_pheromone(self, angle_offset):           # sample pheromone at a point ahead with angle offset
        ang = self.heading + angle_offset               # sampling angle = current heading + offset
        sx = self.pos[0] + math.cos(ang) * SAMPLE_DIST  # sample x coordinate at SAMPLE_DIST along ang
        sy = self.pos[1] + math.sin(ang) * SAMPLE_DIST  # sample y coordinate at SAMPLE_DIST along ang
        r, c = self._cell_index(sx, sy)                 # convert sample point to grid cell indices
        return pheromone[r][c], (r, c)                  # return pheromone value and the cell tuple

    # ---------- NEW: collision avoidance ----------
    def avoid_collision(self, uavs):                    # simple avoidance routine given list of other UAVs
        for other in uavs:                              # iterate all UAVs
            if other is self:                           # skip self
                continue
            dx = other.pos[0] - self.pos[0]             # delta x from self to other
            dy = other.pos[1] - self.pos[1]             # delta y from self to other
            dist = math.hypot(dx, dy)                   # Euclidean distance to other

            if dist < COLLISION_DIST and dist > 0:      # if within collision threshold and not exactly same pos
                angle_to_other = math.atan2(dy, dx)     # angle toward the other UAV
                away_angle = angle_to_other + math.pi  # opposite direction to move away
                self.heading += AVOID_STRENGTH * (away_angle - self.heading)  # nudge heading toward away_angle

    # ---------- Step ----------
    def step(self, dt):                                 # update function called every frame with dt seconds
        # ---- choose direction based on pheromone ----
        candidates = [(0.0,), (-STEER_ANGLE,), (STEER_ANGLE,)]  # candidate offsets: straight, left, right (as tuples)
        samples = []                                   # list to hold sampled pheromone values and offsets
        for (offset,) in candidates:                   # iterate candidate offsets
            pval, cell = self.sample_pheromone(offset) # sample pheromone at that offset
            pval += random.uniform(0, RANDOMNESS)     # add a small random noise to encourage exploration
            samples.append((pval, offset))             # store pheromone value and offset in samples

        samples.sort(key=lambda x: x[0])               # sort samples ascending by pheromone value
        chosen_offset = samples[0][1]                  # choose the offset with lowest pheromone (samples[0])

        target_heading = self.heading + chosen_offset  # desired heading is current heading plus chosen offset

        def normalize(a):                              # helper to normalize angle to (-pi, pi]
            while a <= -math.pi: a += 2*math.pi
            while a > math.pi: a -= 2*math.pi
            return a

        diff = normalize(target_heading - self.heading) # compute smallest angular difference to desired heading
        max_rot = ROTATION_SPEED * dt                   # maximum rotation allowed this frame
        if abs(diff) <= max_rot:                        # if needed rotation within limit
            self.heading = normalize(self.heading + diff)  # rotate directly to target
        else:
            self.heading = normalize(self.heading + math.copysign(max_rot, diff))  # rotate by max_rot toward target

        # ---------- NEW: avoid collisions before moving ----------
        self.avoid_collision(uavs_global)                # call avoidance using global UAV list

        # ---------- MOVE ----------
        dx = math.cos(self.heading) * self.speed * dt   # compute displacement x (cos * speed * time)
        dy = math.sin(self.heading) * self.speed * dt   # compute displacement y (sin * speed * time)
        self.pos[0] = (self.pos[0] + dx) % WIDTH        # update x position, wrap around screen horizontally
        self.pos[1] = (self.pos[1] + dy) % HEIGHT       # update y position, wrap around screen vertically

        # ---------- Deposit pheromone ----------
        r, c = self._cell_index(self.pos[0], self.pos[1])  # find cell under current position
        pheromone[r][c] += PHEROMONE_DEPOSIT            # add pheromone deposit to that grid cell

    # ---------- Detection ----------
    def scan_and_detect(self, victims):                 # check nearby victims and mark detected probabilistically
        for v in victims:                               # iterate all victims
            if v.detected:                              # skip if already detected globally
                continue
            vx, vy = v.pos                               # victim coordinates
            d = math.hypot(self.pos[0] - vx, self.pos[1] - vy)  # compute distance to victim
            if d <= SENSOR_RADIUS:                      # if within sensor radius
                if random.random() <= DETECTION_PROB:   # probabilistic detection test
                    v.detected = True                   # mark victim as detected
                    self.found_count += 1               # increment this UAV's personal found counter
                    # NEW:
                    self.known_detections.add(id(v))    # remember detection by storing unique id(v)

# ---------- Helpers ----------
def make_cell_centers(rows, cols):                     # generate center coordinates for each grid cell
    centers = []                                       # list to hold centers
    for r in range(rows):                              # iterate rows
        for c in range(cols):                          # iterate columns
            cx = c * cell_w + cell_w/2                 # compute center x of cell
            cy = r * cell_h + cell_h/2                 # compute center y of cell
            centers.append((cx, cy))                   # append tuple (center x, center y)
    return centers                                     # return list of centers

def assign_waypoints_to_uavs(centers, num_uavs):      # partition cell centers among UAVs as waypoint lists
    assignments = [[] for _ in range(num_uavs)]       # create empty list for each UAV
    for i, center in enumerate(centers):               # iterate each center with index
        assignments[i % num_uavs].append(center)      # assign center to UAV in round-robin fashion
    for i, a in enumerate(assignments):                # iterate assignments for optional path ordering
        if i % 2 == 1:                                 # for every second UAV (odd indices)
            a.reverse()                                # reverse its waypoint order (snake pattern)
    return assignments                                 # return list of waypoint-lists

# ---------- Setup ----------
centers = make_cell_centers(GRID_ROWS, GRID_COLS)     # compute list of grid cell centers
assignments = assign_waypoints_to_uavs(centers, NUM_UAVS)  # assign centers to UAVs
uavs = [UAV(i, assignments[i]) for i in range(NUM_UAVS)]  # create UAV objects, each with their waypoint list

# NEW
uavs_global = uavs                                    # create a global reference for avoidance calls

victims = []                                          # list to hold victim objects
padding = 20                                          # padding from screen edges when spawning victims
for _ in range(NUM_VICTIMS):                          # spawn NUM_VICTIMS victims
    x = random.uniform(padding, WIDTH - padding)      # random x within padded range
    y = random.uniform(padding, HEIGHT - padding)     # random y within padded range
    victims.append(Victim(x, y))                      # create Victim and add to list

covered_cells = set()                                 # set tracking which grid cell indices have been visited
total_cells = GRID_ROWS * GRID_COLS                   # total number of cells in grid
time_elapsed = 0.0                                    # simulation elapsed time counter

# ---------- Main Loop ----------
running = True                                        # flag to keep main loop running
while running:                                        # main loop
    dt = clock.tick(FPS) / 1000.0                     # tick the clock and get dt in seconds (ms -> s)
    time_elapsed += dt                                # accumulate elapsed time

    for event in pygame.event.get():                  # process all pygame events
        if event.type == pygame.QUIT:                 # if window close button pressed
            running = False                           # exit main loop
        if event.type == pygame.KEYDOWN:              # if any key is pressed
            if event.key == pygame.K_r:               # if the key is 'r'
                for v in victims:                     # iterate all victims
                    v.detected = False                # reset detected flag for each victim
                pheromone = [[0.0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]  # reset pheromone grid
                covered_cells.clear()                 # clear coverage tracking set

    # Step UAVs
    for u in uavs:                                    # update each UAV
        u.step(dt)                                    # call step() with dt to move and deposit pheromone

        grid_x = int(u.pos[0] // cell_w)              # compute grid column index under UAV
        grid_y = int(u.pos[1] // cell_h)              # compute grid row index under UAV
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:  # safety check indices in bounds
            covered_cells.add(grid_y * GRID_COLS + grid_x)     # add linear index to covered set

        u.scan_and_detect(victims)                    # let UAV scan for nearby victims

    # ---------- NEW: Communication ----------
    for u in uavs:                                    # for each UAV
        for other in uavs:                            # compare against each other UAV
            if u is other:                            # skip self
                continue
            dx = u.pos[0] - other.pos[0]              # dx from other to u
            dy = u.pos[1] - other.pos[1]              # dy from other to u
            dist = math.hypot(dx, dy)                 # distance between them

            if dist <= COMM_RANGE:                    # if within communication range
                for v in victims:                     # iterate victims
                    if id(v) in u.known_detections:   # if u knows about this victim
                        v.detected = True            # mark victim as detected globally
                        other.known_detections.add(id(v))  # let other UAV also remember this detection

    # Pheromone decay
    for r in range(GRID_ROWS):                        # for each grid row
        for c in range(GRID_COLS):                    # for each grid column
            pheromone[r][c] *= PHEROMONE_DECAY        # apply multiplicative decay to pheromone value
            if pheromone[r][c] < 1e-6:                # if very small value
                pheromone[r][c] = 0.0                 # clamp to zero to avoid tiny floats

    # ---------- Drawing ----------
    screen.fill(BG)                                   # fill the screen with background color

    # Grid
    for r in range(GRID_ROWS):                        # draw grid rows
        for c in range(GRID_COLS):                    # draw grid columns
            x = c * cell_w                            # top-left x of this cell
            y = r * cell_h                            # top-left y of this cell
            rect = pygame.Rect(int(x + CELL_MARGIN),  # create a rect representing the cell with margin
                               int(y + CELL_MARGIN),
                               int(cell_w - 2 * CELL_MARGIN),
                               int(cell_h - 2 * CELL_MARGIN))
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)  # draw rectangle outline for the cell

    # Victims
    detected_count = 0                                # counter for how many victims are detected
    for v in victims:                                 # iterate victims to draw them
        color = VICTIM_COLOR if v.detected else RUBBLE_COLOR  # choose color depending on detection state
        if v.detected:                                # if victim detected
            detected_count += 1                       # increment detected counter
        pygame.draw.circle(screen, color, (int(v.pos[0]), int(v.pos[1])), 6)  # draw small circle for victim

    # UAVs
    for u in uavs:                                    # iterate UAVs to draw sensors and agent
        s = pygame.Surface((SENSOR_RADIUS*2, SENSOR_RADIUS*2), pygame.SRCALPHA)  # create transparent surface for sensor
        pygame.draw.circle(s, (50,200,255,30), (SENSOR_RADIUS, SENSOR_RADIUS), SENSOR_RADIUS)  # draw translucent sensor circle
        screen.blit(s, (int(u.pos[0] - SENSOR_RADIUS), int(u.pos[1] - SENSOR_RADIUS)))  # blit sensor surface centered on UAV

        color = UAV_COLOR if u.found_count == 0 else UAV_FOUND_COLOR  # UAV color depends on found_count
        pygame.draw.circle(screen, color, (int(u.pos[0]), int(u.pos[1])), 6)  # draw UAV as a small filled circle

    # Stats
    coverage_pct = len(covered_cells) / total_cells * 100  # compute coverage percentage of visited cells
    stats = [                                         # build a list of stat strings
        f"Time: {int(time_elapsed)}s",               # show elapsed time in seconds
        f"UAVs: {NUM_UAVS}",                          # show number of UAVs
        f"Victims detected: {detected_count}/{NUM_VICTIMS}",  # show detected victims count
        f"Coverage: {coverage_pct:.1f}%"             # show coverage percentage with one decimal
    ]

    for i, text in enumerate(stats):                  # render each stat line to the screen
        img = font.render(text, True, TEXT_COLOR)     # render text to an image surface
        screen.blit(img, (10, 10 + 20*i))             # blit stat at left with vertical spacing 20px

    help_text = font.render("Press R to reset detections and pheromone", True, TEXT_COLOR)  # render help text
    screen.blit(help_text, (10, HEIGHT - 25))         # blit help text near bottom-left of screen

    pygame.display.flip()                             # update the full display surface to the screen

pygame.quit()                                        # uninitialize all pygame modules after loop ends
sys.exit()                                           # exit the Python process
