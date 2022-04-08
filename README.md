# TechConf Registration Website

## Project Overview

The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:

- The web application is not scalable to handle user load at peak
- When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
- The current architecture is not cost-effective

In this project, you are tasked to do the following:

- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:

- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App

1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
     - `POSTGRES_URL`
     - `POSTGRES_USER`
     - `POSTGRES_PW`
     - `POSTGRES_DB`
     - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function

1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

   **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.

   - The Azure Function should do the following:
     - Process the message which is the `notification_id`
     - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
     - Query the database to retrieve a list of attendees (**email** and **first name**)
     - Loop through each attendee and send a personalized subject message
     - After the notification, update the notification status with the total number of attendees notified

2. Publish the Azure Function

### Part 3: Refactor `routes.py`

1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis

Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

# Free / Basic Tier

| Azure Resource            | Service Tier | Monthly Cost |
| ------------------------- | ------------ | ------------ |
| _Azure Postgres Database_ | Basic        | 25.32        |
| _Azure Service Bus_       | Basic        | 0.05         |
| _Azure Web App Service_   | F1           | Free         |
| _Azure Storage Account_   | Basic        | < 0.1        |
| _Azure Function_          | Basic        | .20/mill     |

For Azure Functions, we are going to be charged $.20/million execution. There is a premium plan that we can opt in that does
not charge for execution, but instead $.173/ vCPU/hr and Memory .0123GB/hr. But not sure for our use, that would be needed.

# Production Cost Analysis

| Azure Resource            | Service Tier | Monthly Cost |
| ------------------------- | ------------ | ------------ |
| _Azure Postgres Database_ | v4 20GiB M   | 255.792      |
| _Azure Service Bus_       | Basic        | 5.00         |
| _Azure Web App Service_   | P1v2         | 146          |
| _Azure Storage Account_   | Hot          | < 5          |
| _Azure Function_          | Basic        | .20/mill     |

# Azure Postgres Database

Good starting point. Making sure we have not too little and not too many memory. Evaluate
as we proceed and determine the amount of records we're storing in our database.

# Service Bus Analysis

The service bus cost above is strictly if we are only dealing with queues and messages.
The basic tier essentially.
We have the ability to opt into the standard qhere that provides topics, transactions,
sessions, forwardTo/SendVia, etc.

# Web App Service Analysis

P1v2 would be a test starting point. 1 Core 3.5 GB Ram 250GB Storage.
This can be changed as we evaluate our traffic, seeing if it's necessary.

# Azure Storage Account Analysis

I would say the hot plan would be okay. Don't think the premium plan would be necessary.

# Azure Function Analysis

This is whether we stay with the basic or premium. We'll start with the basic, as we'll
get charged per execution. If we find the benefits that premium provides satisfactory,
then we can switch.

## Architecture Explanation

This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.
Performance - Great performance to use a web app for the front end and Azure Function for the backend. Especially for the operations and load they're going to be
operating.

With an azure function we're running serverless so we're able to run our code without provisioning servers. We also also not have control of the
underlying OS of the web app. Wouldn't have to worry about that.

Both offer vertical and horizontal scalability.
