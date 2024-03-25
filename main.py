from colorama import Fore, Style
import configparser, requests, time, json, re, os, threading,datetime
from kucoin.client import Market
from kucoin.client import Trade
from kucoin.client import User
os.system('cls')
coin = ""

# Programme vente rapide: (Il permet de vendre à tout moment pendant le pump en appuyant sur la touche "ENTRÉE" dans le cmd)
def vente_rapide(numb_coin_buy,coin,order_info_buy):
    while True:
        try:
            input(Fore.YELLOW +"VENTE PANIQUE ACTIVÉ\nAppuyez sur la touche entrée pour vendre le plus rapidement possible vos "+ str(numb_coin_buy) + " " + coin +"...\n\n"+ Fore.RESET)
            verif = input(Fore.RED + "Confirmer la vente rapide? (Y/N) :\n\n" + Fore.RESET).upper()
            if verif == "Y":
                order_id_sell = trade.create_market_order(coin, 'sell', size=round(numb_coin_buy, 3))
                print(Fore.YELLOW +"\nVous avez vendu " + str(numb_coin_buy) + " " + coin + " avec l'ordre suivant :\n" + str(order_id_sell) + Fore.RESET)
                # affichage de si on a gagner ou perdu
                order_sell_info = trade.get_order_details(str(order_id_sell['orderId']))
                gain_perte = round(float(order_sell_info['dealFunds'])-float(order_info_buy["dealFunds"])-float(order_info_buy["fee"])-float(order_sell_info["fee"]),4)
                if gain_perte > 0:
                    print(Fore.GREEN +"Vous avez gagné " + f'{gain_perte}' + " USDT" + Style.RESET_ALL)
                else:
                    print(Fore.RED +"Vous avez perdu " + f'{gain_perte}' + " USDT" + Style.RESET_ALL)
                print(Fore.YELLOW +"VENTE PANIQUE FIN, Cependant, le premier programme continue de tourner pour voir l'évolution du pump\n\n" + Fore.RESET)
                return True
            else:
                print(Fore.RED +"Vous avez annulé la vente rapide." + Fore.RESET)
        except:
            print(Fore.RED +"Impossible de vendre le coin, Veuillez réessayez." + Fore.RESET)


#récupération des infos dans le fichier de configuration :
config = configparser.ConfigParser()
config.read('config.txt')

investissment_en_pourcentage = (float(config.get('INVESTISSEMENT', 'investissement en pourcentage')))/100
sell_pourcentage = float(config.get('INVESTISSEMENT', 'benefice en pourcentage'))
discord_id = config.get('DISCORD', 'discord id')
cookie = config.get('DISCORD', 'cookie')


# Connexion à l'API de kucoin
api_key,api_secret,api_passphrase = config.get('API KUCOIN', 'api_key'), config.get('API KUCOIN', 'api_secret'), config.get('API KUCOIN', 'api_passphrase')
client = User(api_key, api_secret, api_passphrase)
trade = Trade(api_key, api_secret, api_passphrase, is_sandbox=False)
market = Market(api_key, api_secret, api_passphrase)

# Récupération du montant d'argent disponible sur le compte trade en USDT
address = client.get_account_list("USDT","trade")
balance = float(address[0]["available"])



