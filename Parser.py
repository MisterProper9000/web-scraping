import webbrowser
import urllib.request
from bs4 import BeautifulSoup
import json
import xlsxwriter
from datetime import datetime
from datetime import timedelta 
import time

workbook = xlsxwriter.Workbook('data'+ datetime.today().strftime('%Y_%m_%d') +'.xlsx', {'strings_to_numbers': True})

date_format = workbook.add_format({'num_format': 'yyyy-m-d'})
review_format = workbook.add_format({'num_format': '#,#'})

filewrite = open('url.txt', 'w')
filewrite.write("")
filewrite.close()

filewrite = open('log.txt', 'w')
filewrite.write("")
filewrite.close()

file = open('list.txt', 'r')
row = 0

worksheet = workbook.add_worksheet()

#print(worksheet.write(row, 0,"apartment name"))
#print(worksheet.write(row, 1, "review"))
#print(worksheet.write(row, 2, "checkin date"))
#print(worksheet.write(row, 3, "checkout date"))
#print(worksheet.write(row, 4, "avaliability"))
#print(worksheet.write(row, 5, "price"))
#row += 1

last_day_of_collecting = datetime.strptime('Apr 14 2019','%b %d %Y')

#print(last_day_of_collecting.strftime('%Y-%m-%d'))
#парсим url, засовывая в него даты заезда/отъезда и число взрослых (позже надо добавить проверку на праздничный день)
for line in file:
    checkin_date = datetime.today() - timedelta(days = 1)
    while checkin_date <= last_day_of_collecting:

        time.sleep(1) #pause requests cycle to avoid problems with website access

        idx,url = line.split(' ')
    
        components = url.split(';')

        cIdx = 0
        checkin_date = checkin_date + timedelta(days = 1)# + timedelta(days = 13) #for testing
        checkout_date = checkin_date + timedelta(days = 1)
        for component in components:
            if cIdx <(len(components)-1):
                component = component + ";"

            components.insert(cIdx, component)
            del components[cIdx  + 1]
            liter, value = component.split('=')

            if liter == "label":
                components.insert(cIdx + 1, "checkin=" + checkin_date.strftime('%Y-%m-%d'))
                components.insert(cIdx + 2, "checkout=" + checkout_date.strftime('%Y-%m-%d') )
            elif liter == "group_adults":
                components.insert(cIdx + 1, "group_children=0")


            cIdx = cIdx + 1

    
        url = ''.join(str(e) for e in components)
        filewrite = open('url.txt', 'a')
        filewrite.write(url)
        filewrite.close()

        try_num = 0

        request = None
        while try_num < 3:
            headers = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.3'}
            request = urllib.request.Request(url,headers=headers)
            if request != None:
                break
            try_num = try_num + 1
            time.sleep(1)

        if try_num == 3:
            filewrite = open('log.txt', 'w')
            filewrite.write('failed to access: ' + url)
            filewrite.close()
            break

        html = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(html,'html.parser')

        #First lets get the HTML of the table called site Table where all the links are displayed
        main_table = soup.find("div", attrs={'id':'bodyconstraint'})

   

        scores = main_table.find_all("div", class_ = "bui-review-score__badge")

        spans = main_table.find_all("div", class_ ="hp__hotel-title")

        col = 0

   
    
        print("_______________________________")
        print(len(scores))
        print(len(spans))

        extracted_records = []
        # Start from the first cell. Rows and columns are zero indexed.
    
    
    
        for span, score in zip(spans, scores):


            hotel = span.find('h2').text.split('\n')[2]
            scor = score.text
            record = {
                'hotel' : hotel,
                'score' : scor
            }
            print("%s - %s"%(span.find('h2').text.split('\n')[2], scor))
            extracted_records.append(record)
            print(worksheet.write(row, col,hotel))
            print(worksheet.write(row, col + 1, scor, review_format))
            print(worksheet.write(row, col + 2, checkin_date.strftime('%Y-%m-%d'), date_format))
            print(worksheet.write(row, col + 3, checkout_date.strftime('%Y-%m-%d'), date_format))


        FINALTEXT = ""
        no_avaliability = main_table.find("div", attrs ={"id" : "no_availability_msg"})
        #rint("NO AVALIABILE %s", no_avaliability)
        if(no_avaliability != None):
            print("not av")
            print(worksheet.write(row, col + 4, "0"))
            print(worksheet.write(row, col + 5, "0"))
        else:
            print(worksheet.write(row, col + 4, "1"))
            #price = main_table.find_all("div", {"class": "hprt-price-price "})
            print("-----")
            specPrice = soup.find(class_ = "hprt-price-smart_deal hprt-price-price-standard ")
            finalText = ""
            if(specPrice == None):
                price = soup.find_all('span', {'class' : "hprt-price-price-standard "})
                for pr in price:
                    finalText = pr.text
                    finalText = finalText.replace(" ", "")
                    finalText = finalText.replace("\n", "")
            
            else:
                finalText = specPrice.text
                finalText = finalText.replace(" ", "")
                finalText = finalText.replace("\n", "")

       
            for cc in range(1, len(finalText)):
                print(cc)
                print(finalText[:cc])
                try: 
                    int(finalText[:cc])
                
                except ValueError:
                    FINALTEXT = finalText[:cc-2]
                    break
            print(worksheet.write(row, col + 5, FINALTEXT))
        row += 1



workbook.close()

print("END")