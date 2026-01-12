from google import genai

client = genai.Client(api_key = "AIzaSyBcC3VLE0pO9eVmUgK6gK7C0aP0aSLXcFE")

response = client.models.generate_content(
    model='gemini-2.5-flash', contents="Describe the color Blue to someone whos's never been able to see in one line."
)
print(response.text)