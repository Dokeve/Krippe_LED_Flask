import React,{useEffect,useState} from 'react'
export default function LivePreview(){
 const [groups,setGroups]=useState([])
 const load=()=>fetch('http://localhost:5000/api/preview').then(r=>r.json()).then(d=>setGroups(d.groups||[]))
 useEffect(()=>{load(); const id=setInterval(load,800); return ()=>clearInterval(id)},[])
 return (<div style={{padding:12,border:'1px solid #eee',borderRadius:8,marginBottom:16}}>
   <h2>Live Preview</h2>
   <div style={{display:'flex',flexDirection:'column',gap:8,maxHeight:500,overflow:'auto'}}>
     {groups.map(g=> <Row key={g.id} group={g}/>) }
   </div>
 </div>)
}
function Row({group}){
  const color=group.color||'#FFFFFF'; const leds=group.led_indices||[]
  return (<div>
    <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:4}}>
      <div style={{width:12,height:12,background:color,borderRadius:2}}/>
      <b>{group.name}</b><span style={{opacity:0.6}}>({leds.length} LEDs)</span>
    </div>
    <div style={{display:'grid',gridTemplateColumns:`repeat(${Math.max(leds.length,1)}, 10px)`,gap:1}}>
      {leds.map((i,idx)=>(<div key={idx} title={`LED ${i}`} style={{width:10,height:10,background:color,borderRadius:2}}/>))}
    </div>
  </div>)
}
