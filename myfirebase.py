import requests
from kivy.app import App
import os
from dotenv import load_dotenv

# cria a conta e login
class MyFirebase():

    load_dotenv()
    API_KEY = os.getenv("API_KEY")


    def criar_conta(self, email, senha):

        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'

        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        #print(requisicao_dic)
        # print(f"Email enviado: '{email}'")
        # email = email.strip()
        if requisicao.ok:
            #print("usuário criado")
            # requisicao_dic["idToken"] > autenticação
            # requisicao_dic["refreshToken"] > token que mantém o usuário logado
            # requisicao_dic["localId"] > id do usuário

            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"] = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            with open ("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            req_id = requests.get(f"https://appvendas-6fd35-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id.json()
            #print(id_vendedor)
            # pegar somente o lavor e converter  para número inteiro e salvar numa nova variável
            novo_id_vendedor = int(id_vendedor['proximo_id_vendedor'])

            link = f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe":"",  "total_vendas": "0", "vendas": "", "id_vendedor":"{novo_id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)
            #print(novo_id_vendedor)

            #atualizar valor do proximo_id_vendedor
            proximo_id_vendedor =int(id_vendedor['proximo_id_vendedor']) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://appvendas-6fd35-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}", data=info_id_vendedor)
            #print(info_id_vendedor)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")

        else:
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = mensagem_erro
            pagina_login.ids["mensagem_login"].color = (1, 0, 0, 1)


    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            refresh_token = requisicao_dic["refreshToken"]
            local_id  = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.local_id = id_token

            with open ("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")

        else:
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = mensagem_erro
            pagina_login.ids["mensagem_login"].color = (1, 0, 0, 1)


    def trocar_token(self, refresh_token):
        link =f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {"grant_type":"refresh_token",
                "refresh_token":refresh_token,}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic["user_id"]
        id_token = requisicao_dic["id_token"]
        return (local_id, id_token)
