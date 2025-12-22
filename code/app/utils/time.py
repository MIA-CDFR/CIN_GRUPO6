

def time_to_seconds(time_str: str) -> int:
    """Converte uma string de tempo GTFS (HH:MM:SS) em segundos desde a meia-noite."""
    try:
        parts = list(map(int, time_str.split(':')))
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except:
        return 0
    
def format_time(seconds):
    """Formata segundos totais em HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{int(h)}h {int(m)}m {int(s)}s"
