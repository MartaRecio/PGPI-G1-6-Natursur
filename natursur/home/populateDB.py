import os
import sys
import threading
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ─── Añadir raíz del proyecto al path ─────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Inicializar Django ─────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "natursur.settings")
import django
django.setup()

from home.models import Producto

# ─── Función para guardar producto en DB ───────────────────────
def guardar_producto(nombre, precio, img_url, link):
    Producto.objects.update_or_create(
        link=link,
        defaults={"nombre": nombre, "precio": precio, "img_url": img_url}
    )

# ─── Función de scraping con scroll dinámico ─────────────────
def extraer_productos(url_base):
    productos_guardados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url_base)
        page.wait_for_load_state("networkidle")

        # Simular scroll hasta que no cargue más productos
        previous_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # esperar que carguen nuevos productos
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break  # ya no hay más productos nuevos
            previous_height = current_height

        # Analizar HTML final
        soup = BeautifulSoup(page.content(), "lxml")
        contenedores = soup.select("article.product-miniature.js-product-miniature")

        for c in contenedores:
            try:
                nombre_tag = c.select_one(".product-title a")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else None

                precio_tag = c.select_one(".price")
                precio = precio_tag.get_text(strip=True) if precio_tag else None

                img_tag = c.select_one(".thumbnail-container img")
                img_url = urljoin(url_base, img_tag.get("src")) if img_tag else None

                link_tag = c.select_one(".product-title a")
                link = urljoin(url_base, link_tag.get("href")) if link_tag else None

                # Guardar en DB en thread para evitar async errors
                t = threading.Thread(target=guardar_producto, args=(nombre, precio, img_url, link))
                t.start()
                t.join()

                productos_guardados.append((nombre, precio, link, img_url))

            except Exception as e:
                print("Error procesando un producto:", e)

        browser.close()

    return productos_guardados

# ─── Ejecutar scraper ─────────────────────────
if __name__ == "__main__":
    URL = "https://herbalspain.com/inicio/"
    productos = extraer_productos(URL)

    print(f"Se guardaron {len(productos)} productos:")
    for p in productos:
        print(p)
