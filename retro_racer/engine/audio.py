"""Procedural Chiptune Audio Synthesizer and Soundtrack Generator.

Uses NumPy and Pygame Sound synthesis to create authentic 80s arcade sound
effects and synthwave music dynamically in memory, without external audio files.
"""

import math
import numpy as np
import pygame
from typing import Dict, Optional

from retro_racer.config import AUDIO_SAMPLE_RATE, MASTER_VOLUME, SFX_VOLUME, MUSIC_VOLUME


class AudioManager:
    """Procedural audio engine for sound effects and background music."""

    def __init__(self, sample_rate: int = AUDIO_SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self.music_sound: Optional[pygame.mixer.Sound] = None
        self.music_channel: Optional[pygame.mixer.Channel] = None
        self.engine_channel: Optional[pygame.mixer.Channel] = None
        self.muted = False
        self.master_volume = MASTER_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.music_volume = MUSIC_VOLUME
        self.initialized = False

        self._init_mixer()

    def _init_mixer(self):
        """Safely initialize pygame mixer."""
        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.music_channel = pygame.mixer.Channel(0)
            self.engine_channel = pygame.mixer.Channel(1)
            self.initialized = True
            self._synthesize_all_sfx()
        except Exception:
            self.initialized = False

    def _create_sound_from_array(self, mono_array: np.ndarray) -> pygame.mixer.Sound:
        """Convert float numpy array (-1.0 to 1.0) into 16-bit stereo Pygame Sound."""
        int16_arr = np.int16(mono_array * 32767)
        # Convert to stereo
        stereo_arr = np.column_stack((int16_arr, int16_arr))
        return pygame.sndarray.make_sound(stereo_arr)

    def _synthesize_all_sfx(self):
        """Pre-generate all sound effects into memory."""
        if not self.initialized:
            return

        # 1. Beep / UI Click
        t = np.linspace(0, 0.08, int(self.sample_rate * 0.08), endpoint=False)
        beep_wave = 0.4 * np.sign(np.sin(2 * np.pi * 660 * t)) * np.exp(-t * 25)
        self.sound_cache["beep"] = self._create_sound_from_array(beep_wave)

        # 2. Coin Collect (B-E Arpeggio)
        dur = 0.2
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        f1 = 987.77   # B5
        f2 = 1318.51  # E6
        half = len(t) // 2
        wave = np.zeros_like(t)
        wave[:half] = 0.35 * np.sign(np.sin(2 * np.pi * f1 * t[:half]))
        wave[half:] = 0.45 * np.sign(np.sin(2 * np.pi * f2 * t[half:]))
        envelope = np.exp(-t * 12)
        self.sound_cache["coin"] = self._create_sound_from_array(wave * envelope)

        # 3. Power-up / Item Pickup (C-E-G-C Major Chime)
        dur = 0.35
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        q = len(t) // 4
        wave = np.zeros_like(t)
        wave[0:q] = 0.3 * np.sin(2 * np.pi * 523.25 * t[0:q])
        wave[q:2*q] = 0.35 * np.sin(2 * np.pi * 659.25 * t[q:2*q])
        wave[2*q:3*q] = 0.4 * np.sin(2 * np.pi * 783.99 * t[2*q:3*q])
        wave[3*q:] = 0.45 * np.sin(2 * np.pi * 1046.50 * t[3*q:])
        wave *= np.exp(-t * 6)
        self.sound_cache["pickup"] = self._create_sound_from_array(wave)

        # 4. Nitro Whoosh
        dur = 0.6
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, len(t))
        sweep_freq = 300 + 900 * (t / dur)
        synth = 0.5 * np.sin(2 * np.pi * sweep_freq * t) + 0.5 * noise
        env = np.sin(t / dur * np.pi)
        self.sound_cache["nitro"] = self._create_sound_from_array(0.4 * synth * env)

        # 5. Crash Explosion
        dur = 0.7
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, len(t))
        boom = np.sin(2 * np.pi * (120 - 90 * (t / dur)) * t)
        wave = (0.7 * noise + 0.5 * boom) * np.exp(-t * 5.5)
        self.sound_cache["crash"] = self._create_sound_from_array(0.7 * wave)

        # 6. Tire Skid / Drift
        dur = 0.3
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, len(t))
        skid_wave = 0.3 * np.sin(2 * np.pi * 880 * t) + 0.4 * noise
        self.sound_cache["skid"] = self._create_sound_from_array(0.3 * skid_wave * np.exp(-t * 8))

        # 7. Near Miss Whoosh
        dur = 0.22
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        freq = 400 + 400 * np.sin(t / dur * np.pi)
        whoosh = 0.4 * np.sin(2 * np.pi * freq * t) * np.sin(t / dur * math.pi)
        self.sound_cache["near_miss"] = self._create_sound_from_array(whoosh)

        # 8. Police Siren Tone
        dur = 0.4
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        siren_freq = 600 + 300 * np.sin(2 * np.pi * 3.5 * t)
        siren_wave = 0.35 * np.sign(np.sin(2 * np.pi * siren_freq * t))
        self.sound_cache["siren"] = self._create_sound_from_array(siren_wave)

        # 9. Engine Loop Sound (Short looping waveform)
        dur = 0.1
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        engine_wave = 0.25 * np.sign(np.sin(2 * np.pi * 75 * t)) + 0.15 * np.sin(2 * np.pi * 150 * t)
        self.sound_cache["engine_loop"] = self._create_sound_from_array(engine_wave)

        # Synthesize Background Synthwave Track
        self._synthesize_synthwave_music()

    def _synthesize_synthwave_music(self):
        """Synthesize a looping 16-bar retro 80s arcade synthwave music loop."""
        tempo = 128  # BPM
        beat_len = 60.0 / tempo
        total_beats = 32  # 8 bars
        duration = total_beats * beat_len
        total_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, total_samples, endpoint=False)

        track = np.zeros(total_samples)

        # Bassline notes (F2, G2, Ab2, Bb2 progression)
        bass_freqs = [87.31, 98.00, 103.83, 116.54]  # F, G, Ab, Bb
        samples_per_beat = int(self.sample_rate * beat_len)

        for beat in range(total_beats):
            idx = (beat // 4) % len(bass_freqs)
            freq = bass_freqs[idx]
            start_s = beat * samples_per_beat
            end_s = min(total_samples, (beat + 1) * samples_per_beat)
            bt = t[start_s:end_s] - t[start_s]

            # 16th note arpeggio pulse
            sub_samples = len(bt) // 4
            for s in range(4):
                ss = s * sub_samples
                se = (s + 1) * sub_samples
                st = bt[ss:se]
                # Sawtooth synth bass
                saw = 0.22 * (2 * (st * freq * (1 + 0.5 * s) - np.floor(0.5 + st * freq * (1 + 0.5 * s))))
                track[start_s + ss : start_s + se] += saw * np.exp(-st * 15)

            # Kick drum on beats 0, 1, 2, 3
            kick_t = bt[:min(len(bt), int(self.sample_rate * 0.15))]
            kick_freq = 140 * np.exp(-kick_t * 22)
            kick = 0.45 * np.sin(2 * np.pi * kick_freq * kick_t) * np.exp(-kick_t * 18)
            track[start_s : start_s + len(kick)] += kick

            # Snare on beats 1 and 3
            if beat % 2 == 1:
                snare_t = bt[:min(len(bt), int(self.sample_rate * 0.18))]
                noise = np.random.uniform(-0.3, 0.3, len(snare_t))
                tone = 0.2 * np.sin(2 * np.pi * 220 * snare_t)
                snare = (noise + tone) * np.exp(-snare_t * 20)
                track[start_s : start_s + len(snare)] += snare

        # Normalize and master
        max_val = np.max(np.abs(track))
        if max_val > 0:
            track = (track / max_val) * 0.55

        self.music_sound = self._create_sound_from_array(track)

    def play_sfx(self, name: str, volume_scale: float = 1.0):
        """Play a one-shot sound effect."""
        if not self.initialized or self.muted:
            return
        sound = self.sound_cache.get(name)
        if sound:
            sound.set_volume(self.master_volume * self.sfx_volume * volume_scale)
            sound.play()

    def start_music(self):
        """Start playing background synthwave music on loop."""
        if not self.initialized or self.muted or not self.music_sound:
            return
        if self.music_channel and not self.music_channel.get_busy():
            self.music_sound.set_volume(self.master_volume * self.music_volume)
            self.music_channel.play(self.music_sound, loops=-1)

    def stop_music(self):
        """Stop background music."""
        if self.music_channel:
            self.music_channel.stop()

    def set_engine_rpm(self, speed_ratio: float):
        """Adjust engine sound pitch and volume based on vehicle speed."""
        if not self.initialized or self.muted:
            return
        if self.engine_channel:
            if not self.engine_channel.get_busy():
                eng_sound = self.sound_cache.get("engine_loop")
                if eng_sound:
                    self.engine_channel.play(eng_sound, loops=-1)
            vol = (0.2 + 0.35 * speed_ratio) * self.master_volume * self.sfx_volume
            self.engine_channel.set_volume(vol)

    def stop_engine(self):
        if self.engine_channel:
            self.engine_channel.stop()

    def toggle_mute(self):
        """Toggle mute state."""
        self.muted = not self.muted
        if self.muted:
            self.stop_music()
            self.stop_engine()
        else:
            self.start_music()