print(Fore.GREEN + "Argent disponible : " + str(balance)," USDT" + Style.RESET_ALL)
argent_en_jeux = round((balance*(investissment_en_pourcentage*100)/100),4)
print(Fore.BLUE + "\n /!\ Argent mis en jeu : ",str(argent_en_jeux)," USDT | Gain potentiel de : "+str(argent_en_jeux*sell_pourcentage/100)+" USDT\n"+ Style.RESET_ALL)
input(Fore.RED +"Appuyez sur entrée pour lancer le programme..." + Style.RESET_ALL)
while True:
    try:
          #Récupération du coin avec discord
        headers = {'authorization': ''+cookie+''}
        params = (('limit', '1'),) # limit permet de récupéré x message exemple : limit 1 recupère le dernier message et limit 5 récupère les 5 derniers messages
        resp = requests.get("https://discord.com/api/v9/channels/"+discord_id+"/messages", headers=headers, params=params) #On les messages dans ce channel discord
        for loopresp in json.loads(resp.text):
            print("\n---------- Voici le contenu du dernier message -----------------")
            print(loopresp["content"] + "\n") #On affiche le contenu du message
            try:
                parsed = re.sub('[^A-Za-z0-9--]+', ' ', loopresp["content"])
                parsed_url = parsed.split(" ")
                for parsed in parsed_url:
                    if re.search("-USDT", parsed): #On vérifie si le message contient le mot "-USDT"
                        if(len(parsed) == 0): #On vérifie si le message est vide
                            continue
                        else:
                            coin = parsed #si le message contient le mot "-USDT" et qu'il n'est pas vide, on récupère le coin
                    else:
                        continue
            except:
                continue
    except Exception as e:
        print("Erreur pour récupéré le coin\n" + e)
        time.sleep(1)
    if len(coin) == 0:
        continue #Si le coin n'est pas récupéré, on continue la recherche du coin
    else:
        with open('coins.txt', 'r') as f:
            coins = f.readlines()
        if coin + "\n" in coins: #On vérifie si le coin est déjà dans le fichier, si oui on arrête le programme car on ne peut pas acheter le même coin 2 fois
            print(Fore.RED +"ERREUR : Un achat à déjà été éffectuer avec cette cryptomonaie\n" + Style.RESET_ALL)
            exit()
        else:
            # Récupération du prix du coin et calcul de l'investissement
            #Achat
            order_id_buy = trade.create_market_order(coin, 'buy', size=round(float(balance//float(market.get_ticker(coin)["price"])*investissment_en_pourcentage), 3)) #On crée l'ordre d'achat
            # récupéré les infos de l'ordre
            order_info_buy = trade.get_order_details(str(order_id_buy['orderId']))
            # Récupération du prix du coin par rapport à l'ordre
            numb_coin_buy = float(order_info_buy['dealSize']) #On récupère le nombre de coin acheté
            total_investit = float(order_info_buy['dealFunds']) #On récupère le montant total investit
            taux_achat = total_investit/numb_coin_buy
            print(Fore.BLUE +"(Mode Pourcentage) Vous avez acheté " + f'{numb_coin_buy}' + " " +f'{coin}' + " pour le prix de " +f'{total_investit}' + " USDT, à "+ str(round(taux_achat,4))+"/unité"+ Style.RESET_ALL)
            print(Fore.GREEN +"Ordre d'achat -> " + str(order_id_buy) + Fore.WHITE)
            #Ajout du coin dans le fichier
            with open('coins.txt', 'w') as f:
                f.write(coin + "\n")

            #Vente
            threading.Thread(target=vente_rapide, args=[numb_coin_buy,coin,order_info_buy]).start() #On lance le programme vente_rapide.py
            date_achat = datetime.datetime.now()
            test = 0
            while True:
                #On vérifie si le gain en pourcentage est supérieur à la valeur marqué dans le fichier
                #Si oui on vend le coin
                #Si non on continue d'afficher le gain potentiel
                if (datetime.datetime.now() - date_achat).seconds > 15 and test == 0:
                    sell_pourcentage = 20
                    test = 1
                pourcentage_gain = round(100*(float(market.get_ticker(coin)["price"])-taux_achat)/taux_achat,2)
                gain_usdt = round((total_investit*pourcentage_gain/100),4)
                print("plus value de " +f'{pourcentage_gain}' + "%" + " soit "+ f'{gain_usdt}' + " USDT")
                if(pourcentage_gain >= sell_pourcentage):
                    try:
                        order_id_sell = trade.create_market_order(coin, 'sell', size=round(numb_coin_buy, 3))
                        print(Fore.GREEN +"Ordre de vente -> " + str(order_id_sell) + Style.RESET_ALL)
                        # affichage du gain
                        order_sell = trade.get_order_details(str(order_id_sell['orderId']))
                        gain_perte = round(float(order_sell['dealFunds'])-total_investit-float(order_info_buy["fee"])-float(order_sell["fee"]),4)
                        if gain_perte > 0:
                            print(Fore.GREEN +"Vous avez gagné " + f'{gain_perte}' + " USDT" + Style.RESET_ALL)
                        else:
                            print(Fore.RED +"Vous avez perdu " + f'{gain_perte}' + " USDT" + Style.RESET_ALL)
                        break
                    except Exception as e:
                        print(Fore.RED + "ERREUR : Une erreur est survenu lors de la revente.\n" + Style.RESET_ALL)
                        print(Fore.RED + "ERREUR : " + str(e) + Style.RESET_ALL)
            exit()