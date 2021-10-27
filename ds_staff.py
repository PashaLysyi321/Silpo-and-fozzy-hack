
# !pip install html2text
# !pip install google_trans_new
import time
from fastapi import HTTPException

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import html2text
from google_trans_new import google_translator
from typing import List
import numpy as np
# import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen


import nltk
nltk.download('vader_lexicon')


def get_component(comp_name):
    url = f'https://dobavkam.net/additives/{comp_name.lower()}'
    while True:
        try:
            response = requests.get(url)
            break
        except:
            continue
    soup = BeautifulSoup(response.text, 'lxml')
    for i in range(1,7):
        try:
            a = soup.find('a', class_=f'addprop-item addprop-item--danger-{i}').text
            try:
                info = soup.find('div', class_='field field--block field--additive-info')
                info = info.find('p').text.replace('\xa0',' ')
                if i>=2:
                    return 0, info
                else:
                    return 1, info
                return i, info
            except:
                return i, -1
        except:
            pass
    return -1


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>|&ndash; ')
    return re.sub(clean, '', text)


def remove_html_tags2(text):
    h = html2text.HTML2Text()
    h.ignore_links = True
    text1 = h.handle(text)
    text2 = remove_html_tags(text1).replace('\n',' ').replace("/",' ').replace("*",' ').replace("[]",' ').replace('_',' ')
    text2 = re.sub(r'\([^)]*\)', '', text2).replace('\\',' ').replace('#',' ').replace('>',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
    if text1 != 'None':
        return text2
    else:
        return text


def parsing_wiki(query):

    URL = "https://ru.wikipedia.org/wiki/"+str(query)
    page = requests.get(URL)

    text = str(page.text).split('<p>')[1]
    text = remove_html_tags2(remove_html_tags(text))
    return text


def get_rating(text):
    neg = []
    pos = []
    for sentence in text.split('.'):
        sid = SentimentIntensityAnalyzer()
        ss = sid.polarity_scores(sentence)
        data14 = 'neg:' + str(ss['neg']) + '  pos:' + str(ss['pos'])
        neg.append(float(ss['neg']))
        pos.append(float(ss['pos']))

    try:
        pos = sum(pos)
        neg = sum(neg)
        summ = pos+neg
        pos /=summ
        neg /=summ
        if pos>0.7:
            res = 1
        else:
            res = 0
        return res
    except:
        return 1


def get_text_from_wiki(query):
    translator = google_translator()
    #return translator.translate(parsing_wiki(query), lang_src='ru',lang_tgt='en')
    return parsing_wiki(query)


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>|&ndash; ')
    return re.sub(clean, '', text)


def replase_to_bool(val):
    if val == 'НЕТ':
        ans = False
    elif val == 'ДА':
        ans = True
    return ans


def scraping_product(id):
    qr_id = id

    qr_url = f'https://listex.info/search/?q={qr_id}&type=goods'
    # qr_html_text=requests.get(qr_url, headers = {'User-agent': 'your bot 0.1'}).text
    qr_html_text = requests.get(qr_url)
    status = qr_html_text.status_code
    qr_soup = BeautifulSoup(qr_html_text.text, 'lxml')
    prod_link = ''
    for link in qr_soup.find_all('a', class_='link-gray'):
        href = re.match(r'.product.', link.get('href'))
        if href:
            prod_link = 'https://listex.info/' + link.get('href')

    if not prod_link:
        raise HTTPException(status_code=404)

    prod_html_text = requests.get(prod_link).text
    prod_soup = BeautifulSoup(prod_html_text, 'lxml')

    try:
        list_text = prod_soup.find('p', class_="product-specifications-title").get_text().split()[1:]
        prod_name = ' '.join(list_text)
    except:
        prod_name = 0

    try:
        log_params = str(prod_soup).split('Материал транспортной тары')[1].split('<div')[0]
        package = \
        log_params.split('Материал транспортной тары')[1].replace('</th>', '').replace('\n', '').replace('<tr>',
                                                                                                         '').replace(
            '<th>', '').replace('<td>', '').replace('</td>', '').replace('</tr>', '').split('Белки, г/100г')[0].replace(
            ' ', '').replace('\t', '').replace('</table>', '')
    except:
        package = None

    try:
        log_params2 = str(prod_soup).split('Вес нетто, пустой box, кг')[1].split('<div')[0]
        mass = log_params2.split('Вес нетто, пустой box, кг')[1].replace('</th>', '').replace('\n', '').replace('<tr>',
                                                                                                                '').replace(
            '<th>', '').replace('<td>', '').replace('</td>', '').replace('</tr>', '').split('Белки, г/100г')[0].replace(
            ' ', '').replace('\t', '').replace('</table>', '')
    except:
        mass = 0

    try:
        nutritional = str(prod_soup).split('Питательные характеристики')[1].split('<div')[0]
        clean_text = remove_html_tags(remove_html_tags(nutritional)).replace('\n', '').replace('\t', '')
        clean_text = clean_text.split('  ')

        ans = []
        for i in clean_text:
            if len(i) != 0:
                ans.append(i)
                pass

        if 'Жиры, г/100г' in ans:
            fats = ans[ans.index('Жиры, г/100г') + 1].replace('&lt;', '')
        elif 'Жиры, г/100мл' in ans:
            fats = ans[ans.index('Жиры, г/100мл') + 1].replace('&lt;', '')
        else:
            fats = '0'

        if 'Углеводы, г/100г' in ans:
            carbohydrates = ans[ans.index('Углеводы, г/100г') + 1].replace('&lt;', '')
        elif 'Углеводы, г/100мл' in ans:
            carbohydrates = ans[ans.index('Углеводы, г/100мл') + 1].replace('&lt;', '')
        else:
            carbohydrates = '0'

        if 'Белки, г/100г' in ans:
            proteins = ans[ans.index('Белки, г/100г') + 1].replace('&lt;', '')
        elif 'Белки, г/100мл' in ans:
            proteins = ans[ans.index('Белки, г/100мл') + 1].replace('&lt;', '')
        else:
            proteins = '0'

        if 'Калорийность, ккал/100г' in ans:
            calories = ans[ans.index('Калорийность, ккал/100г') + 1].replace('&lt;', '')
        elif 'Калорийность, ккал/100мл' in ans:
            calories = ans[ans.index('Калорийность, ккал/100мл') + 1].replace('&lt;', '')
        else:
            calories = '0'

    except Exception as e:
        print(e)
        fats = 0
        proteins = 0
        calories = 0
        carbohydrates = 0
        kdg = 0

    try:
        main = str(prod_soup).split('Основные')[1].split('<div')[0]
        clean_text = remove_html_tags(main).replace('\n', '').replace('\t', '')
        clean_text = clean_text.split('  ')

        ans = []
        for i in clean_text:
            if len(i) != 0:
                ans.append(i)
                pass
        if 'Органический продукт' in ans:
            organic = ans[ans.index('Органический продукт') + 1] == 'ДА'
        else:
            organic = False
        if 'ГМО' in ans:
            gmo = ans[ans.index('ГМО') + 1] == 'ДА'
        else:
            gmo = False
        if 'Подходит вегетарианцам' in ans:
            vegetarian = ans[ans.index('Подходит вегетарианцам') + 1] == 'ДА'
        else:
            vegetarian = False
        if 'Подходит веганам' in ans:
            vegan = ans[ans.index('Подходит веганам') + 1] == 'ДА'
        else:
            vegan = False

    except Exception as e:
        print(e)
        gmo = 0
        organic = 0
        vegetarian = 0
        vegan = 0

    try:
        description = str(prod_soup).split('Состав товара')[1].split('<div')[0]
        components = remove_html_tags(description).replace('\n', '').replace('\t', '').split('Состав (рус.)')[1].split(
            'Состав (укр.)')[0].replace('  ', '')
    except Exception as e:
        print(e)
        components = ''

    try:
        package1 = str(prod_soup).replace('\n', '').replace('\t', '').split('Упаковка    ')[1].split('<div')[0]
        ans1 = []
        for i in remove_html_tags(package1).replace('\n', '').replace('\t', '').split('   '):
            if len(i) != 0:
                ans1.append(i)
    except:
        ans1 = [0, 0, 0, 0]

    images = prod_soup.findAll('img')
    img = ''
    for image in images:
        if re.findall(r'https://', image['src']):
            img = image['src']
            break

    dict_ = {
        'barcode': qr_id,
        'name': prod_name,
        'proteins': proteins,
        'fats': fats,
        'carbohydrates': carbohydrates,
        'calories': calories,
        'mass': float(mass),
        'package': package if package else ans1[1] + ', ' + ans1[3],
        'is_gmo': gmo,
        'is_organic': organic,
        'is_vegetarian': vegetarian,
        'is_vegan': vegan,
        'components': components,
        'image_url': img
    }
    return dict_


def main(query):
    try:
        rating = get_component(query)
        if rating == -1:
            rating = get_rating(get_text_from_wiki(query))
            # text = translator.translate(get_text_from_wiki(query), lang_src='en',lang_tgt='ru')
            if query:
                text = get_text_from_wiki(query)
                text = re.sub(r'\[[^\]]+\]', '', text)
                if text == 'У Википедии нет статьи с таким именем. ':
                    rating = 1
                return rating, text
            else:
                return 1, ''
        else:
            return 1, ''
    except Exception as e:
        print(e)
        return 1, ''


def form_component(component_name: str) -> dict:
    data = {'name': component_name}
    is_positive, description = main(component_name)
    data['is_healthy'] = bool(is_positive)
    data['description'] = description
    return data


def runn(id):
    json = scraping_product(id)

    s = json.get('components')
    mass = s.split(',')
    mass1 = []
    check_mass = []

    for jj in re.findall(r'(?:[^\d]|\A)(\d{3})(?:[^\d]|\Z)', s):
        mass1.append('E' + jj)
        check_mass.append('Е' + jj)

    for i in mass:
        try:
            checker = 0
            for ji in check_mass:
                if ji in i:
                    checker = 1
            if checker == 0:
                tt = i.replace('(', '').replace(')', '').replace('"', '').replace("'", '')
                if tt[0] == ' ':
                    tt = tt[1:]
                mass1.append(tt)
        except Exception as e:
            print(e)

    component_names: List[str] = str(mass1).replace('[', '').replace(']', '').replace("'", '').split(',')
    json["components"] = [comp_name.strip() for comp_name in component_names if comp_name]

    garbage_disposal = {
        "стекло": "Выбрасываем: бутылки, банки, стеклобой (битый тара) от напитков, лекарственных средств и т.п.",
        "бумага": "Выбрасываем: белую бумагу, картон, бумажные упаковки, пакеты из бумаги, книги, открытки, газеты, журналы, тетради, альбомы",
        "пластик": "Выбрасываем: тару и упаковку – если видите на упаковке цифру 1 или маркировки PET, PETE; полиэтилен высокой и низкой плотности – маркировка HDPE, LDPE, или цифры 2 или 4",
        "сухая фракция": "Выбрасываем: металл (металлические банки и крышечки из-под напитков, консервов, косметики, другие предметы из металла, очищенные от остатков грязи и пищи). Не выбрасываем: пищевые отходы, одноразовую посуду, вакуумную упаковку и упаковку типа “шуршик”, бумагу с остатками пищи и жира, пенопласт, резиновые изделия, одежду и текстиль."
        }

    if 'стекло' in s:
        recycling = garbage_disposal.get('стекло')
    elif 'метал' in s or 'алюминий' in s or 'сталь' in s:
        recycling = garbage_disposal.get('сухая фракция')
    elif 'картон' in s or 'пакет' in s:
        recycling = garbage_disposal.get('бумага')
    else:
        recycling = garbage_disposal.get('пластик')

    json["utilize"] = recycling if recycling else ''
    return json


if __name__ == '__main__':
    print(runn(4823063109017))
