def analyze(events):
    total = 0

    levels = {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }

    sourses = {}  # создали пустой словарь для новых значений

    error_sourses = {}  # создали словарь только для ошибок

    first_time = None
    last_time = None

    for event in events:  # идем по одному событию за раз
        total += 1
        levels[event.level] += 1
        sourses[event.sourse] = sourses.get(event.sourse, 0) + 1

        if event.level in ("ERROR", "CRITICAL"):
            error_sourses[event.sourse] = error_sourses.get(event.sourse, 0) + 1

        if first_time is None or event.time < first_time:
            first_time = event.time

        if last_time is None or event.time > last_time:
            last_time = event.time

    top5_errors = sorted(error_sourses.items(), key=lambda item: (-item[1], item[0]))[:5]  # сортируем ошибки сначала по значениям, потом в алфовитном порядке

    return total, levels, sourses, error_sourses, first_time, last_time, top5_errors
