from config import Config
import threading, time
class LEDController:
  def __init__(self,on_phase=None):
    self.count=Config.LED_COUNT; self.brightness=Config.LED_BRIGHTNESS
    self.mode=0; self.uniform=(255,255,255); self.on_phase=on_phase
    self.preview=[(0,0,0)]*self.count; self.groups={}
    self._stop=threading.Event(); self._th=None
  def set_groups(self, groups):
    self.groups=groups
  def get_preview(self):
    return self.preview
  def _apply_groups(self):
    pc=[(0,0,0)]*self.count
    for g in self.groups.values():
      col=g.get('color',(255,255,255))
      for i in g.get('indices',[]):
        if 0<=i<self.count: pc[i]=col
    self.preview=pc
  def _fill(self,color):
    self.preview=[color]*self.count
  def start_mode2(self, color=None):
    self.mode=2; self.uniform=color or self.uniform; self._start(self._run2)
  def start_mode1(self):
    self.mode=1; self._start(self._run1)
  def stop(self):
    self.mode=0; self._stop.set()
    if self._th and self._th.is_alive(): self._th.join(timeout=1)
    self._th=None; self._fill((0,0,0))
  def _start(self,target):
    self._stop.set();
    if self._th and self._th.is_alive(): self._th.join(timeout=1)
    self._stop.clear(); self._th=threading.Thread(target=target,daemon=True); self._th.start()
  def _run2(self):
    while not self._stop.is_set():
      if self.groups: self._apply_groups()
      else: self._fill(self.uniform)
      time.sleep(0.05)
  def _run1(self):
    seq=[('day',100),('d2n',50),('night',100),('n2d',50)]
    while not self._stop.is_set():
      for name,dur in seq:
        if self.on_phase:
          try: self.on_phase(name)
          except Exception: pass
        base={'day':(255,255,255),'d2n':(128,100,40),'night':(5,5,20),'n2d':(128,140,80)}.get(name,(255,255,255))
        t0=time.time()
        while time.time()-t0<dur and not self._stop.is_set():
          if self.groups: self._apply_groups()
          else: self._fill(base)
          time.sleep(0.05)
