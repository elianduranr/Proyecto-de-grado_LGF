import {useState} from 'react';
import {Check,LoaderCircle,Save,Upload,X} from 'lucide-react';
import {Dialog,ErrorBox,Select} from './components';

type Receipt={duplicate:boolean;state:string;report:{message:string}};
type Entry={file:File;state:'pending'|'sending'|'received'|'duplicate'|'error';percent:number;message:string};

function send(form:FormData,onProgress:(percent:number)=>void):Promise<Receipt>{
 return new Promise((resolve,reject)=>{
  const xhr=new XMLHttpRequest();xhr.open('POST','/api/uploads');xhr.timeout=180000;
  const token=localStorage.getItem('gaitana_token');if(token)xhr.setRequestHeader('Authorization',`Bearer ${token}`);
  xhr.upload.onprogress=e=>{if(e.lengthComputable)onProgress(Math.round(100*e.loaded/e.total))};
  xhr.onload=()=>{let body;try{body=JSON.parse(xhr.responseText)}catch{reject(new Error('El servidor no confirmó la recepción. Reintenta; los archivos ya recibidos no se duplican.'));return}
   if(xhr.status>=200&&xhr.status<300)resolve(body);else reject(new Error(typeof body.detail==='string'?body.detail:'No se pudo guardar el archivo.'))};
  xhr.onerror=()=>reject(new Error('Se perdió la conexión. Reintenta este archivo; si ya fue recibido, se reconocerá sin duplicarlo.'));
  xhr.ontimeout=()=>reject(new Error('No hubo confirmación en 3 minutos. Revisa la conexión y reintenta; no se duplicarán archivos ya recibidos.'));
  xhr.send(form);
 });
}

