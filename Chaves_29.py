import speech_recognition as sr  # Biblioteca para reconhecimento de fala. Converte áudio captado pelo microfone em texto.
import paho.mqtt.client as mqtt  # Biblioteca para comunicação via MQTT, usada para publicar e subscrever mensagens entre dispositivos.
import time  # Biblioteca para manipulação de tempo, como criar delays e registrar timestamps.
import pygame  # Biblioteca para multimídia, como reprodução de áudio e manipulação de eventos relacionados a jogos.
import pyautogui  # Biblioteca para automação de GUI. Permite controlar o mouse, teclado e interagir com a tela.
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # Controle avançado de áudio no Windows, uso no volume
import pyttsx3  # Biblioteca para síntese de texto em fala (TTS). Permite que o programa "fale" mensagens em voz alta.
import openai  # Biblioteca para interação com os modelos da OpenAI, como ChatGPT. Usada para IA generativa.
import spotipy  # Biblioteca para integração com a API do Spotify. Permite controlar playlists, músicas e interagir com a conta do usuário.
from spotipy.oauth2 import SpotifyOAuth  # Submódulo do Spotipy para autenticação segura no Spotify usando o protocolo OAuth.
import os  # Biblioteca para manipulação do sistema operacional, como navegar por diretórios e gerenciar arquivos.
from datetime import datetime  # Módulo para trabalhar com data e hora, útil para registrar eventos ou criar timers.
import requests  # Biblioteca para realizar requisições HTTP, usada para interagir com APIs externas ou baixar dados da web.
import random  # Biblioteca para trabalhar com escolhas aleatórias
import webbrowser
from pytube import Search
from gtts import gTTS
import as_config as conf
import Chaves_Audios_lista as lista


audios_chaves = lista.audios_chaves_lista # Lista com os nomes dos arquivos de áudio

engine = pyttsx3.init() # Inicializa o engine de texto para fala

pygame.mixer.init() # Inicializa o mixer de áudio do pygame


# Configuração do MQTT
BROKER = conf.MQTT_BROKER  # Define o endereço IP do broker MQTT
PORT = conf.MQTT_PORT  # Define a porta de conexão com o broker MQTT
TOPIC = conf.MQTT_TOPIC  # Define o tópico para enviar os comandos

# Inicializa o cliente MQTT
client = mqtt.Client()  # Cria uma instância do cliente MQTT
client.connect(BROKER, PORT, 60)  # Conecta o cliente MQTT ao broker
client.publish(TOPIC, "39") # Inicia desligando dispositivos

recognizer = sr.Recognizer()  # Inicializa o reconhecedor de voz, cria uma instância dele

pygame.mixer.music.load("chaves_Bem_Vindo.wav")
pygame.mixer.music.play()
time.sleep(16)

# Inicialize o estado atual do led
estado_led = 0  # 0: desligado, 1: velocidade 1, 2: velocidade 2, 3: velocidade 3
def publicar_led(valor2, vezes2):
   
    for _ in range(vezes2):
        client.publish(TOPIC, valor2)
        time.sleep(2)  # Pequeno atraso para garantir que o ventilador registre os comandos

# Inicialize o estado atual do vapor
estado_vapor = 0  # 0: desligado, 1: velocidade 1, 2: velocidade 2, 3: velocidade 3
def publicar_vapor(valor1, vezes1):
    """
    Publica o comando no MQTT um número específico de vezes.
    """
    for _ in range(vezes1):
        client.publish(TOPIC, valor1)
        time.sleep(0.5)  # Pequeno atraso para garantir que o ventilador registre os comandos

# Inicialize o estado atual do ventilador como uma variável global
estado_atual = 0  # 0: desligado, 1: velocidade 1, 2: velocidade 2, 3: velocidade 3
def publicar_mqtt(valor, vezes):
    """
    Publica o comando no MQTT um número específico de vezes.
    """
    for _ in range(vezes):
        client.publish(TOPIC, valor)
        time.sleep(0.5)  # Pequeno atraso para garantir que o ventilador registre os comandos

