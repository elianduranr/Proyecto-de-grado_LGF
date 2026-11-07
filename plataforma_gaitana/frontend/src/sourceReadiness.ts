import type {SourceStatus} from './types';

export function requiresUpdate(source:SourceStatus,useClimate=false){
 return (source.required||source.source==='clima'&&useClimate)&&
  (!source.through||source.rows===0||source.pending_files>0||source.pending_uploads>0||source.source==='clima'&&useClimate&&source.status_label==='Opcional · sin clima');
}
