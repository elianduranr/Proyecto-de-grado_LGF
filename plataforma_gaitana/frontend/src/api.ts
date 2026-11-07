export async function api<T>(path:string, init:RequestInit={}):Promise<T> {
  const headers=new Headers(init.headers);
  if(init.body && !(init.body instanceof FormData)) headers.set('Content-Type','application/json');
  const token=localStorage.getItem('gaitana_token');
  if(token)headers.set('Authorization',`Bearer ${token}`);
  const response=await fetch(`/api${path}`,{...init,headers});
  if(!response.ok){const body=await response.json().catch(()=>({detail:'No se pudo conectar con el servidor.'}));throw new Error(typeof body.detail==='string'?body.detail:JSON.stringify(body.detail));}
  const body=await response.json();
  if(init.method&&init.method!=='GET')window.dispatchEvent(new Event('gaitana:data-changed'));
  return body;
}
export async function download(path:string){
  const token=localStorage.getItem('gaitana_token');
  const response=await fetch(`/api${path}`,{headers:token?{Authorization:`Bearer ${token}`}:{}});
  if(!response.ok)throw new Error('No se pudo descargar el estimado.');
  const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');a.href=url;a.download=response.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)?.[1]||'Estimado.xlsx';a.click();URL.revokeObjectURL(url);
}
export const num=(n:number|null|undefined)=>n==null?'—':new Intl.NumberFormat('es-CO',{maximumFractionDigits:0}).format(n);
export const pct=(n:number|null|undefined)=>n==null?'—':`${n>0?'+':''}${n.toFixed(2).replace('.',',')} %`;
export const date=(s:string)=>s?new Date(s.slice(0,10)+'T12:00:00').toLocaleDateString('es-CO',{day:'numeric',month:'short',year:'numeric'}):'—';
export function week(s:string){const d=new Date(s.slice(0,10)+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+4-(d.getUTCDay()||7));const y=new Date(Date.UTC(d.getUTCFullYear(),0,1));return `S${Math.ceil((((+d-+y)/86400000)+1)/7).toString().padStart(2,'0')}`;}
export function isoWeek(s:string){const d=new Date(s+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+4-(d.getUTCDay()||7));return `${d.getUTCFullYear()}-W${week(s).slice(1)}`;}
export function weekMonday(value:string){if(!/^\d{4}-W\d{2}$/.test(value))return '';const [year,n]=value.split('-W').map(Number);const d=new Date(Date.UTC(year,0,4));d.setUTCDate(d.getUTCDate()-(d.getUTCDay()||7)+1+(n-1)*7);return d.toISOString().slice(0,10);}
