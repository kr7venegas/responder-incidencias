from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 1. Configuración de opciones para el navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Pantalla completa al iniciar
chrome_options.add_experimental_option("detach", True)  # Mantiene el navegador abierto

# 2. Inicializar el WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 3. Ir a la URL del proyecto
url = "https://portal.fccma.com/vision/#/ma_prc_609_300/INC/93545/1"
driver.get(url)

print("Navegador listo y en la web del portal FCCMA.")