"""Regenera el Excel de envíos semanales faltantes usando el inventario vigente.

Este script no descarga correo ni procesa las bases. Su único propósito es
comparar las semanas iniciales disponibles con el calendario esperado y crear
una lista amigable para buscar los archivos que aún faltan.
"""

from datetime import date
from pathlib import Path
import re
import unicodedata

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


PROYECTO = Path(__file__).resolve().parents[1]
PREPROCESADOS = (
    PROYECTO / "Datos" / "Estimados semanales" / "datos preprocesados"
)
INVENTARIO = PREPROCESADOS / "por año" / "inventario_bases_por_envio.csv"
SALIDA_EXCEL = PREPROCESADOS / "Estimados_faltantes_para_buscar.xlsx"
SALIDA_MD = PREPROCESADOS / "ESTIMADOS_FALTANTES_PARA_BUSCAR.md"

# El benchmark comienza en 2023. Para años cerrados se esperan 52 semanas;
# para el año actual, solamente hasta la semana ISO de hoy.
ANIO_INICIAL = 2023
HOY = date.today()
ANIO_FINAL = HOY.year
SEMANA_ACTUAL = HOY.isocalendar().week

if not INVENTARIO.exists():
    raise FileNotFoundError(
        f"No existe {INVENTARIO}. Ejecuta primero Run All en el notebook principal."
    )

inventario = pd.read_csv(INVENTARIO, encoding="utf-8-sig")
inventario["anio_emision"] = pd.to_numeric(inventario["anio_emision"], errors="coerce")
inventario["semana_inicio"] = pd.to_numeric(inventario["semana_inicio"], errors="coerce")

# El nombre original manda para la auditoría del calendario. Esto corrige los
# cierres de año: un Excel puede estar almacenado en 2023 y llamarse sem 01-2024.
anios_detectados = []
semanas_detectadas = []
for fila in inventario.itertuples(index=False):
    nombre = unicodedata.normalize("NFKD", Path(str(fila.archivo_excel)).stem)
    nombre = nombre.encode("ascii", "ignore").decode().lower()
    coincidencia_semana = re.search(r"(?:sem|semana)\D*(\d{1,2})", nombre)
    coincidencias_anio = [int(valor) for valor in re.findall(r"20\d{2}", nombre)]
    anios_detectados.append(
        coincidencias_anio[0]
        if coincidencias_anio
        else pd.to_numeric(fila.anio_emision, errors="coerce")
    )
    semanas_detectadas.append(
        int(coincidencia_semana.group(1))
        if coincidencia_semana
        else pd.to_numeric(fila.semana_inicio, errors="coerce")
    )
inventario["anio_calendario"] = pd.to_numeric(anios_detectados, errors="coerce")
inventario["semana_calendario"] = pd.to_numeric(semanas_detectadas, errors="coerce")

# Conserva estados escritos manualmente si la semana sigue faltando.
estados_previos = {}
if SALIDA_EXCEL.exists():
    try:
        anterior = pd.read_excel(SALIDA_EXCEL, sheet_name="Faltantes para buscar")
        for fila in anterior.itertuples(index=False):
            anio = int(getattr(fila, "Año"))
            semana = int(getattr(fila, "Semana_inicial_faltante"))
            estado = str(getattr(fila, "Estado", "Pendiente de buscar"))
            estados_previos[(anio, semana)] = estado
    except Exception:
        estados_previos = {}

