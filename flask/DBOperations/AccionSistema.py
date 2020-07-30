from enum import Enum

class AccionSistema(Enum):

    # Acciones para el sistema interno
    SCRAPPING = 1
    DATA_CLEANING = 2
    MODEL_CONSTRUCTION = 3
    MODEL_SELECTION = 4
    MV_REFRESH = 5


    # Acciones para aplicativo web
    PRICE_PREDICTION = 101
    FEATURE_COMPARATION = 102
    CONFIGURATION = 103