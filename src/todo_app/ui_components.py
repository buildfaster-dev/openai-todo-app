"""UI Components for OpenAI Apps SDK integration"""

from typing import Optional


def create_todo_list_component(todos: list, title: str = "Your Todos") -> dict:
    """
    Create a UI component displaying the todo list.

    This returns an OpenAI Apps SDK UI component that can be rendered in ChatGPT.
    """
    # Generate HTML for the todo list widget
    todos_html = ""
    for todo in todos:
        status_icon = "✅" if todo["status"] == "completed" else "⏳" if todo["status"] == "in_progress" else "📝"
        priority_color = "#dc2626" if todo["priority"] == "high" else "#f59e0b" if todo["priority"] == "medium" else "#3b82f6"

        todos_html += f"""
        <div style="padding: 12px; margin: 8px 0; background: #f9fafb; border-left: 4px solid {priority_color}; border-radius: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 20px;">{status_icon}</span>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #1f2937;">{todo['title']}</div>
                    {f'<div style="font-size: 14px; color: #6b7280; margin-top: 4px;">{todo["description"]}</div>' if todo.get("description") else ''}
                    <div style="font-size: 12px; color: #9ca3af; margin-top: 4px;">
                        Priority: {todo['priority'].upper()} • Status: {todo['status'].replace('_', ' ').title()}
                    </div>
                </div>
            </div>
        </div>
        """

    if not todos_html:
        todos_html = '<div style="text-align: center; padding: 40px; color: #9ca3af;">No todos yet! Create one to get started.</div>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 16px;
                background: white;
            }}
            .header {{
                font-size: 20px;
                font-weight: 700;
                color: #111827;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 2px solid #e5e7eb;
            }}
        </style>
    </head>
    <body>
        <div class="header">{title}</div>
        <div class="todos">
            {todos_html}
        </div>
    </body>
    </html>
    """

    return {
        "type": "component",
        "component": {
            "type": "html",
            "html": html,
            "height": 400,
            "width": 600
        }
    }


def create_stats_component(stats: dict) -> dict:
    """
    Create a UI component displaying todo statistics.

    This returns an OpenAI Apps SDK UI component for displaying stats.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: white;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 16px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 24px;
                border-radius: 12px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 48px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            .stat-label {{
                font-size: 14px;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        </style>
    </head>
    <body>
        <div style="font-size: 24px; font-weight: 700; margin-bottom: 20px; color: #111827;">📊 Todo Statistics</div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats.get('total', 0)}</div>
                <div class="stat-label">Total Todos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('pending', 0)}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('in_progress', 0)}</div>
                <div class="stat-label">In Progress</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('completed', 0)}</div>
                <div class="stat-label">Completed</div>
            </div>
        </div>
    </body>
    </html>
    """

    return {
        "type": "component",
        "component": {
            "type": "html",
            "html": html,
            "height": 300,
            "width": 500
        }
    }
