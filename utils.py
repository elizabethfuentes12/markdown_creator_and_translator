import os
import re
import base64
import requests
from bs4 import BeautifulSoup
import html2text
import translate

# brew install pandoc

def convert_docx_to_markdown(docx_file):
    folder = os.path.dirname(docx_file)
    input_file = os.path.basename(docx_file)
    current_dir  = os.path.dirname(__file__)
    os.chdir(folder)
    output_file = input_file.split(".")[0] + ".md"
    print (f"{input_file} --> {output_file}")

    command = f"pandoc -s {input_file} -t markdown -o {output_file} --extract-media ."
    os.system(command)
    os.chdir(current_dir)
    return docx_file.split(".")[0] + ".md"



def load_content(file_name):
    with open(file_name, 'r') as f:
        return f.read()
    
def load_with_images(file_name):
    folder = os.path.dirname(file_name)    
    text_content = load_content(file_name)

    pattern = r'([\w\./]+\.(jpg|png))'
    substrings = re.split(pattern, text_content)
    splits = []
    for spl in substrings:
        if len(spl)> 3:
            splits.append(spl)

    content = []

    for match in splits:
        if os.path.exists(f"{folder}/{match}"):
            print(f"The file '{match}' exists.")
            content.append(load_image_as_content(f"{folder}/{match}"))
        else:
            content.append({"type":"text", "text": match})

    return content



def load_image_as_content(image_path):

    media_type = "image/jpeg"
    if image_path.endswith(".png"):
        media_type = "image/png"

    with open(image_path, "rb") as image_file:
        content_image = base64.b64encode(image_file.read()).decode('utf8')

    return { "type": "image","source": { "type": "base64", "media_type": media_type,"data": content_image}}

def convert_html_component_to_markdown(url, element_type, output_file):
    try:
        # Fetch the HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the specific element using the provided element type
        element = soup.find(element_type)

        if element:
            #tag = element.div
            #soup_2 = BeautifulSoup(str(tag), 'html.parser')
            # Convertir el HTML a Markdown utilizando la biblioteca html2text
            md_converter = html2text.HTML2Text()
            md_converter.body_width = 0  # Evita el ajuste de línea automático
            markdown = md_converter.handle(element.prettify())
            with open(output_file, 'w') as file:
                file.write(markdown)
            print(f"Conversion successful. Markdown file saved as {output_file}")
            return markdown
        else:
            print(f"Element not found with the tag: {element_type}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the HTML content: {e}")


def split_markdown_file(file_path, chunk_size=2500, output_dir='output'):
    # Leer el contenido del archivo Markdown
    with open(file_path, 'r') as file:
        content = file.read()

    # Dividir el contenido en líneas
    lines = content.split('\n')

    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Inicializar variables
    chunk_counter = 1
    current_chunk = ''

    # Recorrer las líneas del contenido
    for line in lines:
        # Agregar la línea actual al chunk actual
        current_chunk += line + '\n'

        # Verificar si el tamaño del chunk actual supera el tamaño máximo
        if len(current_chunk) >= chunk_size:
            # Buscar la última separación de línea en el chunk actual
            last_newline_index = current_chunk.rfind('\n', 0, chunk_size)

            # Dividir el chunk en el último salto de línea encontrado
            chunk_to_write = current_chunk[:last_newline_index]
            current_chunk = current_chunk[last_newline_index + 1:]

            # Generar el nombre del archivo de salida
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_chunk_{chunk_counter}.md")

            # Escribir el chunk en el archivo de salida
            with open(output_file, 'w') as file:
                file.write(chunk_to_write)

            # Incrementar el contador de chunks
            chunk_counter += 1

    # Escribir el último chunk si no está vacío
    if current_chunk.strip():
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_chunk_{chunk_counter}.md")
        with open(output_file, 'w') as file:
            file.write(current_chunk)

    print(f"El archivo {file_path} se ha dividido en {chunk_counter} chunks en el directorio {output_dir}.")

def join_markdown_files(input_dir, output_file,language):
    # Obtener la lista de archivos Markdown en el directorio de entrada
    markdown_files = [file for file in os.listdir(input_dir) if file.endswith('.md')]

    # Ordenar los archivos por nombre
    markdown_files.sort()

    # Abrir el archivo de salida en modo escritura
    with open(output_file, 'w') as output:
        # Recorrer los archivos Markdown
        for file in markdown_files:
            file_path = os.path.join(input_dir, file)
            old_blog_content = load_with_images(file_path)
            translate_review = translate.get_suggestions(chat, old_blog_content,language)

            # Escribir el contenido en el archivo de salida
            output.write(translate_review)

            # Agregar una línea en blanco entre los archivos
            output.write('\n\n')

    print(f"Los archivos Markdown en {input_dir} se han unido en el archivo {output_file}.")

