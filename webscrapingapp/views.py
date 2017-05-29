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
        data = ast.literal_eval(query.results)
        weburl = ast.literal_eval(query.weburl)
    else:
        data = {}
        appName = []
        href = []

        url = "https://play.google.com/store/search?q=%s" % q
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        links = soup.find_all("a", {"class":"title"})
        #links_text = [link.text for link in links]

        links = links[0:10]

        for link in links:
            href.append(link.attrs.get("href"))
            appName.append(link.attrs.get("title"))

        appID = [i.split("id=")[1] for i in href]

        websites = ["https://play.google.com"+i for i in href][0:10]

        mailto = []
        for url in websites:
            p = requests.get(url)
            sup = BeautifulSoup(p.content)
            mail_link = sup.find_all("a", {"class":"dev-link"}) 

            if not mail_link:
                mailto.append('')
            else:
                for d in mail_link:
                    if "mailto" in d.attrs.get("href"):
                        mailto.append(d.attrs.get("href"))
        emails = []
        for i in mailto:
            if i != '':
                emails.append(i.replace("mailto:", "Email: "))
            else:
                emails.append('')

        for i in range(10):
            data[appName[i]] = ["AppID: " + appID[i], "Website: " + websites[i], emails[i]]


        weburl = {}
        for i in range(10):
            weburl[appName[i]] = websites[i]

        new_query = Query(query=q,results=data,weburl=weburl)
        new_query.save()

    return render(request, 'search_results.html', {'data':data, 'query':q, 'websites': weburl})

def description(request):
    url = request.GET['url']
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    data = soup.find_all("div", {"class":"show-more-content text-body"})
    return HttpResponse(data)
