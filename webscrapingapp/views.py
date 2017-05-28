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

        for i in range(len(links_text)):
            if links_text[i] == '  Pre-ordered    ':
                appName.append(links_text[i+2])
                href.append(links[i+2].get("href"))
                
        appID = [i.split("id=")[1] for i in href]

        websites = ["https://play.google.com"+i for i in href][0:10]

        for i in range(10):
            data[appName[i]] = ["AppID: " + appID[i], "Website: " + websites[i]]

        new_query = Query(query=q,results=data)
        new_query.save()

    return render(request, 'search_results.html', {'data':data, 'query':q})
