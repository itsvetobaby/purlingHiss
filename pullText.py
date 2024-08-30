from openai import OpenAI
import time

client = OpenAI()

def pullFirstListing(imageURL):
  #wait 3 seconds
  time.sleep(5)
  print(imageURL, ' text pull file')
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Whats the name of the first product listing in this photo? Give it to me as one string. Nothing more."},
          {
            "type": "image_url",
            "image_url": {
              "url": imageURL,
            },
          },
        ],
      }
    ],
    max_tokens=300,
  )

  return (response.choices[0].message.content)
