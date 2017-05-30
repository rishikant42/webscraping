from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
from webscrapingapp.models import Query, Description
import requests
import ast
import threading

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

# store list of tuples
content = []

def fetch_url(i, url):
    global content
    r = requests.get(url)
    content.append((i, r.content))

def email_icon_scrap(urls):
    emails = []
    icon_urls = []

    threads = [threading.Thread(target=fetch_url, args=(i, urls[i])) for i in range(len(urls))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    global content

    content.sort()

    # fetch actual url contents from list of tuples
    contents = []
    for i in content:
        contents.append(i[1])

    for c in contents:
        soup = BeautifulSoup(c, "html.parser")
        emails.append(email_scrap(soup))
        icon_urls.append(icon_url_scrap(soup))

    # set global content to empty again
    content = []

    return(emails, icon_urls)


def search(request):
    q = request.GET['q']

    # check queries in db
    queries = Query.objects.values_list('query', flat=True)

    if q in queries:
        query = Query.objects.get(query=q)
        data = ast.literal_eval(query.results)
        weburl = ast.literal_eval(query.weburl)
    else:
        data = {}
        url = "https://play.google.com/store/search?q=%s" % q

        # scrap app name & href
        appName, href = app_name_href_scrap(url)

        # extract appID from href
        appID = [i.split("id=")[1] for i in href]

        # making websites url from href
        websites = ["https://play.google.com"+i for i in href][0:10]

        # scrap emailID & icon urls
        emails, icon_urls = email_icon_scrap(websites)

        for i in range(10):
            data[appName[i]] = ["AppID: " + appID[i], "Website: " + websites[i], "Icon url: " + icon_urls[i], emails[i]]

        weburl = {}
        for i in range(10):
            weburl[appName[i]] = websites[i]

        # save new query in db
        new_query = Query(query=q,results=data,weburl=weburl)
        new_query.save()

    # check & delete duplicate query from db
    for row in Query.objects.filter(query=q):
        if Query.objects.filter(query=q).count() > 1:
            row.delete()

    return render(request, 'search_results.html', {'data':data, 'query':q, 'websites': weburl})

def search_form(request):
    return render(request, 'search_form.html')

def description(request):
    url = request.GET['url']

    # extract urls from db
    urls = Description.objects.values_list('url', flat=True)

    if url in urls:
        query = Description.objects.get(url=url)
        data = query.description
    else:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        data = soup.find_all("div", {"class":"show-more-content text-body"})

        # save new url description in db
        new_url_des = Description(url=url, description=data)
        new_url_des.save()

    # check & delete duplicate entry from db
    for row in Description.objects.filter(url=url):
        if Description.objects.filter(url=url).count() > 1:
            row.delete()

    return HttpResponse(data)
