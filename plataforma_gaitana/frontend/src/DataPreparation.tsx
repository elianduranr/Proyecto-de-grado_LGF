import {useEffect,useState} from 'react';
import {CalendarDays,Check,CloudSun,Database,LoaderCircle,Play,RefreshCw} from 'lucide-react';
import {api,date,num,week} from './api';
import {Card,ErrorBox,Tag} from './components';
import type {Job,Status} from './types';
import {SourceTable} from './SourceTable';
import {requiresUpdate} from './sourceReadiness';

export function DataPreparation({status,editable,variant,onVariant,onGenerate,generating,reload,onUpload}:{status?:Status;editable:boolean;variant:string;onVariant:(v:string)=>void;onGenerate:()=>void;generating:boolean;reload:()=>void;onUpload:(source:string)=>void}){
 const [jobId,setJobId]=useState('');const [job,setJob]=useState<Job>();const [error,setError]=useState('');
 useEffect(()=>{if(status?.etl_job)setJobId(status.etl_job.id)},[status?.etl_job?.id]);
 useEffect(()=>{
  if(!jobId)return;let live=true;let timer:ReturnType<typeof setTimeout>;
  async function poll(){try{const result=await api<Job>(`/jobs/${jobId}`);if(!live)return;setJob(result);
   if(result.state==='completado'||result.state==='error'){setJobId('');reload();if(result.state==='error')setError(result.message)}
   else timer=setTimeout(poll,4000);
  }catch(e){if(live){setError((e as Error).message);setJobId('')}}}
  void poll();return()=>{live=false;clearTimeout(timer)};
 },[jobId]);
 async function process(){setError('');try{const result=await api<{job_id:string}>('/data/rebuild',{method:'POST'});setJobId(result.job_id);reload()}catch(e){setError((e as Error).message)}}
 async function webflor(){setError('');try{const result=await api<{job_id:string}>('/data/webflor',{method:'POST'});setJobId(result.job_id);reload()}catch(e){setError((e as Error).message)}}
 const active=!!jobId||!!status?.etl_job;
 const mandatoryPending=status?.sources.some(source=>requiresUpdate(source,variant==='Clima_basico'));
 return <Card className="readiness">
  <div className="readiness-main"><div className="round-icon"><CalendarDays size={24}/></div><div><span className="eyebrow">FUENTES PARA LA SEMANA H1 ELEGIDA</span><h2>{status?`${week(status.origin)} · ${date(status.origin)}`:'Consultando fuentes…'}</h2><p>Producción real procesada hasta la semana de {status?date(status.latest_observed_week):'…'}. H1–H5 · Gaitana.</p></div><Tag tone={active?'amber':status?.ready&&!mandatoryPending?'green':status?'red':'neutral'}>{status?.ready?<Check size={13}/>:<Database size={13}/>} {active?'Procesando fuentes':status?.ready&&!mandatoryPending?'Listo para generar':'Requiere preparación'}</Tag></div>
  <div className="forecast-calendar" aria-label="Semanas del próximo pronóstico">{status&&[0,1,2,3,4].map(index=>{const target=new Date(new Date(status.origin+'T12:00:00').getTime()+index*7*864e5).toISOString().slice(0,10);return <div key={index}><span>H{index+1}{index===0?' · primera semana':''}</span><strong>{week(target)}</strong><small>Desde {date(target)}</small></div>})}</div>
  <p className="preparation-explainer">Las cinco semanas parten de H1, la semana que elegiste arriba. La producción y el clima necesarios deben ser anteriores a ese lunes. Revisa qué está cargado y qué debes actualizar para ese inicio. <strong>«Procesado» no significa que la fuente tenga que renovarse cada semana.</strong></p>
  {status&&<p className={`note ${status.available_origins.includes(status.origin)?'':'red'}`}>{status.generation_note}</p>}
  {status&&<SourceTable status={status} disabled={!editable||active||generating} onUpload={onUpload} onWebFlor={webflor} useClimate={variant==='Clima_basico'}/>}
  <p className="caption">Los conteos conservan las fincas presentes en las fuentes. En esta versión, las fechas de referencia y el pronóstico se presentan para Gaitana.</p>
  {status?.processing_required&&<div className={`note ${mandatoryPending?'red':'amber'}`}><Database size={17}/><span>{mandatoryPending&&<strong>Obligatorio antes de generar. </strong>}Hay archivos disponibles que todavía no alimentan el pronóstico. Usa <strong>Procesar archivos</strong>; no necesitas volver a subirlos. El corte avanzará después de validar la limpieza, las proyecciones y la base analítica.</span></div>}
  {status&&!status.processing_required&&status.data_age_days>7&&<div className="note amber"><CalendarDays size={17}/><span>La semana H1 elegida está {status.data_age_days} días detrás del calendario. Si buscas un pronóstico actual, elige una semana más reciente y revisa la producción disponible.</span></div>}
  {status&&!status.climate_ready&&<p className="caption">El clima no alcanza el origen actual. Puedes generar con <strong>Sin clima</strong>; el sistema no inventa mediciones para habilitar la otra variante.</p>}
  {status?.prediction_basis&&!active&&<p className="caption">Para este origen: {num(status.prediction_basis.theory)} casos usan teoría corregida y {num(status.prediction_basis.memory)} usan producción reciente como referencia. Un caso es una combinación de producto, color, variedad y horizonte. {!!status.prediction_basis.missing_plan&&<>En {num(status.prediction_basis.missing_plan)} casos aún no hay plano de este origen; para incorporar su proyección teórica, carga el plano de {week(status.origin)}. Puedes pronosticar con la ruta de producción reciente del mismo modelo.</>}</p>}
  <div className="preparation-actions"><button className="button secondary" disabled={!editable||active||generating} onClick={process}><RefreshCw size={16} className={active?'spin':''}/>{active?'Procesando…':'Procesar archivos'}</button><small><strong>Dos controles antes de activar:</strong> 1. Archivo y modalidad válidos. 2. Limpieza, conservación de tallos y conteos SQL verificados. Si falla, la base vigente se conserva.</small></div>
  <ErrorBox message={error}/>
  {!active&&job?.state==='completado'&&<div className="note green" role="status"><Check size={17}/><span>{job.message}</span></div>}
  {active&&<div className="progress" role="status"><span>{job?.message||status?.etl_job?.message||'Preparando la carga…'}</span><progress max="100" value={job?.progress||status?.etl_job?.progress||0}/></div>}
  <div className="generate-row"><label className="toggle"><input type="checkbox" checked={variant==='Clima_basico'} disabled={!status?.climate_ready||active} onChange={e=>onVariant(e.target.checked?'Clima_basico':'Sin_clima')}/><span className="toggle-track"/><CloudSun size={18}/><span>Usar clima<small>{variant==='Sin_clima'?'Modelo seleccionado del 19':'Variante básica validada del 19'}</small></span></label><div><small className="muted">Crear una propuesta no modifica la versión publicada.</small><button className="button primary" disabled={!status?.ready||generating||active||!editable||(variant==='Clima_basico'&&!status.climate_ready)} onClick={onGenerate}>{generating?<LoaderCircle className="spin" size={17}/>:<Play size={16}/>}Generar pronóstico</button></div></div>
 </Card>;
}
