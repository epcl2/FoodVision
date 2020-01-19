import os, io, base64
from flask import Flask, render_template, request, jsonify
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
# import google
import webbrowser
import csv

credentials = CognitiveServicesCredentials('d539943fc0e149c4a6aa5c88a311c345')
computervision_client = ComputerVisionClient('https://computervisionhackcambridge.cognitiveservices.azure.com/', credentials)

obj_detected = []
ingredients_list = ["pasta","noodles", "sweet potato","corn", "bean","salmon","drumstick","turkey", "hummus", "jam","butter", "banana", "apple", "garlic","leaf vegetable", "rice", "egg", "tomato","chicken","meat","beef","pork","ham","potato","spinach","mushroom","radish","milk","cheese","fish","cream","yoghurt"]

"""ingredients_list = []
with open('ingredients.csv','rt')as f:
    data = csv.reader(f)
    for row in data:
        ingredients_list.append(row) """


app = Flask(__name__)

# The root route, returns the home.html page
@app.route('/')
def home():
    # Add any required page data here
    page_data = {}
    return render_template('home.html', page_data = page_data)

@app.route('/process_image', methods=['POST'])
def check_results():
    # Get the JSON passed to the request and extract the image
    # Convert the image to a binary stream ready to pass to Azure AI services
    body = request.get_json()
    image_bytes = base64.b64decode(body['image_base64'].split(',')[1])
    image = io.BytesIO(image_bytes)

    # Send the image to the Computer Vision service
    tag_results = computervision_client.tag_image_in_stream(image)
    
    #Uncomment line below if using url image instead
    #tag_results = computervision_client.tag_image('https://st.depositphotos.com/2045405/2014/i/950/depositphotos_20143109-stock-photo-apple-and-banana-on-white.jpg')

    # Get the captions (descriptions) from the response, with confidence level
    description = 'Tags in remote image: '
    if (len(tag_results.tags) == 0):
        print('No tag detected.')
    else:
        #f = open("contents.csv", "a")
        for tag in tag_results.tags:
            if tag.confidence >=0.5 and tag.name in ingredients_list:
                obj_detected.append(tag.name)
                #obj_output.append(tag.name)
                #f.write(tag.name + "\n")
                #obj_detected= tag.name
                print(tag.name, tag.confidence)
            #print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))

        try: 
            from googlesearch import search 
        except ImportError:  
            print("No module named 'google' found") 

        obj_list = " ".join(str(e) for e in obj_detected)
        print("The ingredients you have is " + obj_list)
        query = obj_list + " recipe"
        print("Searching for: " + query)
  
        if query !=" recipe":
            for j in search(query, tld="co.in", num=10, stop=1, pause=2): 
                website = j
                print(j)
                webbrowser.open_new(website)
    
    return jsonify({'description' : "The ingredient(s) you have is/are: " +obj_list +'\n' +'Searching for: ' +obj_list +" recipe"})

    #f.close()
    

#for reading recipes that are in a csv file instead of searching the web  
"""with open('recipes.csv') as csvfile:
    reader = csv.reader(csvfile)
    my_list = list(reader)
    print(my_list)
    for row in my_list:
        if row['Ingredients'] in obj_detected and obj_detected != []: 
            print(row['Ingredients'])
            print(obj_detected)
            print(my_list['Name'])
        else:
            break"""