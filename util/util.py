from fuzzywuzzy import fuzz, process
from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas as pd

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def match_value(valores, contato):
    quem = []
    eleito = []
    quem.append(process.extractOne(contato, valores.Contato.to_list()))
    quem.append(process.extractOne(contato, valores.Setor.to_list()))
    eleito = process.extractOne(contato, quem)
    eleito = eleito[0][0]

    # TODO Tratar quando ocorrem mais de um eleito. Busque por 'Antônia Custódia Pedreira'

    rowContato = valores.loc[valores.Contato == eleito]
    rowSetor = valores.loc[valores.Setor == eleito]

    if len(rowContato):
        return rowContato
    else:
        return rowSetor

    return []

def scraping_table_as_dataframe(url):
    html = urlopen(url)
    soup = BeautifulSoup(html,'html.parser')
    tables = soup.find_all('table')

    res = []
    for table in tables:
        table_rows = table.find_all('tr')
        for tr in table_rows:
            td = tr.find_all('td')
            row = [tr.text.strip() for tr in td if tr.text.strip()]
            if row:
                res.append(row)
    df = pd.DataFrame(res, columns=["Setor", "Contato", "Prefixo", "Ramal"])

    ## tratamento de dados:
    filtro_ramal1 = df["Ramal"].isnull()
    filtro_ramal2 = df["Prefixo"].notnull()
    filtro = filtro_ramal1 & filtro_ramal2


    df.loc[filtro, 'Ramal'] = df.loc[filtro, 'Prefixo']
    df.loc[filtro, 'Prefixo'] = df.loc[filtro, 'Contato']
    df.loc[filtro, 'Contato'] = None

    ## Copia o setor principal para o responsável.
    filtro_nonono = df.Ramal.isnull()
    index_nonono = df.loc[filtro_nonono].index
    
    for i in index_nonono:
        proximo = i + 1
        df.loc[proximo].Setor = df.loc[proximo].Setor + " " +  df.loc[i].Setor 

    ## exclui o setor principal sem responsável e telefone.
    df = df.loc[~filtro_nonono]

    #TODO Tratar o prefixo que conta nome de cidade

    #TODO Tratar o nome do contato para narrar apenas dois dois primeiros nomes

    #TODO Tratar os campos com mais de uma pessoa para narrar o nome das duas pessoas concatenados por 'e'

    return df

def contato_format_msg(contato):
    text = ""
    quem = ""
    onde = ""
    prefixo = ""
    ramal = ""
    print(contato)
    if contato.Contato.to_list()[0] != None:
        quem = contato.Contato.to_list()[0]
    if len(contato.Setor.to_list()[0]) != None:
        onde = contato.Setor.to_list()[0]
    if len(contato.Prefixo.to_list()[0]) != None:
        prefixo = contato.Prefixo.to_list()[0].split(" ")
        prefixo = prefixo[1]
        prefixo = list(prefixo)
        tmp = " ".join(prefixo)
        prefixo = tmp
    if len(contato.Ramal.to_list()[0]) != None:
        # TODO verificar a formatação da mensagem para narar os dois ramais, quando for o caso.
        ramal = contato.Ramal.to_list()[0].split("/")
        ramal = ramal[0]
        if(len(ramal) > 3):
            ramal = ramal[:2] + " " + ramal[2:]
        else:
            ramal = ""
    
    # TODO Alterar para narrar também o setor
    if len(ramal) > 1:
        if len(quem) < 2:
            text = "Para falar com {}, ligue para {} {}".format(onde, prefixo, ramal)
        else:
            text = "Para falar com {}, ligue para {} {}".format(quem, prefixo, ramal)
    else:
        text = "Infelizmente não tenho o telefone solicitado."
    return text