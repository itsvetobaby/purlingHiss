from openai import OpenAI

client = OpenAI()


def findClasses(div):
  prompt = f'''
  from the following html:

  {div}

    what class selector do i use to get product name, brand, price, seller (if applicable) and the href to the full page listing? Return them as  name:class, brand:class, price: class,seller: link, link: @href, parent: parent. return the parent of these so it can be targetted as a recursive element. Format your answer as a dictionary. Nothing else in the answer please.
  '''

  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {
              "role": "user",
              "content": prompt
          }
      ],
      max_tokens=300,
  )

  # Extract the content from the response
# Find the first '[' and return everything starting from that to the end
  content = response.choices[0].message.content.strip()
  return content