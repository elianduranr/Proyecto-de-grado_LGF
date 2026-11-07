import {Select} from './components';
import type {Identity} from './types';

export const human=(s:string)=>s.replaceAll('_',' ').toLowerCase().replace(/^./,c=>c.toUpperCase());
export const evaluationOptions=[{value:'updated',label:'Evaluación actualizada · cuaderno 26'},{value:'train',label:'Entrenamiento · diagnóstico H1'},{value:'validation',label:'Sólo validación 2025'},{value:'test',label:'Prueba 2026 · cuadernillo 19'},{value:'live',label:'Nuevas semanas · seguimiento'}];
const opts=(values:string[],all='Todos')=>[{value:'',label:all},...values.map(value=>({value,label:human(value)}))];

export function Filters({identities,value,onChange,hideProduct=false,labelPrefix=''}:{identities:Identity[];value:{product:string;color:string;variety:string};onChange:(v:typeof value)=>void;hideProduct?:boolean;labelPrefix?:string}){
 const products=[...new Set(identities.map(x=>x.producto))].sort();
 const colors=[...new Set(identities.filter(x=>!value.product||x.producto===value.product).map(x=>x.color))].sort();
 const varieties=[...new Set(identities.filter(x=>(!value.product||x.producto===value.product)&&(!value.color||x.color===value.color)).map(x=>x.variedad))].sort();
 return <>{!hideProduct&&<Select label={`${labelPrefix}Producto`} value={value.product} options={opts(products)} onChange={product=>onChange({product,color:'',variety:''})}/>}<Select label={`${labelPrefix}Color`} value={value.color} options={opts(colors)} onChange={color=>onChange({...value,color,variety:''})}/><Select label={`${labelPrefix}Variedad`} value={value.variety} options={opts(varieties)} onChange={variety=>onChange({...value,variety})}/></>
}
