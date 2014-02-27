# -*- coding: utf-8 -*-

import MySQLdb
import requests
import sys
import json

#ENDPOINT = "http://brainiak.semantica.globoi.com/g1/EditoriaG1/"
ENDPOINT = "http://localhost:5100/g1/EditoriaG1/"

def retrieve_folders():
    response = requests.get(ENDPOINT + "?per_page=1000&p=g1:editoria_id")
    return [int(editoria["g1:editoria_id"]) for editoria in response.json()["items"]]


def load_data_from_mysql():
    db = MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="",
        db='g1')
    db.set_character_set('utf8')
    cursor = db.cursor()


    QUERY = """
    SELECT DISTINCT
        folder.name_txt, folder.folder_id
    FROM
        folder
    """

    cursor.execute(QUERY)
    return cursor.fetchall()

def insert_in_brainiak(folders_and_ids, already_existent_folder_ids):
    print('Inserting in Brainiak %s' % ENDPOINT)
    print("New folders {0}".format(len(folders_and_ids)))
    print("Already existing folders {0}".format(len(already_existent_folder_ids)))

    print(already_existent_folder_ids)
    for label, _id in folders_and_ids:
        editoria_id = int(_id)
        if editoria_id in already_existent_folder_ids:
            continue
        payload_template = {
            "rdfs:label": label,
            "g1:editoria_id": editoria_id
        }
        payload = json.dumps(payload_template)
        print(payload)
        response = requests.post(ENDPOINT, data=payload)
        print(response.status_code)
        if response.status_code != 201:
            print(response.text)
            sys.exit(1)


if __name__ == "__main__":
    unique_folder_ids = retrieve_folders()
    folders_and_ids = load_data_from_mysql()
    insert_in_brainiak(folders_and_ids, unique_folder_ids)
