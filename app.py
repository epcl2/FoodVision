import os, io, base64
from flask import Flask, render_template, request, jsonify
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import azure.cognitiveservices.speech as speechsdk

#credentials = CognitiveServicesCredentials(os.environ['computer_vision_key'])
#computervision_client = ComputerVisionClient(os.environ['computer_vision_endpoint'], credentials)

credentials = CognitiveServicesCredentials('d539943fc0e149c4a6aa5c88a311c345')
computervision_client = ComputerVisionClient('https://computervisionhackcambridge.cognitiveservices.azure.com/', credentials)

speech_key, service_region = "7312537c21c24fcb9f0873bef0f17bac", "uksouth"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates a speech synthesizer using the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

caption_obj_detected = " "

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
    description_results = computervision_client.describe_image_in_stream(image)

    # Get the captions (descriptions) from the response, with confidence level
    description = 'Description of remote image: '
    if (len(description_results.captions) == 0):
        description = description + 'No description detected.'
    else:
        for caption in description_results.captions:
            if caption.confidence >=0.7:
                description = description + caption.text
                caption_obj_detected = description
                print(description)
    
    print("cap:" + caption_obj_detected)
    #print("cap:" + caption_obj_detected)
    if (caption_obj_detected)!= " ":
        text = caption_obj_detected

        # Synthesizes the received text to speech.
        # The synthesized speech is expected to be heard on the speaker with this line executed.
        result = speech_synthesizer.speak_text_async(text).get()

        # Checks result.
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            print("Did you update the subscription info?")    

    # Return a result
    return jsonify({'description' : description})

"""    

    ######################################################
    #                                                   #
    # Add your code here to use the Computer Vision SDK #
    #                                                   #
    #####################################################
"""



# Receives a text from console input.
print("Type some text that you want to speak...")

"""

tag_results = computervision_client.tag_image_in_stream(image)

    # Get the captions (descriptions) from the response, with confidence level
    description = 'Tags in remote image: '
    if (len(tag_results.tags) == 0):
        print('No tag detected.')
    else:
        f = open("contents.csv", "a")
        for tag in tag_results.tags:
            objectdetected = tag.name
            f.write(tag.name + "\n")
            print(tag.name, tag.confidence)
            #print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))
    f.close()

"""

    
