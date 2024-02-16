import requests
import concurrent.futures
import streamlit as st
from streamlit_extras.colored_header import colored_header
import json

results = []
args = []


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
        highlighted_text = result_text.replace(f"{key_word2}", f":green[{key_word2}]")
    elif key2 == '':
        highlighted_text = result_text.replace(f"{key_word}", f":green[{key_word}]")
    else:
        highlighted_text = result_text.replace(f"{key_word}", f":green[{key_word}]").replace(f"{key_word2}",
                                                                                             f":green[{key_word2}]")

    return highlighted_text


def searchComments(id, movie_title, download):
    global key_word
    global key_word2
    global test
    global test2

    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/121.0.0.0 Safari/537.36'
              }
    payload = {'getComentarios': id
               }

    response = requests.post(f'https://subdivx.com/inc/ajax.php', data=payload, headers=header)
    data = json.loads(response.text)

    for item in data['aaData']:
        comment = item['comentario'].lower()

        if key_word in comment and key_word2 in comment:
            downloads = download
            title = movie_title
            url = f'https://subdivx.com/descargar.php?id={id}_blank'
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

columna1, columna2 = st.columns([1, 1.5], gap="medium")

if 'title' not in st.session_state:
    st.session_state.title = None

with columna1:
    form = st.form(key='Buscar')
    with form:
        movie = st.text_input('Título de la película o serie: ').lower()
        key_word = st.text_input('Palabra clave 1 (p. ej. 720p o 1080p): ').lower()
        key_word2 = st.text_input('Palabra clave 2 (p. ej. argenteam): ').lower()
        form.form_submit_button('Buscar')

header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/121.0.0.0 Safari/537.36'
          }

payload = {'buscar': movie,
           'tabla': 'resultados',

           }

if movie:
    if 'extracted' not in st.session_state:
        st.session_state.extracted = []

    if st.session_state.title != movie:
        st.session_state.extracted = []
        st.session_state.title = movie

    if st.session_state.extracted == []:
        response = requests.post(f'https://subdivx.com/inc/ajax.php', data=payload, headers=header)
        data = json.loads(response.text)

        extracted_data = []
        for item in data['aaData']:
            extracted_item = {
                'id': item['id'],
                'descripcion': item['descripcion'],
                'descargas': item['descargas'],
                'titulo': item['titulo']
            }
            extracted_data.append(extracted_item)

        st.session_state.extracted = extracted_data

        if  st.session_state.extracted == []:
            st.warning(f'Subdivx no encuentra resultados para esa película o serie')
            st.stop()

        results.clear()

    test = False
    test2 = False
    movie_link = ""
    for item in st.session_state.extracted:
        description = item['descripcion'].lower()
        if key_word in description and key_word2 in description:
            movie_link = f'https://subdivx.com/descargar.php?id={item["id"]}_blank'
            movie_title = item['titulo']
            downloads = item['descargas']
            green_description = highlightGreen(key_word, key_word2, description)

            results.append([downloads, movie_link, green_description, movie_title])

        if key_word in description:
            test = True
        if key_word2 in description:
            test2 = True


    results.sort(key=lambda x: int(-x[0]))

    if len(results) > 0:
        with columna2:
            showResults(results)

    elif not movie_link:
        for item in st.session_state.extracted:
            id = item['id']
            movie_title = item['titulo']
            downloads = item['descargas']
            args.append((id, movie_title, downloads))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(searchComments, *zip(*args))

        args.clear()
        results.sort(key=lambda x: int(-x[0]))

        if len(results) > 0:
            with columna2:
                showResults(results)

    if len(results) == 0:
        if test is False and test2 is True:
            st.warning(f'La palabra "{key_word}" no se pudo encontrar')
            st.stop()
        elif test is True and test2 is False:
            st.warning(f'La palabra "{key_word2}" no se pudo encontrar')
            st.stop()
        elif test is False and test2 is False:
            st.warning(f'Ninguna palabra se pudo encontrar')
            st.stop()
        else:
            st.warning(f'Las 2 palabras existen pero no en la misma frase.  Intenta buscando solo una de ellas')
            st.stop()

    elif len(results) == 1:
        with columna1:
            st.success(f"{len(results)} resultado encontrado")
    else:
        with columna1:
            st.success(f"{len(results)} resultados encontrados")
