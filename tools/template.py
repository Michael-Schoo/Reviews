from flask import render_template
from jinja2 import Template
import typing as t
from tools.jwt_token import get_auth_user



# extends the render_template function to include the current user
def render_user_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> str:
    """Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """
    current_user = get_auth_user() or None
    # if current_user: current_user = current_user
    # else: current_user = None

    return render_template(template_name_or_list, current_user=current_user, **context)