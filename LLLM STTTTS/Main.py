from ollama import chat, ChatResponse
import ollama
import pyttsx3
import speech_recognition as sr

stuff = input("Enter the model should use: ")
stuff = stuff + ' You must never use emojis or any formated text in your responses. This includes punctuation, paragraphs, and line breaks.'

ollama.create(model='EnM', from_='gemma3:12b', system=stuff)

class LLM:
    def __init__(self):
        self.speech_to_text = ""
        self.response = None
        self.engine = pyttsx3.init(driverName='espeak')  # Initialize the engine once
        
    def LLM_response(self):
        try:
            chat_response: ChatResponse = chat(model='tst', messages=[
                {
                    "role": "user",
                    "content": self.speech_to_text
                }
            ])
            self.response = chat_response.get('message', {}).get('content', None)
            print(f"Debug: Response from chat: {self.response}")
            if not self.response:
                print("Failed to retrieve a valid response from the model.")
        except Exception as e:
            print(f"Error in LLM_response: {e}")
            self.response = None

    def TTS(self):
        if self.response:
            try:
                print(f"Debug: Starting TTS with response: {self.response}")
                voices = self.engine.getProperty('voices')
                rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', rate-100)
                self.engine.setProperty('voice', voices[1].id)
                
                # Split response into words
                words = self.response.split()
                max_chunk_size = 50
                chunks = []
                current_chunk = ""

                for word in words:
                    # Check if adding the next word exceeds the max_chunk_size
                    if len(current_chunk) + len(word) + 1 <= max_chunk_size:
                        current_chunk += (word + " ")
                    else:
                        chunks.append(current_chunk.strip())
                        current_chunk = word + " "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                for chunk in chunks:
                    print(f"Debug: Speaking chunk: {chunk}")
                    self.engine.say(chunk)
                    self.engine.runAndWait()
                
                print("Debug: TTS completed successfully.")
            except Exception as e:
                print(f"Error in TTS: {e}")
        else:
            print("No response available for TTS.")

    def STT(self):
        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        try:
            self.speech_to_text = r.recognize_whisper(audio, language="english")
            print("Debug: You said: " + self.speech_to_text)
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Whisper; {e}")

# Create an instance of LLM and call the methods
run = True
while run:
    print("Debug: Starting the LLM process.")

    llm_instance = LLM()
    llm_instance.STT()

    if not llm_instance.speech_to_text:
        print("No valid input detected. Please try again.")
        continue

    llm_instance.LLM_response()

    if not llm_instance.response:
        print("No valid response from the model. Please try again.")
        continue

    llm_instance.TTS()