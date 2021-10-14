from logging import exception
from termcolor import colored  # que permite usar
import termcolor

from mysql.connector import Error
import mysql.connector

import os

import genanki

import random


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


def query_read(connection, query):
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

query_mazos = "SELECT * FROM maz_mazo"
mazos = query_read(connection,query_mazos)
# Creación del mazo principal
nombre_deck_root = 'P6Anki'
p6anki = genanki.Deck(
    mazos[-1][1], 
    nombre_deck_root
)

mazos_lec = []
mazos_sublec = []

# Obtención de todas las sublecciones
query_lecs = "SELECT * FROM lec_lecciones ORDER BY lec_num,lec_id"
lecs = query_read(connection, query_lecs)
contador_lec = 0
lec_actual = None
nombre_deck_lec = None
estilo = """
.card {
 font-family: tahoma;
 font-size: 40px;
 text-align: center;
 color: #4a4a4a;
 background-color: white;
}


a {color:#496899}



img {
  max-width: none;
  max-height: none;
}


alter{
color: gray;
 font-size: 0.5em;
}

"""
card_palabra = genanki.Model(
    2091182666,
    'Tarjeta Simple',
    fields=[
        {'name': 'Palabra'},
        {'name': 'Alternativas'},
        {'name': 'Definiciones'}
    ],
    templates=[
        {
            'name': 'Tarjeta 1',
            'qfmt': '<b>{{Palabra}}</b><br><alter>{{Alternativas}}</alter>',
            'afmt': '{{FrontSide}}<hr id="answer">{{Definiciones}}'
        }
    ],
    css=estilo
)
card_palabra_img = genanki.Model(
    1532808237,
    'Tarjeta con Imagen',
    fields=[
        {'name': 'Palabra'},
        {'name': 'Alternativas'},
        {'name': 'Imagen'},
        {'name': 'Leyendas'},
        {'name': 'Definiciones'},
        {'name': 'Gloss'}
    ],
    templates=[
        {
            'name': 'Tarjeta 1',
            'qfmt': '<b>{{Palabra}}</b><br><alter>{{Alternativas}}</alter>',
            'afmt': '{{FrontSide}}<hr id="answer">{{Imagen}}<br>{{Leyendas}}<br>{{Definiciones}}<br>{{Gloss}}'
        }
    ],
    css=estilo
)

my_model = genanki.Model(
    1607392319,
    'Simple Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ])

path_media = []

for lec in lecs:
    if lec[1] != contador_lec:
        # Creación de nuevo submazo
        nombre_deck_lec = 'Lesson-' + str(mazos[contador_lec][0])
        mazo_lec_temp = genanki.Deck(
            mazos[contador_lec][1],
            nombre_deck_root + "::" + nombre_deck_lec
        )
        contador_lec = lec[1]
        print("Lección " + str(lec[1]))
        mazos_lec.append(mazo_lec_temp)
        mazos_sublec.append([])
    lec_actual = lec[0]
    mazo_sublec = genanki.Deck(
        lec[2], 
        nombre_deck_root + "::" + nombre_deck_lec + "::" + lec[0]
    )
    print("| Sublección " + lec[0])
    my_note = genanki.Note(
        model=my_model,
        fields=['Capital of Argentina', 'Buenos Aires'])
    mazo_sublec.add_note(my_note)
    mazos_sublec[contador_lec - 1].append(mazo_sublec)

    query_pal = "SELECT * FROM pal_palabra WHERE lec_id='" + lec[0] + "'"
    pals = query_read(connection, query_pal)

    for pal in pals:
        pal_con_imagen = False
        pal_imagen = False
        pal_gloss = False
        datos_pal = {'defs': [], 'caps': []}
        print("| | Palabra " + str(pal[0]) + ": " + pal[1])
        query_defs = "SELECT * FROM def_definicion WHERE pal_id='" + \
            pal[0] + "' ORDER BY def_orden"
        defs = query_read(connection, query_defs)
        # Alternativas de la palabra
        alternativas = None
        for defi in defs:
            print("| | | Definición " + str(defi[3]) + ": ")
            print("| | | | " + defi[2])
            datos_pal['defs'].append(defi[2])

        query_caps = "SELECT * FROM cap_caption WHERE pal_id='" + \
            pal[0] + "' ORDER BY cap_orden"
        caps = query_read(connection, query_caps)

        captions = []

        for cap in caps:
            saltar = False
            for c in captions:
                if c == cap[2]:
                    saltar = True
            if(saltar):
                continue
            print("| | | Leyenda " + str(cap[3]) + ": ")
            print("| | | | " + cap[2])
            captions.append(cap[2])
            datos_pal['caps'].append(cap[2])

        if(contador_lec < 3):
            print("| | | Imagen ")
            path = './' + lec_actual[:-1] + '/' + \
                lec_actual[-1] + '/' + pal[0] + '_'
            if(os.path.exists(path + 'Gloss.png')):
                print("| | | | " + path + 'Gloss.png')
                datos_pal['gloss'] = path + 'Gloss.png'
                pal_con_imagen = True
                pal_gloss = True
            if(os.path.exists(path + 'Image.png')):
                print("| | | | " + path + 'Image.png')
                datos_pal['img'] = path + 'Image.png'
                pal_con_imagen = True
                pal_imagen = True
        # Declaración de la slaternativas para la palabra y las posibles
        # definiciones que pueda llegar a tener
        alternativas = datos_pal['defs'][0]
        del datos_pal['defs'][0]
        try:
            definiciones = '<br>'.join(datos_pal['defs'])
        except:
            definiciones = ''
        try:
            leyendas_pal_anki = '<br>'.join(datos_pal['caps'])
        except:
            leyendas_pal_anki = ''
        if(pal_con_imagen):
            if(pal_imagen):
                path_imagen = '<img src="' + path + 'Image.png">' 
                path_media.append(path + 'Image.png')
            else:
                path_imagen = ''
            if(pal_gloss):
                path_gloss = '<img src="' + path + 'Gloss.png">' 
                path_media.append(path + 'Gloss.png')
            else:
                path_gloss = ''
            nota_pal = genanki.Note(
                model=card_palabra_img,
                fields=[
                    pal[1],
                    alternativas,
                    path_imagen,
                    leyendas_pal_anki,
                    definiciones,
                    path_gloss
                ]
            )
        else:
            nota_pal = genanki.Note(
                model=card_palabra,
                fields=[
                    pal[1],
                    alternativas,
                    definiciones
                ]
            )
        mazo_sublec.add_note(nota_pal)
        # TODO: Crear las notas

print(mazos_lec, "\n")
print(mazos_sublec, "\n")
print(p6anki)

packs_mazos_sublec = []

mazos_sin_orden = []
contador = 0
for k in mazos_sublec:
    for l in k:
        mazos_sin_orden.append(l)

pack_temp = genanki.Package([i for i in mazos_sin_orden])
pack_temp.media_files = [i for i in path_media]
pack_temp.write_to_file('p6anki.apkg')

#genanki.Package(p6anki).write_to_file('p6anki.apkg')
