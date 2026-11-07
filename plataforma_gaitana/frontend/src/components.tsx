import {useEffect,useRef,useState,type ReactNode} from 'react';
import * as echarts from 'echarts/core';
import {LineChart,BarChart} from 'echarts/charts';
import {GridComponent,LegendComponent,TooltipComponent,MarkAreaComponent,AriaComponent} from 'echarts/components';
import {SVGRenderer} from 'echarts/renderers';
import type {EChartsOption} from 'echarts';
import {AlertCircle,ArrowUpRight,X} from 'lucide-react';
import {api} from './api';
echarts.use([LineChart,BarChart,GridComponent,LegendComponent,TooltipComponent,MarkAreaComponent,AriaComponent,SVGRenderer]);

export function useResource<T>(path:string){
  const [data,setData]=useState<T>();const [error,setError]=useState('');const [loading,setLoading]=useState(false);const [tick,setTick]=useState(0);
  useEffect(()=>{if(!path)return;
    const refresh=()=>{if(/^\/(history|comparison)(\?|$)/.test(path))setData(undefined);setTick(t=>t+1)};
    const poll=()=>{if(document.visibilityState==='visible')setTick(t=>t+1)};
    window.addEventListener('gaitana:data-changed',refresh);
    const timer=/^\/(history|comparison|data\/status|forecasts)/.test(path)?setInterval(poll,30000):undefined;
    return()=>{window.removeEventListener('gaitana:data-changed',refresh);clearInterval(timer)};
  },[path]);
  useEffect(()=>{if(!path){setData(undefined);return;}let live=true;setLoading(true);setError('');
    api<T>(path).then(d=>{if(live)setData(d)}).catch(e=>{if(live)setError(e.message)}).finally(()=>{if(live)setLoading(false)});
    return ()=>{live=false};},[path,tick]);
  return {data,error,loading,reload:()=>setTick(t=>t+1)};
}
export function Card({children,className=''}:{children:ReactNode;className?:string}){return <section className={`card ${className}`}>{children}</section>}
export function ErrorBox({message}:{message:string}){return message?<div className="error" role="alert"><AlertCircle size={18}/>{message}</div>:null}
export function Select({label,value,onChange,options}:{label:string;value:string;onChange:(v:string)=>void;options:{value:string;label:string}[]}){return <label className="field"><span>{label}</span><select aria-label={label} value={value} onChange={e=>onChange(e.target.value)}>{options.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}</select></label>}
export function Tag({children,tone='neutral'}:{children:ReactNode;tone?:string}){return <span className={`tag ${tone}`}>{children}</span>}
export function Chart({option,height=330,label}:{option:EChartsOption;height?:number;label:string}){
  const ref=useRef<HTMLDivElement>(null);
  useEffect(()=>{if(!ref.current)return;const instance=echarts.init(ref.current,undefined,{renderer:'svg'});instance.setOption(option);const observer=new ResizeObserver(()=>instance.resize());observer.observe(ref.current);return ()=>{observer.disconnect();instance.dispose()}},[option]);
  return <div ref={ref} style={{height,width:'100%'}} role="img" aria-label={label}/>;
}
export function MetricCard({label,value,description,accent=false}:{label:string;value:string;description:string;accent?:boolean}){return <Card className={`metric ${accent?'metric-accent':''}`}><div className="metric-label">{label}<ArrowUpRight size={16}/></div><strong>{value}</strong><p>{description}</p></Card>}
export function Dialog({title,children,onClose}:{title:string;children:ReactNode;onClose:()=>void}){
  const ref=useRef<HTMLDialogElement>(null);
  useEffect(()=>{ref.current?.showModal();return ()=>ref.current?.close()},[]);
  return <dialog ref={ref} onCancel={event=>{event.preventDefault();onClose()}} aria-labelledby="dialog-title"><div className="dialog-heading"><h2 id="dialog-title">{title}</h2><button className="icon-button" aria-label="Cerrar" onClick={onClose}><X size={20}/></button></div>{children}</dialog>
}
export function Bloom(){return <svg className="bloom" viewBox="0 0 140 180" aria-hidden="true"><g fill="none" stroke="currentColor" strokeWidth="1.2">{Array.from({length:16},(_,i)=><ellipse key={i} cx="70" cy="45" rx="16" ry="31" transform={`rotate(${i*22.5} 70 70)`}/>)}<circle cx="70" cy="70" r="12"/><path d="M70 101v70M70 145c-27-3-32-19-33-29 23 1 30 15 33 29M70 158c26-3 31-20 32-30-22 2-29 17-32 30"/></g></svg>}
export const chartBase={color:['#800020','#315f82','#b88b52','#698b78'],textStyle:{fontFamily:'Roboto,sans-serif',color:'#647068',fontSize:11},tooltip:{trigger:'axis' as const,backgroundColor:'#fff',borderColor:'#e8e8e8'},legend:{bottom:0,icon:'roundRect',itemWidth:16,itemHeight:3,textStyle:{fontSize:11}},grid:{left:65,right:25,top:25,bottom:55}};
