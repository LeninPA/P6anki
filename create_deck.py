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

print(mazos_lec, "\n")
print(mazos_sublec, "\n")
print(p6anki)

packs_mazos_sublec = []

contador = 1

for j in range(len(mazos_lec)):
    pack_temp = genanki.Package([i for i in mazos_sublec[j]])
    packs_mazos_sublec.append(pack_temp)
    pack_temp.write_to_file('p6anki' + str(contador) + '.apkg')
    contador += 1


#genanki.Package(p6anki).write_to_file('p6anki.apkg')
