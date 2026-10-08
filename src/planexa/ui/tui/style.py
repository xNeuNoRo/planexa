from prompt_toolkit.styles import Style

APP_STYLE = Style.from_dict(
    {
        "logo": "#55d6ff bold",
        "title": "#ffffff bold",
        "subtitle": "#8b949e",
        "separator": "#30363d",
        "item": "#f0f6fc",
        "item.selected": "bg:#0aa2c0 #071013 bold",
        "description": "#55d6ff",
        "hint": "#8b949e",
        "pager": "#8b949e",
        "success": "#3fb950 bold",
        "warning": "#d29922 bold",
        "error": "#f85149 bold",
    }
)
