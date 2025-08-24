import pygame, os, time, threading
from config import Config
class AudioSystem:
  def __init__(self):
    try:
      pygame.mixer.init(); self.ok=True
    except Exception:
      self.ok=False
    self.bg=pygame.mixer.Channel(0) if self.ok else None
    self.fx=pygame.mixer.Channel(1) if self.ok else None
    self.phase={}; self.cur=None
    if self.ok: self.set_volume(Config.AUDIO_VOLUME)
  def set_volume(self,v):
    if self.ok: self.bg.set_volume(v); self.fx.set_volume(v)
  def load_phase_file(self,ph,path):
    if self.ok and os.path.exists(path): self.phase[ph]=pygame.mixer.Sound(path)
  def play_phase_bg(self,ph):
    if not self.ok: return
    if ph==self.cur: return
    self.cur=ph; self.bg.stop(); s=self.phase.get(ph);
    if s: self.bg.play(s, loops=-1)
  def stop_bg(self):
    if self.ok: self.bg.stop()
  def play_file_ducking(self, path, volume_percent, duck_to):
    if not self.ok or not os.path.exists(path): return
    s=pygame.mixer.Sound(path); s.set_volume(max(0.0,min(1.0,volume_percent/100.0)))
    cur=self.bg.get_volume(); self.bg.set_volume(duck_to); self.fx.play(s)
    while self.fx.get_busy(): time.sleep(0.02)
    self.bg.set_volume(cur)
