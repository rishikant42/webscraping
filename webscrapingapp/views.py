from django.shortcuts import render
from django.http import HttpResponse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from webscrapingapp.models import Query, Description
import requests
import ast

def search_form(request):
    return render(request, 'search_form.html')

def app_name_href_scrap(url):
    appName = []
    href = []

    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    links = soup.find_all("a", {"class":"title"})
    links = links[0:10]

    for link in links:
        href.append(link.attrs.get("href"))
        appName.append(link.attrs.get("title"))

    return(appName, href)

def icon_url_scrap(soup):
    icon_data =  soup.find_all("img", {"class":"cover-image", "alt":"Cover art"})
    icon_data = icon_data[0]
    return("https:" + icon_data.get("src"))

def email_scrap(soup):
    mail_link = soup.find_all("a", {"class":"dev-link"}) 

    if not mail_link:
        return ''
    else:
        for link in mail_link:
            if "Email" in link.text:
                return(link.text)

def email_icon_scrap(urls):
    emails = []
    icon_urls = []

    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        emails.append(email_scrap(soup))
        icon_urls.append(icon_url_scrap(soup))

    return(emails, icon_urls)

def search(request):
    q = request.GET['q']
    queries = Query.objects.values_list('query', flat=True)

    if q in queries:
        query = Query.objects.get(query=q)
        data = ast.literal_eval(query.results)
        weburl = ast.literal_eval(query.weburl)
    else:
        data = {}

        url = "https://play.google.com/store/search?q=%s" % q

        appName, href = app_name_href_scrap(url)

        appID = [i.split("id=")[1] for i in href]

        websites = ["https://play.google.com"+i for i in href][0:10]

        emails, icon_urls = email_icon_scrap(websites)


        for i in range(10):
            data[appName[i]] = ["AppID: " + appID[i], "Website: " + websites[i], "Icon url: " + icon_urls[i], emails[i]]


        weburl = {}
        for i in range(10):
            weburl[appName[i]] = websites[i]

        new_query = Query(query=q,results=data,weburl=weburl)
        new_query.save()

    for row in Query.objects.filter(query=q):
        if Query.objects.filter(query=q).count() > 1:
            row.delete()

    return render(request, 'search_results.html', {'data':data, 'query':q, 'websites': weburl})

def description(request):
    url = request.GET['url']

    urls = Description.objects.values_list('url', flat=True)

    if url in urls:
        query = Description.objects.get(url=url)
        data = query.description

    else:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        data = soup.find_all("div", {"class":"show-more-content text-body"})

        new_url_des = Description(url=url, description=data)
        new_url_des.save()

    for row in Description.objects.filter(url=url):
        if Description.objects.filter(url=url).count() > 1:
            row.delete()

    return HttpResponse(data)
