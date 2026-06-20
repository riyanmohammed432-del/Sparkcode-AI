from openai import OpenAI
import re

key = "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"
client = OpenAI(api_key=key)

response = client.responses.create(
    model="gpt-5.4-mini",
    input="Give some code for a app in python.",
    store=True,
)

text = response.output_text
print(text)
match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
poem = match.group(1).strip() if match else text.strip()
print(poem)
'''
# Print with typing effect and color
def typing_print(text, delay=0.03, color=GREEN):
    for char in text:
        print(color + char, end='', flush=True)
        time.sleep(delay)
        # Add a slightly longer delay for newlines
        if char == '\n':
            time.sleep(delay * 2)
    print(RESET)  # Reset color at the end
    
#typing_print(poem)

'''