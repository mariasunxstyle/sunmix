# utils.py

def format_duration(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return f"{hours} ч {mins} мин"
    elif hours:
        return f"{hours} ч"
    else:
        return f"{mins} мин"
