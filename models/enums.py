import enum


class RolEnum(str, enum.Enum):
    ADMIN = "admin"
    PROFESOR = "profesor"
    CLIENTE = "cliente"


class MetodoPagoEnum(str, enum.Enum):
    TARJETA = "tarjeta"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    MERCADO_PAGO = "mercado_pago"


class GrupoMuscularEnum(str, enum.Enum):
    PECHO = "pecho"
    ESPALDA = "espalda"
    PIERNA = "pierna"
    HOMBRO = "hombro"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    ABDOMEN = "abdomen"
    GLUTEO = "gluteo"
    FULL_BODY = "full_body"
