import pygame, random, math, sys
from collections import deque

# ---------- Parameters ----------
WIDTH, HEIGHT = 900, 600
GRID_ROWS, GRID_COLS = 12, 18         # coverage grid (cells = GRID_ROWS * GRID_COLS)
NUM_UAVS = 8
NUM_VICTIMS = 12
UAV_SPEED = 80.0                      # pixels per second
SENSOR_RADIUS = 40                    # detection radius (pixels)
DETECTION_PROB = 0.9                  # probability to detect when in range
CELL_MARGIN = 2                       # visual margin inside each grid cell
FPS = 60

# ---------- NEW: Collision + communication parameters ----------
COMM_RANGE = 150
COLLISION_DIST = 20
AVOID_STRENGTH = 1.0

# ---------- NEW: Pheromone parameters ----------
PHEROMONE_DECAY = 0.995
PHEROMONE_DEPOSIT = 5.0
STEER_ANGLE = math.radians(40)
SAMPLE_DIST = max(WIDTH/GRID_COLS, HEIGHT/GRID_ROWS) * 0.9
ROTATION_SPEED = math.radians(120)
RANDOMNESS = 0.2

# Colors
BG = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
UAV_COLOR = (50, 150, 240)
UAV_FOUND_COLOR = (0, 220, 0)
RUBBLE_COLOR = (120, 110, 100)
VICTIM_COLOR = (220, 40, 40)
TEXT_COLOR = (230, 230, 230)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)

# ---------- Derived ----------
cell_w = WIDTH / GRID_COLS
cell_h = HEIGHT / GRID_ROWS

# ---------- Victim class ----------
class Victim:
    def __init__(self, x, y):
        self.pos = (x, y)
        self.detected = False


