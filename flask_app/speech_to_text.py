import os
import time
import azure.cognitiveservices.speech as speechsdk
import sys
base_path = sys.path[0]
import json

config_json = base_path + "/config.json"
with open(config_json) as user_file:
    json_config_file = json.load(user_file)
SPEECH_KEY = json_config_file["SPEECH_KEY"]
SPEECH_REGION = json_config_file["SPEECH_REGION"]
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

def transcribe():
    audio_config = speechsdk.AudioConfig(filename= base_path + "/data/customercall.wav")
    # speech_config.speech_recognition_language="en-US"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False

    output_file = open(base_path+"/return_data/transcript.txt", "w")

    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        output_file.close()
        print("Transcript saved in file:", base_path + "/data/customercall.wav")
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True
    def recognized_cb(evt : speechsdk.SpeechRecognitionEventArgs) :
        if speechsdk.ResultReason.RecognizedSpeech == evt.result.reason and len(evt.result.text) > 0 :
            print('RECOGNIZED:', evt.result.text)
            output_file.write(evt.result.text.replace("code","coat") + " ") #TODO: better transcription. Not focus of this demo.
            output_file.flush()
    
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    # speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)


    # speech_recognizer.start_continuous_recognition()
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)


    # result = speech_recognizer.recognize_once_async().get()
    # print(result.text)

    # if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    #     print("Recognized: {}".format(result.text))
    # elif result.reason == speechsdk.ResultReason.NoMatch:
    #     print("No speech could be recognized: {}".format(result.no_match_details))
    # elif result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = result.cancellation_details
    #     print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         print("Error details: {}".format(cancellation_details.error_details))
    #         print("Did you set the speech resource key and region values?")

transcribe()