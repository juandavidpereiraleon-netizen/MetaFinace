def formato_pesos(monto):
    """Formatea un número como pesos colombianos."""
    try:
        return f"${float(monto):,.0f}"
    except:
        return "$0"
def parsear_monto(monto_str):
    """
    Convierte un string como "1.200" o "1200" a número float.
    Elimina puntos y comas.
    """
    if not monto_str:
        return 0.0
    # quitar puntos y reemplazar coma por punto si hay decimales
    monto_str = monto_str.replace(".", "").replace(",", ".")
    try:
        return float(monto_str)
    except ValueError:
        raise ValueError(f"Monto inválido: {monto_str}")