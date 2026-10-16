def make_report(stats):
    total, levels, sources, error_sources, first_time, last_time, top5_errors = stats

    report = {    #распаковываем кортеж
        "total": total,
        "levels": levels,
        "sources": sources,
        "error_sources": error_sources,
        "first_time": first_time.isoformat() if first_time is not None else None,   #проверка если существует время
        "last_time": last_time.isoformat() if last_time is not None else None,
        "top5_errors": top5_errors,
    }

    return report