def frases_chaves():
     # Escolhe um áudio aleatório da lista
    audio_escolhido = random.choice(audios_chaves)
    # Reproduz o áudio escolhido
    pygame.mixer.music.load(audio_escolhido)  # Carrega o arquivo MP3
    pygame.mixer.music.play()  # Reproduz o áudio
    while pygame.mixer.music.get_busy():  # Aguarda até que o áudio termine
        pygame.time.Clock().tick(10)
 
def climaTempo():

    # Defina a sua chave da API
    api_key = conf.api_key_open_weather

    # Inicializa o engine de TTS (Text to Speech)
    engine = pyttsx3.init()

    # Função para falar o texto (saída de áudio)
    def falar(texto):
        engine.say(texto)
        engine.runAndWait()

    # Função para obter o clima
    def obter_clima(cidade):
        # URL da API com parâmetros
        url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"

        # Fazendo a requisição à API
        resposta = requests.get(url)

        # Verificando se a resposta foi bem-sucedida
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Extraindo informações do clima
            nome_cidade = dados['name']
            temperatura = dados['main']['temp']
            descricao = dados['weather'][0]['description']
            umidade = dados['main']['humidity']
            
            # Preparando a resposta em texto
            client.publish(TOPIC, "23")
            texto_resposta = f"Clima em {nome_cidade}: Temperatura {temperatura}°C, {descricao}, Umidade {umidade}%."
            falar(texto_resposta)  # Fala a resposta
            print(texto_resposta)  # Imprime a resposta para o console
        else:
            erro_texto = "Cidade não encontrada ou erro na API."
            falar(erro_texto)
            print(erro_texto)

    # Função para ouvir a fala do usuário
    def ouvir_fala():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Fale o nome da cidade...")
            falar("Fale o nome da cidade...")
            client.publish(TOPIC, "22")
            
            r.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
            audio = r.listen(source)  # Escuta o que é falado
            try:
                cidade = r.recognize_google(audio, language='pt-BR')  # Reconhece o que foi falado
                print(f"Você disse: {cidade}")
                return cidade
            except sr.UnknownValueError:
                falar("Não consegui entender. Tente novamente.")
                return None
            except sr.RequestError:
                falar("Erro na solicitação. Verifique sua conexão com a internet.")
                return None

    # Execução principal
    cidade = ouvir_fala()
    if cidade:
        obter_clima(cidade)

def dia ():
    # Obtém a data e a hora atual
    data_hora = datetime.now().strftime("%d/%m/%Y, são %H horas e %M minutos")
    
    # Formata a resposta
    client.publish(TOPIC, "23")
    resposta = f"Hoje é dia {data_hora}"
    
    # Inicializa o mecanismo de fala
    engine = pyttsx3.init()
    
    # Fala a resposta
    engine.say(resposta)
    engine.runAndWait()
    
    # Retorna a resposta para impressão no console
    return resposta