# ---------- NEW: pheromone grid ----------
pheromone = [[0.0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]


# ---------- UAV class ----------
class UAV:
    def __init__(self, uid, waypoints):
        self.id = uid
        self.pos = list(waypoints[0])
        self.waypoints = deque(waypoints)
        self.speed = UAV_SPEED
        self.found_count = 0

        self.heading = random.uniform(0, 2 * math.pi)

        # NEW: communication memory
        self.known_detections = set()

    # NEW
    def _cell_index(self, px, py):
        cx = int(px // cell_w)
        cy = int(py // cell_h)
        cx = max(0, min(GRID_COLS - 1, cx))
        cy = max(0, min(GRID_ROWS - 1, cy))
        return cy, cx

    # NEW
    def sample_pheromone(self, angle_offset):
        ang = self.heading + angle_offset
        sx = self.pos[0] + math.cos(ang) * SAMPLE_DIST
        sy = self.pos[1] + math.sin(ang) * SAMPLE_DIST
        r, c = self._cell_index(sx, sy)
        return pheromone[r][c], (r, c)

    # ---------- NEW: collision avoidance ----------
    def avoid_collision(self, uavs):
        for other in uavs:
            if other is self:
                continue
            dx = other.pos[0] - self.pos[0]
            dy = other.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)

            if dist < COLLISION_DIST and dist > 0:
                angle_to_other = math.atan2(dy, dx)
                away_angle = angle_to_other + math.pi
                self.heading += AVOID_STRENGTH * (away_angle - self.heading)

    # ---------- Step ----------
    def step(self, dt):
        # ---- choose direction based on pheromone ----
        candidates = [(0.0,), (-STEER_ANGLE,), (STEER_ANGLE,)]
        samples = []
        for (offset,) in candidates:
            pval, cell = self.sample_pheromone(offset)
            pval += random.uniform(0, RANDOMNESS)
            samples.append((pval, offset))

        samples.sort(key=lambda x: x[0])
        chosen_offset = samples[0][1]
        target_heading = self.heading + chosen_offset

        def normalize(a):
            while a <= -math.pi: a += 2*math.pi
            while a > math.pi: a -= 2*math.pi
            return a

        diff = normalize(target_heading - self.heading)
        max_rot = ROTATION_SPEED * dt
        if abs(diff) <= max_rot:
            self.heading = normalize(self.heading + diff)
        else:
            self.heading = normalize(self.heading + math.copysign(max_rot, diff))

        # ---------- NEW: avoid collisions before moving ----------
        self.avoid_collision(uavs_global)

        # ---------- MOVE ----------
        dx = math.cos(self.heading) * self.speed * dt
        dy = math.sin(self.heading) * self.speed * dt
        self.pos[0] = (self.pos[0] + dx) % WIDTH
        self.pos[1] = (self.pos[1] + dy) % HEIGHT

        # ---------- Deposit pheromone ----------
        r, c = self._cell_index(self.pos[0], self.pos[1])
        pheromone[r][c] += PHEROMONE_DEPOSIT

    # ---------- Detection ----------
    def scan_and_detect(self, victims):
        for v in victims:
            if v.detected:
                continue
            vx, vy = v.pos
            d = math.hypot(self.pos[0] - vx, self.pos[1] - vy)
            if d <= SENSOR_RADIUS:
                if random.random() <= DETECTION_PROB:
                    v.detected = True
                    self.found_count += 1
                    # NEW:
                    self.known_detections.add(id(v))


# ---------- Helpers ----------
def make_cell_centers(rows, cols):
    centers = []
    for r in range(rows):
        for c in range(cols):
            cx = c * cell_w + cell_w/2
            cy = r * cell_h + cell_h/2
            centers.append((cx, cy))
    return centers

def assign_waypoints_to_uavs(centers, num_uavs):
    assignments = [[] for _ in range(num_uavs)]
    for i, center in enumerate(centers):
        assignments[i % num_uavs].append(center)
    for i, a in enumerate(assignments):
        if i % 2 == 1:
            a.reverse()
    return assignments


# ---------- Setup ----------
centers = make_cell_centers(GRID_ROWS, GRID_COLS)
assignments = assign_waypoints_to_uavs(centers, NUM_UAVS)
uavs = [UAV(i, assignments[i]) for i in range(NUM_UAVS)]

# NEW
uavs_global = uavs

victims = []
padding = 20
for _ in range(NUM_VICTIMS):
    x = random.uniform(padding, WIDTH - padding)
    y = random.uniform(padding, HEIGHT - padding)
    victims.append(Victim(x, y))

covered_cells = set()
total_cells = GRID_ROWS * GRID_COLS
time_elapsed = 0.0


# ---------- Main Loop ----------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    time_elapsed += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                for v in victims:
                    v.detected = False
                pheromone = [[0.0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                covered_cells.clear()

    # Step UAVs
    for u in uavs:
        u.step(dt)

        grid_x = int(u.pos[0] // cell_w)
        grid_y = int(u.pos[1] // cell_h)
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
            covered_cells.add(grid_y * GRID_COLS + grid_x)

        u.scan_and_detect(victims)

    # ---------- NEW: Communication ----------
    for u in uavs:
        for other in uavs:
            if u is other:
                continue
            dx = u.pos[0] - other.pos[0]
            dy = u.pos[1] - other.pos[1]
            dist = math.hypot(dx, dy)

            if dist <= COMM_RANGE:
                for v in victims:
                    if id(v) in u.known_detections:
                        v.detected = True
                        other.known_detections.add(id(v))

    # Pheromone decay
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            pheromone[r][c] *= PHEROMONE_DECAY
            if pheromone[r][c] < 1e-6:
                pheromone[r][c] = 0.0

    # ---------- Drawing ----------
    screen.fill(BG)

    # Grid
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = c * cell_w
            y = r * cell_h
            rect = pygame.Rect(int(x + CELL_MARGIN),
                               int(y + CELL_MARGIN),
                               int(cell_w - 2 * CELL_MARGIN),
                               int(cell_h - 2 * CELL_MARGIN))
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    # Victims
    detected_count = 0
    for v in victims:
        color = VICTIM_COLOR if v.detected else RUBBLE_COLOR
        if v.detected:
            detected_count += 1
        pygame.draw.circle(screen, color, (int(v.pos[0]), int(v.pos[1])), 6)

    # UAVs
    for u in uavs:
        s = pygame.Surface((SENSOR_RADIUS*2, SENSOR_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (50,200,255,30), (SENSOR_RADIUS, SENSOR_RADIUS), SENSOR_RADIUS)
        screen.blit(s, (int(u.pos[0] - SENSOR_RADIUS), int(u.pos[1] - SENSOR_RADIUS)))

        color = UAV_COLOR if u.found_count == 0 else UAV_FOUND_COLOR
        pygame.draw.circle(screen, color, (int(u.pos[0]), int(u.pos[1])), 6)

    # Stats
    coverage_pct = len(covered_cells) / total_cells * 100
    stats = [
        f"Time: {int(time_elapsed)}s",
        f"UAVs: {NUM_UAVS}",
        f"Victims detected: {detected_count}/{NUM_VICTIMS}",
        f"Coverage: {coverage_pct:.1f}%"
    ]

    for i, text in enumerate(stats):
        img = font.render(text, True, TEXT_COLOR)
        screen.blit(img, (10, 10 + 20*i))

    help_text = font.render("Press R to reset detections and pheromone", True, TEXT_COLOR)
    screen.blit(help_text, (10, HEIGHT - 25))

    pygame.display.flip()

pygame.quit()
sys.exit()