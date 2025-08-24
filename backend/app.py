from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import datetime
from config import Config
from models import init_db, SessionLocal, Group, CalendarEntry, AudioPhase, Announcement
from importer import import_mapping
from led_controller import LEDController
from audio import AudioSystem
from gpio_worker import GPIOWorker
from scheduler import Scheduler
import os
app=Flask(__name__); CORS(app); app.config['SECRET_KEY']='dev'
socketio=SocketIO(app, cors_allowed_origins='*', async_mode='threading')
init_db()
audio=AudioSystem()

def reload_phase_audio():
  with SessionLocal() as s:
    for p in s.query(AudioPhase).all(): audio.load_phase_file(p.phase, p.file_path)

def on_phase_change(phase):
  audio.play_phase_bg(phase)
  # mapping switch (merge) by phase filenames from env kept simple here

led=LEDController(on_phase=on_phase_change)

def on_button():
  socketio.emit('button_press', {'ts': datetime.now().isoformat()})
  audio.play_file_ducking('assets/voice_clip.wav', 100, 0.2)

gpio=GPIOWorker(on_button=on_button)

def scheduler_mode_change(mode, color):
  if mode==1:
    led.start_mode1(); gpio.set_pump(True); socketio.emit('mode_update', {'mode':1})
  elif mode==2:
    hexcol=color or '#FFFFFF'; rgb=tuple(int(hexcol[i:i+2],16) for i in (1,3,5))
    led.start_mode2(rgb); gpio.set_pump(False); socketio.emit('mode_update', {'mode':2,'color':hexcol})
  else:
    led.stop(); gpio.set_pump(False); socketio.emit('mode_update', {'mode':0})

def scheduler_announcement(fp, vol):
  audio.play_file_ducking(fp, vol, 0.2)

sched=Scheduler(scheduler_mode_change, scheduler_announcement)

def initial_import():
  path=os.path.join(os.path.dirname(__file__),'mappings','mapping_dauer.txt')
  if os.path.exists(path):
    import_mapping(path, mode='reset'); refresh_groups()

initial_import(); reload_phase_audio(); gpio.start(); sched.start()

@app.get('/api/status')
def status():
  return jsonify({'mode': led.mode, 'led_count': Config.LED_COUNT})

@app.get('/api/preview')
def preview():
  with SessionLocal() as s:
    groups=[{'id':g.id,'name':g.name,'color':g.color,'led_indices':[int(x) for x in g.led_indices.split(',') if x]} for g in s.query(Group).all()]
  return jsonify({'groups': groups, 'colors': led.get_preview()})

@app.post('/api/mode')
def set_mode():
  data=request.get_json(force=True); mode=int(data.get('mode',0))
  if mode==1:
    led.start_mode1(); gpio.set_pump(True)
  elif mode==2:
    hexcol=data.get('color','#FFFFFF'); rgb=tuple(int(hexcol[i:i+2],16) for i in (1,3,5))
    led.start_mode2(rgb); gpio.set_pump(False)
  else:
    led.stop(); gpio.set_pump(False)
  return jsonify({'ok':True})

@app.post('/api/mode/stop')
def stop_mode():
  led.stop(); gpio.set_pump(False); return jsonify({'ok':True})

@app.route('/api/groups', methods=['GET','POST'])
def groups():
  if request.method=='GET':
    with SessionLocal() as s:
      return jsonify([{'id':g.id,'name':g.name,'color':g.color,'led_indices':[int(x) for x in g.led_indices.split(',') if x]} for g in s.query(Group).all()])
  d=request.get_json(force=True)
  with SessionLocal() as s:
    from models import Group
    g=Group(name=d.get('name','Gruppe'), color=d.get('color','#FFFFFF'), led_indices=','.join(map(str,d.get('led_indices',[]))))
    s.add(g); s.commit()
  refresh_groups(); return jsonify({'ok':True})

@app.route('/api/groups/<int:gid>', methods=['PUT','DELETE'])
def group_update(gid):
  with SessionLocal() as s:
    g=s.get(Group, gid)
    if not g: return jsonify({'error':'not found'}),404
    if request.method=='DELETE': s.delete(g); s.commit(); refresh_groups(); return jsonify({'ok':True})
    d=request.get_json(force=True)
    if 'name' in d: g.name=d['name']
    if 'color' in d: g.color=d['color']
    if 'led_indices' in d: g.led_indices=','.join(map(str,d['led_indices']))
    s.commit()
  refresh_groups(); return jsonify({'ok':True})

@app.post('/api/import-mapping')
def import_map():
  if request.content_type and 'multipart/form-data' in request.content_type:
    f=request.files.get('file'); mode=request.form.get('mode','merge')
    if not f: return jsonify({'error':'no file'}),400
    name='upload_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.txt'
    save=os.path.join(os.path.dirname(__file__),'mappings',name)
    os.makedirs(os.path.dirname(save), exist_ok=True); f.save(save)
    from importer import import_mapping as imp; imp(save, mode=mode)
  else:
    d=request.get_json(force=True); fn=d.get('file'); mode=d.get('mode','merge')
    if not fn: return jsonify({'error':'file required'}),400
    path=os.path.join(os.path.dirname(__file__),'mappings',os.path.basename(fn))
    if not os.path.exists(path): return jsonify({'error':'not found'}),404
    from importer import import_mapping as imp; imp(path, mode=mode)
  refresh_groups(); return jsonify({'ok':True})

def refresh_groups():
  with SessionLocal() as s:
    mapping={}
    for g in s.query(Group).all():
      col=(255,255,255)
      if isinstance(g.color,str) and g.color.startswith('#') and len(g.color)==7:
        col=tuple(int(g.color[i:i+2],16) for i in (1,3,5))
      mapping[g.name]={'indices':[int(x) for x in g.led_indices.split(',') if x], 'color': col}
  led.set_groups(mapping)

if __name__=='__main__':
  socketio.run(app, host='0.0.0.0', port=5000, debug=True)
