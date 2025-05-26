from borb.pdf import Document, Page, Paragraph, TableCell
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal
from borb.pdf.pdf import PDF
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from pathlib import Path
from datetime import datetime
from foodgram.settings import STATIC_ROOT

FONT = TrueTypeFont.true_type_font_from_file(Path(STATIC_ROOT / "fonts/DejaVuSans.ttf"))


class ShoppingCartDocument:
    def __init__(self, recipes):
        self.recipes = recipes
        self.document = Document()
        self.page = Page()
        self.document.add_page(self.page)
        self.layout = SingleColumnLayout(self.page)
        self.create_document()

    def _generate_ingredients_list(self):
        ingredients = {}
        for recipe in self.recipes:
            for ingredient in recipe["ingredients"]:
                name = ingredient["name"].lower().strip()
                amount = ingredient["amount"]
                unit = ingredient["measurement_unit"]

                if name in ingredients:
                    existing = ingredients[name]
                    if existing["unit"] == unit:
                        existing["amount"] += amount
                    else:
                        pass
                else:
                    ingredients[name] = {
                        "amount": amount, 
                        "unit": unit,
                        "recipes": [recipe["name"]]
                    }
                if recipe["name"] not in ingredients[name].get("recipes", []):
                    ingredients[name].setdefault("recipes", []).append(recipe["name"])

        return ingredients

    def _add_metadata(self):
        """Adds metadata to the PDF document."""
        self.document.info.author = "Foodgram"
        self.document.info.title = "Список покупок"
        self.document.info.subject = "Список ингредиентов для рецептов"
        self.document.info.creation_date = datetime.now()

    def create_document(self):
        self._add_metadata()
        self.layout.add(Paragraph("Список покупок", font=FONT, font_size=Decimal(20)))
        self.layout.add(Paragraph(f"Дата составления: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 
                              font=FONT, font_size=Decimal(10)))
        self.layout.add(Paragraph(" "))

        self.layout.add(Paragraph("Рецепты:", font=FONT, font_size=Decimal(14)))
        for recipe in self.recipes:
            recipe_name = recipe["name"]
            author = f"{recipe['author']['first_name']} {recipe['author']['last_name']}"
            self.layout.add(
                Paragraph(f"- {recipe_name} (автор: {author})", font=FONT)
            )

        self.layout.add(Paragraph(" "))

        ingredients = self._generate_ingredients_list()

        table = FixedColumnWidthTable(
            number_of_columns=4,
            number_of_rows=len(ingredients) + 1
        )

        # Add table headers with styling and borders
        table.add(TableCell(Paragraph("#", font=FONT, font_weight=Decimal(700)), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))
        table.add(TableCell(Paragraph("Ингредиент", font=FONT, font_weight=Decimal(700)), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))
        table.add(TableCell(Paragraph("Количество", font=FONT, font_weight=Decimal(700)), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))
        table.add(TableCell(Paragraph("Ед. измерения", font=FONT, font_weight=Decimal(700)), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))

        # Add ingredient rows with borders
        for i, (name, data) in enumerate(sorted(ingredients.items()), 1):
            table.add(TableCell(Paragraph(str(i), font=FONT), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))
            table.add(TableCell(Paragraph(name.capitalize(), font=FONT), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))
            table.add(TableCell(Paragraph(str(data["amount"]), font=FONT), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))
            table.add(TableCell(Paragraph(data["unit"], font=FONT), border_bottom=Decimal(1), border_top=Decimal(1), border_left=Decimal(1), border_right=Decimal(1)))

        self.layout.add(table)

        return self.document

    def save(self, buffer):
        PDF.dumps(buffer, self.document)