"""
webbrowser únicamente permite acceder
a un sitio web
"""
import webbrowser as wb
"""
requests permite llevar a cabo peticiones 
a páginas usando los siguientes comandos

requests.get('http://www.gutenberg.org/cache/epub/1112/pg1112.txt')

res.raise_for_status()
    Levanta excepciones

# Requests permite escribir archivos

res = requests.get('http://www.gutenberg.org/cache/epub/1112/pg1112.txt') >>> res.raise_for_status()
playFile = open('RomeoAndJuliet.txt', 'wb')
for chunk in res.iter_content(100000):
    playFile.write(chunk)
playFile.close()


"""

import requests as r

"""
BeautifulSoup is invoqued in an text string that contains html and returns a beautiful soup object like this

>>> import requests, bs4
>>> res = requests.get('http://nostarch.com') >>> res.raise_for_status()
>>> noStarchSoup = bs4.BeautifulSoup(res.text) >>> type(noStarchSoup)
<class 'bs4.BeautifulSoup'>

It uses CSS selectors to find the HTML, like this:

soup.select('input[type="button"]')

select returns a list that contains more soup objects

"""

import bs4

import time as t

import os

import csv

# Página web inicial
# try:
    # res = r.get('https://learnthesewordsfirst.com/LearnTheseWordsFirst.html')
    # res.raise_for_status()
    # print("Se accedió al sitio")
    # pag = bs4.BeautifulSoup(res.text)
#     # print(pag.prettify())
# except Exception as e:
#     print("No se ha podido acceder a la página correctamente")
#     print(e)
"""
Acceso a la página principal
"""
pag = open('pag.html','rt')
html = bs4.BeautifulSoup(pag.read(), features="html.parser")
path = "https://learnthesewordsfirst.com/"
data = {}
try:
    lessons = html.find_all('a', class_ = "Section")
    # Análisis de lecciones
    for les in lessons:
        data_l = {}
        enlace = path + les['href']
        exito = False
        try:
            # Acceso a la lección individual
            res = r.get(enlace)
            res.raise_for_status()
            print("Se accedió a la lección", end=" ")
            pag = bs4.BeautifulSoup(res.text, features="html.parser")
            exito = True
        except Exception as e:
            print("Surgió un error durante el procesamiento de la lección" + les.text)
            print(e)
        if(exito):
            # Acceso exitoso
            # Análisis de secciones
            caracteres = []
            for char in les.text:
                if char.isalnum():
                    caracteres.append(char)
                    if len(caracteres) == 2:
                        break
            path_aux = caracteres[0] + '/' + caracteres[1]
            les_numero = caracteres[0] + caracteres[1]
            print(les_numero)
            os.makedirs(path_aux, exist_ok=True)
            print("| Se creó el directorio de la lección " + les_numero)
            try:
                sections = pag.select('div > div')
                #print(sections)
                # print(sections[0].prettify())
                data_sec = {}
                for s in sections:
                    if s['id'] == 'Quiz':
                       continue
                    print("| Estoy en una nueva sección")
                    # if s == '\n':
                    #     continue
                    # print(s.contents)
                    primeraDef = True
                    primeraCap = True
                    # Análisis de cada párrafo de cada lección
                    # Los datos se almacenan en este índice temporalmente
                    idx_tmp = {}
                    for p in s.contents:
                        if p == '\n':
                            continue
                        print("| | Estoy en un nuevo párrafo con clase", end=" ")
                        #print(p.attrs)
                        #print("Hijo 1:", end="\n    ")
                        #print(type(p),"\n")
                        data_p = {}
                        try:
                            # Clasificación por casos
                            clase = p['class'][0]
                            print(clase)
                            # print(clase)
                            if clase == 'Definition':
                                if primeraDef:
                                    idx = p.text[0:4]
                                    txt = p.text[6:]
                                    data_p['idx'] = idx
                                    idx_tmp = idx
                                    data_p['def'] = [txt]
                                    data_sec[idx] = {'def': [txt]}
                                    primeraDef = False
                                else:
                                    data_p['def'].append(p.text)
                                    data_sec[idx_tmp]['def'].append(p.text)
                            elif clase == 'Image' or clase == 'Gloss':
                                tag_img = p.img['src'].lstrip('/')
                                print(
                                    "| | | La imagen tiene una ruta relativa de: ", tag_img)
                                try:
                                    print(
                                        "| | | La imagen tiene una ruta absoluta de: ", path + tag_img)
                                    res = r.get(path + tag_img)
                                    res.raise_for_status()
                                    print("| | | La imagen se va a guardar en:",
                                          path_aux + '/' + idx_tmp + "_" + clase + ".png")
                                    img = open(path_aux + '/' + idx_tmp + "_" + clase + ".png", 'wb')
                                    for chunk in res.iter_content(100000):
                                        print("| | | | Guardado en proceso")
                                        img.write(chunk)
                                    img.close()
                                    print("| | | | Guardado completo")
                                except Exception as e:
                                    print(
                                        "| | | | Error al momento de descargar la imagen")
                                    print(type(e))
                                    print(e)
                            elif clase == 'Caption':
                                txt = p.text
                                if primeraCap:
                                    data_p['cap'] = [txt]
                                    data_sec[idx_tmp]['cap'] = [txt]
                                    primeraDef = False
                                else:
                                    data_p['cap'].append(txt)
                                    data_sec[idx_tmp]['cap'].append(txt)
                        except Exception as e:
                            print("Error al procesar los contenidos de la lección")
                            print(e)
                    print("| | Datos obtenidos:\n| | ", data_sec)
                    t.sleep(2)
                    # break
            except Exception as e:
                print("| No se ha podido acceder a los contenidos de la lección", les.text)
                print(e)
        break # Eliminar una vez comprobado que esto funciona
except Exception as e:
    print("No se ha podido acceder a alguna lección")
    print(e)
