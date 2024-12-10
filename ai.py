from dspbot import token
from random import choice
import google.generativeai as genai
queryText='How does AI work'
wordLimit=['50', '100', '150', '200']

genai.configure(api_key=token)
model = genai.GenerativeModel("gemini-1.5-flash")


response = model.generate_content(queryText+"in {0} words".format(choice(wordLimit)))
print(response.text)