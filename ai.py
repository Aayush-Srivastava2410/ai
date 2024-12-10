from dspbot import token
from random import choice
import google.generativeai as genai
import t2s as tts


queryText='How does AI work'
wordLimit=['50', '100', '150', '200']

genai.configure(api_key=token)
model = genai.GenerativeModel("gemini-1.5-flash")


response = model.generate_content(queryText+"in about 50 words")
tts.T2S(
    response.text
).save('1.mp3')