import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import RecipeForm, RecipeAddForm, UploadForm
from .models import Recipe
from .utils import get_xml_files, new_filename, save_recipe, read_recipe


def is_duplicate(data, exclude_pk=None):
    """Дубликат - рецепт с таким же названием и категорией (без учёта регистра)."""
    # Сравниваем в Python, т.к. SQLite не умеет сравнивать кириллицу без учёта регистра
    name = data['name'].lower()
    category = data['category'].lower()
    for r in Recipe.objects.exclude(pk=exclude_pk):
        if r.name.lower() == name and r.category.lower() == category:
            return True
    return False


def recipe_list(request):
    """Список рецептов. Источник выбирается параметром ?source=db или ?source=xml."""
    source = request.GET.get('source', 'db')
    if source == 'db':
        return render(request, 'recipes/recipe_list.html',
                      {'source': 'db', 'recipes': Recipe.objects.order_by('name')})

    files = get_xml_files()
    recipes = []
    errors = []
    for name in files:
        path = os.path.join(settings.RECIPES_DIR, name)
        try:
            recipes.append(read_recipe(path))
        except ValueError as e:
            errors.append(name + ': ' + str(e))
    return render(request, 'recipes/recipe_list.html',
                  {'source': 'xml', 'files': files, 'recipes': recipes, 'errors': errors})


def add_recipe(request):
    if request.method == 'POST':
        form = RecipeAddForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            storage = data.pop('storage')
            if storage == 'xml':
                save_recipe(data)
                messages.success(request, 'Рецепт сохранён в XML-файл')
                return redirect('/?source=xml')
            if is_duplicate(data):
                messages.error(request, 'Такой рецепт уже есть в базе данных, запись не добавлена')
            else:
                Recipe.objects.create(**data)
                messages.success(request, 'Рецепт сохранён в базу данных')
                return redirect('/?source=db')
    else:
        form = RecipeAddForm()
    return render(request, 'recipes/add_recipe.html', {'form': form})


def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST)   # те же проверки, что и при добавлении
        if form.is_valid():
            data = form.cleaned_data
            if is_duplicate(data, exclude_pk=pk):
                messages.error(request, 'Рецепт с таким названием и категорией уже существует')
            else:
                for field, value in data.items():
                    setattr(recipe, field, value)
                recipe.save()
                messages.success(request, 'Рецепт обновлён')
                return redirect('/?source=db')
    else:
        form = RecipeForm(initial={
            'name': recipe.name, 'category': recipe.category, 'cook_time': recipe.cook_time,
            'servings': recipe.servings, 'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
        })
    return render(request, 'recipes/edit_recipe.html', {'form': form, 'recipe': recipe})


@require_POST
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.delete()
    messages.success(request, 'Рецепт удалён')
    return redirect('/?source=db')


def search_recipes(request):
    """AJAX-поиск по текстовым полям. Возвращает кусок HTML со строками таблицы."""
    q = request.GET.get('q', '').strip().lower()
    recipes = []
    for r in Recipe.objects.order_by('name'):
        text = ' '.join([r.name, r.category, r.ingredients, r.instructions]).lower()
        if q in text:
            recipes.append(r)
    return render(request, 'recipes/_db_rows.html', {'recipes': recipes})


def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['file']

            os.makedirs(settings.RECIPES_DIR, exist_ok=True)
            path = os.path.join(settings.RECIPES_DIR, new_filename())

            # Сохраняем файл под своим именем
            with open(path, 'wb') as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)

            # Проверяем содержимое, если файл плохой - удаляем
            try:
                read_recipe(path)
                messages.success(request, 'Файл загружен и прошёл проверку')
                return redirect('/?source=xml')
            except ValueError as e:
                os.remove(path)
                messages.error(request, 'Файл не валиден и был удалён: ' + str(e))
    else:
        form = UploadForm()
    return render(request, 'recipes/upload.html', {'form': form})
