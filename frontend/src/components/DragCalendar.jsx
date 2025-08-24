import React,{useEffect,useState} from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
export default function DragCalendar(){
 const [events,setEvents]=useState([])
 const load=()=>fetch('http://localhost:5000/api/calendar').then(r=>r.json()).then(list=>setEvents(list.map(e=>({id:String(e.id),title:`${e.name} (M${e.mode})`,start:e.start,end:e.end,extendedProps:{mode:e.mode,color:e.color}}))))
 useEffect(()=>{load()},[])
 const onDateSelect=(info)=>{ const name=prompt('Name?'); if(!name) return; const mode=parseInt(prompt('Modus (0/1/2)?')||'1'); const color=prompt('Farbe (#RRGGBB)', '#FFFFFF'); fetch('http://localhost:5000/api/calendar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name, start:info.startStr, end:info.endStr, mode, color})}).then(load) }
 const onEventDropResize=(chg)=>{ const ev=chg.event; fetch('http://localhost:5000/api/calendar/'+ev.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({start:ev.start.toISOString(), end:ev.end?ev.end.toISOString():ev.start.toISOString()})}).then(load) }
 const onEventClick=(ci)=>{ if(confirm('Event löschen?')) fetch('http://localhost:5000/api/calendar/'+ci.event.id,{method:'DELETE'}).then(load) }
 return (<div style={{padding:12,border:'1px solid #eee',borderRadius:8,marginBottom:16}}>
  <h2>Kalender</h2>
  <FullCalendar plugins={[dayGridPlugin, interactionPlugin]} initialView='dayGridMonth' selectable editable events={events} select={onDateSelect} eventDrop={onEventDropResize} eventResize={onEventDropResize} eventClick={onEventClick} height='auto'/>
 </div>)
}
