from django.shortcuts import render, redirect, reverse
from . import util
from markdown2 import Markdown
from django.http import HttpResponseRedirect
from django import forms
import random


entries = util.list_entries()

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    content = forms.CharField(label="Markdown content", widget=forms.Textarea(
        attrs={'class': 'form-control'}))


class EditPageForm(forms.Form):
    content = forms.CharField(label="Markdown content", widget=forms.Textarea(
        attrs={'class': 'form-control'}))
    

def getDetails(title):
    try:
        details = Markdown().convert(util.get_entry(title))
    except TypeError:
        details = None
    return details

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    details = getDetails(title)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "details": details
    })

def search(request):
    searchString = request.GET['q']
    details = getDetails(searchString)

    if details is None:
        searchResults = []
        for entry in entries:
            if searchString.upper() in entry.upper():
                searchResults.append(entry)
        return render(request, "encyclopedia/results.html", {
            "results": searchResults, "searchString": searchString
        })
    
    else:
        return redirect("encyclopedia:entry", title=searchString)

def create(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        title = form.data['title']
        if form.is_valid():
            if util.get_entry(title) is None:
                title = form.cleaned_data['title']
                content = form.cleaned_data['content']
                util.save_entry(title, content)
                return redirect("encyclopedia:entry", title=title) 
            else:
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "error": f"Error: Page with title {title} does already exist!"
                })
        else:
            return render(request, "encyclopedia/create.html", {
                "form": form
            })

    return render(request, "encyclopedia/create.html", {
        "form": NewPageForm()
    })

def edit(request, title):
    content = util.get_entry(title)
    if request.method == "POST":
        form = EditPageForm(request.POST)
        title = title
        if form.is_valid():
            content = form.cleaned_data['content']
            util.save_entry(title, content)
            return redirect("encyclopedia:entry", title=title)
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title
            })
        
    return render(request, "encyclopedia/edit.html", {
        "form": EditPageForm(initial={'content': content}),
        "title": title
    })

def randomEntry(request):
    randomEntry = random.choice(entries)
    return redirect("encyclopedia:entry", title=randomEntry)