def spotipy_playlist():
    import os
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    import speech_recognition as sr

    # Credenciais do Spotify Developer
    CLIENT_ID = conf.CLIENT_ID_spotify
    CLIENT_SECRET = conf.CLIENT_SECRET_spotify
    REDIRECT_URI = conf.REDIRECT_URI_spotify

    # Deletar o arquivo de cache (se existir) para forçar uma nova autenticação caso necessário
    if os.path.exists(".cache"):
        os.remove(".cache")

    # Autenticação com o Spotify (usando o cache para evitar a URL de autenticação)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                    client_secret=CLIENT_SECRET,
                                                    redirect_uri=REDIRECT_URI,
                                                    scope=conf.scope_spotify,
                                                    cache_path=".cache"))

    # Função para capturar entrada por voz
    def capturar_voz():
        client.publish(TOPIC, "22")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Diga o nome da música que você quer tocar:")
            try:
                audio = recognizer.listen(source)
                termo = recognizer.recognize_google(audio, language='pt-BR')
                print(f"Você disse: {termo}")
                return termo
            except sr.UnknownValueError:
                client.publish(TOPIC, "5")
                print("Desculpe, não entendi. Tente novamente.")
                return None
            except sr.RequestError as e:
                print(f"Erro no serviço de reconhecimento de voz: {e}")
                return None

    # Função para buscar música no Spotify
    def buscar_musica(termo):
        resultados = sp.search(q=termo, limit=1, type='track')
        if resultados['tracks']['items']:
            track = resultados['tracks']['items'][0]
            print(f"Música encontrada: {track['name']} - {track['artists'][0]['name']}")
            return track
        else:
            print("Música não encontrada.")
            return None

    # Função para buscar playlists relacionadas a uma música
    def buscar_playlist_da_musica(track_id):
        # Obtém informações detalhadas sobre a música
        track_info = sp.track(track_id)
        if track_info and 'album' in track_info:
            album_id = track_info['album']['id']
            album_tracks = sp.album_tracks(album_id)
            print(f"Playlist encontrada: {track_info['album']['name']}")
            return album_tracks['items']
        return None

    # Função para tocar a playlist
    def tocar_playlist(playlist_tracks, dispositivo_id):
        uris = [track['uri'] for track in playlist_tracks]
        if uris:
            try:
                sp.start_playback(device_id=dispositivo_id, uris=uris)
                print("Playlist tocando!")
                return True
            except spotipy.exceptions.SpotifyException as e:
                print(f"Erro ao tentar tocar a playlist: {e}")
        return False

    # Função para verificar os dispositivos conectados
    def verificar_dispositivos():
        dispositivos = sp.devices()
        if dispositivos['devices']:
            print("Dispositivos conectados ao Spotify:")
            for dispositivo in dispositivos['devices']:
                print(f"{dispositivo['name']} - {'Ativo' if dispositivo['is_active'] else 'Inativo'}")
            return dispositivos['devices']
        else:
            print("Nenhum dispositivo conectado.")
            return []

    # Exemplo de uso
    termo = capturar_voz()
    if termo:
        track = buscar_musica(termo)
        if track:
            dispositivos = verificar_dispositivos()
            if dispositivos:
                dispositivo = dispositivos[0]  # Seleciona o primeiro dispositivo ativo
                playlist_tracks = buscar_playlist_da_musica(track['id'])
                if playlist_tracks:
                    tocar_playlist(playlist_tracks, dispositivo['id'])

