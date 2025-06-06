from dotenv import load_dotenv
import os
from locust import HttpUser, task, between

class TransliterationUser(HttpUser):
    wait_time = between(1, 5)  # Waiting 1-5 seconds between tasks to simulate realistic user behavior

    # Realistic sample texts for the three supported languages, text translation taken from google translate
    # Orignal text: "My name is Rahul. I live in Delhi."

    sample_texts = {
        "hi": "मेरा नाम राहुल है। मैं दिल्ली में रहता हूँ।",  # Hindi
        "ta": "என் பெயர் ராகுல். நான் டெல்லியில் வசிக்கிறேன்.",  # Tamil
        "bn": "আমার নাম রাহুল। আমি দিল্লিতে থাকি।"  # Bengali
    }

    # Tasks for transliteration in different languages
    # Translation from Hindi to English
    @task
    def transliterate_hi(self):
        self.transliterate("hi")

    # Translation from Tamil to English
    @task
    def transliterate_ta(self):
        self.transliterate("ta")

    # Translation from Bengali to English
    @task
    def transliterate_bn(self):
        self.transliterate("bn")

    # Method to perform transliteration for a given language
    # Uses the SARVAM API to transliterate text from the specified language to English
    # The API key is loaded from an environment variable using dotenv
    # The API endpoint is "/transliterate" as mentioned in the documentation
    def transliterate(self, language):
        payload = {
            "input": self.sample_texts[language],
            "source_language_code": language + "-IN",
            "target_language_code": "en-IN"
        }
        
        load_dotenv()
        headers = {"api-subscription-key": os.getenv("SARVAM_API_KEY")}
        self.client.post(
            "/transliterate",
            json=payload,
            headers=headers,
            name=f"Transliterate {language.capitalize()}"
        )
