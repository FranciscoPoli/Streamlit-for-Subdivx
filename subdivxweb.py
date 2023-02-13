import requests
from bs4 import BeautifulSoup
import concurrent.futures
import streamlit as st
from streamlit_extras.colored_header import colored_header


results = []
links = []


def showResults(array):
    for item in array:
        st.write(f'Título: {item[3]}')
        st.write(f'Link: {item[1]}')
        st.write(f'Descripción: {item[2]}')
        st.write(f'Número de descargas: {item[0]}')
        st.markdown('---')


def highlightGreen(key1, key2, result_text):
    if key1 == '' and key2 == '':
        highlighted_text = result_text
    elif key1 == '':
        highlighted_text = result_text.replace(f"{key_word2}",f":green[{key_word2}]")
    elif key2 == '':
        highlighted_text = result_text.replace(f"{key_word}",f":green[{key_word}]")
    else:
        highlighted_text = result_text.replace(f"{key_word}",f":green[{key_word}]").replace(f"{key_word2}",f":green[{key_word2}]")
    
    return highlighted_text
            
        
def searchComments(url):
    global key_word
    global key_word2
    global test
    global test2
    
    r = requests.get(url)
    soup2 = BeautifulSoup(r.text, 'html.parser')
    comments = soup2.find_all('div', id='detalle_reng_coment1')
    title = soup2.find_all('div', id='menu_titulo_buscador')[0].find('b').find('span').text
    for item in comments:
        comment = item.text.lower()
        if key_word in comment and key_word2 in comment:
            downloads = int(str(soup2.find_all('div', id='detalle_datos')[0].find_all('span')[2].text).replace(',', ''))
            green_comment = highlightGreen(key_word, key_word2, comment)
            
            results.append([downloads, url, green_comment, title])
            break
            
        if key_word in comment:
            test = True
        if key_word2 in comment:
            test2 = True


st.set_page_config(page_title='Buscador para Subdivx', layout='wide')

colored_header(
    label="Buscador de subtítulos para Subdivx.com",
    description="Busca tanto en descripciones como en comentarios.  No es obligatorio ingresar 2 palabras claves",
    color_name="violet-70",
)

columna1, columna2 = st.columns([1,1.5], gap="medium")

with columna1:
    form = st.form(key='Buscar')
    with form:
        movie = st.text_input('Título de la película o serie: ').lower()
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
    if not descriptions:
        st.warning(f'Subdivx no encuentra resultados para esa película o serie')
        st.stop()

    results.clear()

    count = 0
    movie_link = ''
    test = False
    test2 = False
    for item in descriptions:
        description = item.text.lower()
        if key_word in description and key_word2 in description:
            movie_link = soup.find_all('a', {'class': 'titulo_menu_izq'}, href=True)[count]['href']
            movie_title = soup.find_all('a', {'class': 'titulo_menu_izq'}, href=True)[count].text
            downloads = int(str(soup.find_all('div', id='buscador_detalle_sub_datos')[count].find('b').next_sibling).replace(',', ''))
            green_description = highlightGreen(key_word, key_word2, description)
            
            results.append([downloads, movie_link, green_description, movie_title])
        
        if key_word in description:
            test = True
        if key_word2 in description:
            test2 = True

        count += 1

    results.sort(key=lambda x: int(-x[0]))
    
    if len(results) > 0:
        with columna2:
            showResults(results)

    elif not movie_link:
        all_links = soup.find_all('a', {'class': 'titulo_menu_izq'}, href=True)
        for item in all_links:
            url = item['href']
            links.append(url)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(searchComments, links)

        links.clear()
        results.sort(key=lambda x: int(-x[0]))
        
        if len(results) > 0:
            with columna2:
                showResults(results)

    if len(results) == 0:
        if test is False and test2 is True:
            st.warning(f'La palabra "{key_word}" no se pudo encontrar')
        elif test is True and test2 is False:
            st.warning(f'La palabra "{key_word2}" no se pudo encontrar')
        elif test is False and test2 is False:
            st.warning(f'Ninguna palabra se pudo encontrar')
        else:
            st.warning(f'Las 2 palabras existen pero no en la misma frase.  Intenta buscando solo una de ellas')
      
