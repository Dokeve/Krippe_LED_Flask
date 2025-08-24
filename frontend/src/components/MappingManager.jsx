import React,{useState} from 'react'
const PRESETS=['mapping_off.txt','mapping_dauer.txt','mapping_day.txt','mapping_d2n.txt','mapping_night.txt','mapping_n2d.txt']
export default function MappingManager(){
 const [file,setFile]=useState(PRESETS[1]); const [mode,setMode]=useState('merge'); const [upload,setUpload]=useState(null)
 const run=async()=>{
  if(upload){ const fd=new FormData(); fd.append('file',upload); fd.append('mode',mode); await fetch('http://localhost:5000/api/import-mapping',{method:'POST',body:fd}) }
  else{ await fetch('http://localhost:5000/api/import-mapping',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file,mode})}) }
  alert('Import abgeschlossen')
 }
 return (<div style={{padding:12,border:'1px solid #eee',borderRadius:8,marginBottom:16}}>
  <h2>Mapping verwalten</h2>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr auto',gap:8}}>
    <select value={file} onChange={e=>setFile(e.target.value)}>{PRESETS.map(p=><option key={p} value={p}>{p}</option>)}</select>
    <select value={mode} onChange={e=>setMode(e.target.value)}>
      <option value='merge'>merge</option><option value='reset'>reset</option>
    </select>
    <input type='file' accept='.txt' onChange={e=>setUpload(e.target.files?.[0]||null)} />
    <button onClick={run}>Import starten</button>
  </div>
 </div>)
}
