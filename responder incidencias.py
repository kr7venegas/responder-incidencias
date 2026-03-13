import time
import csv
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- CONFIGURACIÓN DE COORDENADAS ---
COORD_FECHA_INI       = (536, 72)
COORD_FECHA_FIN       = (680, 72)
COORD_BOTON_CONSULTAR = (93, 74)
COORD_BOTON_INSERTAR  = (937, 727)
COORD_CAMPO_ESTADO    = (800, 600)

# --- FUNCIONES DE CLICK POR COORDENADAS ---

def click_absoluto(driver, wait, x, y, descripcion=""):
    try:
        # Aseguramos que el body esté presente antes de actuar
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        actions = ActionChains(driver)
        # Click relativo al inicio de la página
        actions.move_by_offset(x, y).click().perform()
        # Reset ratón
        actions.move_by_offset(-x, -y).perform()
        print(f"🖱️ Click ejecutado en ({x}, {y}) - {descripcion}")
    except Exception as e:
        print(f"❌ Error al hacer click en {descripcion}: {e}")

def escribir_texto_en_posicion(driver, wait, x, y, texto, descripcion=""):
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        actions = ActionChains(driver)
        
        # 1. Click para dar foco
        actions.move_by_offset(x, y).click().perform()
        time.sleep(0.3)
        
        # 2. LIMPIAR el campo (Seleccionar todo y borrar)
        # Usamos CONTROL + A y BACKSPACE para asegurar que el campo esté vacío
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        actions.send_keys(Keys.BACKSPACE).perform()
        
        # 3. Escribir el nuevo texto
        actions.send_keys(texto).send_keys(Keys.ENTER).perform()
        
        # 4. Reset ratón
        actions.move_by_offset(-x, -y).perform()
        print(f"✍️ Texto '{texto}' enviado a {descripcion}")
    except Exception as e:
        print(f"❌ Error al escribir en {descripcion}: {e}")

# --- INICIO DEL SCRIPT ---

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
wait = WebDriverWait(driver, 10)

try:
    # 1. Login
    driver.get("https://portal.fccma.com/vision/#/ma_prc_609_300/INC/93545/1")
    
    user_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    user_input.send_keys("su_granada")
    driver.find_element(By.NAME, "password").send_keys("Inagra_2025")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    print("Sesión iniciada. Esperando carga...")

    # 2. Cargar CSV
    directorio = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(directorio, 'wp_incidencias_gecor.csv')
    codigos_aviso = []
    
    with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
        lector = csv.reader(f)
        for fila in lector:
            if fila and fila[0].strip().isdigit():
                codigos_aviso.append(fila[0].strip())

    # 3. Fechas
    hace_x_dias = datetime.now() - timedelta(days=3)
    f_ini = hace_x_dias.strftime("%d/%m/%Y 00:00:00")
    f_fin = hace_x_dias.strftime("%d/%m/%Y 23:59:59")

    # 4. Bucle de Procesamiento
    for cod in codigos_aviso:
        print(f"\n--- TRABAJANDO CON CÓDIGO: {cod} ---")
        time.sleep(10)
        
        # Paso A: Fechas
        escribir_texto_en_posicion(driver, wait, COORD_FECHA_INI[0], COORD_FECHA_INI[1], f_ini, "Fecha Inicio")
        time.sleep(1) # Pequeña pausa entre campos
        escribir_texto_en_posicion(driver, wait, COORD_FECHA_FIN[0], COORD_FECHA_FIN[1], f_fin, "Fecha Fin")

        # Paso B: Click en Consultar
        click_absoluto(driver, wait, COORD_BOTON_CONSULTAR[0], COORD_BOTON_CONSULTAR[1], "Botón Consultar")
        time.sleep(3) 

        # Paso C: Click en Insertar
        click_absoluto(driver, wait, COORD_BOTON_INSERTAR[0], COORD_BOTON_INSERTAR[1], "Botón Insertar")
        time.sleep(2) 

        # Paso D: Escribir 999 en el Estado
        escribir_texto_en_posicion(driver, wait, COORD_CAMPO_ESTADO[0], COORD_CAMPO_ESTADO[1], "999", "Campo Estado")
        
        print(f"✅ Proceso completado para {cod}.")
        time.sleep(2)

except Exception as e:
    print(f"❌ Error general: {e}")

# driver.quit()