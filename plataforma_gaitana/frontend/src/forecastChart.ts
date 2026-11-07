import type {EChartsOption} from 'echarts';
import type {ForecastLine} from './types';
import {chartBase} from './components';
import {isoWeek,num} from './api';

export interface WeeklyObservation {semana_inicio:string;tallos_reales:number}
export interface ForecastView {start?:string;end?:string;observedAfterOrigin?:boolean;visible?:Record<string,boolean>}
export function forecastChart(lines:ForecastLine[],history:WeeklyObservation[],origin:string,view:ForecastView={}):EChartsOption {
 const targets=[...new Set(lines.map(x=>x.target))].sort();
 const observations=history.filter(x=>view.observedAfterOrigin||x.semana_inicio.slice(0,10)<origin);
 let dates=[...new Set([...observations.map(x=>x.semana_inicio.slice(0,10)),...targets])].sort();
 if(view.start&&view.end){dates=[];for(let t=Date.parse(view.start+'T12:00:00Z');t<=Date.parse(view.end+'T12:00:00Z');t+=7*864e5)dates.push(new Date(t).toISOString().slice(0,10))}
 const label=(s:string)=>`${isoWeek(s).replace('-W','-S')} · ${new Date(s+'T12:00:00').toLocaleDateString('es-CO',{day:'numeric',month:'short'})}`;
 const visibleTargets=targets.filter(s=>dates.includes(s));
 const aggregate=(s:string,field:'model'|'final'|'theory')=>{const group=lines.filter(x=>x.target===s);if(!group.length||group.some(x=>x[field]===null))return null;return group.reduce((sum,x)=>sum+(x[field]||0),0)};
 return {...chartBase,legend:{...chartBase.legend,selected:view.visible,selectedMode:view.visible?false:true},tooltip:{...chartBase.tooltip,valueFormatter:(v:unknown)=>num(Number(v))},
   xAxis:{type:'category',data:dates.map(label),axisTick:{show:false},axisLine:{lineStyle:{color:'#ddd'}}},
   yAxis:{type:'value',name:'Tallos',axisLabel:{formatter:(v:number)=>v>=1e6?`${(v/1e6).toLocaleString('es-CO',{maximumFractionDigits:1})} M`:v>=1000?`${(v/1000).toLocaleString('es-CO',{maximumFractionDigits:1})} mil`:num(v)},splitLine:{lineStyle:{color:'#f0f2ef'}}},
   series:[
    {name:'Producción real',type:'line',smooth:false,symbolSize:5,itemStyle:{color:'#64806d'},data:dates.map(s=>observations.find(x=>x.semana_inicio.slice(0,10)===s)?.tallos_reales??null)},
    {name:'Sugerencia del modelo',type:'line',smooth:false,symbol:'diamond',symbolSize:8,lineStyle:{type:'dashed',width:3},itemStyle:{color:'#800020'},data:dates.map(s=>aggregate(s,'model')),markArea:{silent:true,itemStyle:{color:'rgba(128,0,32,.035)'},data:visibleTargets.length?[[{xAxis:label(visibleTargets[0])},{xAxis:label(visibleTargets.at(-1)!)}]]:[]}},
    {name:'Revisión actual del ingeniero',type:'line',smooth:false,symbol:'emptyCircle',symbolSize:7,lineStyle:{width:1.8},itemStyle:{color:'#b88b52'},data:dates.map(s=>aggregate(s,'final'))},
    {name:'Proyección teórica',type:'line',smooth:.25,smoothMonotone:'x',symbolSize:5,lineStyle:{type:'dotted',width:2.5},itemStyle:{color:'#315f82'},data:dates.map(s=>aggregate(s,'theory'))}
   ]};
}
