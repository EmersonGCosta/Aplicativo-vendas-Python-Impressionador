from logging import exception

from kivy.app import App
from kivy.lang import Builder
import requests
from bannervenda import BannerVenda
import os
from myfirebase import MyFirebase
from datetime import date
from telas import *
from botoes import *
from functools import partial
from BannerVendedor import BannerVendedor
GUI = Builder.load_file('main.kv')

class MainApp(App):
    cliente= None
    produto= None
    unidade= None
    # id_usuario = 1 > utilizado para testes, antes de validar o login e armazenar os dados no firebase

    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):
        # carregar as fotos de perfil
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            #print(foto)
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}",
                                 on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        #carregar as fotos dos clientes
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}",
                                 on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text = foto_cliente.replace(".png", ""). capitalize(),
                                on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(label)
            lista_clientes.add_widget(imagem)

        #carregar as fotos dos produtos
        #listar os itens que estão dentro da pasta fotos_produtos
        arquivos = os.listdir("icones/fotos_produtos")
        #pegar a página adicionar vendas
        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        # Dentro da página pegar o ID lista produtos (scroll view de produtos)
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        #para cada produto dentro da lista de arquivos
        for foto_produto in arquivos:
            # criar uma imagem com a foto do produto
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}",
                                 on_release=partial(self.selecionar_produto, foto_produto))
            #criar um texto com o nome do produto com a primeira letra em maiúscula
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_produto, foto_produto))
            # adicionar a imagem no app
            lista_produtos.add_widget(label)
            #adicionar o texto no app
            lista_produtos.add_widget(imagem)

        #carregar a data atual.
        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        label_data = pagina_adicionarvendas.ids["label_data"]
        label_data.text = f"Data:{date.today().strftime('%d/%m/%Y')}"

        #carrega as informações do usuário
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open ("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # pegar informações do usuário
            # link = "https://appvendas-6fd35-default-rtdb.firebaseio.com/"
            requisicao = requests.get(f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{str(self.local_id)}.json?auth={self.id_token}")
            requisicao_dic= requisicao.json()
                #print(requisicao_dic)

            # preencher foto de perfil
            avatar = requisicao_dic["avatar"]
            self.avatar = avatar
            #print(avatar)
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            # preencher o id único
            id_vendedor = requisicao_dic["id_vendedor"]
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_vendedor"].text = f"Seu id Único: {id_vendedor}"

            #preencher o total de vendas
            total_vendas = requisicao_dic["total_vendas"]
            self.total_vendas = total_vendas
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            # Preencher Equipe
            self.equipe = requisicao_dic["equipe"]

            # preencher lista de vendas
            try:
                # print(requisicao_dic)
                vendas = requisicao_dic["vendas"]
                self.vendas = vendas
                pagina_homepage = self.root.ids["homepage"]
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                for id_venda in vendas:
                    #print(venda)
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                         produto=venda["produto"], foto_produto=venda["foto_produto"],
                                         data=venda["data"], preco=venda["preco"], unidade=venda["unidade"],
                                         quantidade=venda["quantidade"], )

                    lista_vendas.add_widget(banner)
            except Exception as exception:
                print(exception)

            #preencher equipe de vendedores

            equipe = requisicao_dic["equipe"]
            lista_equipe = equipe.split(",")
            pagina_listavendedores= self.root.ids["ListarVendedoresPage"]
            lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
            #print(equipe)
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela("homepage")

        except:
            pass
            # print (requisicao_dic)

    # função mudar tela

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"
        # Para mudar as informações da foto no firebase. Deve ser enviado um dicionário em formato de texto e a chave e o valor dentro de aspas duplas
        # Edição com aspas simples e o dicionário precisa estar em chaves duplas.
        info =f'{{"avatar": "{foto}"}}'
        requisicao=requests.patch(f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                  data= info)
        self.mudar_tela("ajustespage")

    def adicionar_vendedor (self, id_vendedor_adicionado):
        link = f'https://appvendas-6fd35-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic= requisicao.json()
        pagina_adicionarvendedor = self.root.ids["AdicionarVendedorPage"]
        mensagem_texto = pagina_adicionarvendedor.ids["mensagem_outrovendedor"]
        if requisicao_dic== {}:
            mensagem_texto.text = "Usuário Não Encontrado"
        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já faz parte da Equipe"
            else:
                self.equipe = self.equipe + f',{id_vendedor_adicionado}'
                info =f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data = info)
                mensagem_texto.text = "vendedor adicionado com sucesso"

                #adicionar um novo banner na lista de vendedores acompanhados
                pagina_listavendedores = self.root.ids["ListarVendedoresPage"]
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)
        #print(requisicao_dic)
    # mudar a cor do cliente selecionado
    def selecionar_cliente(self, foto, *args):
        # linha usada para a função adicionar_venda(removendo a extensão .png do nome da foto)
        self.cliente = foto.replace(".png", "")
        # pintar de branco todas as outras letras
        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]

        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            # pintar de azul a letra do item que selecionamos
            # foto -> carrefour.png / Label -> Carrefour -> carrefour -> carrefour.png
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    # mudar a cor do produto selecionado
    def selecionar_produto(self, foto, *args):
        # linha usada para a função adicionar_venda(removendo a extensão .png do nome da foto)
        self.produto = foto.replace(".png", "")
        # pintar de branco todas as outras letras
        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]

        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            # pintar de azul a letra do item que selecionamos
            # foto -> carrefour.png / Label -> Carrefour -> carrefour -> carrefour.png
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label,*args):
        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        # linha usada para a função adicionar_venda
        self.unidade = id_label.replace("unidades_", "")
        #pintar textos de branco
        pagina_adicionarvendas.ids["unidades_kg"].color = (1,1,1,1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)
        #pintar o item selecionado de azul
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        pagina_adicionarvendas = self.root.ids["AdicionarVendasPage"]
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids["preco_total"].text
        quantidade = pagina_adicionarvendas.ids["quantidade"].text

        if not cliente:
            pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 0, 0, 1)
        else:
            pagina_adicionarvendas.ids["label_selecione_cliente"].color = (0, 207/255, 219/255, 1)
        if not produto:
            pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 0, 0, 1)
        else:
            pagina_adicionarvendas.ids["label_selecione_produto"].color = (0, 207/255, 219/255, 1)
        if not unidade:
            pagina_adicionarvendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_litros"].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)

        # dado que ele preencheu tudo, vamos executar o código de adicionar venda
        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (
                type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", ' \
                   f'"foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", ' \
                   f'"preco": "{preco}", "quantidade": "{quantidade}"}}'
            link = f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}"
            requests.post(link,data=info)
            banner=BannerVenda(cliente=cliente,produto=produto, foto_cliente=foto_cliente, foto_produto= foto_produto,
                               data=data,preco=preco,quantidade=quantidade, unidade=unidade)
            pagina_homepage = self.root.ids["homepage"]
            lista_vendas = pagina_homepage.ids["lista_vendas"]
            lista_vendas.add_widget(banner)

            link=f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}"

            requisicao = requests.get(link)
            total_vendas=float(requisicao.json())
            total_vendas += preco
            # print(total_vendas)
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://appvendas-6fd35-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                           data=info)
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            self.mudar_tela("homepage")

        # retornar os valores das variáveis para vazio,
        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_todasvendas = self.root.ids["TodasVendasPage"]
        lista_vendas = pagina_todasvendas.ids["lista_vendas"]

        for item in  list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        #preencher a página todasvendaspage
        # pegar informações da empresa
        link = f'https://appvendas-6fd35-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        # print(requisicao_dic)

        # preencher foto de da empresa
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/hash.png"


        lista_vendas = pagina_todasvendas.ids["lista_vendas"]
        total_vendas = 0
        # # preencher lista de vendas
        # buscar o item vendas dentro do  usuário
        for local_id_usuario in requisicao_dic:
            try:
                vendas=requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda["preco"])
                    banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"],
                                         foto_cliente=venda["foto_cliente"],
                                         foto_produto=venda["foto_produto"],
                                         data=venda["data"], preco=venda["preco"], quantidade=venda["quantidade"],
                                         unidade=venda["unidade"])
                    lista_vendas.add_widget(banner)
            except:
                pass

        # preencher total de vendas
        pagina_todasvendas.ids["label_total_vendas"].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

        #redirecionar para a página todasasvendas
        self.mudar_tela("TodasVendasPage")

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"

        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):

        try:
            vendas=dic_info_vendedor["vendas"]
            pagina_vendasoutrovendedor = self.root.ids["VendasOutrovendedorPage"]
            lista_vendas = pagina_vendasoutrovendedor.ids["lista_vendas"]
            # limpar todas as vendas anteriores
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)

            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"],
                                     foto_cliente=venda["foto_cliente"],
                                     foto_produto=venda["foto_produto"],
                                     data=venda["data"], preco=venda["preco"], quantidade=venda["quantidade"],
                                     unidade=venda["unidade"])
                lista_vendas.add_widget(banner)
        except:
            pass
        total_vendas = dic_info_vendedor["total_vendas"]
        pagina_vendasoutrovendedor.ids["label_total_vendas"].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

        # preencher total de vendas
        foto_perfil = self.root.ids["foto_perfil"]
        avatar = dic_info_vendedor["avatar"]
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"
        self.mudar_tela("VendasOutrovendedorPage")


MainApp().run()