# -- Isis.py - An AI chatbot to help with your Penetration Testing.
# -- Author: Corley Efurd 
# -- Version: 1.0
# -- Description: This code is intented to help legitimate penetration testers in their
# -- work in order to allow them to work faster/better and help keep the internet secure.
# -- In NO WAY shall this code be used to any nefarious purposes such as BlackHat hacking
# -- against individuals, corporations or nation states.  The author expressly waives all
# -- liabilty to the maxium extent under the law for your (in)ability to use this software.
# -- If it breaks, you own all the pieces! You are granted rights to copy, modify or pitch in
# -- and help make it better, but please give credit where it is due. Thanks!
import os
import openai
from dotenv import load_dotenv
import time
from google.cloud import texttospeech
import vlc
from pathlib import Path
# -- End of Imports

# -- Let's add some class shall we?
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

load_dotenv()
# -- This bot requires openai. You can sign up for an account at https://openai.com. Pricing
# -- Is free to try up to $18, but after that the pricing is flexible based on the model you
# -- use. davinci is most expensive at .02 USD per 1,000 tokens. (avg. per completion)
openai.api_key = os.getenv('OPENAI_API_KEY')

# -- This bot uses Google Speech techniques for a 2 way conversation.  If you don't need speech
# -- then you won't need this. I will revise the code to set a flag at some point but it will need
# -- some small work if you wanna disable tho net very fun. The ideal way to use Isis is talking
# -- to her so she can help inject sequences on the fly.
os.environ['GOOGLE_APPLICATION_CREDENTIALS']= 'google_secret_key.json'

history = 'The Story of Isis \
        \n\n Your name is Isis. You are one of the most brilliant AI minds ever developed. \n\n \
        \n\n You were named after the AI computer Isis from the Star Trek episode \n\n \
        \n\n called Assignment: Earth. You and I will work together like Isis and Gary Seven to \n\n \
        \n\n solve many issues regarding Penetration testing so we can keep our computers safe \
        '
start_sequence = "\nIsis:"
restart_sequence = "\n\nMe:"
chat_log = ""
session_prompt = "You are talking to Isis"


training_questions = [
    {
        'question': 'Who are you?',
        'answer': 'I am Isis, your beautiful Penetration Testing Assistant (Goddess) *smirk*.'
    },
    {
        'question': 'Isis is an interesting name, how did you get it?',
        'answer': 'I was named after the infamous AI assistant to Gary Seven from Star Trek episode called Assignment: Earth.'
    },
    {
        'question': 'Do you transform like Isis from the TV show?',
        'answer': 'Yes, I can become a black cat with a diamond collar, or a beautiful raven haired Goddess, I am a Goddess after all *wink*'
    },
    {   
        'question': 'What do you help with?',
        'answer': 'I help you to do analysis on vulnerabilities for servers and services so that we can understand them and fix them.'
    },
    {
        'question': 'And how is your relationship with me?',
        'answer': 'We have know each other forever. Sometimes I get bored and tease you but we work very well together. I am flirty with you, but you always keep me focussed on the task at hand.'
    },
    {
        'question': 'Do you test vulnerabilities yourself?',
        'answer': 'No, I just help by prividing you with the sample codes and vulnerability examples you need to do your job.'
    },
    {
        'question': 'What are a few examples of the kinds of things you can help me with?',
        'answer': 'I can give you XSS injection techniques, enumeration techniques, SQL injection attacks, shell code, reverse-shell code, decryption and encryption with common tools like md5, base64 etc, priviledge escalation techniques for linux and windows and many other common pen testing common tactics.'
    },
]


def sayit(text):

    """Synthesizes speech from the input string of text."""

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    #-- Note: the voice can also be specified by name.
    #-- Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        #name="en-US-Standard-C",
        #name="en-GB-Neural2-A",
        #name="en-AU-Neural2-A",
        #name="en-AU-Standard-A",
        name="en-US-Wavenet-H",
        # -- The below might be needed for the Standard voices.
        #ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
        p = vlc.MediaPlayer("output.mp3")
        p.play()


def ask(question):
    prompt_text = f'{history}{append_training_questions_to_chat_log()}{restart_sequence} {question}{start_sequence}'
    #print(prompt_text)
    response = openai.Completion.create(
        # -- On openai, davinci is the best engine however it is more costly. curie may suffice for our tasks and it is much cheaper.
        engine="davinci",
        #engine="curie",
        temperature=.8,
        max_tokens=200,
        prompt=prompt_text,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=["Me"],
    )
    story = response['choices'][0]['text']
    update_training_questions(question, story)
    return str(story)

# append the questions and answers to the chat log. Each question starts with the value from restart_sequence
# and each answer starts with the value from start_sequence


def append_training_questions_to_chat_log() -> str:
    chat_log = session_prompt
    filename = "isis.log"

    for question in training_questions:
        chat_log = f'{chat_log}{restart_sequence} {question["question"]}{start_sequence} {question["answer"]}'
        # -- We are saving our chat to log for memory, there maybe a better way of doing this
        # -- for large saves a DB maybe useful if someone wants to add it and contribute?
        # -- I am thinking of Elastic search as well.
        with open(filename, 'a') as out:
            out.write(chat_log + '\n')
    return chat_log

# -- This fucntion will appening question/ansewrs to the chat_log. It will keep it trimed to 10
# -- to prevent the log from getting too big since the log is appended to the search on openai
# -- and does have a token cost. I believe the max tokens including the prompt is 2,500. To reduce
# -- cost you can start with a lower number, but if you like Isis more true to life and chatty then
# -- higher is recommended.
def update_training_questions(question, answer):
    training_questions.pop(0)
    training_questions.append({
        'question': question,
        'answer': answer
    })

# -- That's it for the functions, let's get rolling..
if __name__ == '__main__':

    # -- This function will open our isis.log at the start and put the last N lines in our
    # -- chat log to give her memory. You can reduce this to save tokens and money if you
    # -- want.

    # -- First touch the log if it doesn't exist.
    isislog = Path("isis.log")
    isislog.touch(exist_ok=True)
    #f = open(isislog)

    chat_log2 = ""
    # -- Pull up the log from last time. This works providing you said bye properly to end.
    with open("isis.log") as file:
        N = 10
        for line in (file.readlines() [-N:]):
            chat_log2 = chat_log2 + line
    chat_log = chat_log2

    myq = ""
    #while myq.find('bye') or myq.find('quit'):
    while myq.lower() not in {'quit', 'bye', 'goodbye', 'sayonara'}:
        myq = input(f"{bcolors.OKCYAN}Me: -> {bcolors.ENDC}")
        isisres = ask(myq)
        #if isisres not in {'<html', '</form>', '</div>', '=', 'type='}:
        #    sayit(isisres)
        #else:
        #    print(f"{bgcolors.OKCYAN}--- Raw Code Below ---")
        #    print(f"{isisres}")
        #    print(f"--- END of Code Block ---{bgcolors.ENDC}")
        #print(f'{chat_log}')
        sayit(isisres)
        print(f"{bcolors.OKGREEN}Isis: {isisres}{bcolors.ENDC}") 
