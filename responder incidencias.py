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
COORD_ZONA_MUERTA = (345, 79)
COORD_CODIGO = (1106, 73)
COORD_ESTADO = (1128, 167)
COORD_FINALIZADA = (939, 269)
COOR_EQUIPO = (1127, 190)
COORD_ENCARGADO_GENERAL = (953, 234)
COORD_ACEPTAR = (982, 77)

# --- FUNCIONES DE CLICK POR COORDENADAS ---

def click_absoluto(driver, wait, x, y, descripcion=""):
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        actions = ActionChains(driver)
        
        # 1. MOVER A ZONA MUERTA PRIMERO (Para quitar cualquier hover previo)
        # Suponiendo que (10, 500) es un sitio seguro
        actions.move_by_offset(10, 500).perform() 
        time.sleep(0.2) # Pausa mínima para que el menú se cierre
        
        # 2. VOLVER AL ORIGEN (0,0) desde la zona muerta
        actions.move_by_offset(-10, -500).perform()

        # 3. AHORA SÍ, IR AL OBJETIVO Y CLICAR
        actions.move_by_offset(x, y).click().perform()
        
        # 4. RESET Y APARTAR (Para no dejar el ratón encima del botón recién pulsado)
        actions.move_by_offset(-x, -y).perform()
        actions.move_by_offset(10, 500).perform()
        actions.move_by_offset(-10, -500).perform() # Reset para la siguiente función
        
        print(f"🖱️ Click limpio en ({x}, {y}) - {descripcion}")
    except Exception as e:
        print(f"❌ Error en {descripcion}: {e}")

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
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
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
    hace_x_dias = datetime.now() - timedelta(days=4)
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
        time.sleep(1) # Pequeña pausa entre campos
        #Código
        escribir_texto_en_posicion(driver, wait, COORD_CODIGO[0], COORD_CODIGO[1], cod, "Código")

        # Paso B: Click en Consultar
        click_absoluto(driver, wait, COORD_BOTON_CONSULTAR[0], COORD_BOTON_CONSULTAR[1], "Botón Consultar")
        time.sleep(3) 

        # Paso C: Click en Insertar
        click_absoluto(driver, wait, COORD_BOTON_INSERTAR[0], COORD_BOTON_INSERTAR[1], "Botón Insertar")
        time.sleep(2) 
        click_absoluto(driver, wait, COORD_ESTADO[0], COORD_ESTADO[1], "Botón Estado")
        time.sleep(2) 
        click_absoluto(driver, wait, COORD_FINALIZADA[0], COORD_FINALIZADA[1], "Botón Finalizada")
        time.sleep(2) 
        click_absoluto(driver, wait, COOR_EQUIPO[0], COOR_EQUIPO[1], "Botón Equipo")
        time.sleep(2)
        click_absoluto(driver, wait, COORD_ENCARGADO_GENERAL[0], COORD_ENCARGADO_GENERAL[1], "Botón Encargado General")
        time.sleep(2)
        click_absoluto(driver, wait, COORD_ACEPTAR[0], COORD_ACEPTAR[1], "Botón Aceptar")
        time.sleep(2) 
        
        print(f"✅ Proceso completado para {cod}.")
        time.sleep(2)

except Exception as e:
    print(f"❌ Error general: {e}")

# driver.quit()