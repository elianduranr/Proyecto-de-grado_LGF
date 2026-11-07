import {useState} from 'react';
import {ArrowDownRight,ChevronRight,RefreshCw,Search,SlidersHorizontal} from 'lucide-react';
import type {EChartsOption} from 'echarts';
import {date,num,pct} from './api';
import {Card,Chart,ErrorBox,MetricCard,Select,Tag,chartBase,useResource} from './components';
import {Filters,human} from './ComparisonFilters';
import type {Comparison,ErrorRow} from './types';
import {EvaluationPicker} from './EvaluationPicker';
import {WeekPicker} from './WeekPicker';

const levels=[{value:'producto',label:'Producto'},{value:'color',label:'Producto y color'},{value:'variedad',label:'Producto, color y variedad'},{value:'semana_objetivo',label:'Semana'}];
const wape=(v:number|null|undefined)=>v==null?'—':`${v.toFixed(2).replace('.',',')} %`;
const rowLabel=(r:ErrorRow)=>Object.entries(r.identity).map(([key,value])=>key==='semana_objetivo'?date(value):human(value)).join(' / ');

export function ComparisonPage({initialEvaluation='updated',initialHorizon='1'}:{initialEvaluation?:string;initialHorizon?:string}){
 const [evaluation,setEvaluation]=useState(initialEvaluation);
 const [horizon,setHorizon]=useState(initialHorizon);
 const [filter,setFilter]=useState({product:'',color:'',variety:''});
 const [selectedWeeks,setSelectedWeeks]=useState<string[]>([]);
 const [level,setLevel]=useState('producto');
 const [focus,setFocus]=useState<'model'|'engineer'>('model');
 const [search,setSearch]=useState('');const [page,setPage]=useState(1);
 const query=new URLSearchParams({...filter,evaluation,horizon,weeks:selectedWeeks.join(','),level,focus});
 const result=useResource<Comparison>(`/comparison?${query}`);
 // No mostrar los resultados del filtro anterior mientras llega la nueva consulta.
 const d=result.loading?undefined:result.data;
 const [showTotals,setShowTotals]=useState(false);
 const [weeklyView,setWeeklyView]=useState('production');
 const rows=(d?.breakdown||[]).filter(r=>rowLabel(r).toLocaleLowerCase().includes(search.toLocaleLowerCase()));
 const shown=rows.slice((page-1)*20,page*20);
 const top=(d?.breakdown||[]).slice(0,8);
 function reset(){setFilter({product:'',color:'',variety:''});setSelectedWeeks([]);setLevel('producto');setSearch('');setPage(1)}
 function drill(row:ErrorRow){
  if(level==='semana_objetivo'){setSelectedWeeks([row.identity.semana_objetivo]);setLevel('producto')}
  else if(level==='producto'){setFilter({product:row.identity.producto,color:'',variety:''});setLevel('color')}
  else if(level==='color'){setFilter({product:row.identity.producto,color:row.identity.color,variety:''});setLevel('variedad')}
  else{setFilter({product:row.identity.producto,color:row.identity.color,variety:row.identity.variedad});setLevel('semana_objetivo')}
  setSearch('');setPage(1);
 }
 function back(){
  if(level==='semana_objetivo'){setFilter({...filter,variety:''});setLevel('variedad')}
  else if(level==='variedad'){setFilter({...filter,color:'',variety:''});setLevel('color')}
  else{setFilter({product:'',color:'',variety:''});setLevel('producto')}
  setSearch('');setPage(1);
 }
 function exportTable(){
  const columns=['Grupo','Casos','Real (tallos)','Modelo (tallos)','Ingeniero (tallos)','WAPE modelo (%)','WAPE ingeniero (%)','Sesgo modelo (%)','Sesgo ingeniero (%)','Error absoluto modelo','Error absoluto ingeniero'];
  const data=rows.map(r=>[rowLabel(r),r.cases,r.real,r.model.estimate,r.engineer.estimate,r.model.wape,r.engineer.wape,r.model.bias,r.engineer.bias,r.model.absolute,r.engineer.absolute]);
  const csv=[columns,...data].map(row=>row.map(v=>`"${String(v??'').replaceAll('"','""')}"`).join(';')).join('\r\n');
  const url=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8;'}));const a=document.createElement('a');a.href=url;a.download=`errores_${evaluation}_H${horizon}_${level}.csv`;a.click();URL.revokeObjectURL(url);
 }
 const bars:EChartsOption={...chartBase,grid:{left:8,right:30,top:15,bottom:45,containLabel:true},
  xAxis:{type:'value',name:'Tallos de error absoluto',nameLocation:'middle',nameGap:26,axisLabel:{formatter:(v:number)=>Math.abs(v)>=1000?`${v/1000} mil`:String(v)}},
  yAxis:{type:'category',inverse:true,data:top.map(rowLabel),axisLabel:{width:145,overflow:'truncate',fontSize:10}},
  series:[{name:'Modelo 19 · sin clima',type:'bar',data:top.map(r=>r.model.absolute),itemStyle:{color:'#800020'}},
          {name:'Ingeniero',type:'bar',data:top.map(r=>r.engineer.absolute),itemStyle:{color:'#315f82'}}]};
 const trajectory:EChartsOption=weeklyView==='difference'?{...chartBase,xAxis:{type:'category',data:d?.series.map(r=>date(r.semana_objetivo))||[]},yAxis:{type:'value',name:'Estimado − real (tallos)'},series:[
  {name:'Diferencia del modelo',type:'bar',data:d?.series.map(r=>r.Seleccion_pre2026-r.y),itemStyle:{color:'#800020'}},
  {name:'Diferencia del ingeniero',type:'bar',data:d?.series.map(r=>r.ingeniero-r.y),itemStyle:{color:'#315f82'}}]}:{...chartBase,xAxis:{type:'category',data:d?.series.map(r=>date(r.semana_objetivo))||[]},yAxis:{type:'value',name:'Tallos'},series:[
  {name:'Real',type:'line',symbolSize:5,data:d?.series.map(r=>r.y),itemStyle:{color:'#64806d'}},
  {name:'Modelo 19 · sin clima',type:'line',symbolSize:5,data:d?.series.map(r=>r.Seleccion_pre2026),itemStyle:{color:'#800020'}},
  {name:'Ingeniero',type:'line',symbolSize:5,lineStyle:{type:'dashed'},data:d?.series.map(r=>r.ingeniero),itemStyle:{color:'#315f82'}}]};

 return <>
  <div className="page-intro"><div><span className="eyebrow">DEL RESULTADO AL ORIGEN DEL ERROR</span><h1>¿Dónde nos equivocamos?</h1><p>Elige las semanas y acércate del producto al color y la variedad. Comparamos al modelo 19 sin clima con el ingeniero, sobre los mismos casos.</p></div><Tag><Search size={13}/> Comparador de errores</Tag></div>
  <Card className="comparison-controls">
   <div className="section-heading"><div><h2>1. Elige qué comparar</h2><p>Las semanas corresponden a la producción que se quería estimar.</p></div><button className="button secondary" onClick={reset}>Limpiar filtros</button></div>
   <EvaluationPicker value={evaluation} onChange={v=>{setEvaluation(v);if(v==='train')setHorizon('1');reset()}}/>
   <div className="comparison-filter-grid">
    <Select label="Horizonte" value={horizon} onChange={v=>{setHorizon(v);reset()}} options={(evaluation==='train'?[1]:[1,2,3,4,5]).map(h=>({value:String(h),label:`H${h} · semana +${h}`}))}/>
   </div>
   <WeekPicker key={`${evaluation}-${horizon}`} weeks={result.data?.available_weeks||[]} selected={selectedWeeks} onChange={v=>{setSelectedWeeks(v);setPage(1)}}/>
   <div className="comparison-filter-grid"><Filters identities={result.data?.identities||[]} value={filter} onChange={v=>{setFilter(v);setLevel(v.variety?'semana_objetivo':v.color?'variedad':v.product?'color':'producto');setPage(1);setSearch('')}}/></div>
   <div className="comparison-context"><button className="link-button" onClick={()=>{setFilter({product:'',color:'',variety:''});setLevel('producto');setSearch('');setPage(1)}}>Gaitana · todos</button><ChevronRight size={12}/><button className="link-button" onClick={()=>{setFilter({...filter,color:'',variety:''});setLevel('color');setPage(1);setSearch('')}}>{filter.product?human(filter.product):'Todos los productos'}</button>{filter.color&&<><ChevronRight size={12}/><button className="link-button" onClick={()=>{setFilter({...filter,variety:''});setLevel('variedad');setPage(1);setSearch('')}}>{human(filter.color)}</button></>}{filter.variety&&<><ChevronRight size={12}/><span>{human(filter.variety)}</span></>}</div>
  </Card>
  <ErrorBox message={result.error}/>{result.loading&&<p className="loading" role="status">Actualizando la comparación…</p>}
  <Card className="comparison-period"><strong>{d?.evaluation_label||'Consultando evaluación'}</strong><p>{d?.test_weeks.length?`${d.test_weeks.length<=8?d.test_weeks.map(w=>w.label).join(' · '):`${d.test_weeks[0].label} a ${d.test_weeks.at(-1)!.label}`} · ${d.test_weeks.length} semanas seleccionadas · ${num(d.model.cases)} casos comparables`:'Sin casos comparables para esta selección.'}</p><small>{d?.evaluation_note}</small>{d?.data_version&&<small>Versión de datos: {d.data_version} · producción hasta {date(d.source_through||'')}. Actualización automática.</small>}<details><summary>Ver las semanas incluidas en los indicadores</summary><p>{d?.test_weeks.map(w=>`${w.label} (${date(w.date)})`).join(' · ')}</p></details>{!!d?.unmatched_cases&&<p className="caption">{num(d.unmatched_cases)} casos sin estimado nominal del ingeniero quedan fuera de ambos indicadores.</p>}<button className="button secondary" onClick={result.reload}><RefreshCw size={14}/>Actualizar evaluación</button></Card>
  {d?.available_cases&&!d.model.cases?<Card><h2>Esta semana tiene predicciones, pero no pareja nominal del ingeniero</h2><p>Hay {num(d.available_cases)} casos del modelo con producción real. Su WAPE es {wape(d.model_available?.wape)}. No asignamos un ganador ni utilizamos un archivo posterior como si fuera H1 de esta semana.</p></Card>:null}
  <div className="metrics"><MetricCard label="WAPE del modelo" value={wape(d?.model.wape)} description="Magnitud del error · mismos casos" accent/><MetricCard label="WAPE del ingeniero" value={wape(d?.engineer.wape)} description="Magnitud del error · mismos casos"/><MetricCard label="Sesgo del modelo" value={pct(d?.model.bias)} description={`${num(d?.model.difference)} tallos netos · estimado menos real`}/><MetricCard label="Sesgo del ingeniero" value={pct(d?.engineer.bias)} description={`${num(d?.engineer.difference)} tallos netos · estimado menos real`}/></div>
  <Card><div className="section-heading"><div><h2>2. Encuentra dónde se concentra el error</h2><p>Ordenamos de mayor a menor error absoluto de quien selecciones.</p></div><SlidersHorizontal size={20}/></div>
   <div className="comparison-filter-grid"><Select label="Ver el error por" value={level} options={levels} onChange={v=>{setLevel(v);setSearch('');setPage(1)}}/><Select label="Priorizar errores de" value={focus} options={[{value:'model',label:'Nuestro modelo'},{value:'engineer',label:'El ingeniero'}]} onChange={v=>{setFocus(v as 'model'|'engineer');setPage(1)}}/></div>
   {top.length?<Chart label="Mayores contribuciones al error absoluto del modelo y del ingeniero" option={bars} height={Math.max(240,top.length*48+75)}/>:<p className="empty">No hay errores comparables para mostrar. Prueba otro período o quita un filtro.</p>}
   <p className="caption">Se muestran hasta ocho grupos. El error absoluto suma las diferencias de cada caso sin compensar sobreestimaciones con subestimaciones. Un grupo grande puede aportar más error en tallos aunque tenga un WAPE menor.</p>
  </Card>
  <Card><div className="section-heading"><div><h2>3. Revisa el detalle</h2><p>Pulsa un grupo para explorar producto → color → variedad → semanas.</p></div><button className="button secondary" onClick={()=>setShowTotals(!showTotals)}>{showTotals?'Ocultar cantidades':'Ver cantidades estimadas'}</button></div>
   <div className="detail-navigation"><button className="button secondary" disabled={level==='producto'&&!filter.product&&!filter.color&&!filter.variety} onClick={back}>← Volver al nivel anterior</button><span className="detail-filter-label">Selecciona directamente o pulsa una fila para profundizar.</span></div>
   <div className="comparison-filter-grid"><Filters labelPrefix="Detalle · " identities={result.data?.identities||[]} value={filter} onChange={v=>{setFilter(v);setLevel(v.variety?'semana_objetivo':v.color?'variedad':v.product?'color':'producto');setPage(1);setSearch('')}}/></div>
   <button className="button secondary" disabled={!rows.length} onClick={exportTable}>Descargar tabla filtrada (CSV)</button><label className="field comparison-search"><span>Buscar en esta tabla</span><input value={search} onChange={e=>{setSearch(e.target.value);setPage(1)}} placeholder="Nombre de producto, color o variedad"/></label>
   <div className="table-scroll"><table className="error-detail-table"><thead><tr><th>Grupo · explorar</th><th>Real (tallos)</th>{showTotals&&<><th>Estimado modelo</th><th>Estimado ingeniero</th></>}<th>WAPE modelo</th><th>WAPE ingeniero</th><th>Sesgo modelo</th><th>Sesgo ingeniero</th><th>Menor error</th><th>Error absoluto modelo</th><th>Error absoluto ingeniero</th><th>Aporte al error {focus==='model'?'del modelo':'del ingeniero'}</th></tr></thead><tbody>{shown.map(r=><tr key={JSON.stringify(r.identity)}><td><button className="link-button" onClick={()=>drill(r)}>{rowLabel(r)}<ArrowDownRight size={13}/></button><small>{num(r.cases)} casos</small></td><td>{num(r.real)}</td>{showTotals&&<><td>{num(r.model.estimate)}</td><td>{num(r.engineer.estimate)}</td></>}<td>{wape(r.model.wape)}</td><td>{wape(r.engineer.wape)}</td><td>{pct(r.model.bias)}</td><td>{pct(r.engineer.bias)}</td><td><Tag tone={r.model.absolute<r.engineer.absolute?'green':'neutral'}>{r.model.absolute===r.engineer.absolute?'Igual':r.model.absolute<r.engineer.absolute?'Modelo':'Ingeniero'}</Tag></td><td>{num(r.model.absolute)}</td><td>{num(r.engineer.absolute)}</td><td><div className="error-share"><span style={{width:`${r[focus].share}%`}}/></div>{r[focus].share.toFixed(1).replace('.',',')} %</td></tr>)}</tbody></table></div>
   {!shown.length&&<p className="empty">No hay filas para estos filtros o esta búsqueda.</p>}
   <div className="comparison-pagination"><small>{rows.length?`${(page-1)*20+1}–${Math.min(page*20,rows.length)} de ${rows.length} grupos`: '0 grupos'} · Buscar sólo cambia esta tabla; los indicadores mantienen todos los filtros superiores.</small><div><button className="button secondary" disabled={page<=1} onClick={()=>setPage(page-1)}>Anterior</button><button className="button secondary" disabled={page*20>=rows.length} onClick={()=>setPage(page+1)}>Siguiente</button></div></div>
  </Card>
  <Card><div className="section-heading"><div><h2>4. Mira cómo ocurrió en el tiempo</h2><p>Real, modelo e ingeniero para la selección actual.</p></div><Tag>H{horizon} · tallos</Tag></div><Select label="Qué ver en el tiempo" value={weeklyView} onChange={setWeeklyView} options={[{value:'production',label:'Producción real y estimados'},{value:'difference',label:'Diferencias en tallos: estimado menos real'}]}/>{weeklyView==='difference'&&<p className="caption">Arriba de cero: sobreestimación. Abajo: subestimación. Son diferencias netas semanales: pueden compensarse entre variedades y no equivalen al error absoluto usado para el WAPE.</p>}<Chart label="Real y estimados de la selección en el tiempo" option={trajectory} height={300}/><details><summary>Cómo interpretar estos resultados</summary><p>WAPE = suma del error absoluto / producción real. Sesgo = (estimado − real) / real: positivo sobreestima y negativo subestima. Aporte al error = error absoluto del grupo / error absoluto de toda la selección. El WAPE total se calcula desde los casos; no es el promedio de los porcentajes de la tabla. No se combinan horizontes para evitar contar varias veces la misma producción.</p></details></Card>
 </>
}
