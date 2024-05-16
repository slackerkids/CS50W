from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
import markdown2

# For random choice in random page
import random

from . import util


def index(request):
    """
    Shows the index page of the Encyclopedia. With list of entry's
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry_page(request, title):
    """
    Function for markdown content view
    """
    try:
        page = markdown2.markdown(util.get_entry(title))
    except TypeError:
        page = ""

    return render(request, "encyclopedia/entry_page.html", {
        "page": page,
        "title": title,
    })


def search(request):
    """
    Function for search bar
    """
    # Taking information from search bar
    query = request.GET.get("q")
    entries = util.list_entries()

    # if user query matches with entry. User will be redirected to result page
    if query in entries:
        return redirect("entry_page", title = query)
    
    # Take any matching entries using list comprehension
    matching_entries = [entry for entry in entries if query.lower() in entry.lower()]
    return render(request, "encyclopedia/search.html", {
        "matching_entries": matching_entries
    })


def new_page(request):
    """
    Function for adding new entry
    """
    # Handle post request
    if request.method == "POST":
        # Take information from request
        title = request.POST.get("title")
        content = request.POST.get("content")
        entries = util.list_entries()

        # Validate title
        if title in entries:
            return render(request, "encyclopedia/new_page.html", {
                "error": "Entry title already exists."
            })
        else:
            # Save content and redirect to content
            util.save_entry(title, content)
            return redirect("entry_page", title = title)

    return render(request, "encyclopedia/new_page.html")


def edit_page(request, title):
    """
    Function to edit entry content
    """
    if request.method == "POST":
        # Take information from edit page request
        updated_title = request.POST.get("updated_title")
        updated_content = request.POST.get("updated_content")

        # Validate empty fields
        if not updated_title and not updated_content:
            return render(request, "encyclopedia/edit_page.html", {
                "error": "Field must be filled"
            })
        else:
            # Handle not updated title
            if title == updated_title:
                util.save_entry(updated_title, updated_content)
                return redirect("entry_page", title = updated_title)
            else:
                # If title updated too, the delete old entry and create a updated entry
                util.save_entry(updated_title, updated_content)
                filename = f"entries/{title}.md"
                default_storage.delete(filename)
                return redirect("entry_page", title = updated_title)
    
    # Pass the initial value of entry page to form fields.
    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "content": util.get_entry(title)
    })


def random_page(request):
    """
    Function for random page selection
    """
    entries = util.list_entries()
    title = random.choice(entries)
    return redirect("entry_page", title=title)