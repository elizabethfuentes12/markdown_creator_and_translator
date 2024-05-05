import os
import re
import base64
import requests
from bs4 import BeautifulSoup
import html2text
import translate
import shutil

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

def convert_html_component_to_markdown(url):

    url_domain = f"{url.split("/")[2]}"
    if url.split("/")[-1] == "":
        output_md_file = f"markdown_files/{url.split('/')[-2]}.md"
    if url_domain == "aws.amazon.com":
        element_type = "section"
    elif url_domain == "community.aws":
        element_type = "article"
    else:
        print("EROR - Create a new element_type for: ", url_domain)
        return
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

            # Convertir el HTML a Markdown utilizando la biblioteca html2text
            md_converter = html2text.HTML2Text()
            md_converter.body_width = 0  # Evita el ajuste de línea automático
            markdown = md_converter.handle(element.prettify())
            with open(output_md_file, 'w') as file:
                file.write(markdown)
            print(f"Conversion successful. Markdown file saved as {output_md_file}")
        else:
            print(f"Element not found with the tag: {element_type}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the HTML content: {e}")
    return output_md_file


def split_markdown_file(file_path, chunk_size=2500, output_dir='output'):
    # Leer el contenido del archivo Markdown
    borrar_contenido_carpeta(output_dir)
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
    return output_dir

def translate_and_join_markdown_files(chat,input_dir, output_file,language):
    # Obtener la lista de archivos Markdown en el directorio de entrada
    markdown_files = [file for file in os.listdir(input_dir) if file.endswith('.md')]

    # Ordenar los archivos por nombre
    markdown_files.sort()

    # Abrir el archivo de salida en modo escritura
    with open(output_file, 'w') as output:
        # Recorrer los archivos Markdown
        for file in markdown_files:
            file_path = os.path.join(input_dir, file)
            print("translate_review",file_path)
            old_blog_content = load_with_images(file_path)
            translate_review = translate.get_suggestions(chat, old_blog_content,language)

            # Escribir el contenido en el archivo de salida
            output.write(translate_review)

            # Agregar una línea en blanco entre los archivos
            output.write('\n\n')
    borrar_contenido_carpeta(input_dir)
    print(f"Los archivos Markdown en {input_dir} se han unido en el archivo {output_file}.")

def create_markdown(input_file):
    try: 
        if input_file.endswith('.docx'):
            print("Converting .docx to .md")
            output_file = convert_docx_to_markdown(input_file)
            print(f"Conversion complete: Review the {output_file} before continuing.")
        elif input_file.startswith("https"):
            print("Converting .html to .md")
            output_file = convert_html_component_to_markdown(input_file)
            print(f"Conversion complete: Review the {output_file} before continuing.")
        else:
            print(f"ERROR: {input_file} File type not supported: ")
            return
    except Exception as e:
        print("Error converting file:", e)
        raise ValueError("Error converting file:", e)
    return output_file

def translate_markdown(chat,markdown_file,language):
    translate_markdown_file = f"{markdown_file.split(".")[0]}_{language}.md"
    output_dir = split_markdown_file(markdown_file)
    translate_and_join_markdown_files(chat,output_dir, translate_markdown_file,language)
    return translate_markdown_file

def borrar_contenido_carpeta(ruta_carpeta):
    """
    Borra el contenido de una carpeta.
    
    Args:
        ruta_carpeta (str): La ruta de la carpeta cuyo contenido se desea borrar.
    """
    # Verificar si la carpeta existe
    if os.path.exists(ruta_carpeta):
        # Recorrer todos los archivos y subcarpetas dentro de la carpeta
        for archivo in os.listdir(ruta_carpeta):
            # Obtener la ruta completa del archivo o subcarpeta
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            
            # Si es un archivo, eliminarlo
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)
            
            # Si es una subcarpeta, eliminarla junto con su contenido
            elif os.path.isdir(ruta_archivo):
                shutil.rmtree(ruta_archivo)
        
        print(f"Se ha borrado el contenido de la carpeta: {ruta_carpeta}")
    else:
        print(f"La carpeta {ruta_carpeta} no existe.")