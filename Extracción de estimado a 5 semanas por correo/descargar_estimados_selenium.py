from __future__ import annotations

import argparse
import calendar
import re
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parent
PROYECTO = ROOT.parent
ANIO = 2025
FORZAR = False
DESTINO = PROYECTO / "Datos" / "Estimados semanales" / str(ANIO)
PERFIL = ROOT / ".perfil_outlook_selenium"
CAPTURAS = ROOT / "capturas"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def esperar_descarga(antes: set[str], limite: int = 90) -> list[Path]:
    fin = time.time() + limite
    while time.time() < fin:
        actuales = {p.name for p in DESTINO.iterdir() if p.is_file()}
        parciales = list(DESTINO.glob("*.crdownload"))
        nuevos = {
            nombre for nombre in actuales - antes
            if Path(nombre).suffix.lower() in {".xlsx", ".xlsm", ".xlsb", ".xls"}
        }
        if nuevos and not parciales:
            return [DESTINO / nombre for nombre in sorted(nuevos)]
        time.sleep(1)
    return []


def nombre_sin_copia(nombre: str) -> str:
    return re.sub(r"\s*\(\d+\)(?=\.[^.]+$)", "", nombre).casefold()


def iniciar_edge() -> webdriver.Edge:
    DESTINO.mkdir(parents=True, exist_ok=True)
    PERFIL.mkdir(parents=True, exist_ok=True)
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    opciones = Options()
    opciones.binary_location = EDGE
    opciones.add_argument(f"--user-data-dir={PERFIL}")
    opciones.add_argument("--start-maximized")
    opciones.add_argument("--window-position=0,0")
    opciones.add_argument("--disable-session-crashed-bubble")
    opciones.add_argument("--no-first-run")
    opciones.add_experimental_option("prefs", {
        "download.default_directory": str(DESTINO.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    })
    driver = webdriver.Edge(options=opciones)
    driver.set_window_position(0, 0)
    driver.maximize_window()
    return driver


def buscar(driver: webdriver.Edge, consulta: str, etiqueta: str) -> None:
    espera = WebDriverWait(driver, 30)
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ALT, "q")
    time.sleep(1)
    activo = driver.switch_to.active_element
    if activo.tag_name.lower() != "input":
        buscador = espera.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "input[aria-label*='Buscar' i], input[placeholder*='Buscar' i], "
            "input[type='search'], [role='combobox']"
        )))
        buscador.click()
        time.sleep(1)
        activo = driver.switch_to.active_element
    activo.send_keys(Keys.CONTROL, "a")
    activo.send_keys(consulta)
    time.sleep(1)
    valor = activo.get_attribute("value") or activo.get_attribute("textContent") or ""
    driver.save_screenshot(str((CAPTURAS / f"{etiqueta}_antes_enter.png").resolve()))
    print(f"VALOR VISIBLE EN BUSCAR: {valor}", flush=True)
    if consulta.lower() not in valor.lower():
        raise RuntimeError("Outlook no conservó el texto dentro del buscador; no se pulsó Enter.")
    activo.send_keys(Keys.ENTER)
    print("ENTER PULSADO", flush=True)
    time.sleep(5)
    driver.save_screenshot(str((CAPTURAS / f"{etiqueta}_busqueda.png").resolve()))


def filas_estimados(driver: webdriver.Edge):
    filas = driver.find_elements(By.CSS_SELECTOR, "[role='option'][data-convid]")
    salida = []
    for fila in filas:
        try:
            texto = " ".join(fila.text.split())
            if re.search(r"estimad.*sem", texto, re.I) and str(ANIO) in texto:
                salida.append((fila, texto))
        except StaleElementReferenceException:
            pass
    return salida