def spotipy_musica():

    # Credenciais do Spotify Developer
    CLIENT_ID = conf.CLIENT_ID_spotify
    CLIENT_SECRET = conf.CLIENT_SECRET_spotify
    REDIRECT_URI = conf.REDIRECT_URI_spotify

    # Deletar o arquivo de cache (se existir) para forçar uma nova autenticação caso necessário
    if os.path.exists(".cache"):
        os.remove(".cache")

    # Autenticação com o Spotify (usando o cache para evitar a URL de autenticação)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                    client_secret=CLIENT_SECRET,
                                                    redirect_uri=REDIRECT_URI,
                                                    scope=conf.scope_spotify,
                                                    cache_path=".cache"))  # Usando cache para armazenar o token de acesso


    # Função para capturar entrada por voz
    def capturar_voz():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Diga o nome da música que você quer tocar:")
            try:
                audio = recognizer.listen(source)
                termo = recognizer.recognize_google(audio, language='pt-BR')  # Reconhece a fala em português
                print(f"Você disse: {termo}")
                return termo
            except sr.UnknownValueError:
                print("Desculpe, não entendi. Tente novamente.")
                return None
            except sr.RequestError as e:
                print(f"Erro no serviço de reconhecimento de voz: {e}")
                return None


    # Função para buscar música no Spotify
    def buscar_musica(termo):
        resultados = sp.search(q=termo, limit=1, type='track')  # Realiza a busca por músicas
        if resultados['tracks']['items']:
            track = resultados['tracks']['items'][0]
            print(f"Tocando: {track['name']} - {track['artists'][0]['name']}")
            return track
        else:
            print("Música não encontrada.")
            return None


    # Função para verificar os dispositivos conectados
    def verificar_dispositivos():
        dispositivos = sp.devices()
        if dispositivos['devices']:
            print("Dispositivos conectados ao Spotify:")
            for dispositivo in dispositivos['devices']:
                print(f"{dispositivo['name']} - {'Ativo' if dispositivo['is_active'] else 'Inativo'}")
            return dispositivos['devices']
        else:
            print("Nenhum dispositivo conectado.")
            return []


    # Função para verificar o status da reprodução
    def verificar_status_reproducao():
        status = sp.current_playback()  # Mudança para current_playback() em vez de playback_state()
        if status and status['is_playing']:
            print("A música está tocando!")
        else:
            print("A música não está tocando.")
        return status and status['is_playing']


    # Função para tocar a música no dispositivo "PENSADOR" (Notebook)
    def tocar_musica(track):
        dispositivos = verificar_dispositivos()

        # Verifica se o dispositivo "PENSADOR" está ativo
        for dispositivo in dispositivos:
            if dispositivo['name'] == "PENSADOR" and dispositivo['is_active']:
                print(f"Tocando no dispositivo: {dispositivo['name']}")
                try:
                    sp.start_playback(device_id=dispositivo['id'], uris=[track['uri']])  # Toca a música no dispositivo ativo
                    return True
                except spotipy.exceptions.SpotifyException as e:
                    print(f"Erro ao tentar tocar no dispositivo {dispositivo['name']}: {e}")
                    continue

        print("Dispositivo 'PENSADOR' não está ativo ou não encontrado.")
        return False


    # Exemplo de uso
    termo = capturar_voz()
    if termo:
        track = buscar_musica(termo)
        if track:
            tocar_musica(track)

def parar_spotipy():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=conf.CLIENT_ID_spotify ,
            client_secret=conf.CLIENT_SECRET_spotify,
            redirect_uri= conf.REDIRECT_URI_spotify,
            scope=conf.scope_spotify
    ))
    print("entrou")
    try:
        # Obtém o estado atual da reprodução
        status = sp.current_playback()
        
        if status and status['is_playing']:
            sp.pause_playback()  # Pausa a reprodução
            print("Música pausada com sucesso.")
        else:
            print("Nenhuma música está tocando no momento.")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Erro ao tentar pausar a música: {e}")
    
def proximaMusica_spotify():
    # Configure o Spotify API
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="SEU_CLIENT_ID",
    client_secret="SEU_CLIENT_SECRET",
    redirect_uri="http://localhost:8080",
    scope="user-modify-playback-state"
))
    try:
        sp.next_track()
        print("Música pulada para a próxima.")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Erro ao pular música: {e}")    

def reconnect_mqtt(client):
    """Verifica a conexão MQTT e tenta reconectar caso esteja desconectado."""
    if not client.is_connected():
        client.publish(TOPIC, "23")  # Comando Liga Sala
        print("MQTT desconectado. Tentando reconectar...")
        try:
            client.reconnect()
            print("Reconexão bem-sucedida!")
        except Exception as e:
            print(f"Falha ao reconectar: {e}")

def youtube():
   

    def ouvir_audio():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Estou ouvindo... Fale o nome da música.")
            try:
                audio = recognizer.listen(source, timeout=10)
                termo = recognizer.recognize_google(audio, language="pt-BR")
                print(f"Você disse: {termo}")
                return termo
            except sr.UnknownValueError:
                print("Desculpe, não entendi. Tente novamente.")
                return ""
            except sr.RequestError as e:
                print(f"Erro no serviço de reconhecimento: {e}")
                return ""

    def abrir_no_navegador(termo):
        # Pesquisar o vídeo no YouTube
        print(f"Pesquisando por: {termo}")
        resultados = Search(termo).results

        if not resultados:
            print("Nenhum resultado encontrado!")
            return False

        # Obter o primeiro resultado
        video_url = resultados[0].watch_url
        print(f"Abrindo o vídeo: {video_url}")

        # Abrir no navegador
        webbrowser.open(video_url)
        return True
    

    def main():
        termo = ouvir_audio()  # Obtém o termo da busca por voz

        if not termo:
            print("Nenhuma música foi reconhecida.")
            return

        sucesso = abrir_no_navegador(termo)

        if not sucesso:
            print("Não foi possível abrir o vídeo. Tente novamente.")

    main()

