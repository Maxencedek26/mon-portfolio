"""
Chart maker with hold notes that prevents other notes from overlapping.
Short holds (<1s) become taps.
"""

import librosa
import json
import numpy as np

def build_chart(song_path, out_path, lanes=4, sensitivity=1.5, hold_threshold=1.0):
    print("Analyzing audio, please wait...")

    y, sr = librosa.load(song_path, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env)
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo.mean())
    else:
        tempo = float(tempo)

    times = librosa.frames_to_time(beats, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)

    avg_energy = float(np.mean(rms))
    energy_threshold = avg_energy * sensitivity

    notes = []
    active_holds = []  # list of (lane, end_time) for hold tracking
    last_lane = -1
    hold_active = False
    hold_start = 0.0
    hold_lane = 0

    for t in times:
        # remove expired holds
        active_holds = [h for h in active_holds if h[1] > t]

        idx = np.searchsorted(rms_times, t)
        if idx >= len(rms):
            continue
        energy = float(rms[idx])

        # get lanes not blocked by active holds
        free_lanes = [i for i in range(lanes) if all(h[0] != i for h in active_holds)]
        if not free_lanes:
            continue  # skip this beat if no lanes available

        # pick a random free lane
        lane = int(np.random.choice(free_lanes))
        while lane == last_lane:
            lane = int(np.random.choice(free_lanes))
        last_lane = lane

        # HOLD detection
        if energy > energy_threshold:
            if not hold_active:
                hold_active = True
                hold_start = float(t)
                hold_lane = lane
        else:
            if hold_active:
                hold_active = False
                hold_end = float(t)
                duration = hold_end - hold_start
                if duration >= hold_threshold:
                    notes.append({
                        "time": float(hold_start),
                        "lane": int(hold_lane),
                        "type": "hold",
                        "end": float(hold_end)
                    })
                    active_holds.append((hold_lane, hold_end))  # block this lane
                else:
                    notes.append({
                        "time": float(hold_start),
                        "lane": int(hold_lane),
                        "type": "tap"
                    })

        # Extra random taps for liveliness (only in free lanes)
        if np.random.random() < 0.35 * sensitivity:
            extra_free = [i for i in free_lanes if i != lane]  # avoid current note lane
            if extra_free:
                notes.append({
                    "time": float(t),
                    "lane": int(np.random.choice(extra_free)),
                    "type": "tap"
                })

    # finalize last active hold
    if hold_active:
        notes.append({
            "time": float(hold_start),
            "lane": int(hold_lane),
            "type": "hold",
            "end": float(hold_start + 1.2)
        })
        active_holds.append((hold_lane, hold_start + 1.2))

    chart = {
        "song": song_path,
        "bpm": tempo,
        "notes": sorted(notes, key=lambda n: n["time"]),
        "offset": 0.0
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chart, f, indent=2)

    print(f"✅ Chart saved: {out_path}")
    print(f"BPM: {tempo:.2f}, Notes: {len(notes)} "
          f"(Holds: {sum(1 for n in notes if n['type']=='hold')})")

# --- EduPython usage ---
if __name__ == "__main__":
    song_path = "Songs/Rumbling.mp3"
    out_path = "Songs/Rumbling.chart.json"
    build_chart(song_path, out_path)

