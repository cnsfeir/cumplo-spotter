<div align="center">
  <img src="https://user-images.githubusercontent.com/58790635/222315487-28fc84f9-c6d0-4a4e-83b5-a2e508fd077a.png" width="650"/>
</div>

<p align="center">
    <em>
      A <b> simple yet powerful </b> Shorcuts app to get notified whenever a promising <br> Cumplo investment opportunity arises
    </em>
</p>
<br>

____

## Context

[**Cumplo**](https://www.cumplo.com/) is a **chilean crowdlending company** and [certified B Corp](https://www.bcorporation.net/en-us/find-a-b-corp/company/cumplo-chile-sa), operating in Chile, Mexico, and Peru which **connects loan applicant companies with a network of investors through its online platform**. Cumplo's aim is to deliver a transparent and excellence service with **fair rate**. Its network consists of about 50,000 registered users on the website, 3,000 investors and 1,000 SMEs.

## The Problem

**⌛ Good investment opportunities are financed in a matter of minutes by big bidders.** <br>
**🚨 No real-time notification system for new investment opportunities.**

## Solution

A simple app that notifies you whenever a promising Cumplo investment opportunity arises. To do so, it relays on the [iOS Shortcuts app](https://apps.apple.com/us/app/shortcuts/id915249334) and a simple scraper that can navigate through Cumplo's website, get all the investement opportunities available, and **filter the promising ones based on a series of customizable factors**.


<div align="center" witdh="100%">
  <img src="https://user-images.githubusercontent.com/58790635/222311408-6bf520a6-fd8a-47c2-b067-e2860e4de823.png" width="250"/>
  <img width="20"/>
  <img src="https://user-images.githubusercontent.com/58790635/222309655-42720654-f9f2-4bff-abcf-45b7387272b3.gif" width="250"/>
</div>

## Features

As mentioned before, the factors used for filtering the available investment opportunities are fully customizable. All this parameters are optional. If any is missing, then it just won't be used in the filtering process.

|name|type|description|
|-----:|:----:|:-------------------|
|`irr`|`float`|The minimum internal rate or return|
|`monthly_profit_rate`|`float`|The minimum monthly profit rate|
|`duration`|`int`|The minimum duration (in days) of the credit|
|`score`|`float`| Value between 0 and 1 that represents the score assigned by Cumplo to the borrower|
|`credits_requested`|`int`|The minimum amount of credits requested by the borrower|
|`amount_requested`|`int`|The minimum total amount requested by the borrower|
|`delinquent_days`|`int`|The minimum average delinquent days of the borrower|
|`paid_in_time`|`float`|The minimum percentage of credits paid in time by the borrower (`<= 30` days)|
|`dicom`|`bool`|Whether the borrower is registered in DICOM|

To not be notified about the same investment opportunities every time, you can set an expiration time for the notifications. Which means that if a new investment opportunity was notified, the app will stop notifying it until it expires and then it'll notify it again.

|name|type|description|
|-----:|:----:|:-------------------|
|`notification_expiration`|`int`|The time in hours needed for a notification to expire|

Besides the notifications themself and the automation, the whole logic of this app is contained in one endpoint. So the scraper can be executed both automatically and on-demand. Although the notification only shows the number of investment opportunities, the endpoint delivers all the information you need to make an informed decision. So whenever you're ready to make an investment, you can call the endpoint directly (ignoring the notified opportunitites) and get a summary of the promising investment opportunities available at the moment ordered by their monthly profit rate.

|name|type|description|
|-----:|:----:|:-------------------|
|`filter_notified`|`bool`|Whether you want to filter the notified investment opportunities|


``` json
{
    "total": 1,
    "ids": [
        67811
    ],
    "opportunities": [
        {
            "id": 67811,
            "monthly_profit_rate": 0.0172,
            "tir": 22.955,
            "score": 0.95,
            "amount": 89900000,
            "funded_amount": 83136846,
            "borrower": {
                "id": "6563",
                "fantasy_name": "CONSTRUCTORA MAGISTRAL",
                "funding_requests": 71,
                "funding_requests_paid": 57,
                "total_requested": 1847900020,
                "instalments_paid_in_time": 1492100018,
                "instalments_paid_percentage": null,
                "history": {
                    "average_deliquent_days": 15,
                    "paid_in_time": 0.91,
                    "dicom": false
                }
            },
            "credit_type": "irrigation",
            "duration": {
                "unit": "day",
                "value": 45
            },
            "institution": {
                "id": "26598",
                "business_name": "SERVICIO DE VIVIENDA Y URBANIZACION REGION ÑUBLE"
            }
        }
    ]
}
```

## Architecture

<div align="center" witdh="100%">
  <img src="https://user-images.githubusercontent.com/58790635/222968535-252db58c-8f1f-4851-967f-de15d5dc75ff.png" width="500"/>
</div>


## To-Do
