from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Painting, Artist, Style
from .forms import PaintingForm, ArtistForm, StyleForm


def painting_list(request):
    paintings = Painting.objects.select_related('artist', 'style').all()
    query = request.GET.get('q', '')
    style_id = request.GET.get('style', '')
    technique = request.GET.get('technique', '')

    if query:
        paintings = paintings.filter(
            Q(title__icontains=query) |
            Q(artist__first_name__icontains=query) |
            Q(artist__last_name__icontains=query) |
            Q(museum__icontains=query)
        )
    if style_id:
        paintings = paintings.filter(style_id=style_id)
    if technique:
        paintings = paintings.filter(technique=technique)

    styles = Style.objects.all()
    techniques = Painting.TECHNIQUE_CHOICES
    context = {
        'paintings': paintings,
        'styles': styles,
        'techniques': techniques,
        'query': query,
        'selected_style': style_id,
        'selected_technique': technique,
    }
    return render(request, 'gallery/painting_list.html', context)


def painting_detail(request, pk):
    painting = get_object_or_404(Painting.objects.select_related('artist', 'style'), pk=pk)
    other_paintings = Painting.objects.filter(artist=painting.artist).exclude(pk=pk)[:4]
    context = {
        'painting': painting,
        'other_paintings': other_paintings,
    }
    return render(request, 'gallery/painting_detail.html', context)


def painting_add(request):
    if request.method == 'POST':
        form = PaintingForm(request.POST)
        if form.is_valid():
            painting = form.save()
            messages.success(request, f'Картина «{painting.title}» успешно добавлена!')
            return redirect('painting_detail', pk=painting.pk)
    else:
        form = PaintingForm()
    return render(request, 'gallery/painting_form.html', {'form': form, 'action': 'Добавить картину'})


def painting_edit(request, pk):
    painting = get_object_or_404(Painting, pk=pk)
    if request.method == 'POST':
        form = PaintingForm(request.POST, instance=painting)
        if form.is_valid():
            painting = form.save()
            messages.success(request, f'Картина «{painting.title}» обновлена!')
            return redirect('painting_detail', pk=painting.pk)
    else:
        form = PaintingForm(instance=painting)
    return render(request, 'gallery/painting_form.html', {
        'form': form,
        'painting': painting,
        'action': 'Редактировать картину'
    })


def painting_delete(request, pk):
    painting = get_object_or_404(Painting, pk=pk)
    if request.method == 'POST':
        title = painting.title
        painting.delete()
        messages.success(request, f'Картина «{title}» удалена.')
        return redirect('painting_list')
    return render(request, 'gallery/painting_confirm_delete.html', {'painting': painting})



def artist_list(request):
    artists = Artist.objects.select_related('style').all()
    return render(request, 'gallery/artist_list.html', {'artists': artists})


def artist_detail(request, pk):
    artist = get_object_or_404(Artist.objects.select_related('style'), pk=pk)
    paintings = artist.paintings.select_related('style').all()
    return render(request, 'gallery/artist_detail.html', {'artist': artist, 'paintings': paintings})


def artist_add(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            artist = form.save()
            messages.success(request, f'Художник {artist.full_name} добавлен!')
            return redirect('artist_detail', pk=artist.pk)
    else:
        form = ArtistForm()
    return render(request, 'gallery/artist_form.html', {'form': form, 'action': 'Добавить художника'})


def artist_edit(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    if request.method == 'POST':
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            artist = form.save()
            messages.success(request, f'Данные художника {artist.full_name} обновлены!')
            return redirect('artist_detail', pk=artist.pk)
    else:
        form = ArtistForm(instance=artist)
    return render(request, 'gallery/artist_form.html', {
        'form': form, 'artist': artist, 'action': 'Редактировать художника'
    })



def style_list(request):
    styles = Style.objects.all()
    return render(request, 'gallery/style_list.html', {'styles': styles})


def style_add(request):
    if request.method == 'POST':
        form = StyleForm(request.POST)
        if form.is_valid():
            style = form.save()
            messages.success(request, f'Стиль «{style.name}» добавлен!')
            return redirect('style_list')
    else:
        form = StyleForm()
    return render(request, 'gallery/style_form.html', {'form': form, 'action': 'Добавить стиль'})


def style_edit(request, pk):
    style = get_object_or_404(Style, pk=pk)
    if request.method == 'POST':
        form = StyleForm(request.POST, instance=style)
        if form.is_valid():
            style = form.save()
            messages.success(request, f'Стиль «{style.name}» обновлён!')
            return redirect('style_list')
    else:
        form = StyleForm(instance=style)
    return render(request, 'gallery/style_form.html', {
        'form': form, 'style': style, 'action': 'Редактировать стиль'
    })
