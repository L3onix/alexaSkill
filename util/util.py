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
    arr = []
    # quem = []
    # eleito = ""
    # quem.append(process.extractBests(valores.Contato.to_list(), contato))
    # print(quem)
    # quem.append(process.extractBests(valores.Setor.to_list(), contato))
    # print()
    # eleito = process.extractOne(quem, contato)
    
    for i, valor in enumerate(valores):
        if valor is not None:
            if fuzz.ratio(valor, contato) > 50:
                arr.append(i)
                print("Ratio: O valor buscado: {} em {} na posição {}.".format(contato, valor,  i))
            else:
                if fuzz.token_sort_ratio(valor, contato) > 60:
                    arr.append(i)
                    print("Token: O valor buscado: {} em {} na posição {}.".format(contato, valor,  i))
    
    return arr

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
    return df