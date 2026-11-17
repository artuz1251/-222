from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('category', models.CharField(max_length=50, verbose_name='Категория')),
                ('cook_time', models.PositiveIntegerField(verbose_name='Время приготовления (мин)')),
                ('servings', models.PositiveIntegerField(verbose_name='Количество порций')),
                ('ingredients', models.TextField(max_length=1000, verbose_name='Ингредиенты')),
                ('instructions', models.TextField(max_length=3000, verbose_name='Способ приготовления')),
            ],
        ),
    ]
