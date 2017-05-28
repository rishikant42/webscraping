from django.shortcuts import render
from django.http import HttpResponse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from webscrapingapp.models import Query
import requests
import ast

def search_form(request):
    return render(request, 'search_form.html')

def search(request):
    q = request.GET['q']

    # Extract searched queries from DB
    queries = Query.objects.values_list('query', flat=True)

    if q in queries:
        query = Query.objects.get(query=q)
        data = query.results
        data = ast.literal_eval(data)
    else:
        data = {}
        appName = []
        href = []

        url = "https://play.google.com/store/search?q=%s" % q
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        links = soup.find_all("a")
        links_text = [link.text for link in links]

        # Extract appName & link address from links_text
        for i in range(len(links_text)):
            if links_text[i] == '  Pre-ordered    ':
                appName.append(links_text[i+2])
                href.append(links[i+2].get("href"))
                
        # Extract appID from links
        appID = [i.split("id=")[1] for i in href]

        # making url address for apps
        websites = ["https://play.google.com"+i for i in href][0:10]

        for i in range(10):
            data[appName[i]] = ["AppID: " + appID[i], "Website: " + websites[i]]

        # save new query in DB
        new_query = Query(query=q,results=data)
        new_query.save()

    # delete duplicate entries from DB
    for row in Query.objects.filter(query=q):
        if Query.objects.filter(query=q).count() > 1:
            row.delete()

    return render(request, 'search_results.html', {'data':data, 'query':q})
