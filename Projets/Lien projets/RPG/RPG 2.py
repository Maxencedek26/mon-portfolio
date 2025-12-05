# Créé par m.boussaert, le 01/10/2024 en Python 3.7
from random import *
from time import *

class Personnage:
    def __init__(self, PV_max):
        self.nom = input("Quel nom voulez-vous donner au personnage ? ")
        self.vie = PV_max
        self.vie_max = PV_max
        self.mult_att = 1
        self.OR = 0
        self.EXP = 0
        self.L = 1
        self.EXP_req = 100
        self.points = 0
        self.inventaire = []

        self.L_sort1=1
        self.L_sort2=1

        self.secStats = self.secStats(self)
    def soigne(self, soin):
        self.vie += soin
        if self.vie > self.vie_max:
            self.vie = self.vie_max

    def perdVie(self, degats):
        self.vie -= degats
        if self.vie < 0:
            self.vie = 0

    def donneEtat(self):
        return self.vie

    def attaque(self, r):
        if r == 1:
            degats = int(4 * self.mult_att)
            chance = randint(1, 6)
        elif r == 2:
            degats = int(8 * self.mult_att)
            m=11//(1+self.L_sort1*0.1)
            chance = randint(1, m)
        else:
            degats = int(16 * self.mult_att)
            m=17//(1+self.L_sort2*0.1)
            chance = randint(1, m)
        if chance <= 5:
            return degats
        else:
            return 0

    def ajouter_inventaire(self, objet):
        self.inventaire.append(objet)
    def retirer_inventaire(self,objet):
        self.inventaire.remove(objet)
    def level_up(self):
        if self.EXP>=self.EXP_req:
            print("Vous avez monté de niveau, vous êtes maintenant au niveau",perso.L)
            self.soigne(self.vie_max//2)
            self.L += 1
            self.EXP -= self.EXP_req
            self.EXP_req += 25 * self.L + 5
            self.points += 5
            ameliore = True
            while ameliore ==True:
                c = int(input("Vous avez " + str(self.points) + " points. Que voulez-vous améliorer ? (1-vie max [" + str(self.vie_max) + "] 2-multiplicateur de dégâts [" + str(self.mult_att) + "] 3-Quitter cette fenêtre) "))
                if c == 1:
                    p = int(input("Combien de points voulez-vous utiliser (1 point= 2 PV max)"))
                    if p > self.points:
                        print("Vous n'avez pas assez de points")
                    else:
                        self.vie_max += p * 2
                        self.vie+= p * 2
                        self.points -= p
                elif c == 2:
                    p = int(input("Combien de points voulez-vous utiliser (1 point= 15 % d'attaque)"))
                    if p > self.points:
                        print("Vous n'avez pas assez de points")
                    else:
                        self.mult_att += p * 0.15
                        self.points -= p
                elif c == 3:
                    ameliore = False
                if "Grimoire de sorts" in self.inventaire:
                    c=int(input("Vous pouvez aussi améliorer un sort. Quel sort voulez-vous améliorer ?(1-Choc électrique 2-Souffle de feu)"))
                    if c==1:
                        self.L_sort1+=1
                    elif c==2:
                        self.Lsort2+=2
                        if self.L_sort2==5:
                            print("Votre souffle de feu peut maintenant enflammer les monstres et leur infliger des dégâts au fil des tours.")
                    r=randint(1,3)
                    if r<3:
                        perso.retirer_inventaire("Grimoire de sorts")
                        print("Le grimoire s'est détruit!")


    def printStats(self):
        print(perso.nom, "\n Vie:", perso.vie, "/", perso.vie_max, "\n Niveau:", perso.L, "\n EXP:", perso.EXP, "/", perso.EXP_req, "\n")
    class secStats:
        def __init__(self, personnage):
            self.soin_total = 0
            self.degats_totaux = 0
            self.degats_recus_totaux = 0
            self.monstres_vaincus = 0
            self.nb_combats = 1
            self.score = 0
            self.personnage = personnage

        def printStats(self):
            print("Stats:\n vie max: ",self.personnage.vie_max,"\n multiplicateur de dégâts: ",self.personnage.mult_att,"\n Niveau: ",self.personnage.L,"\n vie soignée: ",self.soin_total,"\n dégâts infligés: ",self.degats_totaux,"\n dégâts reçus: ",self.degats_recus_totaux,"\nmonstres vaincus: ",self.monstres_vaincus,"\n combats: ",self.nb_combats,"\n score: ",self.score,"\n")
        def sauvegarderScore(self):
            classement =[]
            try:
                with open('Classement.txt', 'r') as f:
                    if f!=[]:
                        for line in f:
                            parts = line.strip().split(',')
                            nom = parts[0]
                            score =parts[1]
                            stats = tuple(map(int, parts[2:]))
                            classement .append((nom, score, stats))
            except FileNotFoundError:
                pass
            stats = (self.personnage.vie_max,
                             self.personnage.mult_att,
                             self.personnage.L,
                             self.soin_total,
                             self.degats_totaux,
                             self.degats_recus_totaux,
                             self.monstres_vaincus,
                             self.nb_combats)

            classement .append((self.personnage.nom, self.score, stats))
            classement = sorted(classement, key=lambda x: x[0], reverse=True)[:10]
            with open('Classement.txt', 'w') as f:
                for nom, score, stats in classement :
                    f.write(f"{nom},{score},{','.join(map(str, stats))}\n")
            print("Classement mis à jour:\n")
            for rank, (nom, score, stats) in enumerate(classement, 1):
                print(rank,".",nom,":",score, "points Stats:",stats)


class Monstre:
    def __init__(self):
        with open('noms.txt', 'r') as file:
            noms = [line.strip() for line in file if line.strip()]
        self.nom = choice(noms)
        vie = randint(15, 20)
        self.vie = vie
        self.vie_max = vie
        self.estenflamme= False

    def soigne(self, soin):
        self.vie += soin
        if self.vie > self.vie_max:
            self.vie = self.vie_max

    def perdVie(self, degats):
        self.vie -= degats
        if self.vie < 0:
            self.vie = 0

    def donneEtat(self):
        return self.vie

    def attaque(self):
        r = randint(1, 3)
        if r == 1:
            degats = 2
            chance = randint(1, 6)
        elif r == 2:
            degats = 4
            chance = randint(1, 10)
        else:
            degats = 8
            chance = randint(1, 15)
        if chance <= 5:
            return degats
        else:
            return 0
    def enflammé(self,duree,degats_par_tour):
        if self.estenflamme==True:
            if duree!=0:
                self.perdVie(degats_par_tour)
                print(self.nom,"brûle et subit",degats_par_tour,"dégâts.")
            duree=duree-1
            if duree==0:
                self.estenflamme=False
                print(self.nom,"ne brûle plus.")
            return degats_par_tour
    def printStats(self):
        print(self.nom,":", self.vie, "/", self.vie_max,end="  |  ")

def combat(ennemis):
    t = 0
    EXP = 0
    OR = 0
    duree=perso.L_sort2//2
    ennemis_vaincus = []
    print("_" * 80)
    for Monstre in ennemis:
        print(Monstre.nom)
    print("vous attaque !\n")
    while len(ennemis) > 0 and perso.donneEtat() > 0:
        if "Bague de régénération" in perso.inventaire:
            perso.soigne(1)
        sleep(2)
        t += 1
        choix_perso = 0
        print("Tour", t, "\n")
        perso.printStats()
        for Monstre in ennemis:
            Monstre.printStats()
        while choix_perso != 1 and choix_perso != 2:
            choix_perso = int(input("\nQue voulez-vous faire ? (1-Attaquer 2-Utiliser un objet dans l'inventaire)"))
            att = 0
            if choix_perso == 1:
                while not 1<=att<=3 :
                    att = int(input("Quelle attaque voulez-vous utiliser ? (1-Coup d'épée (faible) 2-Choc électrique(moyen) 3-Souffle de feu (fort))"))
                if len(ennemis) > 1:
                    cible = int(input("Quel monstre voulez-vous attaquer ?(1-" + str(len(ennemis)) + ")")) - 1
                else:
                    cible = 0
            elif choix_perso == 2:
                if perso.inventaire == []:
                    print("Votre inventaire est vide.")
                    choix_perso = 0
                else:
                    q = 0
                    c=0
                    choix_possibles=[]
                    print("Vous avez:")
                    for i in set(perso.inventaire):
                        q = perso.inventaire.count(i)
                        print(i, "X", q)
                    if "Potion de soin" in perso.inventaire:
                        print ("Vous pouvez utiliser une potion de soin pour vous soigner (1)")
                        choix_possibles.append(1)
                    if "Potion de soin améliorée" in perso.inventaire:
                        print ("Vous pouvez utiliser une potion de soin améliorée pour vous soigner (2)")
                        choix_possibles.append(2)
                    if "Bombe" in perso.inventaire:
                        print ("Vous pouvez utiliser une bombe sur l'ennemi de votre choix (3)")
                        choix_possibles.append(3)
                    while c not in choix_possibles:
                        c=int(input("Quel objet voulez-vous utiliser ?"))
                        if c not in choix_possibles:
                            print("Veuillez entrer un numéro parmi les choix disponibles")
                        elif c==1:
                            perso.soigne(50)
                            sleep(2)
                            print("Vous utilisez une potion de soin et regagner 50 points de vie.")
                            perso.retirer_inventaire("Potion de soin")
                        elif c==2:
                            perso.soigne(200)
                            sleep(2)
                            print("Vous utilisez une potion de soin et regagner 200 points de vie.")
                            perso.retirer_inventaire("Potion de soin améliorée")
                        elif c==3:
                            if len(ennemis) > 1:
                                cible = int(input("Quel monstre voulez-vous attaquer ?(1-" + str(len(ennemis)) + ")")) - 1
                            else:
                                cible = 0
                            ennemi = ennemis[cible]
                            degats = randint(15,20)
                            ennemi.perdVie(degats)
                            sleep(2)
                            print("Vous lancer une bombe sur",ennemi.nom,"et infligez",degats,"dégâts.")
                            perso.retirer_inventaire("Bombe")
        if att != 0:
            ennemi = ennemis[cible]
            degats = perso.attaque(att)
            ennemi.perdVie(degats)
            sleep(2)
            if degats > 0:
                print("Vous attaquez", ennemi.nom, "et infligez", degats, "dégâts.")
                if att==3 and perso.L_sort2>=5:
                    ennemi.estenflamme=True
                    print(ennemi.nom,"prend feu.")
                perso.secStats.degats_totaux += degats

            else:
                print(ennemi.nom, "a esquivé votre attaque.")
        for ennemi in ennemis:
            if ennemi.estenflamme==True:
                degats=ennemi.enflammé(duree,perso.L_sort2//5)
                perso.secStats.degats_totaux += degats
            if ennemi.donneEtat() == 0:
                print("Vous avez vaincu", ennemi.nom)
                ennemis_vaincus.append(ennemi)
                ennemis.remove(ennemi)
                perso.secStats.score += ennemi.vie_max
                perso.secStats.monstres_vaincus += 1

        for Monstre in ennemis:
            if ennemi.donneEtat() == ennemi.vie_max:
                Choix_ennemi = 1
            else:
                Choix_ennemi = randint(1, 3)
            if Choix_ennemi <3:
                sleep(2)
                degats = Monstre.attaque()
                perso.perdVie(degats)
                if degats > 0:
                    print(Monstre.nom, "vous attaque et inflige", degats, "dégâts")
                    perso.secStats.degats_recus_totaux += degats
                else:
                    print("Vous avez esquivé l'attaque de", Monstre.nom)
            elif Choix_ennemi == 3:
                sleep(2)
                soin = randint(0, 3)
                Monstre.soigne(soin)
                if soin>0:
                    print(Monstre.nom, "se soigne de", soin, "points de vie.")
                else:
                    print(Monstre.nom, "essaie de se soigner mais vous l'interrompez")
    if len(ennemis) == 0:
        for Monstre in ennemis_vaincus:
            EXP += Monstre.vie_max*2
            OR += Monstre.vie_max
        perso.EXP += EXP
        perso.OR += OR
        print("Vous avez gagné le combat\n+", OR, "Or\n+", EXP, "EXP")
        sleep(2)
        perso.secStats.nb_combats += 1
        perso.secStats.score += 5 * (len(ennemis_vaincus) ** 2)
    if perso.donneEtat() == 0:
        print("Vous avez été vaincu.")
        sleep(3)
        perso.secStats.printStats()
        perso.secStats.sauvegarderScore()
    print("_" * 80)


def cree_monstre(n):
    Monstres = []
    for i in range(n):
        monstre = Monstre()
        Monstres.append(monstre)
    return Monstres

def marché():
    def achat_article(nom_article,prix,niv_minimum):
            if perso.L>=niv_minimum:
                q=int(input("Combien de "+str(nom_article)+"s voulez-vous ?(1"+str(nom_article)+"="+str(prix)+" pièces)"))
                if prix*q<=perso.OR:
                    perso.OR-=prix*q
                    for i in range(q):
                        perso.ajouter_inventaire(nom_article)
                        message="Marchand: <<Merci pour votre achat!>>"
                else:
                    message="Marchand: <<Vous n'avez pas assez de pièces>>"
            else:
                message="Marchand: <<Navré, cet article n'est disponible qu'à partir du niveau ",niv_minimum,">>"
            return message
    def achat_article_unique(nom_article,prix,niv_minimum):
            if perso.L>=niv_minimum:
                if nom_article not in perso.inventaire:
                    if prix<=perso.OR:
                                perso.OR-=prix
                                perso.ajouter_inventaire(nom_article)
                                message="Marchand: <<Merci pour votre achat !>>"
                    else:
                        message="Marchand: <<Vous n'avez pas assez de pièces>>"
                else:
                    message="Marchand: <<Vous possédez déjà cet objet.>>"
            else:
                message="Marchand: <<Navré, cet article n'est disponible qu'à partir du niveau ",niv_minimum,">>"
            return message

    if perso.secStats.nb_combats>1:
        r=randint(1,3)
    else:
        r=1
    if r==1:
        c=int(input("Par chance, vous trouvez un marché. Souhaitez-vous vous y rendre ? (1-oui 2-non) (Vous possédez "+str(perso.OR)+" or)"))
        if c==1:
            print("Marchand:<<Bonjour, jeune aventurier! Que souhaitez-vous acheter?>>")
            a=999
            print("1) Potions de soin: 15 pièces\nLes potions de soin sont utilisables en combat et vous régénèrent jusqu'à 50 points de vie chacune.")
            if perso.L>=12:
                print("2) Potions de soin améliorées: 70 pièces \nLes potions de soin améliorées sont utilisables en combat et vous régénèrent 200 points de vie chacune.")
            else:
                print("2) Potions de soins améliorées \nDisponible à partir du niveau 12")
            if perso.L>=5:
                print("3) Potions d'expérience: 25 pièces\nLes potions d'expérience vous permettent d'obtenir 50 points d'expérience chacune, instantanément. (Utilisable seulement hors combat)")
            else:
                print("3) Potions d'expérience \nDisponible à partir du niveau 5")
            print("4) Bombes: 30 pièces\n Vous pouvez utilisez les bombes pour infliger 15 à 20 dégâts au monstre ciblé lors d'un combat.")
            print("5) Grimoire de sorts: 250 pièces\n Permet d'améliorer l'un de vos sorts lors de la montée d'un niveau (66% de chance de se détruire après une utilisation).")
            print("6) Bague de régénération: 120 pièces:\n Régénère 1 point de vie par tour lors d'un combat.(Vous ne pouvez en posséder qu'un seul)")
            sleep(5)
            while a!=0:
                a=int(input("Que voulez-vous acheter ?(1-6)(0 pour quitter)"))
                sleep(2)
                if a==1:
                    print(achat_article("Potion de soin",15,0))
                elif a==2:
                    print(achat_article("Potion de soin améliorée",70,12))
                elif a==3:
                    print(achat_article("Potion d'expérience",25,5))
                elif a==4:
                    print(achat_article("Bombe",30,0))
                elif a==5:
                    print(achat_article_unique("Grimoire de sorts",250,0))
                elif a==6:
                    print(achat_article_unique("Bague de régénération",120,0))
                elif a==0:
                    print("Marchand: <<Au revoir et à bientôt!>>")

def boucle_jeu():
    while perso.donneEtat() > 0:
        perso.level_up()
        marché()
        if "Potion d'expérience" in perso.inventaire:
            q=0
            for objet in perso.inventaire:
                if objet== "Potion d'expérience":
                    q+=1
            c=int(input("Vous possédez "+str(q)+" potions d'expérience. Voulez-vous en utilisez ?(1-oui 2-non)"))
            if c==1:
                k=999
                while k>q:
                    k=int(input("Combien voulez-vous en utilisez ?(1-potion= 50 points d'expérience)"))
                    if k>q:
                        print("Vous n'avez pas assez de potions.")
                    else:
                        perso.EXP+=50*k
                        print("Vous gagnez",50*k,"points d'expérience")
                        for i in range (k):
                            perso.retirer_inventaire("Potion d'expérience")

        m = perso.secStats.nb_combats
        if perso.donneEtat() < perso.vie_max // (1 + perso.secStats.nb_combats):
            m -= 1
        elif perso.donneEtat() > perso.vie_max * (perso.secStats.nb_combats ) // (1 + perso.secStats.nb_combats) and perso.secStats.nb_combats > 1:
            m += 1
        n_monstres = randint(1, m)
        monstres = cree_monstre(n_monstres)
        combat(monstres)

perso = Personnage(50)
boucle_jeu()
