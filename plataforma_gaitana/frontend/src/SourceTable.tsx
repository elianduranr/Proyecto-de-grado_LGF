import {CloudDownload,FileUp} from 'lucide-react';
import {date,num,week} from './api';
import {Tag} from './components';
import type {Status} from './types';
import {requiresUpdate} from './sourceReadiness';

export function SourceTable({status,disabled,onUpload,onWebFlor,useClimate=false}:{status:Status;disabled:boolean;onUpload:(source:string)=>void;onWebFlor:()=>void;useClimate?:boolean}){
 const origin=new Date(`${status.origin}T00:00:00Z`);
 const lastTarget=new Date(origin.getTime()+28*864e5).toISOString().slice(0,10);
 const period=`${week(status.origin)}–${week(lastTarget)}`;
 const edition=`${week(status.origin)} de ${origin.getUTCFullYear()}`;
 const previousThursday=new Date(origin.getTime()-4*864e5).toISOString().slice(0,10);
 const engineerMissing=!status.sources.find(s=>s.source==='estimados')?.reference_available;
 return <div className="source-table-wrap"><table className="source-table" aria-label="Fuentes disponibles y qué actualizar para H1">
  <thead><tr><th scope="col">Fuente</th><th scope="col">Ya está cargado</th><th scope="col">Qué necesitas para este pronóstico</th><th scope="col">Siguiente acción</th></tr></thead>
  <tbody>{status.sources.map(source=><tr key={source.source}>
   <td data-label="Fuente"><strong>{source.name}</strong><Tag tone={requiresUpdate(source,useClimate)||(source.source==='planos'&&!source.reference_available)?'red':source.tone}>{requiresUpdate(source,useClimate)?`Obligatorio · ${source.pending_files||source.pending_uploads?'por procesar':'actualizar fuente'}`:source.source==='estimados'&&engineerMissing&&!source.pending_files&&!source.pending_uploads?`Sin estimado para comparar ${week(status.origin)}`:source.status_label}</Tag></td>
   <td data-label="Ya está cargado"><strong>{source.source==='estimados'?(source.latest_edition?`Último archivo: empieza en ${week(source.latest_edition)}`:'Sin estimados procesados'):(source.through?date(source.through):'Sin datos procesados')}</strong>
    <small>{source.source==='planos'&&source.through?`Último plano: ${week(source.through)}`:source.source==='estadisticas'?'Fecha del último corte utilizado en las curvas':source.source==='estimados'?`Su primera semana pronosticada (H1) empieza el ${date(source.latest_edition||'')}.`:'Último día con registros'}</small>
    {source.source==='estimados'&&source.through&&<small>Incluye semanas futuras hasta el {date(source.through)}. Eso no reemplaza un archivo nuevo para comparar el próximo pronóstico.</small>}
    {source.webflor_closed_through&&<small>WebFlor consultado hasta {date(source.webflor_closed_through)} · días cerrados. La fecha superior indica el último día con movimientos.</small>}
    <small>{num(source.rows)} registros · {num(source.loaded_files??0)} archivos procesados</small>
    {!!source.latest_files?.length&&<details><summary>Ver archivos recientes</summary><ul>{source.latest_files.map(file=><li key={file}>{file}</li>)}</ul></details>}
   </td>
   <td data-label="Para este pronóstico"><strong>{source.source==='estimados'?`Estimado del ingeniero ${period}`:source.period_needed}</strong><p>{source.source==='estimados'?`La primera semana del nombre debe ser ${edition}: ése es su H1. Corresponde al envío del jueves ${date(previousThursday)}. Es opcional: permite comparar al ingeniero con el modelo; no se necesita para generar.`:source.purpose}</p>
    {!!(source.pending_files||source.pending_uploads)&&<div className={`source-pending ${requiresUpdate(source,useClimate)?'required-update':''}`}>{requiresUpdate(source,useClimate)&&<strong>Obligatorio antes de generar. </strong>}{source.pending_files} archivos originales y {source.pending_uploads} cargas por procesar. No necesitas volver a subirlos.{!!source.examples.length&&<details><summary>Ver pendientes</summary><ul>{source.examples.map(name=><li key={name}>{name}</li>)}</ul></details>}</div>}
   </td>
   <td data-label="Siguiente acción"><p>{source.source==='estimados'?(engineerMissing?`Suba el Excel del ingeniero cuyo nombre indica ${period.replaceAll('S','')}. Si todavía no lo tiene, puede generar el pronóstico igualmente.`:'El estimado para este H1 ya está cargado. Sólo suba otra edición si tiene un archivo nuevo.'):source.instruction}</p>{source.source==='estimados'&&engineerMissing&&<small>La semana en curso que también aparezca dentro del Excel no es H1; manda la primera semana del nombre del archivo.</small>}<div className="source-buttons">
    {source.source==='produccion'&&<><button className="button primary" onClick={onWebFlor} disabled={disabled||!status.webflor_configured||!status.dataset_id}><CloudDownload size={15}/>Actualizar desde WebFlor</button><small>Vuelve a consultar los últimos 45 días hasta ayer y sustituye ese rango en una nueva versión validada. Incluye correcciones de días ya cargados.</small></>}
    <button className="button secondary" disabled={disabled} onClick={()=>onUpload(source.source)}><FileUp size={15}/>{source.source==='produccion'?'Usar Excel':source.source==='planos'?'Cargar planos':source.source==='estimados'&&engineerMissing?`Subir estimado ${period}`:'Cargar archivo'}</button>
   </div></td>
  </tr>)}</tbody>
 </table></div>
}
