# foodimage/utils.py
import pandas as pd

def proc_img(file_list):
    """
    Convierte una lista de archivos en un DataFrame con columnas:
    - Filepath: ruta al archivo
    - Label: nombre de la carpeta (la clase)
    """
    data = []
    for f in file_list:
        label = f.parent.name  # la carpeta padre es la etiqueta
        data.append({"Filepath": str(f), "Label": label})

    df = pd.DataFrame(data)
    return df
