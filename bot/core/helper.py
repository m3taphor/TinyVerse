def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int(seconds % 3600) // 60
    remaining_seconds = int(seconds % 60)
    return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}, " \
           f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