filas_faltantes = []
filas_resumen = []
for anio in range(ANIO_INICIAL, ANIO_FINAL + 1):
    ultima_esperada = SEMANA_ACTUAL if anio == ANIO_FINAL else 52
    disponibles = set(
        inventario.loc[inventario["anio_calendario"].eq(anio), "semana_calendario"]
        .dropna()
        .loc[lambda serie: serie.between(1, 53)]
        .astype(int)
    )
    faltantes = sorted(set(range(1, ultima_esperada + 1)) - disponibles)
    versiones_adicionales = int(
        inventario.loc[inventario["anio_calendario"].eq(anio)].shape[0]
        - len(disponibles)
    )

    filas_resumen.append(
        {
            "Año": anio,
            "Esperadas hasta": ultima_esperada,
            "Semanas disponibles": len(disponibles & set(range(1, ultima_esperada + 1))),
            "Semanas faltantes": len(faltantes),
            "Lista de faltantes": ", ".join(f"{semana:02d}" for semana in faltantes) or "Ninguna",
            "Versiones adicionales": versiones_adicionales,
        }
    )

    for semana in faltantes:
        prioridad = 1 if anio >= ANIO_FINAL - 1 else 2
        filas_faltantes.append(
            {
                "Prioridad": prioridad,
                "Año": anio,
                "Semana inicial faltante": semana,
                "Búsqueda principal": f'"Estimado sem {semana:02d}" {anio}',
                "Búsqueda alternativa": f'"Estimado semana {semana:02d}" {anio} LG OR GF OR Gaitana',
                "Estado": estados_previos.get((anio, semana), "Pendiente de buscar"),
                "Observación": "Hueco probable; confirmar si esa semana tuvo envío",
            }
        )

faltantes_df = pd.DataFrame(
    filas_faltantes,
    columns=[
        "Prioridad",
        "Año",
        "Semana inicial faltante",
        "Búsqueda principal",
        "Búsqueda alternativa",
        "Estado",
        "Observación",
    ],
)
resumen_df = pd.DataFrame(filas_resumen)

with pd.ExcelWriter(SALIDA_EXCEL, engine="openpyxl") as writer:
    faltantes_df.to_excel(writer, sheet_name="Faltantes para buscar", index=False)
    resumen_df.to_excel(writer, sheet_name="Resumen", index=False)
    instrucciones = pd.DataFrame(
        {
            "Cómo usar": [
                "Ejecuta primero Run All en el notebook principal para actualizar el inventario.",
                "Busca cada asunto usando Búsqueda principal y luego Búsqueda alternativa.",
                "Un faltante significa que no existe una emisión cuya semana inicial sea esa; no prueba que nunca se enviara.",
                "Archivos ajustados/corregidos se conservan como versiones, pero no cuentan como otra semana disponible.",
                "Al guardar un Excel encontrado y volver a ejecutar el notebook y este script, desaparecerá de la lista.",
            ]
        }
    )
    instrucciones.to_excel(writer, sheet_name="Cómo usar", index=False)

    libro = writer.book
    for hoja in libro.worksheets:
        hoja.freeze_panes = "A2"
        for celda in hoja[1]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor="1F4E78")
            celda.alignment = Alignment(horizontal="center", vertical="center")
        if hoja.max_row > 1 and hoja.max_column > 0:
            tabla = Table(
                displayName="Tabla" + "".join(c for c in hoja.title if c.isalnum()),
                ref=hoja.dimensions,
            )
            tabla.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False
            )
            hoja.add_table(tabla)
        for numero, columna in enumerate(hoja.columns, 1):
            ancho = min(max(len(str(celda.value or "")) for celda in columna) + 2, 65)
            hoja.column_dimensions[get_column_letter(numero)].width = max(ancho, 12)

lineas = [
    "# Estimados faltantes para buscar",
    "",
    f"Actualizado: {HOY.isoformat()}.",
    "",
    "Se espera una emisión por semana inicial. Para el año actual solamente se evalúa hasta la semana ISO vigente.",
    "",
    "| Año | Esperadas hasta | Disponibles | Faltantes | Semanas |",
    "|---:|---:|---:|---:|---|",
]
for fila in resumen_df.itertuples(index=False):
    lineas.append(
        f"| {fila[0]} | {fila[1]} | {fila[2]} | {fila[3]} | {fila[4]} |"
    )
SALIDA_MD.write_text("\n".join(lineas) + "\n", encoding="utf-8")

print(f"Inventario leído: {len(inventario):,} archivos/emisiones")
print(f"Faltantes probables: {len(faltantes_df):,}")
print(resumen_df.to_string(index=False))
print(f"\nExcel generado: {SALIDA_EXCEL}")
