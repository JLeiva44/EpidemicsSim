import logging
import os

def setup_logger(log_file="simulation_log.txt", log_level=logging.DEBUG):
    """
    Configura un logger que escribe en un archivo y en la consola.

    :param log_file: Nombre del archivo donde se guardarán los logs.
    :param log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    :return: Logger configurado.
    """
    # Crear el directorio de logs si no existe
    log_directory = "epidemics_sim/logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Ruta completa del archivo de log
    log_path = os.path.join(log_directory, log_file)

    # Configurar el logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Formato de los mensajes de log
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler para escribir en un archivo
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # Handler para escribir en la consola (opcional)
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(log_format)
    # logger.addHandler(console_handler)

    return logger

