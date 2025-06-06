from dotenv import load_dotenv
import os
from locust import HttpUser, task, between

class TransliterationUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks to simulate realistic user behavior

    # Realistic sample texts for supported languages
    sample_texts = {
        "hi": "मेरा नाम राहुल है। मैं दिल्ली में रहता हूँ।",  # Hindi: "My name is Rahul. I live in Delhi."
        "ta": "என் பெயர் ராகுல். நான் டெல்லியில் வசிக்கிறேன்.",  # Tamil: "My name is Rahul. I live in Delhi."
        "bn": "আমার নাম রাহুল। আমি দিল্লিতে থাকি।"  # Bengali: "My name is Rahul. I live in Delhi."
    }

    @task
    def transliterate_hi(self):
        self.transliterate("hi")

    @task
    def transliterate_ta(self):
        self.transliterate("ta")

    @task
    def transliterate_bn(self):
        self.transliterate("bn")

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
