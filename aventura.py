"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os
import time
import configparser

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
load_dotenv()

config = configparser.ConfigParser()
config.read("config.ini")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 10000,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  safety_settings={
	HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
	HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
	HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
  }
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)
def create_session(personagem = None):
	chat_session = model.start_chat(
		history=[]
	)
	aventura(chat_session,personagem)
	return chat_session

def print_com_delay(string):
	for char in string:
		print(char, end='', flush=True)
		time.sleep(.015)
	print("\n")

def aventura_historia_opcoes(historia):
	if historia.find("FIM.") != -1:
		print(historia[:historia.find("FIM.") + 4], "\n")
		return
	opcoes = historia.split("|")
	print_com_delay(opcoes[0])
	i = 1
	while i < 6:
		print(opcoes[i].strip())
		i += 1
	user_input = input("Opcoes:\n[1] [2] [3]\n[0] Sair\n  -- ")
	if user_input == "1":
		return opcoes[1]
	if user_input == "2":
		return opcoes[3]
	if user_input == "3":
		return opcoes[5]
	if user_input == "0":
		return

def aventura(chat_session,personagem):
	historia_instrucao = "No final, me dê três opções de ação numeradas de 1 a 3. *IMPORTANTE*: Esta aventura precisa acabar em 5 ações e, quando acabar, NÃO ofereça mais opções de continuação ao jogador e escreva: 'FIM.'."
	historia = chat_session.send_message(f'Inicie uma aventura rpg como se fosse um mestre. O meu personagem se chama {personagem._nome}, \
										  sua classe é {personagem._classe} \
												  {historia_instrucao} \n Formatação das escolhas:\n---\n\nEscolha uma ação:\n\n|1. Seguir o caminho pela floresta.|\n|2. Explorar o rio.|\n|3. Investigar a cabana.|\n---').text
	

											#   sua raça é {personagem._raca}. \

										#    seu genero é {personagem._genero}, \