def parar_musica():
    # Envia o atalho de teclado para fechar a aba atual (Ctrl + W)
    pyautogui.hotkey("ctrl", "w")
    print("Aba fechada com sucesso!")
    client.publish(TOPIC, "5")  # 

def ajustar_volume(nivel):
    """Ajusta o volume com base no nível especificado (0 a 10)."""
    volume_level = nivel  # Define o nível de volume
    def set_volume(volume_level):
        volume = volume_level / 10.0  # Mapeia o volume para a escala de 0.0 a 1.0
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
        volume_interface = interface.QueryInterface(IAudioEndpointVolume)
        volume_interface.SetMasterVolumeLevelScalar(volume, None)  # Ajusta o volume
    set_volume(volume_level)  # Chama a função passando o nível como argumento
    client.publish(TOPIC, 5)  # Publica o nível no tópico MQTT
    
def gpt():
    openai.api_key = conf.openai_chave_api  # Configuração da chave da API OpenAI 
    sintetizador = pyttsx3.init() # Inicialização do sintetizador de voz
    vozes = sintetizador.getProperty("voices") # Listar e selecionar a voz desejada
    for index, voz in enumerate(vozes):
        print(f"{index}: {voz.name} ({voz.languages})")

    indice_voz = 0  # Altere o índice para escolher a voz desejada
    sintetizador.setProperty("voice", vozes[indice_voz].id)

    # Configurar velocidade e volume da voz
    sintetizador.setProperty("rate", 180)  # Velocidade da fala
    sintetizador.setProperty("volume", 1)  # Volume (0.0 a 1.0)

    # Função para capturar áudio do usuário
    def ouvir_audio():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Estou ouvindo...")
            client.publish(TOPIC, "22")
            try:
                audio = recognizer.listen(source, timeout=5)
                texto = recognizer.recognize_google(audio, language="pt-BR")
                print(f"Você disse: {texto}")
                return texto
            except sr.UnknownValueError:
                print("Desculpe, não entendi. Tente novamente.")
            except sr.RequestError:
                print("Erro ao conectar ao serviço de reconhecimento de fala.")
        return ""
    

    # Função para gerar resposta do chatbot
    def enviar_mensagem(mensagem, lista_mensagens=[]):
        lista_mensagens.append({"role": "user", "content": mensagem})
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=lista_mensagens,
        )
        client.publish(TOPIC, "23")
        return resposta["choices"][0]["message"]

    # Função para falar o texto
    def falar_texto(texto):
        sintetizador.say(texto)
        sintetizador.runAndWait()
        

    # Loop de conversa
    if __name__ == "__main__":
        lista_mensagens = []
        print("Bem-vindo ao Chatbot com entrada e saída de voz!")
        pygame.mixer.music.load("chaves_pesquisar.wav")
        pygame.mixer.music.play()
        time.sleep(3)
        
        '''Caso queira colocar o chat em looping'''
        while True:
            try:
                # Publica a mensagem inicial no tópico
                client.publish(TOPIC, "24")
                
                # Ouve o áudio do usuário
                texto_usuario = ouvir_audio()
                
                # Verifica se o usuário quer sair
                if texto_usuario.lower() in ["sair da pesquisa", "encerrar pesquisa", "chaves"]:
                    falar_texto("Encerrando a pesquisa.")
                    client.publish(TOPIC, "25")
                    break
                
                # Processa o texto do usuário, envia a mensagem e responde
                if texto_usuario:
                    resposta = enviar_mensagem(texto_usuario, lista_mensagens)
                    lista_mensagens.append(resposta)
                    print("Chatbot:", resposta["content"])
                    falar_texto(resposta["content"])
            
            except Exception as e:
                # Exibe uma mensagem de erro e tenta novamente
                client.publish(TOPIC, "23")
                print(f"Erro: {e}. Tentando novamente...")
                time.sleep(2)

