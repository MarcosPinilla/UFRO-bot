# coding=utf8
from flask import Flask, request
import requests
import pprint
import httplib
import time
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

ACCESS_TOKEN ="Insert your access token" 
VERIFY_TOKEN = "Insert your verify token"

last = ""


#Method that prepares and send a message to the user
def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    
    #for logging purposes only
    #pprint.pprint(resp.content)

#Sets the response for verification on a GET method.
@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"

#Sets the messages listener on a POST method on the same route
@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json

    #Flag for preventing multiple requests from facebook
    global last

    #Uncomment next line for logging purposes
    #pprint.pprint(data)
    

    #Starts connection to another site to make a request
    c = httplib.HTTPSConnection("intranet.ufro.cl")
    day = str(int(time.strftime('%w')) )

    #This list will contain every response you want to make 
    ramos = []
    ramos.append("Horarios de Hoy "+ "\n")
    
    #saves requesting user data
    sender = data['entry'][0]['messaging'][0]['sender']['id']

    try:
        if(last!=data['entry'][0]['messaging'][0]['message']['seq']):
            last=data['entry'][0]['messaging'][0]['message']['seq']
            
            #Response for grateful message
            if("gracias" in str(data['entry'][0]['messaging'][0]['message']['text']).lower()):
                reply(sender, "Gracias a ti por usar Ufro BOT! :) ")
                return "ok"

            #Send usage instructions on a message that contains "Hola"
            if("hola" in str(data['entry'][0]['messaging'][0]['message']['text']).lower()):
                reply(sender, "Hola, para consultar tus horarios de hoy ingresa tu matrícula de la UFRO, recuerda que la matrícula se compone de tu rut más los últimos dos dígitos del año que ingresaste")
                reply(sender, "Mi rut es 13.337.801-9 y mi año de ingreso 2014, entonces tendría que enviar '13337801914'")
                reply(sender, "Inténtalo! Dame tu número de matrícula'")
                return "ok"

            #responses to love messages
            if("amo" in str(data['entry'][0]['messaging'][0]['message']['text']).lower()):
                reply(sender, "<3")
                return "ok"
            if("<3" in str(data['entry'][0]['messaging'][0]['message']['text']).lower()):
                reply(sender, "<3 <3")
                return "ok"


            #If it's an ID number, prepares and parse the desired URL to this particular case.
            #You must change this logic as needed.
            else:
                matricula = str(data['entry'][0]['messaging'][0]['message']['text'])
                print matricula
                if(len(matricula)>9):
                    for i in range(12):
                        #matricula = data['entry'][0]['messaging'][0]['message']['text']
                        c.request("GET", "/horario/horario_alumno_detalle2.php?matricula="+matricula+"&periodo="+str(i)+"&dia="+day+"&ano=2017&nro_semest=1&estado=N")
                        response = c.getresponse()
                        data = BeautifulSoup(response.read(), 'html.parser')
                        ramo = data.find_all("td")
                        if(len(ramo)>5):
                            actual=""
                            actual+= ramo[2].contents[0].encode("utf-8").strip() + " -> "
                            actual+= ramo[3].contents[0].encode("utf-8").strip() + "\n"
                            actual+= ramo[9].contents[0].encode("utf-8").strip() + "\n"
                            actual+= ramo[8].contents[0].encode("utf-8").strip() + "\n"
                            actual+= ramo[7].contents[0].encode("utf-8").strip() + "\n"
                            actual+="\n"
                            ramos.append(actual)
                    for msg in ramos:
                        reply(sender, msg)
                    return "ok"
                reply(sender, "Se produjo un error, recuerda escribir tu numero de matricula en el formato 18123456k12")
                return "failed"

            #End of Specific code


        else:
            return "ok"

    #Catch any exception ocurred
    except Exception as e:
        print e
        reply(sender, "Se produjo un error, recuerda escribir tu numero de matricula en el formato 18123456k12")
        return "fail"
    

#Start Flask
if __name__ == '__main__':
    app.run(debug=True)
