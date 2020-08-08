from enum import Enum

class AccionSistema(Enum):

    # Errores
    ERROR = 1
    WARNING = 2

    # Acciones para el sistema interno
    SCRAPPING = 3
    DATA_CLEANING = 4
    MODEL_CONSTRUCTION = 5
    MODEL_SELECTION = 6
    MV_REFRESH = 7


    # Acciones para aplicativo web
    PRICE_PREDICTION = 101
    FEATURE_COMPARATION = 102
    CONFIGURATION = 103