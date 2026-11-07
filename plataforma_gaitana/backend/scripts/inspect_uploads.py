"""Estado de recepción y trabajos propios; sin credenciales ni datos de cultivo."""
import json
from sqlalchemy import select
from app.db import Session,Upload,Job

with Session() as db:
    uploads=db.scalars(select(Upload).order_by(Upload.created_at.desc()).limit(12)).all()
    jobs=db.scalars(select(Job).where(Job.state.in_(['pendiente','en_proceso'])).order_by(Job.created_at)).all()
    print(json.dumps({'uploads':[{'id':r.id,'source':r.source,'filename':r.filename,'state':r.state,
        'bytes':r.report.get('bytes'),'sha256':r.sha256,'created_at':str(r.created_at)} for r in uploads],
        'active_jobs':[{'id':r.id,'kind':r.kind,'state':r.state,'message':r.message} for r in jobs]},ensure_ascii=False,indent=2))
