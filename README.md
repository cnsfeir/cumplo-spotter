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
  <img src="https://user-images.githubusercontent.com/58790635/222311408-6bf520a6-fd8a-47c2-b067-e2860e4de823.png" width="230"/>
  <img width="20"/>
  <img src="https://user-images.githubusercontent.com/58790635/222309655-42720654-f9f2-4bff-abcf-45b7387272b3.gif" width="230"/>
</div>

## Features

As mentioned before, the factors used for filtering the available investment opportunities are fully customizable. All this parameters are optional. If any is missing, then it just won't be used in the filtering process.

|name|type|description|
|-----:|:----:|:-------------------|
|`irr`|`float`|The minimum internal rate or return|
|`monthly_profit_rate`|`float`|The minimum monthly profit rate|
|`duration`|`int`|The minimum duration (in days) of the credit|
|`score`|`float`| The minimum Cumplo score assigned to the borrower|
|`credits_requested`|`int`|The minimum amount of credits requested by the borrower|
|`amount_requested`|`int`|The minimum total amount requested by the borrower|
|`average_days_delinquent`|`int`|The maximum average days delinquent of the borrower|
|`paid_in_time_percentage`|`float`|The minimum percentage of credits paid in time by the borrower (`<= 30` days)|
|`filter_dicom`|`bool`|Whether you want to filter out the borrowers registered in [DICOM](https://www.misabogados.com/dicom#Que-es-DICOM)|

To not be notified about the same investment opportunities every time, you can set an expiration time for the notifications. Which means that if a new investment opportunity was notified, **the app will stop notifying it until it expires and then it'll notify it again.**

|name|type|description|
|-----:|:----:|:-------------------|
|`notification_expiration`|`int`|The time in hours needed for a notification to expire|

Besides the notifications themself and the automation, the whole logic of this app is contained in a single endpoint. So the scraper can be executed both automatically and on-demand. Although the notification only shows the number of investment opportunities, the endpoint delivers all the information you need to make an informed decision. So whenever you're ready to make an investment, **you can call the endpoint directly (ignoring the notified opportunitites) and get a summary of all the promising investment opportunities available at the moment ordered by their monthly profit rate.**

|name|type|description|
|-----:|:----:|:-------------------|
|`filter_notified`|`bool`|Whether you want to filter the notified investment opportunities|


``` json
{
    "total": 1,
    "ids": [
        68047
    ],
    "opportunities": [
        {
            "id": 68047,
            "score": "0.55",
            "irr": "23.107",
            "monthly_profit_rate": "0.0172",
            "amount": "$93.500.000",
            "funded_amount": "$63.949.920",
            "funded_amount_percentage": "0.6840",
            "credit_type": "IRRIGATION",
            "url": "https://secure.cumplo.cl/68047",
            "duration": {
                "unit": "day",
                "value": 24
            },
            "institution": {
                "id": "26658",
                "business_name": "SERVICIO REGIONAL DE LA VIVIENDA Y URBAN"
            },
            "borrower": {
                "id": "8184",
                "name": "CONSTRUCTORA CASTILLO Y ASOCIADOS LIMITADA",
                "dicom": true,
                "average_days_delinquent": 11,
                "funding_requests_count": 29,
                "paid_funding_requests_count": 20,
                "paid_funding_requests_percentage": "0.690",
                "total_amount_requested": "$1.170.600.005"
                "amount_paid_in_time": "$914.861.711",
                "paid_in_time_percentage": "0.920",
            },
            "supporting_documents": [
                "COPIA DEL CONTRATO DE LA CONSTRUCTORA CON LA EGIS",
                "RESPALDO SUBSIDIO BAJO EL DS 255 CONSTRUCCION DE VIVIENDAS",
                "OBRA TERMINADA AL 100"
            ]
        }
    ]
}
```
Since Cumplo's front-end only shows the last `20` investment opportunities, when there are `>20` opportunities available some of them cannot be accessed through the webpage. But as you may noticed, **each investment opportunity in the response has an `url` key that allows you to access all opportunities regardless of whether they are hidden or not**.

## Try it
```bash
curl --location 'https://fetch-investment-opportunities-ryugxhk4ca-uc.a.run.app' \
--header 'x-api-key: 0000_TESTING_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "filter_notified": false,
    "paid_in_time_percentage": 0.8,
    "average_days_delinquent": 20,
    "monthly_profit_rate": 0.015,
    "filter_dicom": true,
    "score": 0.4
}'
```
> This API key will be available only **temporarily**. For extended use, please contact **cnsfer@uc.cl** to obtain your own official API key.


## Architecture

As mentioned before, the whole logic of the app is contained in a single endpoint. From there, you can create two simple shortcuts that call this endpoint and display the results in a notification. You can find these two shortcuts in the `/shortcuts` directory, download them and import them into your iPhone.

<div align="center" witdh="100%">
  <img src="https://user-images.githubusercontent.com/58790635/227660611-df4627bd-7fea-4362-874e-3d5135a7f78a.png" width="380"/>
  <img width="10"/>
  <img src="https://user-images.githubusercontent.com/58790635/227660069-08bc10b4-a15b-43f7-b4b0-671df8c98bb4.png" width="430"/>
</div>

> Since the iOS Shortcuts app doesn't support cron jobs, how often the endpoint is called will depend on the quantity of ["automations"](https://support.apple.com/guide/shortcuts/create-a-new-personal-automation-apdfbdbd7123/6.0/ios/16.0) you create.



## To-Do
- Calculate the monthly profit rate for credits with **multiple instalments**.
- Add a `limit` parameter to get only the first `N` investment opportunities.
