import React,{useState} from 'react'
export default function ModeControl(){
  const [color,setColor]=useState('#FFFFFF')
  const post=(mode)=>fetch('http://localhost:5000/api/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(mode)})
  return (<div style={{padding:12,border:'1px solid #eee',borderRadius:8,marginBottom:16}}>
    <h2>Modi</h2>
    <button onClick={()=>post({mode:1})}>Modus 1</button>
    <input type='color' value={color} onChange={e=>setColor(e.target.value)}/>
    <button onClick={()=>post({mode:2,color})}>Modus 2</button>
    <button onClick={()=>fetch('http://localhost:5000/api/mode/stop',{method:'POST'})}>Stop</button>
  </div>)
}
