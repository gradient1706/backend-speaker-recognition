import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something")
    audio = r.listen(source)
    print("Time's over, Thank!")

try:
    print("Text: "r.recognize_google(audio, language = "vi"))
except:
    pass;
