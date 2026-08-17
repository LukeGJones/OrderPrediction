import csv
import glob
import openmeteo_requests
import datetime
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ExcludeList = ["", "Description", "1 Scoop Kellys", "2 scoop Kellys", "Bacon Fries 24g", "Biscuit packs", "Black Pudding & Mustard Fiddlers Crisps 40g", "Bombay Sapphire Single", "Bombay Sapphire Double", "Cheese & Onion Fiddlers Crisps 40g", "Chilli nuts", "Chilly Billy ", "Cornetto Classico", "Cornetto Mint", "Cornetto Strawberry", "Doggie Bags", "Dry Roasted Nuts", "Exhibit rose", "FAB", "Feast", "Fruit Pastille ", "Fruity Rainbow", "Gin 0% Single", "Gin 0% Double", "Gordons Lemon Single", "Gordons Gin Single", "Gordons Gin Double", "Gordons Orange Double", "Gordons Orange Single", "Gordons Peach Double ", "Gordons Peach Single", "Gordons Pink Double", "Gordons Pink Single", "Gordons Gin Single", "Greenalls Double", "Hendricks Single", "Hendricks Double", "Ice Cream", "Kleidal Chenin blanc", "Kit Kat 41.5g", "Lion Bar 50g", "Magnum Almond", "Magnum Classic", "Magnum Mint ", "Magnum White Chocolate", "Montguéret Tête Det", "Mini Cheddars 50g", "Place du village white", "Pork Scratchings", "Quavers", "Rountrees Black Current Push Up", "Rountrees Fruit Stack", "Rountrees Orange Push Up", "Salted Cashews 50g", "Salted Nuts 50g", "Scampi Fries 27g", "Sea Salt & Vinegar Fiddlers Crisps 40g", "Sea Salt Fiddlers Crisps 40g", "Smartie Push Up", "Smarties", "Solero", "Sweet Chilli Fiddlers Crisps 40g", "Tanqueray Single", "Tanqueray Double", "Twiglets 45g", "Twix 50g", "Watermelon Rowntrees"]

fileDates = []

def readFiles(dayOfWeek, isTotalAverage):
    itemList = {}
    files = glob.glob("DailySalesFiles/*.csv")
    totalnumfiles = 0
    dayNumFiles = 0
    for file in files:
        totalnumfiles += 1
        fileDate = file[16:26]
        fileDates.append(fileDate)
        if(datetime.date(int(fileDate[:4]), int(fileDate[5:7]), int(fileDate[8:10])).weekday() == dayOfWeek or isTotalAverage == True):
            dayNumFiles += 1
            with open(file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if(row[2] not in ExcludeList):
                        if row[2] in itemList:
                            itemList.update({row[2]: int(itemList[row[2]]) + int(row[6])})
                        else:
                            itemList.update({row[2]: int(row[6])})

    itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[0])}
    return itemList, totalnumfiles, dayNumFiles

def printDict(inDict):
    for x, y in inDict.items():
        print(x, y)

def AverageOrders(inDict, numfiles):
    averagesList = inDict.copy()
    for item, amount in averagesList.items():
        averagesList[item] = round((amount / numfiles), 2)
    return averagesList

def getWeather(date, forcast):
    openmeteo = openmeteo_requests.Client()
    if forcast == True:
        url = "https://api.open-meteo.com/v1/forecast"
    else:
        url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": 51.576367630995136,
        "longitude": -0.7164894580753421,
        "daily": ["temperature_2m_max", "rain_sum"],
        "start_date": date,
        "end_date": date
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    return { "temp_max": daily.Variables(0).ValuesAsNumpy()[0], "rain": daily.Variables(1).ValuesAsNumpy()[0] }

def createDataSet():
    dataset = []
    files = glob.glob("DailySalesFiles/*.csv")

    for file in files:
        fileDate = file[16:26]

        totalOrders = 0
        with open(file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if(row[2] not in ExcludeList):
                        totalOrders += int(row[6])

        weather = getWeather(fileDate, False)

        row = {
            "Date": fileDate,
            "Orders": totalOrders,
            "MaxTemp": round(float(weather["temp_max"]), 1),
            "Rain": weather["rain"],
            "DayofWeek": datetime.date(int(fileDate[:4]), int(fileDate[5:7]), int(fileDate[8:10])).weekday(),
            "Month": int(fileDate[5:7]),
            "IsWeekend": datetime.date(int(fileDate[:4]), int(fileDate[5:7]), int(fileDate[8:10])).weekday() >= 5,
            "IsEventOn" : False
        }

        dataset.append(row)
        dataset = sorted(dataset, key=lambda x: x["Date"])

    return pd.DataFrame(dataset)

def prediction(date):
    dataset = getDataSet()

    features = [
        "MaxTemp",
        "Rain",
        "DayofWeek",
        "Month",
        "IsWeekend",
        "IsEventOn"
    ]

    x = dataset[features]
    y = dataset["Orders"]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(x, y)

    weather = getWeather(date, True)
    future = pd.DataFrame([{
        "MaxTemp": round(float(weather["temp_max"]), 1),
        "Rain": weather["rain"],
        "DayofWeek": datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10])).weekday(),
        "Month": int(date[5:7]),
        "IsWeekend": datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10])).weekday() >= 5,
        "IsEventOn": False
    }])

    prediction = model.predict(future)[0]
    return(prediction)

def getDataSet():
    try:
        dataset = pd.read_csv("dataset.csv")
    except:
        dataset = createDataSet()
        dataset.to_csv("dataset.csv", index=False)
    return dataset

def updateDataSet():
    dataset = createDataSet()
    dataset.to_csv("dataset.csv", index=False)

def AllDaysMenu():
    itemList, numfiles, _ = readFiles(-1, True)
    print("All Days Menu")
    inp = input("1.All Days Average\n2.All Days Top Orders\n3.Return to Main Menu\n:")
    if inp == "1":
        printDict(AverageOrders(itemList, numfiles))
    elif inp == "2":
        itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[1], reverse=True)}
        printDict(itemList)
    elif inp == "3":
        mainMenu() 
    else:
        print("Command not valid")
        AllDaysMenu()

def SpecficDayMenu():
    print("Specific Day Menu")
    specDay = input("Enter a specific day of the week\n:")
    specDayNum = daysOfWeek.index(specDay[0].upper() + specDay[1:].lower())
    itemList, _, dayNumFiles = readFiles(specDayNum, False)
    inp = input("1.Specific Day Average\n2.Specific Day Top Orders\n3.Return to Main Menu\n:")
    if inp == "1":
        printDict(AverageOrders(itemList, dayNumFiles))
    elif inp == "2":
        itemList = {k: v for k, v in sorted(itemList.items(), key=lambda item: item[1], reverse=True)}
        printDict(itemList)
    elif inp == "3":
        mainMenu() 
    else:
        print("Command not valid")
        SpecficDayMenu()

def PredictionMenu():
    inpDate = input("Enter date in form YYYY-MM-DD\n:")
    orderPrecition = round(float(prediction(inpDate)))
    print(orderPrecition)

def mainMenu():
    print("Welcome message")
    inp = input("1.All Days Menu\n2.Specific Day Menu\n3.Order Prediction\n4.Display Dataset\n5.Update Dataset\n6.Add Event on Date\n:")
    if inp == "1":
        AllDaysMenu()
    elif inp == "2":
        SpecficDayMenu()
    elif inp == "3":
        PredictionMenu()
    elif inp == "4":
        print(getDataSet())
    elif inp == "5":
        updateDataSet()
    elif inp == "5":
        updateDataSet()

mainMenu()