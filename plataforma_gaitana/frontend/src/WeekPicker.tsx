import {useState} from 'react';
import {date} from './api';
import {Select} from './components';

export function WeekPicker({weeks,selected,onChange}:{weeks:{date:string;label:string;winner?:string|null;model_wape?:number|null;engineer_wape?:number|null;cases?:number}[];selected:string[];onChange:(v:string[])=>void}){
 const [year,setYear]=useState('');
 const years=[...new Set(weeks.map(w=>w.label.slice(0,4)))];
 const visible=weeks.filter(w=>!year||w.label.startsWith(year));
 const all=selected.length===0;
 const shown=selected.length?weeks.filter(w=>selected.includes(w.date)):weeks;
 function toggle(value:string){const current=all?[]:selected;const next=current.includes(value)?current.filter(w=>w!==value):[...current,value];onChange(next.sort())}
 return <div className="week-picker">
  <div className="week-toolbar"><div><strong>Semanas objetivo</strong><small>{all?'Todas las semanas disponibles':`${shown.length} semanas seleccionadas`}. Pulsa una semana para verla; marca otras para compararlas juntas.</small></div><Select label="Año de las semanas" value={year} onChange={setYear} options={[{value:'',label:'Todos los años'},...years.map(v=>({value:v,label:v}))]}/></div>
  <div className="week-shortcuts"><button className="button secondary" aria-pressed={all} onClick={()=>onChange([])}>Todas</button>{[1,4,8].map(n=><button key={n} className="button secondary" onClick={()=>onChange(visible.slice(-n).map(w=>w.date))} disabled={!visible.length}>{n===1?'Última disponible':`Últimas ${n}`}</button>)}<details><summary>Seleccionar un rango</summary><div className="comparison-filter-grid"><Select label="Desde" value={shown[0]?.date||''} options={visible.map(w=>({value:w.date,label:w.label}))} onChange={v=>{const end=shown.at(-1)?.date||v;onChange(weeks.filter(w=>w.date>=v&&w.date<=(end<v?v:end)).map(w=>w.date))}}/><Select label="Hasta" value={shown.at(-1)?.date||''} options={visible.map(w=>({value:w.date,label:w.label}))} onChange={v=>{const start=shown[0]?.date||v;onChange(weeks.filter(w=>w.date<=(v)&&w.date>=(start>v?v:start)).map(w=>w.date))}}/></div></details></div>
  <div className="week-winner-legend"><span className="model">Modelo: menor WAPE</span><span className="engineer">Ingeniero: menor WAPE</span><span>Gris: empate o sin comparación</span></div>
  <div className="week-grid" role="group" aria-label="Seleccionar semanas objetivo">{visible.map(w=><button key={w.date} className={`winner-${w.winner||'none'} ${selected.includes(w.date)?'selected':''}`} title={`WAPE modelo: ${w.model_wape?.toFixed(2)??'—'} % · ingeniero: ${w.engineer_wape?.toFixed(2)??'—'} % · ${w.cases??0} casos comunes`} aria-pressed={selected.includes(w.date)} aria-label={`${w.label} desde ${date(w.date)}`} onClick={()=>toggle(w.date)}><strong>{w.label}</strong><small>{date(w.date)}</small><small>{w.winner==='model'?'Modelo':w.winner==='engineer'?'Ingeniero':w.winner==='tie'?'Empate':'Sin comparación'}</small></button>)}</div>
  {!weeks.length&&<p className="empty">No hay semanas comparables en esta evaluación y horizonte.</p>}
  <p className="caption">{all?'El análisis incluye todo el período.':`Selección: ${shown.map(w=>w.label).join(' · ')}.`} Son las semanas de producción estimada; el horizonte indica con cuánta anticipación se pronosticaron. La selección se mantiene al explorar colores y variedades.</p>
 </div>
}
