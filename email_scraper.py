from bs4 import BeautifulSoup  # Importa a classe BeautifulSoup do módulo bs4 para fazer o parsing do HTML
import requests  # Importa o módulo requests para fazer as requisições HTTP
import requests.exceptions  # Importa as exceções relacionadas a requisições no módulo requests
import urllib.parse  # Importa o módulo urllib.parse para fazer o parsing de URLs
from collections import deque  # Importa a classe deque do módulo collections para criar uma fila
import re  # Importa o módulo re para trabalhar com expressões regulares

user_url = str(input('[+] Enter Target URL To Scan: '))  # Solicita ao usuário que insira a URL alvo
urls = deque([user_url])  # Cria uma fila com a URL alvo como único elemento

scraped_urls = set()  # Cria um conjunto vazio para armazenar as URLs já processadas
emails = set()  # Cria um conjunto vazio para armazenar os emails encontrados

count = 0  # Inicializa uma variável de contagem
try:
    while len(urls):
        count += 1  # Incrementa a contagem a cada iteração
        if count == 100:  # Se já processou 100 URLs, para o loop
            break
        url = urls.popleft()  # Remove e retorna o primeiro elemento da fila
        scraped_urls.add(url)  # Adiciona a URL atual ao conjunto de URLs processadas

        parts = urllib.parse.urlsplit(url)  # Faz o parsing da URL para dividir em partes
        base_url = '{0.scheme}://{0.netloc}'.format(parts)  # Obtém o URL base (esquema + netloc)

        path = url[:url.rfind('/')+1] if '/' in parts.path else url  # Obtém o caminho da URL

        print('[%d] Processing %s' % (count, url))  # Imprime uma mensagem indicando o número de URL atual

        try:
            response = requests.get(url)  # Faz uma requisição HTTP GET para a URL atual
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):  # Lida com exceções de requisição
            continue  # Continua para a próxima iteração do loop se houver um erro

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))  # Encontra todos os emails na resposta HTTP usando uma expressão regular
        emails.update(new_emails)  # Adiciona os emails encontrados ao conjunto de emails

        soup = BeautifulSoup(response.text, features="lxml")  # Faz o parsing do conteúdo HTML usando a classe BeautifulSoup

        for anchor in soup.find_all("a"):  # Encontra todos os elementos 'a' (links) na página
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''  # Obtém o valor do atributo 'href' do elemento 'a' ou uma string vazia se não existir
            if link.startswith('/'):  # Se o link começa com '/', é relativo à URL base
                link = base_url + link  # Concatena o link com o URL base
            elif not link.startswith('http'):  # Se o link não começa com 'http', é relativo à URL atual
                link = path + link  # Concatena o link com o caminho da URL atual
            if not link in urls and not link in scraped_urls:  # Verifica se o link já foi processado ou está na fila
                urls.append(link)  # Adiciona o link à fila

except KeyboardInterrupt:  # Lida com a interrupção do usuário (Ctrl+C)
    print('[-] Closing!')

for mail in emails:  # Itera sobre os emails encontrados
    print(mail)  # Imprime cada email encontrado
