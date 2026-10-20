import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RecipeForm, UploadForm
from .utils import get_xml_files, new_filename, save_recipe, read_recipe


def recipe_list(request):
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
                  {'files': files, 'recipes': recipes, 'errors': errors})


def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            save_recipe(form.cleaned_data)
            messages.success(request, 'Рецепт сохранён в XML-файл')
            return redirect('recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'recipes/add_recipe.html', {'form': form})


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
                return redirect('recipe_list')
            except ValueError as e:
                os.remove(path)
                messages.error(request, 'Файл не валиден и был удалён: ' + str(e))
    else:
        form = UploadForm()
    return render(request, 'recipes/upload.html', {'form': form})