export function UploadDialog({close,notify,initialSource,onReceived}:{close:()=>void;notify:(s:string)=>void;initialSource:string;onReceived:()=>void}){
 const [year,setYear]=useState('2026');const [source,setSource]=useState(initialSource);
 const [mode,setMode]=useState(['clima','produccion','planos'].includes(initialSource)?'adicional':'completo');
 const [entries,setEntries]=useState<Entry[]>([]);const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 const modes=['clima','produccion'].includes(source)?['completo','adicional']:source==='planos'?['adicional']:['completo'];
 const multiple=['planos','estimados','estadisticas'].includes(source)||mode==='adicional';
 function patch(index:number,change:Partial<Entry>){setEntries(previous=>previous.map((entry,i)=>i===index?{...entry,...change}:entry))}
 function select(files:FileList|null){setError('');const next=Array.from(files||[]).map<Entry>(file=>({file,state:'pending',percent:0,message:'Listo para enviar'}));setEntries(previous=>multiple?[...previous,...next.filter(e=>!previous.some(p=>p.file.name===e.file.name&&p.file.size===e.file.size&&p.file.lastModified===e.file.lastModified))]:next)}
 async function submit(){
  setBusy(true);setError('');let received=0,duplicates=0,failed=0;
  try{
   for(let index=0;index<entries.length;index++){
    const entry=entries[index];if(entry.state==='received'||entry.state==='duplicate')continue;
    if(!entry.file.name.toLowerCase().endsWith('.xlsx')||entry.file.size>300*1024*1024){patch(index,{state:'error',message:'Selecciona un Excel .xlsx de máximo 300 MB.'});failed++;continue}
    patch(index,{state:'sending',percent:0,message:'Enviando archivo…'});
    const form=new FormData();form.append('year',year);form.append('source',source);form.append('mode',mode);form.append('file',entry.file);
    try{
     const receipt=await send(form,percent=>patch(index,{percent,message:percent>=100?'Enviado. Confirmando recepción…':`Enviando · ${percent} %`}));
     patch(index,{state:receipt.duplicate?'duplicate':'received',percent:100,message:receipt.report.message});
     if(receipt.duplicate)duplicates++;else received++;
    }catch(e){failed++;patch(index,{state:'error',message:(e as Error).message})}
   }
   if(received||duplicates){window.dispatchEvent(new Event('gaitana:data-changed'));onReceived()}
   if(failed)setError(`${failed} archivo(s) no pudieron confirmarse. Revisa el mensaje junto a cada uno y pulsa Reintentar pendientes.`);
   notify(`${received} archivo(s) recibidos · ${duplicates} ya existentes · ${failed} con error.`);
  }finally{setBusy(false)}
 }
 const pending=entries.some(e=>e.state==='pending'||e.state==='error');
 const completed=entries.filter(e=>e.state==='received'||e.state==='duplicate').length;
 return <Dialog title="Actualizar una fuente" onClose={()=>{if(!busy)close()}}>
  <p>Primero recibimos los archivos. Después, <strong>Procesar archivos</strong> ejecuta la limpieza y actualiza la base analítica.</p>
  <fieldset disabled={busy} className="upload-fields">
   <Select label="Fuente" value={source} onChange={s=>{setSource(s);setMode(['clima','produccion','planos'].includes(s)?'adicional':'completo');setEntries([]);setError('')}} options={[{value:'produccion',label:'Producción real'},{value:'clima',label:'Clima'},{value:'planos',label:'Planos de siembra'},{value:'estadisticas',label:'Estadísticas de producción'},{value:'estimados',label:'Estimados del ingeniero'}]}/>
   <Select label="Modalidad" value={mode} onChange={v=>{setMode(v);setEntries([])}} options={modes.map(value=>({value,label:value==='adicional'?'Sólo registros adicionales':'Archivo completo'}))}/>
   <Select label="Año de la fuente" value={year} onChange={v=>{setYear(v);setEntries([])}} options={[2026,2025,2024,2023,2022,2021].map(y=>({value:String(y),label:String(y)}))}/>
   <div className="note">{source==='planos'?'Puedes seleccionar varios planos del mismo año. Se envían uno por uno y sólo se incorporan semanas faltantes.':source==='clima'||source==='produccion'?(mode==='adicional'?'Puedes seleccionar varios archivos del mismo año con fechas nuevas y sin cruces entre archivos.':'Un único archivo completo por año: reemplaza los archivos de ese año.'):source==='estadisticas'?'Puedes seleccionar varios archivos completos del mismo año, uno por familia. No selecciones dos versiones de la misma familia.':'Puedes seleccionar varias ediciones del mismo año; cada archivo conserva su H1 nominal.'} Mantén los nombres, hojas y columnas originales.</div>
   <label className="file-input"><Upload size={26}/><strong>{entries.length?`${entries.length} archivo(s) seleccionados${multiple?' · pulsa para agregar más':''}`:multiple?'Seleccionar uno o varios archivos Excel':'Seleccionar un archivo Excel'}</strong><span>.xlsx · máximo 300 MB por archivo{multiple?' · Ctrl o Mayús para seleccionar varios':''}</span><input key={`${source}-${mode}`} type="file" accept=".xlsx" multiple={multiple} aria-label={source==='planos'?'Archivos Excel de planos':multiple?'Archivos Excel de la fuente':'Archivo Excel de la fuente'} onChange={e=>{select(e.target.files);e.target.value=''}}/></label>
  </fieldset>
  {!!entries.length&&<div className="upload-queue" aria-live="polite">{entries.map((entry,index)=><div className={`upload-entry ${entry.state}`} key={`${entry.file.name}-${index}`}>
   <strong>{entry.state==='sending'?<LoaderCircle className="spin" size={14}/>:entry.state==='received'||entry.state==='duplicate'?<Check size={14}/>:null}{entry.file.name}</strong><small>{(entry.file.size/1024/1024).toFixed(1)} MB · {entry.state==='received'?'Recibido':entry.state==='duplicate'?'Ya existente':entry.state==='error'?'Error':entry.state==='sending'?'En curso':'Pendiente'}</small>
   {entry.state==='sending'&&<progress max={100} value={entry.percent} aria-label={`Envío de ${entry.file.name}`}/>}
   <p>{entry.message}</p>{!busy&&entry.state!=='received'&&entry.state!=='duplicate'&&<button className="icon-button" aria-label={`Quitar ${entry.file.name}`} onClick={()=>setEntries(previous=>previous.filter((_,i)=>i!==index))}><X size={14}/>Quitar</button>}
  </div>)}</div>}
  <ErrorBox message={error}/>
  {!busy&&completed>0&&<div className="note green">{completed} de {entries.length} archivos confirmados. Los recibidos quedan pendientes de <strong>Procesar archivos</strong>; los ya procesados no necesitan repetirse.</div>}
  <div className="dialog-actions"><button className="button secondary" onClick={close} disabled={busy}>Cerrar</button><button className="button primary" onClick={submit} disabled={!pending||busy}>{busy?<LoaderCircle className="spin" size={16}/>:<Save size={16}/ >}{busy?'Enviando…':entries.some(e=>e.state==='error')?'Reintentar pendientes':source==='planos'?'Guardar planos':'Guardar fuente'}</button></div>
 </Dialog>
}
