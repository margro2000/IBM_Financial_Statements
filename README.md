# Financial Statements Automated Extraction
This tool takes inputs of financial statements in a png format and extracts out specified information. This would prevent financial analysts from having to spend time transferring data from financial statements into excel documents. The program was designed in python and used google vision and cloud systems for data processing. 

# Motivation
When tracking the financial data of a large amount of companies, there are certain sets of data that appear in the same format on a yearly schedule. When processing this data into excel, it is important to have updated and accurate information. Previously, companies have relied on financial analysts to extract and process data. This tool specifies certain metrics, and automatically extracts any inputted information, updating a company’s CSV file as new metrics and financial documents are released. 

# Code Example
![alt text](https://github.com/margro2000/IBM_Financial_Statements/blob/master/Screen%20Shot%202019-04-27%20at%201.33.17%20PM.png)

# Installation
Links:
1) To see the documentation and setup Google Cloud Vision account, go to: https://cloud.google.com/vision/docs/libraries
2) Link on how to use client libraries: https://cloud.google.com/vision/docs/quickstart-client-libraries
3) Installing pip: https://pip.readthedocs.io/en/stable/installing/
4) Setting up authentication: https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python

Steps for getting ready to work with Google OCR Vision API:

1) Go to the link listed above to setup your free account with Google Cloud Vision by clicking “Try Free” and completing the steps listed. 
2) Set up your first project and google cloud vision.
3) At the bottom of the tutorial, you will see an example of how to use the client library. This shows one execution of the google cloud library. Our goal for this project is to run and execute the code already given locally. However, before we can do this you need to go through the Python setup tutorial called Vision API Quickstart Using Client Libraries. Here is the link: https://cloud.google.com/vision/docs/quickstart-client-libraries
4) Run the pip install command given in your local terminal. If it doesn’t work, the you probably do not have pip installed. Go to Link 3 to install it. 
5) To set up your authentication key, go to link number four and scroll down to the "Creating a service account" section. Follow the instructions from the GCP Console option. After creating a json file with your credentials, store it securely and save its path. 
6) Before running the code, run the command: export GOOGLE_APPLICATION_CREDENTIALS="[PATH]" with tha path to your json file. This will allow you to run the code.

