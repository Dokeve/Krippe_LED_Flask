try:
  import RPi.GPIO as GPIO; HAVE=True
except Exception:
  HAVE=False
import threading,time
class GPIOWorker:
  def __init__(self,on_button):
    self.on_button=on_button; self.running=False; self.thread=None
    self.pump_pin=10; self.button_pin=17
    if HAVE:
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(self.pump_pin, GPIO.OUT); GPIO.output(self.pump_pin, GPIO.LOW)
  def start(self):
    self.running=True; self.thread=threading.Thread(target=self._loop,daemon=True); self.thread.start()
  def stop(self):
    self.running=False
    if self.thread: self.thread.join(timeout=1)
    if HAVE: GPIO.cleanup()
  def _loop(self):
    last=False
    while self.running:
      pressed=(HAVE and GPIO.input(self.button_pin)==GPIO.LOW)
      if pressed and not last:
        try: self.on_button()
        except Exception: pass
      last=pressed; time.sleep(0.03)
  def set_pump(self,on):
    if HAVE: GPIO.output(self.pump_pin, GPIO.HIGH if on else GPIO.LOW)
