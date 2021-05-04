from bs4 import BeautifulSoup
import urllib3
import requests
import shutil
import pandas as pd
import os
import time


urllib3.disable_warnings()


def lista_enlaces(iter):
    url_base = "https://mapoteca.siap.gob.mx/index.php/page/"
    query = "/?s=ciudad+de+méxico"

    r = requests.get(url_base + iter + query, verify=False)
    cont = r.content

    sopa = BeautifulSoup(cont, 'html.parser')

    links = sopa.find_all("h2", class_="c-post__title")

    return [l.find('a').get('href') for l in links]


def get_img_ruta(url):
    r = requests.get(url, verify=False)
    cont = r.content
    sopa = BeautifulSoup(cont, 'html.parser')

    contenido = sopa.find_all('div', class_="c-post__content")

    return [c.find('a').get('href') for c in contenido][0]


def descargar_img(url):
    enlace_imagen = get_img_ruta(url)

    r_img = requests.get(enlace_imagen, stream=True, verify=False)

    nombre_archivo = enlace_imagen.split("/")[-1]
    print(nombre_archivo)

    if r_img.status_code == 200:
        r_img.raw.decode_content = True
        with open("descargas/" + nombre_archivo, 'wb') as a:
            shutil.copyfileobj(r_img.raw, a)
    else:
        print("error")


def get_titulo_item(url):
    try:
        r = requests.get(url, verify=False)
        cont = r.content
        sopa = BeautifulSoup(cont, 'html.parser')

        titulo_raw = sopa.find_all('header', class_="c-post__header")
        return [t.text for t in titulo_raw][0].replace("\n", "")
    except urllib3.exceptions:
        return "error_titulo-" + url.split("/")[-1]

def metadata(url):
    titulo = get_titulo_item(url)

    tabla = pd.read_html(url, encoding='utf-8')
    tabla = tabla[0]

    url_img = get_img_ruta(url)

    tabla.loc[len(tabla.index)] = ['Enlace descarga', url_img]

    print("descargando metadatos del mapa titulado \"{}\"".format(titulo))
    tabla.to_json("descargas/" + titulo + ".json",
                  orient='split', force_ascii=False)


enlaces_completos = []

for i in range(0, 173):
    try:
        enlaces_completos.extend(lista_enlaces(str(i)))
        print(enlaces_completos[:10])
        print(len(enlaces_completos) / 10)
    except:
        print("la página {} está fuera del rango".format(enlaces_completos / 10))
        pass

with open('enlaces_completos.txt', 'w', encoding='utf-8') as f:
    f.write(str(enlaces_completos))

for e in enlaces_completos:
    try:
        if not os.path.isfile('descargas/' + get_titulo_item(e) + ".json"):
            metadata(e)
            descargar_img(e)
            time.sleep(2)
        else:
            print("El archivo ya existe")
    except:
        raise