def descargar_visibles(driver: webdriver.Edge, etiqueta: str) -> list[str]:
    espera = WebDriverWait(driver, 30)
    descargados: list[str] = []
    procesados: set[str] = set()

    for vuelta in range(40):
        filas = filas_estimados(driver)
        pendiente = None
        for fila, texto in filas:
            rango = re.search(rf"sem\D*(\d{{1,2}})\D+(\d{{1,2}})\D+{ANIO}", texto, re.I)
            clave = rango.group(0).lower() if rango else texto
            if clave not in procesados:
                pendiente = (fila, texto, clave)
                break

        if pendiente is None:
            if filas:
                driver.execute_script("arguments[0].scrollIntoView({block:'end'});", filas[-1][0])
                driver.execute_script("arguments[0].parentElement.scrollTop += 700;", filas[-1][0])
            time.sleep(2)
            if vuelta > 5:
                break
            continue

        fila, texto, clave = pendiente
        procesados.add(clave)
        driver.execute_script("arguments[0].click();", fila)
        clave_segura = clave.encode("ascii", "replace").decode("ascii")
        print(f"CORREO ABIERTO: {clave_segura}", flush=True)
        time.sleep(2)

        tarjetas = driver.find_elements(By.XPATH,
            "//*[@role='option'][contains(translate(.,'XLSM','xlsm'),'.xls')]"
        )
        tarjetas = [t for t in tarjetas if t.is_displayed()]
        numeros_clave = re.search(r"sem\D*(\d{1,2})\D+(\d{1,2})", clave, re.I)
        if numeros_clave:
            inicio_rango, fin_rango = numeros_clave.groups()
            coincidentes = [
                t for t in tarjetas
                if re.search(rf"(?<!\d)0?{int(inicio_rango)}\D+0?{int(fin_rango)}(?!\d)", t.text)
            ]
            if coincidentes:
                tarjetas = coincidentes
        if not tarjetas:
            print("SIN ADJUNTO EXCEL VISIBLE", flush=True)
            continue

        tarjeta = tarjetas[0]
        nombre = next((line.strip() for line in tarjeta.text.splitlines()
                       if re.search(r"\.xls[xmb]?$", line.strip(), re.I)), tarjeta.text.splitlines()[0])
        existentes = {
            nombre_sin_copia(p.name) for p in DESTINO.iterdir()
            if p.is_file() and p.suffix.lower() in {".xlsx", ".xlsm", ".xlsb", ".xls"}
        }
        if not FORZAR and nombre_sin_copia(nombre) in existentes:
            print(f"YA EXISTE, OMITIDO: {nombre}", flush=True)
            continue
        antes = {p.name for p in DESTINO.iterdir() if p.is_file()}
        # Algunos adjuntos de Outlook no abren vista previa y solo ofrecen
        # Descargar desde la flecha/menú de la propia tarjeta.
        try:
            ActionChains(driver).move_to_element(tarjeta).perform()
            botones_tarjeta = [b for b in tarjeta.find_elements(By.CSS_SELECTOR, "button") if b.is_displayed()]
            if botones_tarjeta:
                botones_tarjeta[-1].click()
                opcion_descargar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                    "//*[@role='menuitem' or @role='button'][contains(.,'Descargar') or contains(.,'Download')]"
                )))
                opcion_descargar.click()
                nuevos = esperar_descarga(antes)
                if nuevos:
                    for archivo in nuevos:
                        descargados.append(archivo.name)
                        print(f"DESCARGADO DESDE MENU: {archivo.name}", flush=True)
                    continue
        except Exception:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

        try:
            ActionChains(driver).move_to_element(tarjeta).click().perform()
        except StaleElementReferenceException:
            print(f"TARJETA CAMBIO; SE CONTINUA: {nombre}", flush=True)
            continue
        try:
            boton = espera.until(EC.element_to_be_clickable((By.XPATH,
                "//button[contains(@aria-label,'Descargar') or contains(@title,'Descargar') or "
                "contains(@aria-label,'Download') or contains(@title,'Download')]"
            )))
            boton.click()
        except TimeoutException:
            driver.save_screenshot(str((CAPTURAS / f"{etiqueta}_sin_boton_{len(procesados)}.png").resolve()))
            print(f"NO APARECIO DESCARGAR: {nombre}", flush=True)
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            continue

        nuevos = esperar_descarga(antes)
        if nuevos:
            for archivo in nuevos:
                descargados.append(archivo.name)
                print(f"DESCARGADO: {archivo.name}", flush=True)
        else:
            print(f"DESCARGA NO CONFIRMADA: {nombre}", flush=True)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)

    driver.save_screenshot(str((CAPTURAS / f"{etiqueta}_final.png").resolve()))
    return descargados


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--desde", default="01/01/2025")
    parser.add_argument("--hasta", default="01/31/2025")
    parser.add_argument("--etiqueta", default="enero_2025")
    parser.add_argument("--barrido", action="store_true")
    parser.add_argument("--inicio", type=int, default=1)
    parser.add_argument("--remitentes", action="store_true")
    parser.add_argument("--consulta")
    parser.add_argument("--anio", type=int, default=2025)
    parser.add_argument("--hasta-mes", type=int, default=12)
    parser.add_argument("--forzar", action="store_true")
    args = parser.parse_args()
    global ANIO, DESTINO, FORZAR
    ANIO = args.anio
    FORZAR = args.forzar
    DESTINO = PROYECTO / "Datos" / "Estimados semanales" / str(ANIO)
    driver = iniciar_edge()
    try:
        print("EDGE CONTROLADO POR SELENIUM", flush=True)
        driver.get("https://outlook.office.com/mail/")
        normales = [(inicio, inicio + 4) for inicio in range(1, 49)]
        especiales = [
            (1, 8), (2, 8), (3, 8), (4, 8),
            (5, 12), (6, 12), (7, 12), (8, 12),
            (9, 18), (10, 18), (11, 18), (12, 18), (13, 18), (14, 18),
        ]
        intervalos = []
        for intervalo in especiales + normales:
            if intervalo not in intervalos:
                intervalos.append(intervalo)
        intervalos = intervalos[args.inicio - 1:]
        remitentes = (
            "(from:produccionlgf@lagaitanacol.com OR "
            "from:rtorres@lagaitanacol.com OR "
            "from:rcubides@lagaitanacol.com)"
        )
        if args.consulta:
            consultas = [args.consulta]
        elif args.remitentes:
            consultas = []
            for mes in range(args.inicio, args.hasta_mes + 1):
                ultimo = calendar.monthrange(ANIO, mes)[1]
                consultas.append(
                    f"{remitentes} Estimado sem received:01/{mes:02d}/{ANIO}..{ultimo:02d}/{mes:02d}/{ANIO}"
                )
        elif args.barrido:
            consultas = [f'Estimado sem {inicio:02d}-{fin:02d} {ANIO}' for inicio, fin in intervalos]
        else:
            consultas = [f"Estimado sem {ANIO}"]
        total = []
        for numero, consulta in enumerate(consultas, 1):
            if args.remitentes:
                mes_real = args.inicio + numero - 1
                etiqueta = f"remitentes_{ANIO}_mes_{mes_real:02d}"
            elif args.barrido:
                inicio, fin = intervalos[numero - 1]
                etiqueta = f"intervalo_{inicio:02d}_{fin:02d}"
            else:
                etiqueta = args.etiqueta
            print(f"\nBUSQUEDA {numero}/{len(consultas)}", flush=True)
            buscar(driver, consulta, etiqueta)
            total.extend(descargar_visibles(driver, etiqueta))
        print(f"TOTAL DESCARGAS NUEVAS: {len(total)}", flush=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
