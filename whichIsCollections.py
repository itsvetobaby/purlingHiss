from openai import OpenAI

client = OpenAI()


def findCollectionsURLs(siteURLs):
  urls_string = "\n".join(siteURLs)

  prompt = f'''
  Out of the following:

  {urls_string}

  which url signals collection page? It should look something like this, https://www.sportsdirect.com/mens/footwear/trainers. Dont allow gender or kids pages. ideally the more deep the params in the url the better. mens/footwear/trainers is better than mens/footwear/ .Return your answer as an array of answers. the answer cannot contain the word product or products in it.  item.url, curly bracket syntax is not allowed either. Nothing else in the answer please.
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
  start_index = content.find('[')
  if start_index != -1:
      return content[start_index:]
  else:
      return 'ANSWER REVEICED, HOWEVER IT BREACHES ARRAY FORMAT'  # or handle the case where the array isn't found as you prefer