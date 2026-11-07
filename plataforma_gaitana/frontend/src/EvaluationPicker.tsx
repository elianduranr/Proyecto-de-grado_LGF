import {evaluationOptions} from './ComparisonFilters';

const explanations:Record<string,string>={
 updated:'Reconstrucción temporal con la configuración fija del 19. Los errores usan la producción y los estimados de la última versión validada; no es una publicación anticipada. Incluye las semanas posteriores a S36.',
 train:'Datos que el modelo ya conocía durante el ajuste. Sirven para diagnosticar el entrenamiento; no demuestran cómo predice semanas nuevas. Sólo se conserva el diagnóstico H1.',
 validation:'Semanas de 2025 usadas para elegir la variante del modelo antes de la prueba final.',
 test:'Semanas de 2026 reservadas para la evaluación retrospectiva del cuadernillo 19. Ésta es la referencia de desempeño fuera del ajuste; no cambia al subir archivos.',
 live:'Semanas nuevas con pronósticos publicados antes de H1 y producción real de semanas terminadas. Se actualiza al incorporar datos.'
};

export function EvaluationPicker({value,onChange}:{value:string;onChange:(v:string)=>void}){
 return <div className="evaluation-picker"><span className="eyebrow">QUÉ DATOS ESTÁS REVISANDO</span><div className="evaluation-tabs" role="group" aria-label="Datos de evaluación">{evaluationOptions.map(o=><button key={o.value} aria-pressed={value===o.value} onClick={()=>onChange(o.value)}>{o.value==='train'?'Entrenamiento (train)':o.value==='test'?'Prueba (test)':o.value==='updated'?'Evaluación actualizada':o.value==='validation'?'Validación':'Seguimiento nuevo'}</button>)}</div><p><strong>{value==='train'?'Entrenamiento':value==='test'?'Prueba fuera del ajuste':value==='validation'?'Selección del modelo':value==='updated'?'Datos más recientes':'Evaluación operativa'}: </strong>{explanations[value]}</p></div>
}
