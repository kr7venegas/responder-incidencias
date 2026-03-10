import time
import csv
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN DE FUNCIONES ---

def preparar_contexto(driver, wait):
    """Busca los componentes de la web en el nivel principal o en iframes."""
    driver.switch_to.default_content()
    try:
        # Intentamos ver si los componentes están en el nivel principal
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "input-date")))
        return True
    except:
        # Si no, buscamos en el primer iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for i in range(len(iframes)):
            driver.switch_to.default_content()
            driver.switch_to.frame(i)
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "input-date")))
                return True
            except:
                continue
    return False

def rellenar_fechas_shadow(driver, inicio, fin):
    try:
        shadow_host = driver.find_element(By.NAME, "dat_inc")
        script = f"""
            const root = arguments[0].shadowRoot;
            const inputFrom = root.querySelector('input[from]');
            const inputTo = root.querySelector('input[to]');
            inputFrom.value = '{inicio}';
            inputFrom.dispatchEvent(new Event('input', {{ bubbles: true }}));
            inputTo.value = '{fin}';
            inputTo.dispatchEvent(new Event('input', {{ bubbles: true }}));
        """
        driver.execute_script(script, shadow_host)
        print(f"✅ Fechas set: {inicio}")
    except Exception as e:
        print(f"❌ Error fechas: {e}")

def escribir_codigo_incidencia(driver, valor_codigo):
    """Inyecta el código en el campo Filtrar usando JavaScript para evitar bloqueos."""
    try:
        # Buscamos el input que contiene 'iltrar' en el placeholder
        selector_filtrar = "input[placeholder*='iltrar']"
        campo_filtro = driver.find_element(By.CSS_SELECTOR, selector_filtrar)

        # Inyección directa por JS
        script = """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('keyup', { bubbles: true }));
        """
        driver.execute_script(script, campo_filtro, valor_codigo)
        print(f"✅ Código {valor_codigo} inyectado en filtro.")
    except Exception as e:
        print(f"❌ Error inyectando código: {e}")

def pulsar_boton_consultar(driver):
    try:
        shadow_host = driver.find_element(By.TAG_NAME, "query-button")
        script = "arguments[0].shadowRoot.querySelector('button').click();"
        driver.execute_script(script, shadow_host)
        print("🚀 Consulta lanzada.")
    except Exception as e:
        print(f"❌ Error botón consultar: {e}")

# --- INICIO DEL SCRIPT ---

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    # 1. Login
    driver.get("https://portal.fccma.com/vision/#/ma_prc_609_300/INC/93545/1")
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("su_granada")
    driver.find_element(By.NAME, "password").send_keys("Inagra_2025")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    print("Sesión iniciada. Esperando carga del portal...")
    time.sleep(8) # Tiempo para que cargue el dashboard tras login

    # 2. Cargar CSV
    directorio = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(directorio, 'wp_incidencias_gecor.csv')
    codigos_aviso = []
    
    with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
        lector = csv.reader(f)
        for fila in lector:
            if fila and fila[0].strip().isdigit():
                codigos_aviso.append(fila[0].strip())

    # 3. Fechas (Ayer)
    ayer = datetime.now() - timedelta(days=1)
    f_ini = ayer.strftime("%d/%m/%Y 00:00:00")
    f_fin = ayer.strftime("%d/%m/%Y 23:59:59")

    # 4. Bucle de Procesamiento
    if preparar_contexto(driver, wait):
        for cod in codigos_aviso:
            print(f"\n--- TRABAJANDO CON CÓDIGO: {cod} ---")
            
            # Limpiar posibles filtros anteriores pulsando ESC
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            
            rellenar_fechas_shadow(driver, f_ini, f_fin)
            escribir_codigo_incidencia(driver, cod)
            pulsar_boton_consultar(driver)
            
            # Esperamos a que la tabla se refresque
            print(f"Esperando resultados de {cod}...")
            time.sleep(6) 
    else:
        print("No se encontró el formulario de búsqueda.")

except Exception as e:
    print(f"Error general en el sistema: {e}")

# driver.quit() # Descomenta si quieres que se cierre solo al terminar