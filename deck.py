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

# print(termcolor.COLORS) 'grey': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37


query_lecs = "SELECT * FROM lec_lecciones ORDER BY lec_num,lec_id"
lecs = query_read(connection, query_lecs)
contador_lec = 0
lec_actual = None
for lec in lecs:
    # query_anki_lecciones = "UPDATE lec_lecciones SET lec_anki='" + \
    #     str(random.randrange(1 << 30, 1 << 31)) + "' WHERE lec_id='" + lec[0] + "'"
    # print(query_anki_lecciones)
    # query_execute(connection, query_anki_lecciones)
    if lec[1] != contador_lec:
        contador_lec = lec[1]
        print("Lección " + str(lec[1]))
    lec_actual = lec[0]
    print("| Sublección " + lec[0])

    query_pal = "SELECT * FROM pal_palabra WHERE lec_id='" + lec[0] + "'"
    pals = query_read(connection, query_pal)

    for pal in pals:
        # query_anki_palabra = "UPDATE pal_palabra SET pal_anki=" + \
        #     str(random.randrange(1 << 30, 1 << 31)) + " WHERE pal_id='" + str(pal[0]) + "'"
        # query_execute(connection, query_anki_palabra)
        print("| | Palabra " + str(pal[0]) + ": " + pal[1])
        # print("| | | " + query_anki_palabra)
        query_defs = "SELECT * FROM def_definicion WHERE pal_id='" + \
            pal[0] + "' ORDER BY def_orden"
        defs = query_read(connection, query_defs)

        for defi in defs:
            print("| | | Definición " + str(defi[3]) + ": ")
            print("| | | | " + defi[2])
        
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

        if(contador_lec < 3):
            print("| | | Imagen ")
            path = './' + lec_actual[:-1] + '/' + lec_actual[-1] + '/' + pal[0] + '_'
            if(os.path.exists(path + 'Gloss.png')):
                print("| | | | " + path + 'Gloss.png')
            if(os.path.exists(path + 'Image.png')):
                print("| | | | " + path + 'Image.png')


# print(random.randrange(1 << 30, 1 << 31))

# Este código se ejecuta una sola vez
# for i in range(0,13):
#     query_mazo = "INSERT INTO maz_mazo VALUES (" + str(i) + ", " + str(
#         random.randrange(1 << 30, 1 << 31)) + ")"
#     print(query_mazo)
#     query_execute(connection,query_mazo)
# Nota: El registro 13 es el deck principal

# TODO: Actualizar los ids de cada lección y de cada nota

# for i in range(0,97):
    # query_lecciones = "UPDATE lec_lecciones SET lec_anki='" + str(random.randrange(1 << 30, 1 << 31)) + "'"
