from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine, MetaData, String, Text, Float, Integer, BigInteger, DateTime, JSON, ForeignKey, UniqueConstraint, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import DATABASE_URL

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def uid():
    return str(uuid4())

engine = create_engine(DATABASE_URL, pool_pre_ping=True, **(
    {'connect_args': {'check_same_thread': False, 'timeout': 60}} if DATABASE_URL.startswith('sqlite') else
    {'fast_executemany': True} if DATABASE_URL.startswith('mssql+pyodbc') else {}))
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine, 'connect')
    def sqlite_config(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA journal_mode=WAL')
Session = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    # SQLite is only the local prototype; SQL Server always uses EP.
    metadata = MetaData(schema='EP' if engine.dialect.name == 'mssql' else None)

class Job(Base):
    __tablename__ = 'lgf_jobs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    kind: Mapped[str] = mapped_column(String(40))
    state: Mapped[str] = mapped_column(String(30), default='pendiente')
    progress: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, default='En cola')
    payload: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Forecast(Base):
    __tablename__ = 'lgf_forecasts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    origin: Mapped[str] = mapped_column(String(10))
    farm: Mapped[str] = mapped_column(String(100), default='GAITANA')
    variant: Mapped[str] = mapped_column(String(50))
    state: Mapped[str] = mapped_column(String(30), default='borrador')
    revision: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Line(Base):
    __tablename__ = 'lgf_forecast_lines'
    __table_args__ = (UniqueConstraint('forecast_id','product','color','variety','horizon'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    forecast_id: Mapped[str] = mapped_column(ForeignKey('lgf_forecasts.id'), index=True)
    product: Mapped[str] = mapped_column(String(150))
    color: Mapped[str] = mapped_column(String(150))
    variety: Mapped[str] = mapped_column(String(150))
    horizon: Mapped[int] = mapped_column(Integer)
    target: Mapped[str] = mapped_column(String(10))
    model_value: Mapped[float] = mapped_column(Float)
    final_value: Mapped[int] = mapped_column(Integer)
    theory: Mapped[float | None] = mapped_column(Float)
    route: Mapped[str] = mapped_column(String(40))

class Publication(Base):
    __tablename__ = 'lgf_publications'
    __table_args__ = (UniqueConstraint('farm','origin'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    farm: Mapped[str] = mapped_column(String(100))
    origin: Mapped[str] = mapped_column(String(10))
    forecast_id: Mapped[str] = mapped_column(ForeignKey('lgf_forecasts.id'))
    revision: Mapped[int] = mapped_column(Integer)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Audit(Base):
    __tablename__ = 'lgf_audit'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(60))
    object_id: Mapped[str] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Upload(Base):
    __tablename__ = 'lgf_uploads'
    __table_args__ = (UniqueConstraint('source','sha256'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    source: Mapped[str] = mapped_column(String(40))
    filename: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64))
    mode: Mapped[str] = mapped_column(String(30))
    state: Mapped[str] = mapped_column(String(40), default='recibido')
    report: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Dataset(Base):
    __tablename__ = 'lgf_datasets'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    state: Mapped[str] = mapped_column(String(30), default='preparado')
    root: Mapped[str] = mapped_column(Text)
    manifest: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime)


class ActiveDataset(Base):
    __tablename__ = 'lgf_active_dataset'
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default='vigente')
    dataset_id: Mapped[str] = mapped_column(ForeignKey('lgf_datasets.id'))


class SourceFile(Base):
    __tablename__ = 'lgf_source_files'
    path: Mapped[str] = mapped_column(String(400), primary_key=True)
    source: Mapped[str] = mapped_column(String(40))
    sha256: Mapped[str] = mapped_column(String(64))
    original_sha256: Mapped[str | None] = mapped_column(String(64))
    active: Mapped[int] = mapped_column(Integer, default=1)
    size: Mapped[int] = mapped_column(Integer)
    dataset_id: Mapped[str] = mapped_column(ForeignKey('lgf_datasets.id'))


class DatasetSource(Base):
    __tablename__ = 'lgf_dataset_sources'
    dataset_id: Mapped[str] = mapped_column(ForeignKey('lgf_datasets.id'), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(60), primary_key=True)
    source_dataset_id: Mapped[str] = mapped_column(ForeignKey('lgf_datasets.id'))
    rows: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64))
