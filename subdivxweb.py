import requests
from bs4 import BeautifulSoup
import concurrent.futures
import streamlit as st



results = []
links = []


def show(array):
    for item in array:
        st.write(f'Link: {item[1]}')
        st.write(f'Descripción: {item[2]}')
        st.write(f'Número de descargas: {item[0]}')
        st.markdown('---')


def search_comments(url):
    global key_word
    global key_word2
    global test
    global test2
    test = False
    test2 = False
    r = requests.get(url)
    soup2 = BeautifulSoup(r.text, 'html.parser')
    comments = soup2.find_all('div', id='detalle_reng_coment1')
    titulo = soup2.find_all('div', id='detalle_datos')[0].find('font').text.lower()
    for item2 in comments:
        comment = item2.text.lower()
        if key_word in comment and key_word2 in comment:
            downloads = int(str(soup2.find_all('div', id='detalle_datos')[0].find_all('span')[2].text).replace(',', ''))
            if key_word == '' and key_word2 == '':
                bold_comment = comment
            elif key_word == '':
                bold_comment = comment.replace(f"{key_word2}",f":green[{key_word2}]")
            elif key_word2 == '':
                bold_comment = comment.replace(f"{key_word}",f":green[{key_word}]")
            else:
                bold_comment = comment.replace(f"{key_word}",f":green[{key_word}]").replace(f"{key_word2}",f":green[{key_word2}]")
            
            
            results.append([downloads, url, bold_comment])
            break
            
        if key_word in comment or key_word in titulo:
            test = True
        if key_word2 in comment or key_word2 in titulo:
            test2 = True


st.set_page_config(page_title='Buscador para Subdivx', layout='wide')

columnaA, columnaB = st.columns(2)
columna1, columna2 = st.columns([1,1.5], gap="medium")

with columnaA:
    st.header('Buscador de subtitulos para Subdivx.com')
    st.write('Busca tanto en descripciones como en comentarios.')
    st.write('No es obligatorio ingresar 2 palabras claves')

with columna1:

    form = st.form(key='Buscar')
    with form:
        movie = st.text_input('Titulo de la película o serie: ').lower()
        key_word = st.text_input('Palabra clave 1 (p. ej. 720p o 1080p): ').lower()
        key_word2 = st.text_input('Palabra clave 2 (p. ej. argenteam): ').lower()
        form.form_submit_button('Buscar')

header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/109.0.0.0 Safari/537.36'
          }

payload = {'buscar2': movie,
           'accion': '5',
           'masdesc': '',
           'subtitulos': '1',
           'realiza_b': '1'
           }

if movie:
    response = requests.post(f'https://www.subdivx.com/index.php', data=payload, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')

    descriptions = soup.find_all('div', id='buscador_detalle_sub')

    results.clear()

    count = 0
    movie_link = ''
    for item in descriptions:
        description = item.text.lower()
        if key_word in description and key_word2 in description:
            movie_link = soup.find_all('a', {'class': 'titulo_menu_izq'}, href=True)[count]['href']
            downloads = int(str(soup.find_all('div', id='buscador_detalle_sub_datos')[count].find('b').next_sibling).replace(',', ''))
            if key_word == '' and key_word2 == '':
                bold_description = description
            elif key_word == '':
                bold_description = description.replace(f"{key_word2}",f":green[{key_word2}]")
            elif key_word2 == '':
                bold_description = description.replace(f"{key_word}",f":green[{key_word}]")
            else:
                bold_description = description.replace(f"{key_word}",f":green[{key_word}]").replace(f"{key_word2}",f":green[{key_word2}]")
            
                
            results.append([downloads, movie_link, bold_description])

        count += 1

    results.sort(key=lambda x: int(-x[0]))

    if len(results) > 0:
        with columna2:
            show(results)

    elif not movie_link:
        all_links = soup.find_all('a', {'class': 'titulo_menu_izq'}, href=True)
        for item in all_links:
            url = item['href']
            links.append(url)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(search_comments, links)

        links.clear()
        results.sort(key=lambda x: int(-x[0]))
        if len(results) > 0:
            with columna2:
                show(results)

    if len(results) == 0:
        try:
            if test is False and test2 is True:
                st.warning(f'La palabra "{key_word}" no se pudo encontrar')
            elif test is True and test2 is False:
                st.warning(f'La palabra "{key_word2}" no se pudo encontrar')
            elif test is False and test2 is False:
                st.warning(f'Ninguna palabra se pudo encontrar')
            else:
                st.warning(f'Las 2 palabras existen pero no en la misma frase.  Intenta buscando solo una de ellas')
        except:
            st.warning(f'Subdivx no encuentra resultados para esa película o serie')