# Publica a mensagem final ao sair do loop
client.publish(TOPIC, "23")
    
def ouvir_comando():
    """Função para escutar um comando de voz."""
    with sr.Microphone() as source:  # Utiliza o microfone como fonte de áudio
        client.publish(TOPIC, "23")
        print("Ajustando para ruído de fundo...")  # Ajusta o reconhecimento para o ruído ambiente
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta o filtro para o ruído de fundo
        client.publish(TOPIC, "22")
        print("Pronto. Fale algo:")  # Solicita ao usuário para falar
        
        try:
            audio = recognizer.listen(source, timeout=20)  # Escuta o comando de voz, com timeout de 20 segundos
            comando = recognizer.recognize_google(audio, language="pt-BR")  # Converte o áudio em texto
            return comando.lower()  # Retorna o comando em minúsculo
        except sr.WaitTimeoutError:  # Captura erro se o tempo de espera para escutar for excedido
            print("Tempo limite de escuta excedido.")  # Imprime erro de timeout
            return ""  # Retorna string vazia
        except sr.UnknownValueError:  # Captura erro se o comando não for reconhecido
            print("Não entendi o que você disse.")  # Imprime erro de comando incompreendido
            client.publish(TOPIC, "16")
            return ""  # Retorna string vazia
        except sr.RequestError as e:  # Captura erro de requisição com o serviço de reconhecimento
            print(f"Erro no serviço: {e}")  # Imprime erro no serviço
            return ""  # Retorna string vazia

