import threading,time,datetime
from models import SessionLocal, CalendarEntry, Announcement
class Scheduler:
  def __init__(self, on_mode_change, on_announcement):
    self.on_mode_change=on_mode_change; self.on_announcement=on_announcement
    self.stop_event=threading.Event(); self.thread=None; self.played=set()
  def start(self):
    self.thread=threading.Thread(target=self._run,daemon=True); self.thread.start()
  def stop(self):
    self.stop_event.set();
    if self.thread and self.thread.is_alive(): self.thread.join(timeout=1)
  def _run(self):
    while not self.stop_event.is_set():
      now=datetime.datetime.now()
      with SessionLocal() as s:
        entries=s.query(CalendarEntry).all()
      active=None
      for e in entries:
        if e.start<=now<=e.end: active=e; break
      if active: self.on_mode_change(active.mode, active.color)
      with SessionLocal() as s:
        anns=s.query(Announcement).all()
      for a in anns:
        if a.start<=now<=a.end:
          key=(a.id, now.date())
          if key not in self.played:
            self.played.add(key)
            self.on_announcement(a.file_path, a.volume)
      time.sleep(2)
