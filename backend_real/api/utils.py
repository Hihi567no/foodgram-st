"""Utility functions for API views."""
from django.http import HttpResponse
from io import StringIO


def format_shopping_list(ingredients):
    """Format ingredients list as shopping list text."""
    if not ingredients:
        return "Shopping List\n" + "=" * 50 + "\n\nYour shopping cart is empty.\n"

    shopping_list = StringIO()
    shopping_list.write("Shopping List\n")
    shopping_list.write("=" * 50 + "\n\n")

    for ingredient in ingredients:
        shopping_list.write(
            f"• {ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}) — "
            f"{ingredient['total_amount']}\n"
        )

    shopping_list.write(f"\n\nTotal items: {len(ingredients)}")
    return shopping_list.getvalue()


def create_shopping_list_response(ingredients):
    """Create HttpResponse for shopping list download."""
    shopping_list_text = format_shopping_list(ingredients)
    response = HttpResponse(
        shopping_list_text,
        content_type='text/plain; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
    return response
