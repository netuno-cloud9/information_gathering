from bs4 import BeautifulSoup  # Importa a biblioteca BeautifulSoup para fazer o parsing do HTML
import requests  # Importa a biblioteca requests para fazer requisições HTTP
import requests.exceptions  # Importa as exceções do módulo requests
import urllib.parse  # Importa o módulo urllib.parse para fazer o parse das URLs
from collections import deque  # Importa a classe deque para criar uma fila
import re  # Importa o módulo re para trabalhar com expressões regulares
import tkinter as tk  # Importa a biblioteca tkinter para criar a interface gráfica
from tkinter import scrolledtext  # Importa o widget scrolledtext do tkinter

user_url = str(input('[+] Enter Target URL To Scan: '))  # Solicita ao usuário a URL a ser verificada
urls = deque([user_url])  # Cria uma fila com a URL informada

scraped_urls = set()  # Cria um conjunto vazio para armazenar as URLs já analisadas
emails = set()  # Cria um conjunto vazio para armazenar os emails encontrados

count = 0  # Inicializa o contador
try:
    while len(urls):  # Executa o loop enquanto houver URLs na fila
        count += 1  # Incrementa o contador
        if count == 100:  # Interrompe o loop quando atingir 100 iterações
            break
        url = urls.popleft()  # Remove a primeira URL da fila
        scraped_urls.add(url)  # Adiciona a URL à lista de URLs analisadas

        parts = urllib.parse.urlsplit(url)  # Faz o parse da URL em partes
        base_url = '{0.scheme}://{0.netloc}'.format(parts)  # Obtém a base da URL

        path = url[:url.rfind('/') + 1] if '/' in parts.path else url  # Obtém o caminho da URL

        print('[%d] Processing %s' % (count, url))  # Imprime a URL sendo processada
        try:
            response = requests.get(url)  # Faz uma requisição GET para a URL
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue  # Ignora a URL se houver erro de conexão ou esquema inválido

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))  # Encontra os emails na página
        emails.update(new_emails)  # Adiciona os emails encontrados ao conjunto de emails

        soup = BeautifulSoup(response.text, features="lxml")  # Faz o parsing do HTML usando BeautifulSoup

        for anchor in soup.find_all("a"):  # Encontra todas as tags <a> na página
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''  # Obtém o valor do atributo href da tag <a> (se existir)
            if link.startswith('/'):  # Se o link começar com '/', é uma URL relativa
                link = base_url + link  # Constrói a URL completa
            elif not link.startswith('http'):  # Se o link não começar com 'http', é uma URL relativa ao caminho da página atual
                link = path + link  # Constrói a URL completa
            if link not in urls and link not in scraped_urls:  # Verifica se a URL já foi processada ou está na fila
                urls.append(link)  # Adiciona a URL à fila
except KeyboardInterrupt:
    print('[-] Closing!')

# Cria a janela da interface gráfica
window = tk.Tk()
window.title("Email Scraper")
window.geometry("400x300")

# Cria um widget scrolledtext para exibir os emails
emails_text = scrolledtext.ScrolledText(window, width=40, height=10)
emails_text.pack(pady=10)

# Exibe os emails na interface gráfica
for mail in emails:
    emails_text.insert(tk.END, mail + "\n")

# Inicia o loop de eventos da interface gráfica
window.mainloop()
