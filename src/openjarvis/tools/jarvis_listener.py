import speech_recognition as sr
import requests
import pyttsx3 # For local voice feedback
import time

engine = pyttsx3.init()
recognizer = sr.Recognizer()

JARVIS_API_URL = "http://127.0.0.1:8000/v1/chat/completions" # Your OpenJarvis backend

def speak(text):
    engine.say(text)
    engine.runAndWait()

def ask_jarvis(prompt, history):
    print(f"Asking Jarvis: {prompt}")
    
    # Append user prompt to history
    history.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "gemma4:latest",
        "messages": history
    }
    
    response = requests.post(JARVIS_API_URL, json=payload)
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        print(f"Jarvis: {reply}")
        speak(reply)
        # Append AI response to history
        history.append({"role": "assistant", "content": reply})
        time.sleep(1) # Prevent microphone from picking up tail of spoken audio
        return True
    else:
        speak("I am having trouble connecting to the backend.")
        time.sleep(1)
        return False

def main():
    conversation_history = [
        {"role": "system", "content": "You are Jarvis, a helpful AI voice assistant. Give short, concise, and conversational answers. Do not use formatting like markdown or bullet points because your answers will be read aloud."}
    ]
    
    try:
        # device_index=1 explicitly selects 'Microphone Array'
        with sr.Microphone(device_index=1) as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)
            print("Jarvis Listener Active! Say 'Jarvis' to wake me.")
            
            while True:
                try:
                    # 1. Wait for Wake Word
                    audio = recognizer.listen(source, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio).lower()
                    
                    if "jarvis" in text:
                        speak("Yes?")
                        
                        # 2. Enter Active Conversation Mode
                        active_conversation = True
                        while active_conversation:
                            print("Listening for command...")
                            try:
                                command_audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                                command = recognizer.recognize_google(command_audio)
                                
                                if "goodbye" in command.lower() or "stop" in command.lower() or "that's all" in command.lower():
                                    speak("Goodbye, sir.")
                                    active_conversation = False
                                    break
                                    
                                ask_jarvis(command, conversation_history)
                                
                            except sr.WaitTimeoutError:
                                # If silence for 5 seconds, drop out of active conversation
                                active_conversation = False
                                print("Silence detected. Returning to sleep mode.")
                            except sr.UnknownValueError:
                                pass # Unrecognizable, wait for next phrase
                                
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    print(f"Error: {e}")
    except AttributeError:
        print("\n" + "="*60)
        print("❌ CRITICAL ERROR: MICROPHONE ACCESS BLOCKED")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
