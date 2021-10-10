"""
webbrowser únicamente permite acceder
a un sitio web
"""
from termcolor import colored # que permite usar 
import csv
from mysql.connector import Error
import mysql.connector
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



def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Conexión exitosa al servidor")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
connection = create_connection("127.0.0.1", "root", "root", "p6anki")

def query_execute(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return True
    except Error as e:
        return e

def query_read(connection,query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        return e

def dd(var):
    print(var)
    exit()

# Conexión a la base de datos

"""
La base de datos se crea con:

CREATE TABLE lec_lecciones(
	lec_id VARCHAR(3) PRIMARY KEY,
	lec_num TINYINT UNSIGNED
);
CREATE TABLE pal_palabra(
	pal_id VARCHAR(5) PRIMARY KEY,
	pal_nombre VARCHAR(100),
	lec_id VARCHAR(3),
	FOREIGN KEY (lec_id) REFERENCES lec_lecciones(lec_id)
)
CREATE TABLE def_definicion(
	def_id INT PRIMARY KEY AUTO_INCREMENT,
	pal_id VARCHAR(5),
	def_contenido TEXT,
	def_orden INT,
	FOREIGN KEY (pal_id) REFERENCES pal_palabra(pal_id)
)
CREATE TABLE cap_caption(
	cap_id INT PRIMARY KEY AUTO_INCREMENT,
	pal_id VARCHAR(5),
	cap_contenido TEXT,
	cap_orden INT,
	FOREIGN KEY (pal_id) REFERENCES pal_palabra(pal_id)
)
"""

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
    contador_lecciones = 0
    for les in lessons:
        contador_lecciones += 1
        # if(contador_lecciones < (8*9 +1)):
        #     continue
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
        # if(contador_lecciones >= 8*9 +1):
        #     break
        if(exito):
            # Acceso exitoso
            # Análisis de secciones
            caracteres = ["",""]
            # TODO: Cambiar esto para que funcione con el id de los hipervínculos
            for char in les['id']:
                if char.isalnum():
                    if char.isdigit():
                        caracteres[0] += char
                    else:
                        caracteres[1] += char
            path_aux = caracteres[0] + '/' + caracteres[1]
            les_numero = caracteres[0] + caracteres[1]
            print(les_numero)
            os.makedirs(path_aux, exist_ok=True)
            print("| Se creó el directorio de la lección " + les_numero)
            les_query = "INSERT IGNORE INTO lec_lecciones VALUES ('" + les_numero + "'," + caracteres[0] + ")"
            db_res = query_execute(connection, les_query)
            if(db_res == True):
                print("| Se creó el registro en la base de datos para la lección " + les_numero)
            else:
                print("| No se pudo crear el registro para " + les_numero + "intentando con la siguiente lección")
                continue
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
                    orden_pal = 1
                    orden_cap = 1
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
                            # TODO: Lidiar con los errores de las definiciones complejas
                            if clase == 'Definition':
                                try:
                                    if primeraDef:
                                        # Obtiene el índice de la palabra
                                        if(contador_lecciones < 73):
                                            idx = p.text[0:4]
                                            txt = p.text[6:]
                                        else:
                                            idx = p.text[0:5]
                                            txt = p.text[7:]
                                        # Guardado de datos
                                        data_p['idx'] = idx
                                        idx_tmp = idx
                                        data_sec[idx] = {'def': [txt]}
                                        data_p['def'] = [txt]
                                        # Guardado en la base de datos
                                        pos = txt.find(',')
                                        if(pos > 0):
                                            palabra = txt[0:pos]
                                        else:
                                            palabra = txt
                                        print("| | | Guardando " + palabra +
                                            " con identificador " + idx_tmp + " en la BD")
                                        query_idx = "INSERT IGNORE INTO pal_palabra VALUES ('" + \
                                            idx_tmp + "', '" + palabra + "', '" + les_numero + "')"
                                        res = query_execute(connection, query_idx)
                                        if(res == True):
                                            print("| | | Se ha guardado "  + palabra + " en la BD con éxito")
                                        else:
                                            print("| | | Error al guardar " + palabra + " en la BD, cancelando iteración")
                                            break
                                        primeraDef = False
                                        # Contenido de query
                                        contenido = txt
                                    else:
                                        # print(colored('| | | Esta es la definición ' + str(orden_pal), 'magenta'))
                                        # print("| | | ", data_p, data_sec)
                                        data_sec[idx_tmp]['def'].append(p.text)
                                        contenido = p.text
                                    print("| | | Guardando nueva definición con orden " + str(orden_pal) + " en la BD")
                                    query_def = "INSERT IGNORE INTO def_definicion(pal_id,def_contenido,def_orden) VALUES ('" + idx_tmp + "', '" + contenido + "', " + str(orden_pal)+ ")"
                                    res = query_execute(connection, query_def)
                                    if(res == True):
                                        print("| | | Se ha guardado la definición en la BD con éxito")
                                    else:
                                        print(
                                            "| | | Error guardando la definición en la BD")
                                    orden_pal += 1
                                except Exception as e:
                                    print("| | | Error con el guardado de definición: ", e)
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
                                contenido = p.text
                                if primeraCap:
                                    #data_p['cap'] = [txt]
                                    data_sec[idx_tmp]['cap'] = [txt]
                                    primeraDef = False
                                else:
                                    #data_p['cap'].append(txt)
                                    data_sec[idx_tmp]['cap'].append(txt)
                                print("| | | Guardando nueva leyenda con orden " + str(orden_cap) + " en la BD")
                                query_def = "INSERT IGNORE INTO cap_caption(pal_id,cap_contenido,cap_orden) VALUES ('" + \
                                    idx_tmp + "', '" + contenido + \
                                    "', " + str(orden_cap) + ")"
                                res = query_execute(connection, query_def)
                                if(res == True):
                                    print(
                                        "| | | Se ha guardado la leyenda en la BD con éxito")
                                else:
                                    print(
                                        "| | | Error guardando la leyenda en la BD")
                                orden_cap += 1
                        except Exception as e:
                            print(
                                "Error al procesar los contenidos de la lección", les_numero)
                            print(e)
                    print("| | Datos obtenidos:\n| | ", data_sec)
                    # t.sleep(2)
                    # break
            except Exception as e:
                print(
                    "| No se ha podido acceder a los contenidos de la lección", les_numero)
                print(e)
        # break # Eliminar una vez comprobado que esto funciona
        # if contador_lecciones >= 49:
            # break
        t.sleep(2)
except Exception as e:
    print("No se ha podido acceder a alguna lección")
    print(e)