def processar_comando(comando): # Chama ás funções de acordo com o esperado
    global chaves_ativa  # Referência à variável global
    
    reconnect_mqtt(client)
    
    if comando == "chaves":  # Se o comando for "chaves"
        client.publish(TOPIC, "35")
        pygame.mixer.music.load("chaves-isso-isso-isso.mp3") 
        pygame.mixer.music.play()  
        while pygame.mixer.music.get_busy():  # Aguarda até que o áudio termine
            pygame.time.Clock().tick(10)
        client.publish(TOPIC, "22")
        chaves_ativa = True  # Marca que "chaves" foi ativado
        return  # Retorna, sem processar mais comandos após ativar "chaves"

    if not chaves_ativa:  # Verifica se "chaves" foi ativado
        client.publish(TOPIC, "33") #Pisca led vermelho caso o primeiro comando nao seja chaves
        return  # Não processa o comando, se "chaves" não estiver ativo
     
    # Comandos que só serão processados após "chaves"
    elif comando == "ligar cozinha":  # Se o comando for "ligar cozinha"
        client.publish(TOPIC, "1")  # Envia comando MQTT para ligar a lâmpada
        frases_chaves()
        chaves_ativa = False
        client.publish(TOPIC, "34")
        
    elif comando == "desligar cozinha":  # Se o comando for "desligar cozinha"
        client.publish(TOPIC, "0")  # Envia comando MQTT para desligar a lâmpada
        frases_chaves()
        chaves_ativa = False
        client.publish(TOPIC, "33")
        
        
    elif comando == "ligar sala":  # 
        client.publish(TOPIC, "2")  # Comando Liga Sala
        frases_chaves()
        chaves_ativa = False
        client.publish(TOPIC, "34")
        
    elif comando == "desligar sala":  # Se o comando for "desligar sala"
        client.publish(TOPIC, "3")  # Envia comando MQTT para desligar a lâmpada
        frases_chaves()
        chaves_ativa = False
        client.publish(TOPIC, "33")

    elif comando == "ligar tudo":  
        client.publish(TOPIC, "2")  # Comando Liga sala
        time.sleep(0.5)
        client.publish(TOPIC, "1")  # Comando liga cozinha
        frases_chaves()
        chaves_ativa = False
        client.publish(TOPIC, "34")

    elif comando == "desligar tudo":  # Se o comando for "desligar tudo"
        frases_chaves()
        client.publish(TOPIC, "3")  # Envia comando MQTT para desligar a lâmpada
        time.sleep(0.5)
        client.publish(TOPIC, "0")  # Envia comando MQTT para desligar a lâmpada
        chaves_ativa = False
        client.publish(TOPIC, "33")

    elif comando == "pesquisar":  # Se o comando for "seu madruga pesquisar"
        client.publish(TOPIC, "36")
        gpt()  # Chama a função
        chaves_ativa = False
        
    elif comando == "youtube":  
        pygame.mixer.music.load("youtube.wav")
        pygame.mixer.music.play()
        time.sleep(5)
        youtube()  # Chama a função youtube
        chaves_ativa = False
         
    elif comando == "parar youtube" :  # Se o comando for "parar música"
        frases_chaves()
        parar_musica()  # Chama a função parar_musica
        chaves_ativa = False

    elif comando.startswith("volume "):  # Verifica se o comando começa com "volume "
        nivel_str = comando.split(" ")[1]  # Extrai o número do volume
        if nivel_str.isdigit():  # Verifica se é um número válido
            nivel = int(nivel_str)
            if 0 <= nivel <= 10:  # Garante que o número está no intervalo válido
                frases_chaves()
                ajustar_volume(nivel)  # Ajusta o volume
                chaves_ativa = False
    
    elif comando == "música":  # Se o comando for "parar música"
        pygame.mixer.music.load("chaves_fale_o_nome_da_musica.wav")
        pygame.mixer.music.play()
        time.sleep(3)
        client.publish(TOPIC, "37")
        spotipy_musica()  # Chama a função
        chaves_ativa = False   
    
    elif comando == "playlist":  # Se o comando for "parar música"
        client.publish(TOPIC, "37")
        pygame.mixer.music.load("playlist.wav")
        pygame.mixer.music.play()
        time.sleep(5)
        spotipy_playlist()  # Chama a função parar_musica
        chaves_ativa = False   
    
    elif comando == "desligar música" :  # Se o comando for "parar música"
        frases_chaves()
        parar_spotipy() # chama a função
        client.publish(TOPIC, "23")  # desliga led azul
        chaves_ativa = False   
   
    elif comando == "próxima":  # Se o comando for "parar música"
        client.publish(TOPIC, "10")
        proximaMusica_spotify()  # Chama a função parar_musica
        chaves_ativa = False   
    
    elif comando == "data hora":  # Se o comando for "parar música"
        frases_chaves()
        client.publish(TOPIC, "5")
        dia()  # Chama a função
        chaves_ativa = False   
    
    elif comando == "clima e tempo":  # Se o comando for "clima e tempo"
        frases_chaves()
        client.publish(TOPIC, "23")
        climaTempo()  # Chama a função
        chaves_ativa = False            
  
    elif comando == "ventilador 1":
        global estado_atual  # Declare que está usando a variável global
        frases_chaves()
        if estado_atual != 1:  # Só realiza ações se o estado for diferente do atual
            pulsos = (1 - estado_atual) % 4  # Calcula os pulsos necessários para chegar à velocidade 1
            publicar_mqtt("40", pulsos)
            estado_atual = 1  # Atualiza o estado atual
        chaves_ativa = False

    elif comando == "ventilador 2":
        #global estado_atual  # Declare que está usando a variável global
        frases_chaves()
        if estado_atual != 2:  # Só realiza ações se o estado for diferente do atual
            pulsos = (2 - estado_atual) % 4  # Calcula os pulsos necessários para chegar à velocidade 2
            publicar_mqtt("40", pulsos)
            estado_atual = 2  # Atualiza o estado atual
        chaves_ativa = False

    elif comando == "ventilador 3":
        #global estado_atual  # Declare que está usando a variável global
        frases_chaves()
        if estado_atual != 3:  # Só realiza ações se o estado for diferente do atual
            pulsos = (3 - estado_atual) % 4  # Calcula os pulsos necessários para chegar à velocidade 3
            publicar_mqtt("40", pulsos)
            estado_atual = 3  # Atualiza o estado atual
        chaves_ativa = False

    elif comando == "ventilador desligar":
        #global estado_atual  # Declare que está usando a variável global
        frases_chaves()
        if estado_atual != 0:  # Só realiza ações se o estado for diferente do atual
            pulsos = (0 - estado_atual) % 4  # Calcula os pulsos necessários para desligar
            publicar_mqtt("40", pulsos)
            estado_atual = 0  # Atualiza o estado atual
        chaves_ativa = False
        
    elif comando == "vapor 1":
        global estado_vapor
        frases_chaves()
        if estado_vapor != 1:  # Só realiza ações se o estado for diferente do atual
            pulsos = (1 - estado_vapor) % 4  # Calcula os pulsos necessários para chegar à velocidade 1
            publicar_vapor("50", pulsos)
            estado_vapor = 1  # Atualiza o estado atual
        chaves_ativa = False

    elif comando == "vapor 2":
        frases_chaves()
        if estado_vapor != 2:  # Só realiza ações se o estado for diferente do atual
            pulsos = (2 - estado_vapor) % 4  # Calcula os pulsos necessários para chegar à velocidade 2
            publicar_vapor("50", pulsos)
            estado_vapor = 2  # Atualiza o estado atual
        chaves_ativa = False

    elif comando == "vapor 3":
        frases_chaves()
        if estado_vapor != 3:  # Só realiza ações se o estado for diferente do atual
            pulsos = (3 - estado_vapor) % 4  # Calcula os pulsos necessários para chegar à velocidade 3
            publicar_vapor("50", pulsos)
            estado_vapor = 3  # Atualiza o estado atual
        chaves_ativa = False

    elif comando == "vapor desligar":
        frases_chaves()
        if estado_vapor != 0:  # Só realiza ações se o estado for diferente do atual
            pulsos = (0 - estado_vapor) % 4  # Calcula os pulsos necessários para desligar
            publicar_vapor("50", pulsos)
            estado_vapor = 0  # Atualiza o estado atual
        chaves_ativa = False
   
    elif comando == "led azul":
        global estado_led
        frases_chaves()
        if estado_led != 1:  
            pulsos = (1 - estado_led) % 4  
            publicar_led("60", pulsos)
            estado_led = 1  
        chaves_ativa = False
        
    elif comando == "led verde":
        frases_chaves()
        if estado_led != 2:  
            pulsos = (2 - estado_led) % 4  
            publicar_led("60", pulsos)
            estado_led = 2  
        chaves_ativa = False

        
    elif comando == "led vermelho":
        frases_chaves()
        if estado_led != 3:  
            pulsos = (3 - estado_led) % 4  
            publicar_led("60", pulsos)
            estado_led = 3  
        chaves_ativa = False

        
    elif comando == "led roxo":
        frases_chaves()
        if estado_led != 5:  
            pulsos = (5 - estado_led) % 4  
            publicar_led("60", pulsos)
            estado_led = 5  
        chaves_ativa = False
        

    elif comando == "led desligar":
        
        frases_chaves()
        if estado_led != 8:  
            pulsos = (8 - estado_led) % 4  
            publicar_led("60", pulsos)
            estado_led = 8  
        chaves_ativa = False
   
    else:
        pygame.mixer.music.load("chaves_comando_nao_reconhecido.wav")
        pygame.mixer.music.play()
        time.sleep(5)
               
chaves_ativa = False # Variável global que controla se o comando "chaves" foi ativado

while True:  # Loop infinito para escutar os comandos continuamente,
    try:
        comando = ouvir_comando()  # Chama a função para ouvir o comando
        if comando:  # Se um comando for reconhecido
            processar_comando(comando)  # Processa o comando
    except:
        print("ocorreu um erro")
   