import os
import uuid
from xml.etree import ElementTree as ET
from defusedxml import ElementTree as SafeET   # безопасный разбор XML
from django.conf import settings
from .forms import RecipeForm

FIELDS = ['name', 'category', 'cook_time', 'servings', 'ingredients', 'instructions']


def get_xml_files():
    """Список XML-файлов в папке. Если папки нет - пустой список."""
    if not os.path.isdir(settings.RECIPES_DIR):
        return []
    files = []
    for name in os.listdir(settings.RECIPES_DIR):
        if name.endswith('.xml'):
            files.append(name)
    return sorted(files)


def new_filename():
    # Имя файла генерируем сами, имя от пользователя не используем
    return uuid.uuid4().hex + '.xml'


def save_recipe(data):
    """Сохраняет данные рецепта в новый XML-файл."""
    os.makedirs(settings.RECIPES_DIR, exist_ok=True)

    root = ET.Element('recipe')
    for field in FIELDS:
        ET.SubElement(root, field).text = str(data[field])

    filename = new_filename()
    path = os.path.join(settings.RECIPES_DIR, filename)
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
    return filename


def read_recipe(path):
    """Читает и проверяет XML-файл. Если файл неверный - ValueError."""
    try:
        root = SafeET.parse(path).getroot()
    except Exception:
        raise ValueError('файл не является корректным XML')

    if root.tag != 'recipe':
        raise ValueError('корневой элемент должен быть <recipe>')

    data = {}
    for field in FIELDS:
        element = root.find(field)
        if element is None:
            raise ValueError('нет элемента <' + field + '>')
        data[field] = (element.text or '').strip()

    # Проверяем значения теми же правилами, что и у формы
    form = RecipeForm(data)
    if not form.is_valid():
        raise ValueError('неверные данные в полях: ' + ', '.join(form.errors.keys()))
    return form.cleaned_data
