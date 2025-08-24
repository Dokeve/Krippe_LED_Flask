import React from 'react'
import ModeControl from './ModeControl'
import MappingManager from './MappingManager'
import LivePreview from './LivePreviewRows'
import DragCalendar from './DragCalendar'
export default function App(){
  return (<div style={{padding:16, display:'grid', gridTemplateColumns:'1fr 1fr', gap:16}}>
    <div>
      <h1>LED Control Suite</h1>
      <ModeControl/>
      <MappingManager/>
      <LivePreview/>
    </div>
    <div>
      <DragCalendar/>
    </div>
  </div>)
}
