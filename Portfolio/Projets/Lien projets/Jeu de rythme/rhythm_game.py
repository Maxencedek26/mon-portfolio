"""
rhythm_game_hold_v2.py
EduPython rhythm game with improved hold logic and scoring
"""

import json
import pygame
from pygame import mixer
from tkinter import Tk, filedialog
from pathlib import Path

# --- SETTINGS ---
WIDTH, HEIGHT = 900, 700
FPS = 60
NOTE_SPEED = 400.0
HIT_LINE_Y = int(HEIGHT * 0.8)
HIT_WINDOWS = {"perfect": 0.06, "good": 0.14, "miss": 0.25}
AUDIO_DELAY = 0.4

KEY_MAPPING = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT]
ARROW_SYMBOLS = ["←", "↓", "↑", "→"]

COLORS = {
    "bg": (15, 15, 25),
    "lane": (30, 30, 45),
    "line": (80, 80, 100),
    "note_tap": (120, 200, 255),
    "note_hold": (180, 255, 200),
    "trail": (80, 180, 255),
    "text": (240, 240, 240)
}

# --- SCORING SETTINGS ---
BASE_TAP_SCORE = 100
BASE_HOLD_SCORE = 150

def combo_multiplier(combo):
    return 1.0 + (combo // 10) * 0.02  # +2% every 10 combo

# --- NOTE CLASS ---
class Note:
    def __init__(self, time, lane, note_type="tap", end_time=None):
        self.time = float(time)
        self.lane = int(lane)
        self.type = note_type
        self.end = float(end_time) if end_time else None
        self.hit = False
        self.hold_active = False
        self.hold_done = False

# --- FILE PICKER ---
def choose_chart_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a chart JSON file",
        filetypes=[("Chart Files", "*.json"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

# --- LOAD CHART ---
def load_chart(path):
    with open(path, "r", encoding="utf-8") as f:
        chart = json.load(f)
    chart["notes"] = sorted(chart.get("notes", []), key=lambda n: n["time"])
    chart_path = Path(path)
    song_path = Path(chart.get("song", ""))
    if not song_path.exists():
        possible = chart_path.parent / song_path.name
        if possible.exists():
            chart["song"] = str(possible)
        else:
            print(f"⚠️ Could not find {song_path.name}.")
    return chart

# --- GAME LOOP ---
def run_game(chart):
    pygame.init()
    mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("EduPython Rhythm Game V2")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)
    arrow_font = pygame.font.SysFont("Arial", 60, bold=True)

    song_path = chart["song"]
    offset = float(chart.get("offset", 0.0)) + AUDIO_DELAY
    notes = [
        Note(n["time"] + offset, n["lane"], n.get("type","tap"), n.get("end"))
        for n in chart["notes"]
    ]

    try:
        mixer.music.load(song_path)
    except Exception as e:
        print("Error loading song:", e)
        return

    # --- Wait for key ---
    screen.fill(COLORS["bg"])
    msg = font.render("Press any arrow key to start...", True, COLORS["text"])
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key in KEY_MAPPING:
                waiting = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                return

    # --- Countdown ---
    for i in [3,2,1]:
        screen.fill(COLORS["bg"])
        count_text = pygame.font.SysFont("Arial",100,bold=True).render(str(i),True,COLORS["text"])
        screen.blit(count_text,(WIDTH//2 - count_text.get_width()//2, HEIGHT//2 -50))
        pygame.display.flip()
        pygame.time.wait(800)
    mixer.music.play()
    start_ticks = pygame.time.get_ticks()

    score, combo = 0,0
    hit_text = ""
    hit_timer = 0.0
    running = True
    note_index = 0
    active_notes = []
    held_keys = {k:False for k in KEY_MAPPING}

    def audio_time():
        ms = mixer.music.get_pos()
        if ms == -1:
            return (pygame.time.get_ticks() - start_ticks)/1000.0
        return ms/1000.0

    while running:
        dt = clock.tick(FPS)/1000.0
        t = audio_time()

        # --- EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    running=False
                elif event.key in KEY_MAPPING:
                    held_keys[event.key]=True
                    lane_hit=KEY_MAPPING.index(event.key)
                    # Check taps or start hold
                    best=None
                    best_dt=999.0
                    for note in active_notes:
                        if note.lane!=lane_hit or note.hit:
                            continue
                        if note.type=="hold" and note.hold_done:
                            continue
                        delta = abs(note.time-t)
                        if delta<=HIT_WINDOWS["miss"] and delta<best_dt:
                            best=note
                            best_dt=delta
                    if best:
                        if best.type=="tap":
                            score_add = int(BASE_TAP_SCORE*combo_multiplier(combo))
                            score+=score_add
                            combo+=1
                            if best_dt<=HIT_WINDOWS["perfect"]:
                                hit_text="PERFECT"
                            elif best_dt<=HIT_WINDOWS["good"]:
                                hit_text="GOOD"
                            else:
                                hit_text="OK"
                            best.hit=True
                            hit_timer=0.6
                        elif best.type=="hold":
                            best.hold_active=True
            elif event.type==pygame.KEYUP:
                if event.key in KEY_MAPPING:
                    held_keys[event.key]=False
                    lane_up=KEY_MAPPING.index(event.key)
                    for note in active_notes:
                        if note.lane==lane_up and note.type=="hold" and note.hold_active:
                            hold_duration = t-note.time
                            full_duration = note.end-note.time
                            ratio = hold_duration/full_duration
                            if ratio>=0.9:
                                hit_text="PERFECT"
                                score_add=int(BASE_HOLD_SCORE*1.0*combo_multiplier(combo))
                                score+=score_add
                                combo+=1
                            elif ratio>=0.5:
                                hit_text="GOOD"
                                score_add=int(BASE_HOLD_SCORE*0.6*combo_multiplier(combo))
                                score+=score_add
                                combo+=1
                            else:
                                hit_text="MISS"
                                combo=0
                            note.hit=True
                            note.hold_done=True
                            note.hold_active=False
                            hit_timer=0.6

        # --- Spawn notes ---
        render_lead=(HIT_LINE_Y+100)/NOTE_SPEED
        while note_index<len(notes) and notes[note_index].time<=t+render_lead:
            active_notes.append(notes[note_index])
            note_index+=1

        # --- Check misses ---
        for note in list(active_notes):
            if note.type=="tap" and not note.hit and t-note.time>HIT_WINDOWS["miss"]:
                active_notes.remove(note)
                combo=0
                hit_text="MISS"
                hit_timer=0.6
            elif note.type=="hold":
                if not note.hold_done and t>note.end+HIT_WINDOWS["miss"]:
                    hit_text="MISS"
                    hit_timer=0.6
                    combo=0
                    note.hit=True
                    note.hold_done=True
                    if note in active_notes:
                        active_notes.remove(note)
            elif note.hit and t-note.time>0.6:
                if note in active_notes:
                    active_notes.remove(note)

        # --- Draw ---
        screen.fill(COLORS["bg"])
        lane_width=WIDTH//4
        for i in range(4):
            pygame.draw.rect(screen,COLORS["lane"],(i*lane_width,0,lane_width,HEIGHT))
            pygame.draw.line(screen,COLORS["line"],(i*lane_width,0),(i*lane_width,HEIGHT),2)
        pygame.draw.line(screen,(255,255,255),(0,HIT_LINE_Y),(WIDTH,HIT_LINE_Y),3)

        for note in active_notes:
            y=HIT_LINE_Y-(note.time-t)*NOTE_SPEED
            x_center=note.lane*lane_width+lane_width//2
            if note.type=="hold" and note.end:
                end_y=HIT_LINE_Y-(note.end-t)*NOTE_SPEED
                trail_rect=pygame.Rect(0,0,int(lane_width*0.5),int(y-end_y))
                trail_rect.centerx=x_center
                trail_rect.top=min(y,end_y)
                pygame.draw.rect(screen,COLORS["trail"],trail_rect,border_radius=8)
            rect=pygame.Rect(0,0,int(lane_width*0.7),20)
            rect.center=(x_center,int(y))
            if -50<=y<=HEIGHT+50:
                color=COLORS["note_tap"] if note.type=="tap" else COLORS["note_hold"]
                pygame.draw.rect(screen,color,rect,border_radius=8)

        # arrows
        for i,sym in enumerate(ARROW_SYMBOLS):
            text=arrow_font.render(sym,True,(255,255,255))
            x=i*lane_width+lane_width//2 - text.get_width()//2
            y=HIT_LINE_Y+15
            screen.blit(text,(x,y))

        # HUD
        score_surf=font.render(f"Score: {score}",True,COLORS["text"])
        combo_surf=font.render(f"Combo: {combo}",True,COLORS["text"])
        screen.blit(score_surf,(10,10))
        screen.blit(combo_surf,(10,40))
        if hit_timer>0:
            ht=font.render(hit_text,True,(255,230,180))
            screen.blit(ht,(WIDTH//2 - ht.get_width()//2,HIT_LINE_Y-80))
            hit_timer-=dt

        pygame.display.flip()

        if not mixer.music.get_busy() and note_index>=len(notes) and len(active_notes)==0:
            running=False

    # End screen
    screen.fill(COLORS["bg"])
    end_text=font.render(f"Done! Final score: {score}",True,COLORS["text"])
    screen.blit(end_text,(WIDTH//2 - end_text.get_width()//2,HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()

# --- MAIN ---
if __name__=="__main__":
    chart_path = choose_chart_file()
    if chart_path:
        chart = load_chart(chart_path)
        run_game(chart)
    else:
        print("No chart selected.")
