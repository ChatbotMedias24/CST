import streamlit as st
import openai
import streamlit as st
from dotenv import load_dotenv
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from streamlit_chat import message  # Importez la fonction message
import toml
import docx2txt
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import docx2txt
from dotenv import load_dotenv
if 'previous_question' not in st.session_state:
    st.session_state.previous_question = []

# Chargement de l'API Key depuis les variables d'environnement
load_dotenv(st.secrets["OPENAI_API_KEY"])

# Configuration de l'historique de la conversation
if 'previous_questions' not in st.session_state:
    st.session_state.previous_questions = []

st.markdown(
    """
    <style>

        .user-message {
            text-align: left;
            background-color: #E8F0FF;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: 10px;
            margin-right: -40px;
            color:black;
        }

        .assistant-message {
            text-align: left;
            background-color: #F0F0F0;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: -10px;
            margin-right: 10px;
            color:black;
        }

        .message-container {
            display: flex;
            align-items: center;
        }

        .message-avatar {
            font-size: 25px;
            margin-right: 20px;
            flex-shrink: 0; /* Empêcher l'avatar de rétrécir */
            display: inline-block;
            vertical-align: middle;
        }

        .message-content {
            flex-grow: 1; /* Permettre au message de prendre tout l'espace disponible */
            display: inline-block; /* Ajout de cette propriété */
}
        .message-container.user {
            justify-content: flex-end; /* Aligner à gauche pour l'utilisateur */
        }

        .message-container.assistant {
            justify-content: flex-start; /* Aligner à droite pour l'assistant */
        }
        input[type="text"] {
            background-color: #E0E0E0;
        }

        /* Style for placeholder text with bold font */
        input::placeholder {
            color: #555555; /* Gris foncé */
            font-weight: bold; /* Mettre en gras */
        }

        /* Ajouter de l'espace en blanc sous le champ de saisie */
        .input-space {
            height: 20px;
            background-color: white;
        }
    
    </style>
    """,
    unsafe_allow_html=True
)
# Sidebar contents
textcontainer = st.container()
with textcontainer:
    logo_path = "medi.png"
    logoo_path = "NOTEPRESENTATION.png"
    st.sidebar.image(logo_path,width=150)
   
    
st.sidebar.subheader("Suggestions:")
questions = [
    "Donnez-moi un résumé du rapport ",
    "Quels sont les principaux types de comptes spéciaux du Trésor mentionnés dans le rapport ?",        
    "Comment les comptes d'affectation spéciale contribuent-ils au développement économique et social ?",        
    "Quels sont les impacts des comptes spéciaux sur la politique économique du Maroc ?",
    "Quels sont les principaux défis rencontrés dans la gestion des comptes spéciaux du Trésor ?"
]
# Initialisation de l'historique de la conversation dans `st.session_state`
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = StreamlitChatMessageHistory()
def main():
    text=r"""
    
INTRODUCTION 
 
Les  Comptes   Spéciaux   du  Trésor   (CST)   constituent   un   instrument    important   pour   la 
programmation  et  l’exécution  des politiques   publiques  et stratégies  sectorielles  et  jouent  un 
rôle crucial  pour  la  mise  en œuvre  efficace  des  programmes  et  projets  ayant  un  caractère 
transverse. Ils  permettent,   également,  aux pouvoirs   publics  d’entreprendre   les mesures  qui 
s’imposent en cas d’urgence et  de nécessité impérieuse et imprévue.  
 
A ce titre, le recours  aux CST et en particulier  les Comptes d’Affectation  Spéciale (CAS)  est un 
moyen privilégié  pour la gestion  des effets  des crises et catastrophes  naturelles à l’instar  de la 
pandémie du Covid-19 et le Séisme d’Al Haouz. 

           
Outre la mise en œuvre  des actions urgentes  prises pour  la gestion des  crises et catastrophes 
naturelles, les politiques   sociales et  économiques,  ainsi que  les infrastructures,  les  domaines 
d’intervention   que  les  CAS  contribuent   à  mettre   en  œuvre,  conformément   aux  règles  et 
procédures budgétaires,  portent,  essentiellement, sur les axes suivants : 
 
        La poursuite  de  la  mise en  œuvre  du  chantier  de  la généralisation  de  la   protection 
          sociale qui  constitue  l’un des fondements  essentiels du nouveau modèle  de l’Etat social, 
          voulu  par  sa  Majesté le  Roi. Dans  ce  cadre, le  CAS «  Fonds  d’appui  à  la protection 
          sociale  et  à la  cohésion  sociale »  joue un  rôle  important   dans la  mise en  œuvre  des 
          différentes   composantes   de   ce  chantier   Royal,  et   ce,  dans  le  respect   absolu   du 
          calendrier  arrêté à cet effet; 
 
        L’accompagnement  de  la politique  de  l’Etat  en matière  de justice  spatiale  à travers  le 
          renforcement   des  moyens  octroyés   aux  régions  et  l’exécution   des  programmes   de 
          réduction   des disparités  territoriales  et  sociales. Dans ce cadre,  force est  de constater 
          que  le Gouvernement  poursuit  ses efforts  en la matière  à travers  la programmation   de 
          versements  et l’affectation   de ressources au profit  du  « Fonds spécial relatif  au produit 
          des parts  d’impôts  affectées  aux régions  » et du  « Fonds de solidarité  interrégionale  ». 
          Dans le  même objectif,  l’Etat  continue  à assurer  le financement  nécessaire des projets 
          programmés  et  exécutés à travers les CAS « Fonds  pour le développement   rural et des 
          zones   de  montagne    »  et   le  «  Fonds   de   soutien   à  l’initiative    nationale  pour   le 
          développement   humain ». En outre,  le CAS « Part  des collectivités   territoriales  dans le 
          produit    de  la  T.V.A  »  mobilise   des  moyens  importants    au  profit   des  collectivités 
          concernées ; 
                                                             
        L’appui   à  l’investissement    selon  une   nouvelle   approche    visant   la  promotion    et 
          l’attraction    de  l’investissement  privé   afin  d’en  faire  un  moteur   de  croissance  et  de 
          création   d’emplois.  C’est dans  cette  optique   que  le CAS  « Fonds  de  promotion   des 
          investissements  » se positionne comme  un instrument  axial pour la mise en œuvre  de la 
          nouvelle  politique  de l’Etat en la matière  ; 

 
        La transition   numérique  et l’ancrage  de  la digitalisation   comme  levier  incontournable 
          pour    la  réforme    de  l’Administration     publique.   A   ce   titre,   le   CAS  «   Fonds   de 
          modernisation   de   l’administration   publique,   d’appui  à  la  transition   numérique   et   à 
          l’utilisation  de  l’amazighe » constitue  l’un des  instruments  destinés au portage  de cette 
          nouvelle  vision; 

 
                                                                                                                                               1

8
                                                                         
PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
   
          La  reconsidération  du  mode d’intervention   de  l’Etat  en matière  d’appui  au secteur  de 
             l’habitat  et  de  l’accès  au logement  à  travers  le  « Fonds solidarité   pour  le soutien  au 
             logement,  d’habitat et  intégration  urbaine » ; 
                                                                
          La  gestion  anticipative   de l’Etat  pour   faire face  aux  répercussions  de la  situation  de 
             stress hydrique  et  de  sécheresse enregistrée au  cours des  dernières années à  travers, 
             notamment,   la  mise  à  contribution    des  différents   partenaires   aux  projets,  dont   le 
             « Fonds  de   lutte   contre   les   effets   des  catastrophes    naturelles »  est   le  principal 
             réceptacle.  
                

  Dans la même  lignée, d’autres CAS ayant  pour vocation  le  renforcement  des infrastructures  à 
  travers  l’amélioration   de la  connectivité   et la  modernisation  des  moyens  de transport,   ainsi 
  que  le   développement   agricole,  continuent    de  bénéficier   de  ressources  à  la  mesure  de 
  l’ambition  affichée  afin de mettre  en œuvre les différentes  politiques  sectorielles en la matière. 
  C’est  le  cas   notamment   du  « Fonds spécial  routier  », du  « Fonds  d’accompagnement   des 
  réformes   du   transport   routier   urbain   et   interurbain  »  et   le  « Fonds  de   développement 
  agricole  » qui  constituent,   tous,  des  instruments   d’intervention   incontournables   dans  leurs 
  domaines respectifs. 
   
  Concernant  le bilan  comptable  des  CAS au titre  de  l’année 2023,  il fait  ressortir  un  montant 
  total  de recettes  réalisées de 316,26 MMDH(*), ventilé comme suit : 
   
      116,08 MMDH au  titre   des  recettes   propres,   en  l’occurrence   les  recettes  fiscales,  les 
        redevances  et les autres produits  affectées ; 
     
      49,84 MMDH au titre  des versements du budget  général ; 
     
      150,35 MMDH au titre du report  du solde dégagé par  les CAS à la fin de l’exercice 2022. 
   
  Le  présent rapport   se propose  de  mettre  en  relief le  rôle  des CST, et  ce à  travers les  deux 
  principaux  chapitres suivants: 
   
  Le premier   chapitre  relate  de premier  d’abord  les données budgétaire  et comptable  des  CST 
  au titre   de l’année 2023  en  comparaison avec  les réalisations  des années 2022  et  2021. Il se 
  propose  également  de  mettre  en évidence  le  volume des  recettes  mobilisées, y  compris  les 
  soldes  reportés,  et  l’importance   des  actions  et  dépenses  desdits  comptes.  Ce  chapitre  se 
  subdivise en deux  sections qui traitent  successivement  les aspects suivants : 

      La maîtrise  de  l’évolution   du  nombre  des  CST en phase  avec  l’effort  de  rationalisation 
        entrepris  au cours  des deux dernières décennies marquées  par la suppression de plusieurs 
        comptes  et le recours  limité aux nouvelles  créations de comptes  ;  

      L’évaluation  budgétaire   et  comptable   des  CST à  travers  l’analyse  des  recettes  et  des 
        dépenses desdits  comptes. 

   


  (*)                                                 
     : Milliards de Dirhams. 
   

   
              2 
                                                                                 
           2   

9
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
Le  deuxième    chapitre    fait  ressortir    le rôle   déterminant    que  jouent   les  comptes   d’affectation 
spéciale  en  matière   de développement     économique    et  social,  d’appui   à l’investissement     et  de 
promotion   de  l’emploi.   La répartition    de  ces comptes   est  établie,  par  domaine,   comme  suit  : 

    Le développement     territorial    ;  

    Le développement     humain  et  social  ; 

    La promotion    économique    et financière   ;   

    Le  renforcement    des  infrastructures    ; 

    Le développement     rural,  agricole   et de  la pêche  ;            

    Les autres  domaines. 

 
 
 
 
 
 
 
 
 
 
 




































 
                                                                                                                                                            3

10
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
CHAPITRE       I  - LES    COMPTES      SPECIAUX       DU   TRESOR      :: QUEL    BILAN ? 
 
Le présent  chapitre   met  en exergue  les  actions,  menées par  l’Etat  durrant les  vingt  dernières 
années, pour l’assainissement  et la  rationalisation  du  recours  aux CST. IIl est structuré  en  deux 
grandes sections   
        La première  section fait  ressortir  l’évoolution du nombre des CST depuis  2005  relatant  les  
          efforts  déployés  pour rationaliser  et optimiser  la gestion de ces comptes. 
         
        La seconde section  fait  valoir, quant  à elle,  les tendances d’évoluttion  des recettes  et des 
          dépenses des différentes  catégories  des CST au cours de la périodee 2021-2023.  
       

SECTION            I  -   EVOLUTION                DU     NOMBRE           DES      COMPTES 
SPECIAUX             DU     TRESOR 
 
Le nombre des  CST a enregistré une baisse substantielle  durant  les vingtt dernières années pour 
s’établir  à  68  en  2023  contre   97  en  2005   sous  l’effet  des  efforts   dééployés en matière   de 
rationalisation  desdits  comptes.  En outre, ill a  été procédé  à  la création,, au cours  de 2023,  par 
décret, du CAS intitulé  « Fonds spécial pour  la gestion  des effets du  tremblement  de  terre ayant 
touché  le Royaume  du  Maroc ». Ledit  décret   a été  ratifié  par  la  loi de  finances  n°55-23  pour 
l’année budgétaire  2024. A l’exception  du CAS susvisé, aucun CST n’a étéé créé durant la période 
2021-2024. 
  
L’analyse de  la  structure   des  CST en  2024,  par   catégorie  de  comptees, met  en  évidence  le 
nombre important   des CAS s’élevant à 56  sur 69 comptes  existants  conttre seulement 45  sur un 
total  de 97  comptes  en  2005, marquant   aiinsi un changement  important   dans la  structure  des 
CST. 
 
Le nombre des comptes  de financement  et d’adhésion  aux organismes internationaux,  a, quant à 
lui, enregistré  une  baisse notable,  passant de  41 comptes  en  2005  à seeulement 7 comptes  en 
2024.  
 
S’agissant des  comptes   d’opérations   monétaires,  leur  nombre   est  ressté stable depuis   2005          
(2 comptes).  
 
En revanche, le nombre des comptes  de dépenses sur dotations  a connu uun net recul, passant de 
9 en 2005 à 4 en 2024.  
 
Le graphique ci-après  retrace l’évolution  du  nombre  des CST, par catégorie de  comptes, au titre 
de la période 2005-2024   : 

                                 EVOLUTION DU NOMBRE DES CST PAR CCATEGORIE DE COMPTES DURANT LA PERIODE 20005-2024

       2
       3
       9                                                                                      CAS CF CDDD CAOI COM
              2      2                                     2     2
              3      3      2      2     2      2
                      7      3      3     3      3      33           2      2      2
              8
                              7      7     6      6      66           3      3      3     2      2
                                                                            6      6      4     3      3      2      22           22            2
                                                                                                                           33           33            3
      38                                                                                         4      4      3      44           44            4
                      20           14 14 12 13 13               8      8      8     6      6      4      44           44            4
              20           16                                                                                  6



      45 45 48 47 51 51 54 55 55 56 57 57 56 56 52 56 56 55 55 56



    2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024
                                                                                                                                                                   

 
            4 

11
                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
L’analyse du  nombre  des CST  par ordonnateur   montre  que  le Ministèree de l’Economie  et  des 
Finances est   le  principal   gestionnaire   de  ces  comptes,   en  sa qualitéé d’ordonnateur    de  25 
comptes en 2024,  dont 16 CAS et 9 comptes  regroupant  l’ensemble des ccomptes d’adhésion aux 
organismes internationaux,  d’opérations monétaires  et de financement.  
Quant au  Ministère  de  l’Intérieur,  il  gère  9  comptes,  suivi  du Ministèree de l’Agriculture,   de  la 
Pêche Maritime, du Développement  Rural et des Eaux et Forêts  (5 comptees), du Département du 
Chef du Gouvernement (5  comptes) et  de l’Administration  de  la Défense Nationale (4 comptes).  
Le Ministère de  la Jeunesse, de la Culture  et de  la Communication,  le Ministère  de l’Equipement 
et de l’Eau, le Ministère de la Transition Energétique  et du Développementt  Durable et le Ministère 
de la justice, pour leur part,  assurent la gestiion de 2 comptes chacun.    
Le graphique  ci-après  fait ressortir  la ventillation,  par  ordonnateur  et parr catégorie  de comptes 
des CST au titre de l’année 2024 : 

                                                         VENTILATION DES CAS PAR ORDONNATEUR 
                                                ET PAR CATEGORIE DE COMPTES AU TITRE DE l'ANNEE 2024



            2
                                                           CAS CFF CDD CAOI COM
            3


            4


                                                                                                                                                       1



            16

                                                                                                                                                      12
                                                          1
                            9
                                                                          2
                                           5
                                                          4
                                                                          2             2              2             2              2

                              r                                                           t                                               e
               es           u              et                                         e                             et e

                              rie
                              é
               nanc       t            time,
                              In          i Eaux 
                                                            du           nse 
                                                                                          e

               Fi
                                              et 
                                           Mar l        du Chef t e              ur ion

                                                                           Déf      ltl
                                                                                          u cat         et Eau    e              c
                                                                                                                            bl
                                                                                                                            a


                                                              nemen 


               omie et                   a
                                                              r

                                            Pêche s

                                           ,

               Econ                   lture ement Rur êt ement on de la

                                                                              ale
                                                                              n

                                                                           ti
                                                For      rt Gouve  a Natio J C                            gétiqu

                                                                                          esse,        pement

                                                                                                                         on Ener ement Dur Justi Autres



                                                                                          eun Communi Equi ti lopp
                                                                           r
                                                                           t

                                                           Dépa       nis                                          ansi

                                           cu
                                           i lopp                                                                     Tr Déve

                                                                           Admi
                                           Agr Déve
                                                                                                                                                                 
SECTION            II   -   RESSOURCES                ET    CHARGES            DES      COMPTES 
SPECIAUX             DU     TRESOR 

1.2.1. Comptes    d’affectation      spéciale 

1.2.1.1. Prévisions    des  ressources    et  des  charges    des  CAS  
Les prévisions  des ressources  et  des charges  des  CAS au titre   de la  période  2021-2023,  sont 
présentées dans le graphique ci-après  : 

 
                                                                                                                                                   5

12
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                                               EVOLUTION DES RESSOURCES ET DES PLAFONDS DE CHARGES DDES CAS 
                                                               AU COURS DE LA PEERIODE 2021-2023 (EN MDH)

                                                                                                                                         99 4033 99 053
                                                                                        87 407 86   707
                                       83 329 81   289












                                          2021                                         2022                                        20233

                                                                   Ressources           Plafonds de charges
                                                                                                                                                                                                
L’analyse    de  l’évolution      des   ressources     prévisionnelles       et  des   plafonds     des   charges    des   CAS  au 
cours   de   la   période     2021-2023,     fait    ressortir     une   hausse    importante      entre     2021   et  2023,    sous 
l’effet,    notamment,      de   l’augmentation       des   ressources     affectées     et  chargees   des   CAS  :  « Part   des 
collectivités      territoriales      dans   le  produit     de   la  TVA   », «  Fonds   pour    la  promotion      de  l’emploi     des 
jeunes   », « Fonds    de  promotion      des   investissements       », «  Fonds   d'assainisssement     liquide    et   solide 
et  d'épuration       des  eaux    usées   et  leur    réutillisation     »  et  «  Fonds   pour    le  développement         rural   et 
des  zones   de  montagne     »  . 

1.2.1.2.    Réalisations          des    recettes       et   des    dépenses       des    CAS  
 
1.2.1.2.1.    Recettes      réalisées      par   les   CAS
       
Le  montant     total    des   recettes     réalisées    par   les   CAS  s’établit     à 316.264     MDH  (**) en  2023,   contre 
265.565   MDH   en  2022   et  228.737    MDH  en  2021. 

Le   graphique      ci-après     retrace     l’évolution       des    recettes     des    CAS,   par    nnature,   au   cours    de   la 
période    considérée     :  

                                                           EVOLUTION DES RECETTTES DES CAS PAR NATURE 
                                                             AU COURS DE LA PERRIODE 2021-2023 (EN MDH)


                                                                                                                                          150 3345

                                                                              129 7966
                 115 020                                                                                                                          116 075

                                                                                           99 417

                               78 683

                                                                                                                                                                     49 884
                                             35 033                                                36 352




                                2021                                                    2022                                                     2023


                                        Solde de recettes reporté         Recettes propres            Dotations buudgétaires
                                                                                                                                                                                                

(**) : Mil                                                 
         lions de Dirhams.  

 
              6 

13
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
L’analyse des recettes  des  CAS par  nature révèle  que  les soldes  reportés  de ces  comptes  ont 
enregistré  une hausse notable  entre  2021 et  2023, passant  de 115.020 MDH en 2021 à  150.345 
MDH en 2023, soit une augmentation  annuelle moyenne de plus de  14%. 
Les recettes  propres  affectées  audits  CAS ont,  quant  à elles,  crû de  plus  de 21% en 2023  par 
rapport  à 2021 en raison, notamment, de la forte  augmentation  des recettes  des CAS « Fonds de 
remploi  domanial », « Part  des  collectivités  territoriales   dans  le produit   de  la T.V.A »,  « Fonds 
d’appui à la protection   sociale et  à la cohésion sociale » et  « Fonds spécial relatif  au produit  des 
parts d’impôts  affectées  aux régions », ainsi qu’à l’affectation   de ressources importantes  au CAS 
nouvellement  créé  « Fonds  spécial  pour  la gestion  des  effets  du  tremblement   de terre   ayant 
touché le Royaume du Maroc ».    
Ces recettes propres ont  été réalisées en 2023, essentiellement, par les CAS suivants : 
 

         Part des collectivités territoriales  dans le produit  de la T.V.A                    :    37.834 MDH ;

         Fonds de remploi domanial                                                                          :     27.170 MDH ;

         Fonds spécial pour la gestion des effets du  tremblement  de terre             :    13.234 MDH ;
            ayant touché  le Royaume du Maroc 

         Fonds d’appui à la protection  sociale et à la cohésion sociale                    :     11.378 MDH ;

         Fonds spécial relatif au produit  des parts d’impôts  affectées aux              :      5.745 MDH ;  
            régions 

         Fonds spécial routier                                                                                    :       3.651 MDH ;

         Fonds  solidarité    pour   le   soutien    au   logement,   d’habitat    et         :       2.179 MDH ;
            intégration  urbaine 

         Masse des services financiers                                                                     :       1.542 MDH ;

         Fonds de lutte contre la fraude  douanière                                                   :        1.101 MDH ;

         Fonds national forestier                                                                                :         992 MDH ;

         Fonds national du développement  du sport                                                :         889 MDH ;

         Fonds de solidarité des assurances                                                             :        804  MDH ;

         Compte spécial des dons des pays du Conseil de Coopération  du            :         784 MDH ;
            Golfe 

         Fonds provenant des dépôts du  Trésor                                                      :         778 MDH ;

         Fonds de développement agricole                                                               :         749 MDH ;

         Fonds spécial pour le soutien des juridictions                                              :        705  MDH ;

         Fonds de solidarité interrégionale                                                                :         638 MDH ;

         Fonds de participation  des Forces Armées Royales aux missions             :        504  MDH ;
            de paix, aux actions humanitaires  et de soutien  au titre de  la 
            coopération  internationale 

         Fonds de soutien des prix de certains produits  alimentaires                      :         464 MDH ;

         Fonds de service universel de télécommunications                                     :         423 MDH ;

         Fonds spécial pour la gestion de la pandémie  du Coronavirus                   :         406  MDH.
            "Le Covid-19" 
 

 
                                                                                                                                                   7

14
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
A  noter   que   les  comptes    gérés   par   les  5   ministères    suivants   concentrent     près   de  96%   des  
recettes  propres   réalisées  en  2023  : 

        Le   Ministère   de   l’Economie    et  des   Finances  :  58.058   MDH   (50%   du  total    des  recettes 
           propres)   ;  

        Le  Ministère   de l’Intérieur   : 45.279  MDH  (soit  39%)  ; 

        Le  Ministère   de l’Equipement    et  de l’Eau  : 3.662  MDH  (3%)  ;  

        Le  Ministère   de l’Aménagement     du Territoire    National,   de l’Urbanisme,   de  l’Habitat   et  de la 
           Politique   de  la Ville  : 2.179 MDH (2%)  ;  

        Le  Ministère   de  l’Agriculture,    de  la  Pêche  Maritime,   du  Développement     Rural  et  des  Eaux 
           et  Forêts  : 1.944  MDH (2%).  

S’agissant  des  dotations   budgétaires    versées  aux CAS,  elles ont  connu   une légère   progression   de 
près  de  4%  entre   2021  et  2022,   avant  d’enregistrer     une  hausse   considérable    de  37%  en  2023 
comparativement      à  2022,   due,  principalement,     aux   versements    effectués    à  partir    du  budget 
général   au  profit    du   CAS  nouvellement     créé  : «  Fonds   spécial   pour   la  gestion    des  effets    du 
tremblement     de   terre   ayant    touché   le   Royaume    du   Maroc  »,  ainsi   qu’au   renforcement     des 
ressources   des  CAS  « Fonds  d’appui    à la  protection     sociale  et  à  la  cohésion   sociale  »,  « Fonds 
national   du  développement     du   sport  »,  « Fonds   pour  le  développement      rural  et   des  zones  de 
montagne   » et  « Fonds  de lutte   contre   les effets  des  catastrophes    naturelles  ». 
 
Ces versements   ont  bénéficié   en 2023,  essentiellement,    aux  comptes   suivants  : 

      Fonds  spécial  pour  la  gestion  des  effets  du  tremblement    de  terre         :                6.476  MDH ;
         ayant  touché   le Royaume   du  Maroc 

      Fonds  de  développement    agricole                                                                :                 4.577  MDH ;

      Fonds  d’appui   à la protection    sociale  et  à la cohésion   sociale                 :                4.400   MDH.

      Fonds  de  soutien  à l’initiative    nationale   pour  le développement               :                4.236   MDH ;
         humain 

      Fonds  national   du développement     du  sport                                               :                 3.692  MDH ;

      Fonds  pour  le  développement    rural  et  des  zones de  montagne              :                  3.561 MDH ;

      Fonds  spécial  relatif   au produit   des  parts  d’impôts   affectées   aux          :                 3.255 MDH ;
         régions 

      Fonds  pour  la  promotion   de  l’emploi   des  jeunes                                       :                 2.528 MDH ;

      Fonds  de  lutte  contre   les effets   des catastrophes    naturelles                   :                 2.445  MDH ;

      Financement   des  dépenses  d’équipement     et de  la lutte   contre  le         :                  2.310 MDH ;
         chômage 

      Fonds  spécial  de  la pharmacie   centrale                                                        :                 2.232 MDH ;

      Fonds  d’accompagnement     des  réformes   du transport    routier                 :                2.200  MDH ;
         urbain  et  interurbain 

      Fonds  d'assainissement    liquide  et  solide et   d'épuration    des eaux         :                 1.500  MDH ;
         usées  et leur  réutilisation 

      Part  des collectivités    territoriales    dans  le produit   de  la T.V.A                 :                 1.392 MDH ;

      Fonds  de  promotion   des  investissements                                                    :                   1.353 MDH ;

      Fonds  de  modernisation    de l’administration     publique,   d’appui   à la      :                  1.180 MDH ;
         transition   numérique    et à l’utilisation    de  l’amazighe 


 
             8 

15
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
      Fonds  d’appui   au financement    de l’entrepreneuriat                                    :                   500  MDH ;

      Fonds  national   pour  l’action   culturelle                                                          :                   430   MDH ;

      Fonds  spécial  pour  le  soutien  de  l’administration     et des                          :                      417 MDH.
         établissements    pénitentiaires 
 
1.2.1.2.2.   Dépenses    des  CAS  
 
Le  montant    global   des   dépenses   exécutées   sur   les  CAS  s’est   établi   à  136.192 MDH   en  2023, 
contre  115.220 MDH et  98.941  MDH, respectivement,    en  2022  et  2021. 

En 2023,  les 6  ministères   suivants  ont  réalisé  près  de  89% des  dépenses  globales   des CAS  : 

         Ministère  de  l’Economie   et  des Finances  : 54.413  MDH  (40%  du total   des  dépenses)  ; 

         Ministère  de  l’Intérieur   : 47.766  MDH  (soit  35%)  ; 

         Ministère   de  l'Agriculture,    de  la  Pêche  Maritime,   du  Développement     Rural  et  des  Eaux  et 
           Forêts   : 7.346  MDH (5%)  ; 

         Département    du Chef  du  Gouvernement    : 5.577 MDH  (4%)  ;   

         Ministère  de  l’Education   Nationale,   du  Préscolaire   et des  Sports  : 4.138 MDH  (3%)  ; 

         Ministère  de  l’Equipement    et de  l’Eau  : 3.211 MDH (2%). 

Par ailleurs,   les dépenses   globales   des  CAS ont   été  imputées   en  2023,  à hauteur   d’environ    97%, 
sur les comptes   suivants   : 

      Part  des collectivités    territoriales    dans  le produit   de  la T.V.A                  :              33.347  MDH  ;

      Fonds  de  remploi  domanial                                                                             :              26.403   MDH ;

      Fonds  d’appui   à la protection    sociale  et  à la cohésion   sociale                 :               13.545 MDH ;

      Fonds  spécial  relatif   au produit   des  parts  d’impôts   affectées   aux          :                8.794  MDH ;
         régions 

      Fonds  de  développement    agricole                                                                :                4.544   MDH ;

      Fonds  de  solidarité   des assurances                                                               :                4.500  MDH ;

      Fonds  de  soutien  à l’initiative    nationale   pour  le développement               :                  4.317 MDH ;
         humain 

      Fonds  national   du développement     du  sport                                               :                  4.138 MDH ;

      Fonds  spécial  routier                                                                                        :                  3.198 MDH ;

      Fonds  solidarité   pour  le  soutien  au  logement,   d’habitat   et                      :                 2.645  MDH ;
         intégration    urbaine 

      Fonds  spécial  pour  la  gestion  des  effets  du  tremblement    de  terre         :                2.388  MDH ;
         ayant  touché   le Royaume   du  Maroc 

      Fonds  d’appui   au financement    de l’entrepreneuriat                                     :                 2.226  MDH ;

      Fonds  pour  le  développement    rural  et  des  zones de  montagne              :                  2.192 MDH ;

      Financement   des  dépenses  d'équipement     et de  la lutte   contre  le          :                2.001  MDH ;
         chômage 

      Fonds  spécial  de  la pharmacie   centrale                                                        :                   1.711 MDH ;

      Fonds  pour  la  promotion   de  l’emploi   des  jeunes                                       :                 1.579 MDH ;

 
                                                                                                                                                                9

16
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
      Fonds  de  lutte  contre   les effets  des  catastrophes    naturelles                    :                  1.541 MDH ;

      Fonds  d’accompagnement     des  réformes   du transport    routier                 :                 1.339 MDH ;
         urbain  et  interurbain 

      Fonds  de  participation    des  Forces  Armées  Royales  aux  missions  de    :                  1.229 MDH ;
         paix,  aux actions   humanitaires   et  de  soutien  au  titre  de  la 
         coopération    internationale 

      Masse des  services  financiers                                                                          :                1.200  MDH ;

      Fonds  de  lutte  contre   la fraude   douanière                                                   :                  1.155 MDH ;

      Fonds  spécial  pour  la  gestion  de  la pandémie   du  Coronavirus   "Le         :                 1.075 MDH ;
         Covid-19" 

      Fonds  d'entraide   familiale                                                                                :                 1.050 MDH ; 

      Fonds  de  solidarité   interrégionale                                                                  :                 1.009  MDH ;

      Fonds  de  promotion   des  investissements                                                     :                    876  MDH ;

      Compte   spécial  des dons  des  pays  du  Conseil  de Coopération    du        :                    828  MDH ;
         Golfe 

      Fonds  spécial  pour  le  soutien  de  l’administration     et des                          :                    776 MDH ;
         établissements    pénitentiaires 

      Fonds  national   pour  l’action   culturelle                                                          :                    769  MDH ;

      Fonds  provenant   des  dépôts   du Trésor                                                        :                   749  MDH ;

      Fonds  spécial  pour  le  soutien  des  juridictions                                              :                     710 MDH.

 
1.2.1.2.3.   Report    de  solde   des   CAS 
 
Le report   de  solde   des  CAS  dégagé  à  fin  2023,  se  situe  à  180.072  MDH  contre   150.345  MDH  et 
129.796 MDH, respectivement,     à fin  2022  et  à fin 2021. 
                                                                                                                                                              (En MDH) 

                                   Désignation                                          2021                   2022                      2023 

  Total des recettes                                                               228.737              265.565                 316.264 

  Total des dépenses                                                              98.941               115.220                 136.192 

                 Solde à reporter à l’exercice suivant                    129.796             150.345                  180.072 
 
L’excédent   dégagé   à  fin  2023  a été   réalisé,  à hauteur   de  96%  de  son  montant,   par  les  comptes   
ci-après  : 

      Fonds  de  remploi  domanial                                                                             :               35.415  MDH ;

      Part  des collectivités    territoriales    dans  le produit   de  la TVA                    :             20.868   MDH  ;

      Fonds  spécial  pour  la  gestion  des  effets  du  tremblement    de  terre         :                17.321 MDH ;
         ayant  touché   le Royaume   du  Maroc  

      Compte   spécial  des dons  des  pays  du  Conseil  de Coopération    du        :               10.737  MDH ;
         Golfe 

      Fonds  d’appui   à la protection    sociale  et  à la cohésion   sociale                 :              10.059  MDH  ;

      Masse des  services  financiers                                                                          :                 7.103 MDH  ;

      Fonds  de  soutien  à l’Initiative    nationale   pour  le développement               :                5.847  MDH  ;


 
            10 

17
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
         Humain 

      Fonds  pour  le  développement    rural  et  des  zones de  montagne              :                 4.795  MDH ;

      Fonds  de  gestion  des  risques  afférents   aux  emprunts   des tiers              :                4.504   MDH ;
         garantis   par  l’Etat 

      Fonds  de  service  universel  de  télécommunications                                      :                3.768  MDH  ;

      Fonds  spécial  routier                                                                                        :                 3.737  MDH ;

      Fonds  solidarité   pour  le  soutien  au  logement,   d’habitat   et                      :                 3.632  MDH ;
         intégration    urbaine 

      Fonds  d’accompagnement     des  réformes   du transport    routier                 :                3.594  MDH  ;
         urbain  et  interurbain 

      Fonds  de  solidarité   des assurances                                                               :                3.437  MDH  ;

      Fonds  de  solidarité   interrégionale                                                                  :                  3.316 MDH ;

      Fonds  d’appui   au financement    de l’entrepreneuriat                                     :                 3.277  MDH ;

      Fonds  spécial  de  la pharmacie   centrale                                                        :                 2.352 MDH  ;

      Fonds  national   forestier                                                                                   :                 2.327 MDH  ;

      Fonds  spécial  pour  la  gestion  de  la pandémie   du  Coronavirus                 :                2.282  MDH ;
         "Le  Covid-19" 

      Fonds  national   du développement     du  sport                                               :                 2.254  MDH ;

      Fonds  de  soutien  à la  sûreté  nationale                                                          :                   2.111 MDH ;

      Fonds  spécial  pour  la  mise  en place  des  titres  identitaires                        :                 2.051  MDH ;
         électroniques    et  des titres   de voyage 

      Fonds  de  lutte  contre   les effets  des  catastrophes    naturelles                   :                    2.011 MDH.

      Fonds  de  lutte  contre   la fraude   douanière                                                   :                 2.010 MDH  ;

      Fonds  de  développement    agricole                                                                :                 1.906  MDH ;

      Fonds  d'assainissement    liquide  et  solide et   d'épuration    des eaux          :                  1.837 MDH ;
         usées  et leur  réutilisation 

      Fonds  national   pour  la protection    de  l’environnement    et  du                   :                 1.787 MDH ;
         développement     durable 

      Fonds  spécial  relatif   au produit   des  parts  d’impôts   affectées   aux          :                 1.633 MDH ;
         régions 

      Fonds  spécial  pour  le  soutien  des  juridictions                                              :                 1.298 MDH  ;

      Fonds  de  participation    des  Forces  Armées  Royales  aux  missions  de    :                  1.279 MDH ;
         paix,  aux actions   humanitaires   et  de  soutien  au  titre  de  la 
         coopération    internationale 

      Fonds  pour  la  promotion   de  l’emploi   des  jeunes                                       :                  1.231 MDH ;

      Financement   des  dépenses  d’équipement     et de  la lutte   contre  le         :                  1.223 MDH ;
         chômage 

      Fonds  de  soutien  à la  Gendarmerie   Royale                                                 :                     1.117 MDH.

      Fonds  de  modernisation    de l’administration     publique,   d’appui   à la       :                  1.058 MDH.
         transition   numérique    et à l’utilisation    de  l’amazighe 

 
                                                                                                                                                                11

18
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
1.2.2.  Autres   comptes    spéciaux    du  Trésor          

1.2.2.1.  Comptes   de  financement 
Les comptes de  financement  décrivent  les versements sous forme  de prêts  de durée  supérieure 
à deux ans, ou d’avances  remboursables  de durée  inférieure ou  égale à deux  ans, effectués  par 
l'Etat  sur les  ressources du  Trésor  et accordés  pour  des  raisons  d’intérêt  public.  Ces prêts  et 
avances sont productifs  d’intérêts.  
L’octroi  par l’Etat de  prêts ou d’avances  par l’entremise desdits  comptes,  fait l’objet  d’un contrat 
entre le  Ministère chargé  des finances  et le  bénéficiaire  qui prévoit,  notamment,   le montant  du 
prêt ou de l’avance, la durée, le taux  d’intérêt  ainsi que les modalités de remboursement.  
C’est dans ce cadre  que trois  (03)  opérations  de  remboursement  ont  été enregistrées  au cours 
de la période  2021-2023, émanant des établissements ayant  bénéficié du  financement  du Trésor, 
en l’occurrence   la  société  de  financement   JAIDA,  le  Crédit  Agricole   du  Maroc  (CAM)   et  la 
Société Marocaine d’Assurance à l’Exportation  (SMAEX). 
L’encours   total    des   comptes   de    financement    est   passé   de   230,60   MDH   en   2021   à  
161,81 MDH en 2022 et à 90,79 MDH en 2023, soit une baisse annuelle moyenne de près de 37%. 
 
   Encours des  prêts par bailleurs  de  fonds :  
                                                      
L’analyse de la structure  de  l’encours des prêts  par bailleurs  de fonds, montre  que  l'Agence  des 
États-Unis  pour  le  Développement   International   (USAID)   est  le  principal   créancier  avec  un 
encours en 2023  de  34,30 MDH, soit  37,78% du total,  suivi  par le  Millenium Challenge  Account 
(MCA) pour  un montant  de 29,75 MDH (32,76%), puis  par l’Italie  avec un encours de  26,74 MDH 
(29,46%). 
 
   Encours des prêts  par catégorie   de bénéficiaires  : 
 
L’évolution de  l’encours des prêts par catégorie  de bénéficiaires,  se décline comme suit : 
 
                                                                                                                         Encours (En MDH) 
                                       Bénéficiaires / Années 
                                                                                                                  2021          2022        2023 

 Société de financement JAIDA                                                                177,70       118,06     56,49 


 Crédit Agricole du Maroc (CAM)                                                              26,12         19,88       13,45 


 Société Marocaine d’Assurance à l’Exportation (SMAEX)                       26,78         23,87       20,85 


                                                   Total                                                      230,60        161,81     90,79 

                 
   Recouvrement  des prêts  programmés  en 2024  et 2025  : 
Le  cumul  des   échéances  programmées   dans  le  cadre   de  la   loi  de   finances  pour   l’année 
budgétaire 2024,  s’élève à 45,40 MDH dont  43,08 MDH au titre  du principal  et 2,32 MDH pour les 
intérêts.  
Pour l’année  2025,  le  recouvrement   des  prêts  se  poursuivra  conformément   aux  échéanciers 
convenus avec les établissements débiteurs. 
Les montants  de recouvrement   des prêts  (principal  et  intérêts)  programmés   en 2024  et  2025, 
par catégorie de  bénéficiaires, sont répartis  comme suit :                            


 
           12 

19
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
                                                                                                                                                                            
                                                                                                                                                               (En MDH) 

                                                                                      2024                                                2025 
             Organismes débiteurs 
                                                               Principal       Intérêts          Total        Principal      Intérêts       Total 


 Société de financement JAIDA                33,31            1,17           34,48           3,57            0,56           4,13 


 Crédit Agricole du Maroc (CAM)              6,62             0,35             6,98            6,82            0,15           6,97 


 Société Marocaine d’Assurance à 
                                                                   3,14            0,80             3,94            3,27            0,68           3,95 
 l’Exportation (SMAEX) 


                         Total(*)                            43,08             2,32           45,40           13,66          1,39          15,05 

(*) A noter que les remboursements au titre du principal sont imputés sur les comptes de financement et ceux au titre des intérêts 
    sont imputés sur le budget général. 
 
1.2.2.2.    Comptes     d'adhésion       aux  organismes       internationaux 
                                   
Ces  comptes   décrivent    les   versements   et   les  remboursements     au  titre    de  la  participation     du 
Maroc  aux organismes   internationaux.    Ils  sont  regroupés   en trois   comptes   :  
 
    Compte   d’adhésion    aux institutions     de  Bretton   Woods   : 
                                        
Ce  compte    comptabilise     les   opérations    afférentes     à  l’adhésion    du   Royaume   du   Maroc    aux 
institutions   de  Bretton   Woods,   en  l’occurrence   le  Fonds  Monétaire   International    (FMI),  la  Banque 
Internationale     pour    la    Reconstruction      et   le   Développement       (BIRD),  la   Société    Financière 
Internationale      (SFI),    l’Agence     Multilatérale      de    Garantie     des    Investissements      (MIGA)     et 
l’Association   Internationale    de  Développement    (AID). 
 
Les parts   détenues   par  le Royaume   du  Maroc  dans  le  capital   desdites  institutions,    se  présentent 
comme  suit  :  
      

                               Institutions de Bretton Woods                                        Part du Maroc dans le capital 


  Société financière internationale                                                                                  0,40% 


  Agence multilatérale de garantie des investissements                                                0,39% 


  Association internationale de développement                                                              0,37% 


  Banque internationale pour la reconstruction et le développement                              0,31% 


  Fonds Monétaire International                                                                                      0,19% 

 
    Compte   d’adhésion    aux organismes    arabes  et  islamiques   : 
      
Ce  compte    comptabilise     les   opérations    afférentes     à  l’adhésion    du   Royaume   du   Maroc    aux 
organismes   arabes  et islamiques   suivants  : 
 

 
                                                                                                                                                               13

20
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                                                                                                                                                                    Part du Maroc 
                                                     Organismes arabes et islamiques 
                                                                                                                                                                   dans le capital 

  Banque maghrébine pour l’investissement  et le commerce  extérieur                                                         20,00%*  

  Fonds monétaire arabe (FMA)                                                                                                                        4,68%  

  Société arabe de garantie des investissements  et des Crédits à l’exportation                                              3,29%  

  Fonds arabe pour le développement  économique  et social (FADES)                                                          2,49% 

  Société arabe d’investissement (SAI)                                                                                                              1,79% 

  Société islamique d’assurance des crédits à l’exportation   et de garantie  des investissements                   1,68%  

  Banque arabe de développement  économique en Afrique  (BADEA)                                                            1,57% 

  Société internationale  islamique pour le  financement du commerce                                                            0,59% 

  Fonds BADIR  pour  le développement   des petits   et moyens  projets  (Compte   spécial pour  le 
                                                                                                                                                                          0,79% 
  financement des PME du secteur privé dans les pays arabes/FADES) 
  Banque islamique de développement  (BID)                                                                                                   0,51% 

  Autorité  arabe pour l'investissement  et le développement  agricole  (AAIDA)                                              0,41% 

  Fonds de solidarité islamique  pour le développement                                                                                   0,20% 

  Société islamique pour le développement   du secteur privé                                                                          0,07% 
(*) Dont la part du Trésor est de 8%. 
       
    Compte     d’adhésion      aux  institutions       multilatérales        : 
             
Ce  compte    a  pour    objet   de   comptabiliser       les  opérations      afférentes     à  l’adhésion     du  Royaume     du 
Maroc   aux  institutions      multilatérales       citées   ci-après    : 
 

                                                   Institutions   multilatérales                                                          Part du Maroc dans le 
                                                                                                                                                                  capital 

                                                                          Africa  50 – Développement  de projets                          10,40% 
  Fonds « Africa 50  » 
                                                                          Africa  50 – Financement de projets                                11,30% 

  Fonds de Solidarité Africain  (FSA)                                                                                                         5,00% 


  Banque africaine de développement  (BAD)                                                                                           4,47% 


  Société Schelter Afrique                                                                                                                          2,92% 


  Banque ouest africaine de développement  (BOAD)                                                                               0,75% 


  Banque de développement  des Etats de l’Afrique  centrale (BDEAC)                                                   0,40% 


  Fonds international  pour le développement  agricole  (FIDA)                                                                0,30% 


  Banque africaine d’import-export   (AFREXIMBANK)                                                                             0,22%* 


  Banque asiatique d’investissement  pour les infrastructures  (BAII)                                                       0,005% 

 (*) Dont la part du Trésor est de 0,08%. 
 

 
             14 

21
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
    Exécution      des    dépenses      imputées      sur    les     comptes      d'adhésion      aux     organismes 
      internationaux      au titre   de  la période   2021-2023    et prévisions    pour  la  période   2024-2027     : 
 
Les  montants     des   participations      du   Maroc   versés   au   cours   de   la   période    2021-2023,    aux 
organismes   internationaux,     ainsi  que  les  prévisions    pour   la période    2024-2027,    se  répartissent 
comme  suit  : 

                                                                                                                                                                                                   (En MDH) 

                                                                  Réalisations                                             Prévisions 
             Institutions ou 
               organismes 
                                                     2021         2022           2023          2024           2025         2026          2027 

 Institutions de Bretton Woods    34,82         117,16       100,05        59,27          82,52         5,27             - 

 Organismes arabes et 
                                                    13,67         14,12         102,72        43,34          58,49        58,49         58,49 
 islamiques 

 Institutions multilatérales           345,27       561,06      1.240,04      463,68        612,85      866,89      600,79 

                    Total                       393,76       692,34       1.442,81     566,29        753,86      930,65       659,28 

 
1.2.2.3.    Comptes     d’opérations        monétaires  
       
Cette  catégorie   de  comptes   décrivant    des mouvements    de  fonds  d’origine   monétaire,    comprend 
deux  comptes   intitulés   « Différence   de  change  sur  ventes  et  achats  de devises   » et « Compte   des 
opérations   d’échanges   de taux  d’intérêt    et  de devises  des  emprunts   extérieurs   ». 
 
Les réalisations    des  comptes   d’opérations    monétaires    pour  la  période   2021-2023,   se présentent 
comme  suit  : 
 
                                                                                                                                                                 (En MDH) 

                                                                             2021                             2022                             2023 
                 Intitulé du compte 
                                                                 Recettes   Dépenses    Recettes   Dépenses   Recettes    Dépenses 

 Différence  de  change sur  ventes  et 
                                                                    16,29         15,88         34,29          23,15          7,20           19,60 
 achats de devises  
 Compte des opérations d’échanges de 
 taux   d’intérêt    et   de   devises  des          -                  -                 -                 -                  -                 - 
 emprunts extérieurs 

                           Total                                 16,29         15,88         34,29          23,15          7,20           19,60 

 
1.2.2.4.    Comptes     de   dépenses     sur   dotations  
 
Les comptes    de dépenses   sur  dotations,    qui  sont  au  nombre   de  quatre   (04)   en 2024,   retracent 
des  opérations    relatives   à  une  catégorie    spéciale   de  dépenses   dont   le  financement    est  assuré 
exclusivement   par  des  dotations   budgétaires. 
 
Le montant    des  recettes   réalisées  par   lesdits  comptes,   compte    tenu  du  solde   reporté,   s’élève  à 
38.145 MDH en  2023  contre   37.163 MDH en  2022  et  35.952  MDH en  2021. 
 
Pour  ce  qui  est   des  dépenses   exécutées   sur  les  comptes    en  question,   elles   se sont   établies   à 
14.008  MDH en  2023,  contre  15.238 MDH  et  14.681 MDH, respectivement,    en 2022   et 2021. 

 


 
                                                                                                                                                               15

22
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
CHAPITRE            II  -     ROLE        DES       COMPTES           D’AFFECTATION                   SPECIALE 
DANS       LE     DEVELOPPEMENT                ECCONOMIQUE ET               SOCIAL,          L’APPUI         A 
L’INVESTISSEMENT                ET   LA    PROMOTION            DE   L’EMPLOI 
     
Ce  chapitre     vise   à  présenter     de   manière    détaillée    les   données    comptables     des   Comptes 
d'Affectation     Spéciale   (CAS)  ainsi  que   leurr rôle  dans   le  financement    dees actions  publiques,   en 
fonction   de  leurs  domaines  d'intervention.     Il  permet  également    de mettree  en évidence   les efforts 
budgétaires   engagés   par  l'Etat   pour  soutenir   les  politiques   économiques    et  sociales,  encourager 
l'investissement    et promouvoir    l’emploi. 
 
Au  titre   de  l’année   2023,   les  dépenses   globales   effectuées    dans  le  cadre   des  CST  s’élèvent   à 
159.045,72  MDH, dont   un montant   de  136.1911,89 MDH a été imputé sur  les CAS  (85,63%  du  total).   

A ce  niveau,   la  contribution     des  CAS  dans  les  différentes    politiques   publiques    économiques    et 
sociales  en 2023,  ventilée   par  domaine  d’intervention,     se présente   commee suit :  

             Le développement     territorial                                         : 43.149        MDH,     soit  31,68 % ;
             Le développement     humain  et  social                           : 30.022        MDH,     soit  22,04 % ;
             La promotion    économique    et financière                      : 13.124       MDH,     soit  9,64 % ;
             Le renforcement    des  infrastructures                             : 11.489         MDDH, soit  8,44 % ;
             Le développement     rural,  agricole  et  de  la pêche      : 7.540          MDDH,  soit  5,54 % ;
             Les autres  domaines                                                        : 30.867 MDH,           soit  22,66 % .
  
                   REPARTITION DES REALISATIONS DES CAS PAR DOMAINNES D'INTERVENTION AU TITRE DE LA PERIODE 20021‐2023  (EN MDH)



                                                                                                                          43 149
                                                                   41 318
            37 526


                                                                                                                                                               30 867
                                                                                                                                         30 022
                           27 976

                                                                                  23 119
                                                                                                        21 991


                                                                                                                                 133 124
                                                                          10 0049  10 862                                            11 489
                    9 159
                                  7 481 8 310 8 490                                  7 882                                              7 540



                               2021                                               2022                                               2023


                  DEVELOPPEMENT TERRITORIAL PROMOTION ECONOMIQUE ET FINANCIERE DEVEELOPPEMENT HUMAIN ET SOCIAL

                  RENFORCEMENT DES INFRASTRUCTURES DEVELLOPPEMENT RURAL, AGRICOLE AUTRRES DOMAINES
                                                                        ET DE LA PECHE
                                                                                                                                                                               

SECTION            I   -  DEVELOPPEMENT                       TERRITORIAL   
 
Les   dépenses    des    CAS    intervenant     dans    le    domaine     du   développement       territorial,      en 
l’occurrence    le  compte   «  Part   des  collectivités     territoriales    dans  le  produit     de  la  TVA  »,    « le 
Fonds   spécial   relatif    au  produit     des  parts    d’impôts    affectées    aux   régions    »,  «  le Fonds    de 



 
            16 

23
                                                                                                          RAPPORT  SUR  LES COMPTESS SPECIAUX  DU  TRESOR 
 
 
solidarité       interrégionale          »  et   le   «  Fonds     de   mise    à   niveau     sociale     »,  repréésentent        31,68%    du   total 
des   dépenses      exécutées       en   2023    par    les  CAS. 
                                                                                                           
                                                  EVOLUTION DES RECETTES ET DES DEPENSES VENTILEES PAR COMPTE 
            EVOLUTION DES RECETTES* AU TITRE DE LA PERIODE          EVOLUTION DES DEPENSES AU TITRE DE LA PERIODE 
                                  2021‐2023 (EN MDH)                                                                     2021‐2023 (EN MMDH)


                                                                                                                                                                                 33 347
                                                                                                                                                   32 020
                                                                    54 214                                     28 429
                                       47 008
           38 222




                                                                                                                             9 094                      9 2993
                                                                                                                                                                                           8 794
                  10 808
                                               10 720                 10 427
                                                                                                                                   3
                       2 338 39               3 329                   4 325                                               0                        4
                                                                                                                                                                      0                      1 009
                                                            49                       59                                                                                                          0


                   2021                     2022                    2023                                         2021                      20222                    2023

          Part des collectivités territoriales dans le produits de la TVA            Parts des collectivités territoriales danns le produits de la TVA

          Fonds spécial relatif au produits des parts d'impôts affectées aux régions Fonds spécial relatiive au produits dess parts d'impôts affectées aux régions

          Fonds de solidarité interrégionale                                                      Fonds de solidarité interrégionale

          Fonds de mise à niveau sociale                                                        Fonds de mise à niveau sociale
                                                                                                                                                                                                                      
(*) Compte tenu du solde reporté. 

2.1.1.    Part      des     collectivités              territoriales              dans      le   produit         de    la    TVA 

Le   plafond      prévisionnel         des    ressources       et    des   charges       de   ce   compte       fixxé  par    la   loi   de   finances 
pour    l’année     2023     s’élève     à  37.608,29       MDH,    contre     31.905,35      MDH    en   20222   et  28.504,27       MDH    en 
2021.  

En   2023,     le   plafond       des    charges      dudit      Fonds      a   été   relevé      à   51.469,39      MDH,     contre      37.686,93 
MDH   et   34.252,91     MDH,    respectivement,           en   2022    et   2021. 

Les   programmes          d’emploi        des   dépenses,        compte       tenu     du   relèvement         du    plafond       des    charges 
dudit     compte       et   des   virements        de   crédits      opérés      en   cours     d’année,      fontt    ressortir,       par   nature      et 
par   catégorie       des   collectivités         territoriales         bénéficiaires,         la  répartition        suivvante     : 

                                                                                                                                                                                                       (En  MDH) 

                                              Dotations                                                             2021                       2022                        2023 

 Dotations     globales    (Fonctionnement)       :                                           14.260,47               14.2600,47                 14.260,47

           -   Provinces   et  préfectures                                                              3.108,90                  3.1088,90                  3.108,90 

           -   Communes                                                                                      11.151,57                11.151,57                  11.151,57 

 Dotations     spéciales   (Equipement      et  Soutien)                                   6.377,33                 8.0688,56                   17.221,09

 Dotations     pour  charges    communes                                                      11.145,51               12.2255,27                16.278,87

 Remboursements,      Dégrèvements      et  Restitutions, 
                                                                                                                       2.401,51                 2.9999,87                   3.609,71 
 fiscaux 

 Crédits    de  reports                                                                                        68,09                      132,776                      99,25 

                                                  Total                                                            34.252,91               37.6866,93                 51.469,39

  
 
                                                                                                                                                                                                   17

24
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
En 2023,  les  dotations   globales  de   fonctionnement   bénéficiant   aux  collectivités   territoriales 
concernées  s’élèvent  à  14.260,47 MDH  soit  une  reconduction   du  montant   attribué   en  2022, 
représentant  environ 28% du  total  de la part  de la  TVA affectée  aux collectivités   territoriales  et 
destinée à contribuer  au financement des dépenses de fonctionnement   desdites collectivités.  
Quant aux dotations  spéciales (équipement  et soutien),  le montant  attribué  s’est élevé en 2023 à 
17.221,09 MDH, contre 8.068,56 MDH en 2022, soit 33% du total de la part de  la TVA affectée aux 
collectivités   territoriales.   Ces  dotations   ont  permis   le  financement   des  actions   à  caractère 
exceptionnel  ou conjoncturel  liées aux  efforts  desdites collectivités   en matière d’équipement   en 
infrastructures,   de  mise  à  niveau  et   de  développement   urbain   ainsi  que  de  protection    de 
l’environnement. 
De leur part,  les  dotations  pour  charges  communes se sont  élevées  à 16.278,87 MDH en 2023, 
contre  12.225,27 MDH en 2022,  soit  environ   32% du  total  de  la  part  de  la  TVA affectée   aux 
collectivités  territoriales.   Elles ont  permis  de couvrir   les dépenses  communes  aux collectivités 
territoriales   ainsi   que   celles   afférentes    à  leur   contribution     au   financement   de   certains 
programmes de développement   socio-économiques structurants. 
Quant aux réalisations  de l’année  2023, les recettes  se sont  élevées, compte  non tenu  du solde 
reporté, à 39.226,34 MDH, contre 37.215,25 MDH en 2022 et 32.966,44 MDH en 2021.  
En ce  qui   concerne  les  dépenses,  elles  se sont   élevées  à  33.346,78  MDH en  2023,   contre 
32.020,26  MDH  en   2022  et   28.428,91  MDH  en  2021.  Lesdites  dépenses   comprennent   les 
dépenses réalisées au titre  des remboursements,  dégrèvements  et  restitutions,  fiscaux relatifs  à 
la TVA, qui  se sont  élevées à 4.911 MDH en 2023, contre  5.007  MDH en 2022  et 3.796  MDH en 
2021. 
 
Le plafond  des charges,  prévu par  la loi  de  finances pour  l’année 2024,  est de  40.691,76 MDH, 
réparti comme  suit : 
                                                                                                                                                                                                          (En MDH)               

                                                                            Prévisions loi de  Plafond après 
                              Dotations                                                                                                 % 
                                                                              finances 2024      relèvement 

 Dotations globales (Fonctionnement)                     14.260,47          14.260,47                 24% 

 Dotations Spéciales (Equipement et Soutien)         9.151,06            18.174,97                 31% 

 Dotations pour charges communes                        13.835,93          22.835,92                 39% 

 Remboursements, dégrèvements et restitutions, 
                                                                                 3.444,30             3.444,30                   6% 
 fiscaux 

 Crédits de reports                                                         -                      69,09                        - 


                                 Total                                        40.691,76          58.784,75                100% 


2.1.2.  Fonds   spécial   relatif    au  produit    des  parts   d’impôts     affectées    aux  régions 

Le plafond  prévisionnel  des ressources et  des charges  de ce  compte  fixé  par la loi  de  finances 
pour l’année  2023 s’est  élevé à 9  MMDH, soit le même  montant  prévu  pour  les années 2022  et 
2021. 
Le plafond des charges  dudit Fonds  a été relevé, en 2023, à 9.626,32 MDH, contre  9.862,23 MDH 
et 10.535,44 MDH, respectivement, en 2022 et 2021. 
Les recettes  réalisées au titre   dudit  compte  ont  atteint,   hors solde  reporté,  9.000,00   MDH en 
2023, contre 9.005,88  MDH en 2022 et  9.009,76  MDH en 2021. 

 
           18 

25
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
Quant  aux   dépenses,   elles  se  sont   élevées  en  2023   à  8.793,53   MDH,  contre   9.293,45    MDH  et          
9.093,68  MDH,  respectivement,    en  2022  et 2021.  

Lesdites   dépenses   comprennent     les  versements    aux   régions   au   titre   de   leurs  parts   dans   les 
recettes   dudit   compte    ainsi  que   les  dépenses   au  titre   des   remboursements,    dégrèvements     et 
restitutions,    fiscaux  relatifs   à  l’impôt   sur  les  sociétés   (IS)  et  l’impôt   sur  le  revenu   (IR)  évalués  à 
82,44  MDH en  2023,  à 40,87  MDH  en 2022  et  à  32,26  MDH  en 2021. 

La  répartition    des   crédits   programmés     et  des  versements    réalisés,   par  région,    durant   l’année  
2023,  se présente   comme  suit  : 
                                                                                                                                                                                                         (En MDH) 

                                                                                   Prévisions loi de finances 
                                 Régions                                                                                 Ressources affectées en 2023 
                                                                                        pour l’année 2023 


 Casablanca-Settat                                                                 1.130,65                                 1.086,20 


 Marrakech-Safi                                                                       903,43                                     872,59 


 Rabat-Salé-Kénitra                                                                 879,01                                     848,12 


  Fès-Meknès                                                                           873,71                                    844,54 


  Tanger-Tétouan-Al Hoceima                                                 765,49                                     740,68 


  Oriental                                                                                  735,06                                     716,60 


 Souss-Massa                                                                          723,15                                    703,05 


 Béni Mellal-Khénifra                                                                667,79                                    648,99 


 Drâa-Tafilalet                                                                           661,58                                    647,15 

 Laayoune-Sakia El Hamra                                                      597,83                                    590,17 


 Dakhla-Oued Eddahab                                                           559,72                                     553,53 


 Guelmim-Oued Noun                                                              466,15                                    459,47 


                               Sous-total                                                8.963,57                                  8.711,09 


 Dépenses  relatives aux Remboursements, 
                                                                                                  36,43                                      82,44 
 dégrèvement et restitutions, fiscaux 


                                   Total                                                    9.000,00                                  8.793,53 

                                                                                                                                                                               
Le plafond   des  charges   prévu  par  la  loi  de  finances  pour   l’année  2024   au niveau   dudit   compte 
s’est établi   à 9 MMDH  et  il se réparti,   entre  les régions,   comme  suit  :    
 
 

 
                                                                                                                                                               19

26
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                                                                                  Prévisions loi de finances 2024 (En MDH) 
                                                                                                                                                                  Part 
                            Régions                                                     Taxe          Contribution                           Régions 
                                                                          IS/IR         Contrats            Budget            TOTAL           (%) 
                                                                                         Assurances        Général 

Casablanca-Settat                                           646,27          131,21            357,89            1.135,37        13% 

Marrakech-Safi                                                526,36          86,44               291,49           904,29            10% 

Fès-Meknès                                                     510,44          81,01              282,67             874,13          10% 

Rabat-Salé-Kénitra                                          510,24          87,59              282,57            880,40           10% 

Tanger-Tétouan-Al Hoceima                           448,82          68,01               248,55            765,38           8% 

Oriental                                                            442,39          44,25              244,99             731,63           8% 

Souss-Massa                                                   431,08          51,18              238,72            720,98            8% 

Drâa-Tafilalet                                                   402,81          31,26              223,07             657,14           7% 

Béni Mellal-Khénifra                                         397,57         48,20               220,17            665,94           7% 

Laayoune-Sakia El Hamra                               375,48          7,04                207,93            590,45            7% 

Dakhla-Oued Eddahab                                    353,63           2,73                195,84           552,20            6% 

Guelmim-Oued Noun                                       291,26           8,29                161,29           460,84            5% 
Dépenses communes relatives aux 
Remboursements, dégrèvement et                      -                  -                        -                  61,25             1% 
restitutions, fiscaux 

                              Total                                 5.336,35        647,21            2.955,18        9.000,00         100% 


    
Ces crédits   contribuent    au  financement    des  interventions    des  régions   dans  divers   domaines 
relevant  de  leurs  compétences. 

2.1.3.   Fonds    de  solidarité       interrégionale  

Ce Fonds,  prévu   par  l’article   142 de  la Constitution,    a  été  créé  par  la loi  de  finances  pour   l’année 
2016, en   vue  de  comptabiliser     les  opérations    visant   à  réduire    les  disparités   entre   les  régions, 
conformément    à la  législation   et à  la réglementation     en vigueur. 
 
Les principales   ressources   dudit  compte    sont  : 
 
         10% du produit   de  la part  de  l’IS affecté   aux  régions  ; 
         10% du produit   de  la part  de  l’IR affecté   aux  régions  ; 
         la part  revenant   à ce  compte   du produit    de la  taxe  sur les contrats    d’assurances  ; 
         10% des contributions    du  budget   de  l’Etat  prévues  au  profit   des régions. 
            
L’affectation    des crédits   programmés    à cet  effet   aux régions   se fait  selon  les  critères   mentionnés 
ci-dessous  :  
 
       L’indice   de  développement    humain   ; 
       Le  produit   intérieur   brut  par  habitant   ; 
       Le  nombre   de chômeurs   ; 
       Le  nombre   d’habitants   en  milieu  rural  ; 
       Le  nombre   d’habitants   en  périphérie   urbaine  ; 
       La  nature  des  projets   financés  suivant  les  priorités   des  politiques   publiques. 
 



 
            20 

27
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
En 2023, le plafond des charges dudit  Fonds a été établi  à 1.000 MDH, maintenu au même niveau 
qu'en 2022 et 2021. 
 
Les recettes enregistrées  au niveau de ce compte,  hors solde à reporter,  se sont élevées lors des 
années 2023, 2022 et 2021, respectivement, à  1.000 MDH, 994,12 MDH et 990,24 MDH.  
 
Quant aux  dépenses réalisées sur  ce compte,  elles  ont  atteint  1.009,09  MDH en 2023  dont  un 
montant  de 1.000 MDH a  été versé au budget   général, représentant  la contribution   des régions 
au « Fonds spécial pour  la gestion des  effets du  tremblement  de terre  ayant touché  le Royaume 
du  Maroc  »,  contre   4,32  MDH  en  2022   et  3,28  MDH  en  2021  au  titre   des  dépenses  des 
remboursements, dégrèvements  et restitutions,  fiscaux. 
 
Aussi, en 2024, un montant  de 500  MDH est destiné  à être versé à partir  dudit  Fonds  au budget 
général, représentant la contribution   des régions  au financement du  chantier de la généralisation 
de la Protection  Sociale, dont une 1ère tranche de 300  MDH est déjà versée. 

2.1.4.  Fonds   de  mise  à niveau    sociale  

Le «  Fonds  de   mise  à niveau   sociale  » a  été   créé  par  la  loi  de  finances  de  l’année  2016, 
conformément  à la  Constitution   de 2011 et aux dispositions  de  l’article  229  de la  loi organique   
n° 111-14 relative aux  régions,  en vue  de  résorber   les déficits   en  matière  de  développement 
humain, d’infrastructures  de base et d’équipements  divers constatés  dans certaines régions. 
 
Les principales ressources de ce compte  sont  : 
 
        Les versements du budget  général ; 
        Les sommes  versées  par les  collectivités   territoriales,   les établissements  et  entreprises 
          publics  pour la réalisation  d’opérations  de mise à niveau sociale des régions ; 
        Les participations  diverses ; 
        Les recettes diverses ; 
        Les dons et legs. 
                 
En ce qui concerne les dépenses, elles concernent essentiellement  : 
        Les dépenses afférentes à l’approvisionnement  en eau potable  et en électricité  ; 
        Les dépenses afférentes à la résorption  de l’habitat  insalubre ; 
        Les dépenses afférentes aux programmes  de santé ; 
        Les dépenses afférentes aux programmes  relatifs à l’éducation  ; 
        Les  dépenses   afférentes    à   la   réalisation   des   réseaux   routiers    et   des   voies    de 
          communication  ; 
        Les versements au budget  général. 
La répartition,  par région, des recettes  dudit Fonds  s’opère sur la base des critères suivants :  
        Le produit  intérieur brut  par habitant  ;  
        Le nombre des habitants  en milieu rural ; 
        Le volume des investissements publics  réalisés au niveau de la région ; 
        Le taux de précarité  au niveau de la région ; 
        La nature des projets  à financer. 
 
Depuis l’année  2018, ce compte   a bénéficié  d’une  dotation   annuelle de  10 MDH au  titre  de  la 
contribution  du budget  général. 
 
 

 
                                                                                                                                                  21

28
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
SECTION               II    -   DEVELOPPEMENT                            HUMAIN              ET      SOCIAL 
Les   recettes      et   les    dépenses     effectuées par          les   comptes      intervenantt       dans    le   domaine      du 
développement       humain    et  social,   au  titre   de   la période     2021-2023,    se  préssentent    comme    suit : 
 
                   RECETTES* ET DEPENSES REALISEES AU NIVEAU DES PRINCIPAUX CAS INTERVENANT DANS LE DOMAINE HHUMAIN ET SOCIAL 
                                                                    AU TITRE DE L'EEXCERCICE 2023 (EN MDH)




                                                                                                                                                                                     23 603
  Fonds d'appui à la protection sociale et à la cohésion sociale
                                                                                                                                             133  545



    Fonds spécial pour la gestion des effets du tremblement de                                                                   19 709
                terre ayant touché le Royaume du Maroc                2 388



                    Fonds de soutien à l'initiative nationale pour le                                  10 164
                                   développement humain                                 4 317



      Fonds solidarité ppour le soutien au logement, d'habitat et               6 277
                               intégration urbaine                                      2 645



                                                                                                        4 062
                               Fonds spécial de la pharmacie centrale
                                                                                               1 711



  Fonds spécial pour la gestion de la pandémie du Coronavirus  3 358
                                 "Le Covid‐19"                                    1 075



                                                                                                     3 258
                                                                    Autres CAS
                                                                                             1 290



        Financement des dépenses d'équipement et  de la lutte     3 224
                                 contre le chômage
                                                                                                2 001



                                                                                              1 352
                                                Fonds d'entraide familiale
                                                                                            1 050




                                                               Recettes                        Dépenses
                                                                                                                                                                                                 
(*) Compte tenu du solde reporté. 


 
             22 

29
                                                                                                          RAPPORT  SUR  LES COMPTESS SPECIAUX  DU  TRESOR 
 
 
 
                           EVOLUTION DES RECETTES* ET DES DEPENSES DES CAAS INTERVENANT DANS LE DOMAINE HUMAIN ETT SOCIAL AU TITRE DE LA 
                                                                                         PERIOODE 2021‐2023 (EN MDH)

                                                                                                                                                             755  007



                                50 054                                                    448 833


                                                     27 976                                                                                                               30 022
                                                                                                                 23 119





                                      2021                                                           2022                                                           2023


                                                                                    Recettees                   Dépenses
                                                                                                                                                                                                                     
   (*) Compte tenu du solde reporté. 

2.2.1.     Fonds        de   soutien         à   l’initiative            nationale           pour      le    développement                 humain  

Les   recettes      et    les   dépenses      du    Fonds     de   soutien      à  l’INDH     ont    enregistréé,      au   titre     de   la   période 
2021-2023,       l’évolution       suivante       : 
 
                        EVOLUTION DES RECETTES* ET DES DEPENSES DU FSINDH AU TITRE DE LA PERIODE 2021‐20023 (EN MDH)



                                                                                          10 3381,24                                                  100 163,55
                        9 437,01



                                                                                                               4 730,78                                                     4 316,93
                                           3 344,34




                                   2021                                                            2022                                                           2023


                                                                                    Recettess            Dépenses
                                                                                                                                                                                                                      
  (*) Compte tenu du solde reporté. 
 
     Réalisations             financières            du     Fonds         de     soutien          à    l’INDH        au      titre        de     la     période 
        2021-2023         : 

Les   réalisations       financières        dudit     Fonds,     se  présentent        comme      suit   :                                                                                    

                                                                                                           
                                                                                                                                                                                                    (En MDH) 
                                                                                                                                                                 Emissions 
                          Crédits            Reports           Total  des                                                Taux               SSur le total              Taux 
   Années                                                                                   Engagement 
                        délégués         de  crédits           crédits                                          d’Engagement         ddes crédits         d’Emission 
                                                                                                                                                               ddisponibles 

     2021            4.797,41          2.469,41          7.266,80               6.102,29                     84%                  3.343,55                  46%


     2022            5.575,91          2.719,45          8.295,36               7.414,63                     89%                  4.729,71                  57%


     2023            5.568,77          2.665,09          8.233,86               7.197,08                     87%                  4.316,38                  52%

 
                                                                                                                                                                                                   23

30
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
       
    Bilan   des  programmes     financés    et  réalisés   au  titre   de  la  période    2021-2023    : 
 
1-Rattrapage  des déficits   en  infrastructures   et  services  de  base dans les  territoires   sous  équipés  : 

Au cours   de la  période   2021-2023,  1.576 projets   ont   été réalisés   dans le  cadre  de  ce  programme, 
pour  un  montant   total   d’environ   2.111,98 MDH, dont  la  contribution    du  Fonds  de  soutien   à l’INDH 
est de  1.873,72 MDH. 

La répartition    des projets   réalisés  par  année  et par  région,   se présente   comme  suit  : 

       a.   Répartition     annuelle   : 
                                                                                                                                                             (En MDH) 
                                                                                                                                             Part du Fonds de 
                     Années                          Nombre de projets                 Coût global 
                                                                                                                                              soutien à INDH 

                       2021                                        476                                660,80                             591,36 

                       2022                                        678                                 781,85                            681,01 

                       2023                                        422                                669,33                             601,35 

                      Total                                        1.576                              2.111,98                           1.873,72 

 

       b.   Répartition     régionale   : 
                                                                                                                                                              (En MDH)           
                                                                                                                                             Part du Fonds de 
                     régions                           Nombre de projets                Coût global 
                                                                                                                                              soutien à INDH 

  Casablanca-Settat                                       302                                 112,20                            100,77 

  Beni Mellal-Khénifra                                     279                                473,27                            332,98 

  Marrakech-Safi                                             223                                328,03                            324,47 

  Fès-Meknès                                                 201                                 393,81                            356,43 

  Rabat-Salé-Kénitra                                       118                                138,26                             126,11 

  Drâa-Tafilalet                                                113                                124,97                             119,77 

  Tanger- Tétouan- Al Hoceima                      109                                210,40                             197,15 

  Oriental                                                         103                                236,45                            230,95 

  Souss-Massa                                                78                                  64,72                               55,80 

  Laâyoune-Sakia El Hamra                            22                                   8,82                                8,72 

  Guelmim-Oued Noun                                    19                                   18,18                              17,71 

  Dakhla-Oued Eddahab                                  9                                    2,86                                 2,86 

                      Total                                        1.576                              2.111,98                           1.873,72 

 

En  termes   d’investissement,     le  secteur   de  désenclavement     routier    représente   39%   du  budget 
global   alloué,  suivi   du  secteur   de   l’éducation    avec  20%,  l’adduction     en  eau  potable    avec  19%, 
l’électrification    rurale  à  15% et la santé  avec  7%.         

 
            24 

31
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
2- Accompagnement      des personnes   en  situation    de  précarité   :  

Dans le  cadre  de la  mise  en œuvre  de  ce  programme,   4.064   projets/actions     ont  été  programmés 
au  titre   de   la  période    2021-2023,   avec   un   montant    global    d’environ    3.007,95    MDH,  dont   la 
contribution    du  Fonds  de soutien   à l’INDH  est  de 1.787,69  MDH.  

La répartition    des projets   réalisés  par  année  et par  région,   se présente   comme  suit  : 

       a.   Répartition     annuelle   : 
                                                                                                                                                             (En MDH) 

                                                                                                                                             Part du Fonds de 
                     Années                          Nombre de projets                 Coût global 
                                                                                                                                              soutien à INDH 

                       2021                                       1.224                             1.105,79                           555,31 

                       2022                                       1.304                               918,83                            586,41 

                       2023                                       1.536                              983,33                            645,97 

                      Total                                       4.064                              3.007,95                         1.787,69 

 

       b.   Répartition     régionale   : 
                                                                                                                                                              (En MDH)           

                                                                                                                                             Part du Fonds de 
                    Régions                          Nombre de projets                 Coût global 
                                                                                                                                              soutien à INDH 

  Casablanca-Settat                                       844                                 911,72                            368,76 

  Marrakech-Safi                                            487                                 213,82                             211,18 

  Rabat-Salé-Kénitra                                      450                                 291,94                            231,63 

  Tanger-Tétouan-Al Hoceima                       437                                 194,12                            169,53 

  Fès-Meknès                                                 418                                 213,68                            191,06 

  Oriental                                                        386                                 195,53                            122,62 

  Souss-Massa                                               267                                628,47                             178,16 

  Béni Mellal-Khénifra                                     255                                 121,59                            109,11 

  Drâa-Tafilalet                                                191                                 89,35                              89,35 

  Laâyoune-Sakia El Hamra                           135                                 46,18                              37,47 

  Dakhla-Oued Eddahab                                100                                 24,00                               23,85 

  Guelmim-Oued Noun                                    94                                  77,55                              54,97 


                      Total                                       4.064                              3.007,95                         1.787,69 

 

Les  projets     de   construction     et   d’équipement      des   centres    d’accueil    représentent      56%  des 
investissements,   suivis  par  les  subventions    de fonctionnement      desdits  centres   avec  29%,  la mise 
à niveau  à hauteur   de 13%, et près  de  2% alloués  aux enquêtes,   études  et  formations. 

 
                                                                                                                                                               25

32
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
3- Amélioration   du revenu  et inclusion  économique  des jeunes : 

Ce programme a permis  la réalisation de 15.090 projets  pour  un coût global  de 3,67 MMDH, dont 
la contribution  du Fonds  de soutien à l’INDH est  de 2,53 MDH, ayant bénéficié à plus de  385.000 
personnes sur l’échelle nationale. 

       Plateformes     des  jeunes   : 

Durant  la  période  2019-2023,  135 plateformes   des  jeunes ont   été  mises en  place  au  niveau 
national  (76  plateformes   Préfectorales/Provinciales    et  59  annexes  réparties  dans  toutes   les 
régions    du    Royaume).   Par    ailleurs,    il    est   important      de   signaler    que    16   espaces 
d'accompagnement   ont  été  créés  par  des  prestataires  de  services  d'entrepreneuriat   dans  le 
cadre du projet  mis en œuvre par  l'INDH dans la région de  Marrakech-Safi, en partenariat  avec la 
Banque Mondiale. 
 
       Aide   à l’employabilité       des  jeunes  : 

Quant à  l’axe « Soutien  à l’employabilité   des  jeunes », 197 projets  ont  été  initiés  au niveau  de           
51 Préfectures/Provinces  sur  la  période  2021-2023 avec  un  budget  total   de  131 MDH, dont la 
contribution   dudit  Fonds  est de  94  MDH. Ces projets  ont  concerné  la  formation   technique  et 
comportementale  des  jeunes ainsi  que l’accompagnement   à  l’insertion  dans le  but  d’améliorer 
leur employabilité.  
Par ailleurs, le nombre  des jeunes  accompagnés a  atteint  16.151 jeunes formés, 5.702 insérés en 
emploi et 4.506  maintenus en emploi  sur une période d’un à trois  mois. 

       Appui    à l’entrepreneuriat       chez  les  jeunes  : 

Dans le cadre de  la mise en œuvre  de l’axe « Appui  à l’entrepreneuriat   chez les jeunes », 10.836 
projets  ont été  réalisés sur  la période  2021-2023  pour un  investissement  de 1,7 MMDH, dont  la 
part de  l’lNDH s’élève à  1,3 MMDH. le nombre des jeunes accompagnés  a atteint   42.400  jeunes 
(31.695 en pré-création et  10.705 en post-création)  au total  dans toutes  les régions du Royaume. 
23% des  projets  appuyés  sont  portés   par  des femmes.  Cela  témoigne  de  l’intérêt   porté  par 
l’INDH à l’entrepreneuriat   féminin  en favorisant   l’approche  genre dans  la perspective   d’assurer 
davantage d’inclusion  socio-économique. 
       Amélioration      du  revenu   : 

Au  cours  de  la  période  2021-2023,  67  études  de  diagnostic   des  chaines  de  valeur  ont  été 
réalisées dans le cadre de l'axe « Amélioration  du revenu  ». Ces études ont permis d’identifier   les 
chaînes de valeurs porteuses d’opportunités  de croissance  et d’emplois pour  les jeunes. 
Dans ce  sens,  3.855 projets   ont  été  validés   par  les  Comités  Préfectoral  de  Développement 
Humain (CPDHs) pour un montant  total  de 1,45 MMDH, dont la part de l’lNDH s’élève à 784 MDH. 
 
4- Impulsion  du capital  humain  des générations  montantes  : 

       Santé   de  la mère   et  de  l’enfant   : 

S’agissant de l’amélioration  de la santé  et nutrition   maternelles et  infantiles en luttant   contre  les 
freins et barrières  du développement  de  la petite  enfance, 1.165 projets/actions ont  été exécutés 
durant la période  2021-2023 avec un  montant  global de  566 MDH, dont  la part de  l’lNDH s’élève 
à 509  MDH. En  outre  les interventions   de  cet  axe concernent   principalement  la  construction, 
l’équipement, le soutien  au fonctionnement  des Dar Al  Oumouma, l’aménagement  des structures 
de santé,  l’acquisition  des  ambulances, l’appui  à la  nutrition,  la  mise  en place  du  dispositif  de 


 
           26 

33
                                                                                  RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
    
    
   santé communautaire  dans 14 Provinces pilotes et  la sensibilisation pour  le changement  social et 
   comportemental.                                                                                                                                                                                                    

           Soutien   au  préscolaire    dans  le  milieu   rural  : 

   Dans le cadre de cet  axe et durant  la période 2019-2023, plus de  10.100 unités de préscolaire ont 
   été programmées  pour  un investissement  de  3,7 MMDH. A cet  effet, le  bilan des  réalisations au 
   titre  du même période  fait ressortir  les éléments suivants : 

           Réalisation  et  mise en  service  de  8.500  unités  de  préscolaire, qui  ont   accueilli  environ 
              302.000  enfants ;  
           Recrutement  de plus de 9.400  éducateurs et  éducatrices issus des douars ciblés. 

           Appui   à l’éducation     et  à l’épanouissement      de  l’enfant    : 

   Durant la période  2021-2023, l'INDH a réalisé 3.328 projets  pour  un montant  total  de 3.510 MDH, 
   visant  à  soutenir  l’éducation   et  l’épanouissement   des  enfants.  Plus de  1.100 projets   ont  été 
   programmés  à Dar Talib(a)  ainsi que l’acquisition  d’environ  1.250 véhicules de transport  scolaire, 
   améliorant  l’accès  à  l’éducation,   notamment   pour  les  filles  en  milieu  rural.  Environ  362.000 
   élèves ont  bénéficié de  soutien scolaire  gratuit  en langue française  et en  mathématiques, tandis 
   que des activités  parascolaires et de santé scolaire  ont été promues.  De plus, environ 4,6 millions 
   d'élèves/an  ont   bénéficié  des  fournitures  scolaires  grâce  à  l'Initiative   Royale  « un  million  de 
   cartables ». 

           Les  réalisations     financières     de  l’INDH   à fin  avril   2024    : 
                
   La situation  des crédits  et  de l’exécution  des dépenses (taux  d’engagement  et  taux  d’émission) 
   par programme,  se présentent comme  suit : 
                                                                                                                                                         (En MDH) 

                                       Crédits                      Crédits                                  Taux                             Taux 
        Programmes                          Reports                      Engagements 
                                     délégués                  disponibles                       d'engagement Émissions 
                                                                                                                                                       d'émission 

Impulsion du capital 
humain des générations 746,03    947,24      1.693,27        989,68              58%           124,09         7% 
montantes 

Amélioration du revenu 
et inclusion économique 699,67     561,41     1.261,08        569,71             45%            31,43          3% 
des jeunes 

Accompagnement des 
personnes en situation     505        421,24      926,24           455,21             49%            36,14          4% 
de précarité 

Soutien à la mise en 
                                        111,98     32,27        144,25          40,73               28%             5,08           4% 
œuvre de l’INDH 

Rattrapage des déficits 
en infrastructures et 
                                         9,09       870,96      880,05           873,84             99%            59,72          7% 
services de base dans les 
territoires sous équipés 


             Total                 2.071,77  2.833,12   4.904,89        2.929,17           60%           256,46         5% 

    
                                                                                                                                                     27

34
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
2.2.2.      Fonds        solidarité          pour       le    soutien         au    logement,          d’habitat           et     intégration 
            urbaine  

L’évolution      des    recettes      et   des   dépenses dudit          Fonds    au   titre     de   la   période      2021-2023     se 
présente    comme    suit   : 
 
                           EVOLUTION DES RECETTES* ET DES DEPENSEES DU FONFS AU TITRE DE LA PERIODE 20211‐2023 (EN MDH)



                           7 195,56                                         7 0110,88
                                                                                                                                          6 2777,17





                                                                                                  2 912,39
                                                                                                                                                          2 644,88
                                          2 399,12





                                    2021                                                2022                                                2023

                                                                                  Reccettes Dépenses
                                                                                                                                                                                                 
(*) Compte tenu du solde reporté. 
 
L’évolution      de   la   contribution        du   Fonds     solidarité      pour    le   soutien     au   logement,      d’habitat      et 
intégration      urbaine    aux   programmes       de   lutte    contre    l’habitat     iinsalubre    eet au   programme      de   la 
politique     de  la ville   au  cours   de   la période     2021-2023,    est  retracé    dans   le  graphique     ci-après    :
  
                               CONTRIBUTION DU FONDS AU PROGRAMME DE LUTTE CONTRE L'HABITAT INSALUBRRE (EN MDH)





                                                                                          2 912,32
                             2 399,11                                                                                                2 4844,92 2 644,47

                                                                                  2 3996,69



                     1 294,42
                                       1 104,69

                                                                                                    515,63
                                                                                                                                                                 159,55


                                2021                                                    2022                                                     2023

                                          Programmes consolidés           Nouveaux programmes             Tootal programmes
                                                                                                                                                                                                
 
Le  programme      prévisionnel      de  financement       dudit    Fonds   pour    l’année   2024,    se  présente    comme 
suit  :                                                                                                                                                                                                
                                                                                                                                                                                                         


 
             28 

35
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
                                                                                                                                                                               (En MDH) 
                                                                                                                                                                     Consolidation 
                                                                                                                                        Subvvention 
                                                                                                          Subvention                                            du reste  à 
                                                                                    Nombre                                         FSSSLHIU 
                            Programmes                                                            FSSLHIU                                          débloquer  en 
                                                                                d’opérations                                 débloqquée à fin 
                                                                                                               Totale                                                 2024 et 
                                                                                                                                             20023 
                                                                                                                                                                         ultérieurs 

  Politique de la ville                                                        163               11.156,95             6.5999,88               4.557,07 

  Restructuration  des quartiers d’habitat  non 
                                                                                       298               7.626,00                5.9336,60               1.689,40 
  réglementaire et  mise à niveau urbaine 

  Villes sans bidonvilles                                                   77                 6.013,99               4.7330,99                1.282,99 

  Provinces du sud                                                            2                  1.851,99               1.7666,55                 85,44 

  Habitat menaçant ruine                                                 44                1.650,00                1.0330,46                 619,85

  Avances pour l’aménagement  foncier                           7                 1.480,00                1.2996,03                 183,97

  Défense nationale                                                           1                  600,00                  4000,00                  200,00

  Tissus anciens                                                              24                   581,71                  4556,51                  125,20

  Séisme AL Haouz                                                          6                   399,07                    477,00                   352,04


  Programme d’urgence                                                    4                    50,41                    477,08                     3,33 


  Zones à aménagement progressif                                 11                  43,42                     299,45                    13,97 

  Etudes                                                                            4                     9,95                      2,,00                        7,95 

                                   Total                                            641               31.463,49             22.3342,55               9.121,21


2.2.3.     Fonds     de   soutien       des    prix    de   certains       produits        alimentairres  

Les  recettes      et   les   dépenses     du   Fonds    de   soutien     des   prix    de   certains     produits      alimentaires 
(FSP)   ont  connu    un  accroissement       annuel   moyen,    respectivement,        de  20,,69%   et  0,03%   durant    la 
période    2021-2023.  

 

                               EVOLUTION DES RECETTES* ET DES DEPENSES DU FSP AU TITRE DE LA PERIODE 2021‐2023 (EN MDH)


                                                                                                                                               7764,60

                                                                                   6001,55
                       524,94


                                        300,84                                                   301                                                       301





                                 2021                                                    2022                                                    2023
                                                                               Recetttes       Dépenses
 (*) Compte tenu du solde reporté. 
 
                                                                                                                                                                               29

36
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 
Les recettes   cumulées   du FSP  ont  atteint   environ   765  MDH  en 2023  conttre  environ   602   MDH en 
2022  enregistrant    ainsi  une  hausse  de  27%.. Cette   hausse  est  due,  essentiellement,    à  la  montée 
des recettes    réalisées  au  cours  de  l’année  2023   s’élevant   à 464   MDH  contre   377  MDH  en 2022, 
soit  une  augmentation    de  23%, et ce,   en  raiison de  l’évolution    concomitante     des importations     et 
du cours  mondial   du  sucre  brut. 
 
A ce titre,   les importations     du sucre  brut,  ont   connu  une augmentation     importante    pour  atteindre 
1.036 KT en  2023,  en  hausse  de 25% par  rapport    à l’année  2022  et  de  69  % par  rapport   à l’année 
2019 pour  combler   le  déficit  continu   de  la production    nationale   en sucre  blanc.  
 
Par ailleurs,  les  dépenses   du  FSP se sont   élevées  à 301  MDH en  2023,  en  stagnation    par  rapport 
aux années  2022  et  2021, et  en baisse  de 50  MDH  par  rapport   à l’année  2020. 
 
Compte   tenu  de   la baisse   de  la  charge   de  compensation    relative    aux  produits    alimentaires   au 
titre   de  l’année   2023   de  31 %  par  rapport    à  l’année   2022,  le  pourcentaage   de  contribution     du 
Fonds  de  soutien   des  prix   de  certains   produits   alimentaires    à la  régulariisation    des  subventions 
alimentaires   a accusé  une  augmentation    en ppassant à 2% en 2022  à 3% en  2023.  
 
                     CONTRIBUTION DU FSP A LA COMPENSATION DES PRODUITS ALIMANTAIRES AU TITRE DE LA PERIODEE 2010‐2023 (EN %)







         16%







                                                                                           8% 8%                        8%
                                                        7%
                     6%                                                      6%                             6%
                                                                                                                                          5%
                                 4%
                                                                                                                                                                 3%
                                                                                                                                                      2%
                                             1%
                                                                    0%

         2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 20200 2021 2022 2023


                                                                                                                                                                              

2.2.4.    Financement        des   dépenses      d’équipement         et   de  la   lutte     contre     le    chômage 
           (Promotion        Nationale) 

L’évolution    des   recettes   et   des   dépenses   effectuées    par   ce  compte    aau cours   de  la  période    
2021-2023,  se présente   comme   suit : 


 
           30 

37
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
                      EVOLUTION DES RECETTES* ET DES DEPENSES DU FONDS AU TITRE DE LA PERIODE 2021‐20223 (EN MDH)




                                                                                                                                      3 223,588
                                                                               2 882,,11
                        2 624,53


                                                                                               2 018,23                                          2 000,61
                                        1 887,53









                                  2021                                               2022                                                2023


                                                                              Recetttes Dépenses
                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 
 
Les  émissions     réalisées    sur   les   crédits    programmés       dans    le  cadre    duditt   compte,     au   titre    de   la 
période    2021-2023,    sont   ventilées,     par  catégorie     de   programme,     comme    ssuit :                                            

                                                                                                                                                                                                      (En MDH) 

                                  Programmes                                                2021                          20222                       2023 


  Programme d'équipement                                                          950,60                      1.054,770                  939,48 

  Programme de développement  des provinces 
                                                                                                     801,00                       844,995                     894,28 
  sahariennes 

  Chantiers des collectivités  territoriales                                       161,80                       162,992                    201,22 


  Dépenses de suivi et de contrôle                                                 0,54                            0,122                          0 


                                        Total                                                    1.913,94                    2.062,,69                  2.034,98

 
En   2023,    le   nombre      de    journées     de   travail      assurées     par   la   Promotioon      Nationale      s’élève    à            
4.119.814  journées,      réalisées     essentiellement        dans    le   cadre    du    programme       de   soutien      et   de 
création    de  l’emploi     aux  provinces     du  Nord   (1.939.799     journées   de   travail)).  
 
Par  ailleurs   le  programme      arrêté    au titre    de  ll’année   2024,   prévoit    la  mobilisation       d’une   enveloppe 
budgétaire     de  1.932,22   MDH,   ventilée    par  catégorie     de   programme,     comme     suit  : 
 
                            Chantiers    de  développement        des  provinces     du  Sud                        : 1.000,16 MDH ;

                            Programmes     d’équipement                                                                           :  764,93   MDH ;

                            Chantiers    des  collectivités      territoriales                                                     :    166,13 MDH ;

                            Dépenses    de  suivi   et  de  contrôle                                                              :         1,00  MDH.

                                                                                                                                                                                                                            
 
                                                                                                                                                                               31

38
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
2.2.5.     Fonds     spécial      de    la  pharmacie         centrale 

L’évolution      des  recettes     et   des   dépenses    du   Fonds    spécial    de  la  pharmaacie    centrale     (FSPC)   au 
titre   de  la  période    2021-2023     se présente     comme    suit : 

                         EVOLUTION DES RECETTES* ET DES DEPENSES DU FSPC AU TITRE DE LA PERIODE 2021‐20223 (EN MDH)






                         4 499,99

                                                                                  4 0449,15                                          4 0662,44



                                         2 945,64
                                                                                                   2 574,20


                                                                                                                                                            1 710,76








                                   2021                                                  2022                                                 2023



                                                                                 Recettes            Dépenses
                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 

Les  recettes    réalisées    de   ce  Fonds   au  titre    de  l’année    2023   sont   répartiess,   par   source   de   recette, 
comme    suit  : 

                                                                             

                                                                                                                                                 Montant           Part dans le 
                                                   Origine  de la recette
                                                                                                                                                ((En MDH)              total


 Versement  du Budget Général                                                                                              2.436,42              94,16% 



 Contribution   des communes au titre  du « RAMED »                                                             129,28                  5% 



 Recettes  diverses                                                                                                                     21,78                 0,84% 



                                                                Total                                                                         2.587,48               100% 

 
Ainsi,     la   grande      part      des    crédits      du    FSPC     est    affectée et          géréee   par     la    Direction       de 
l’approvisionnement         en   médicaments      et   en  produits      de  santé    du  Ministèère   de   la  Santé   et   de   la 
Protection     Sociale,    comme    le montre     le tableau     suivant   : 
                                                                                                                                                                          

 
             32 

39
                                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
 
                                                                                                                                                                              (En MDH) 

                                                                                                     2021                            2022                         2023 


  Crédit  du FSPC                                                                      3.099,88                      2.656,82                   2.374,71 


                                                                                                                                                                       2.352,63 
  Crédits engagés    (avec  taux d’engagement)               3.092,20  (99,75%)     2.632,46  (99,08%) 
                                                                                                                                                                       (99,07%) 


  La part  de la Direction de                    En crédit                     1.603,26                      1.348,18                   1.226,37 
  l’approvisionnement   en 
  médicaments  et en produits 
  de santé dans les crédits 
  engagés                                                   En %                        51,84%                        51,21%                     52,13% 



  La part  de l’Ordonnateur                     En crédit                      974,42                         175,66                      780,50 
  Délégué dans les crédits 
  engagés 
                                                                  En %                         31,51 %                       6,67%                       33,18% 


  La part  des Sous                                 En crédit                       514,52                        445,93                      295,29 
  Ordonnateurs  Centraux et 
  Déconcentrés dans les crédits 
  engagés                                                   En %                        16,63 %                       16,94%                     12,55% 

 
          Réalisations     du   FSPC  au  titre    de  l’année    2023    : 
 
Les  crédits    alloués   aux   achats   de  produits     pharmaceutiques        au  profit    des  établissements       des  soins 
de  santé   primaires    au  titre    de  l’année   2023   sont   répartis,     par  région,    comme    suit   :     
                                                                        

                                                    Régions                                                              Montant (en MDH)             Part (en%) 

 Casablanca-Settat                                                                                                             60                                16% 

 Fès-Meknès                                                                                                                       60                                16% 

 Marrakech-Safi                                                                                                                   51                               13% 

 Rabat-Salé-Kénitra                                                                                                            43                                11% 

 Oriental                                                                                                                              35                                 9% 

 Tanger-Tétouan-AL  Hoceima                                                                                         32,60                             8 % 

 Beni Mellal-Khénifra                                                                                                           30                                8% 

 Souss-Massa                                                                                                                     28                                 7% 

 Darâa-Tafilalet                                                                                                                 21,50                              6% 

 Guelmim-Oued Noun                                                                                                       13,60                             3% 

 Laayoune-Sakia El Hamra                                                                                               8,50                               2% 

 Dakhla-Oued Eddahab                                                                                                     2,35                               1% 

                                                      Total                                                                          385,55                           100% 

 
 
                                                                                                                                                                               33

40
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
Les crédits    alloués  aux  achats   de  services   liés  aux  prestations    de  dialysse au  titre   de  l’exercice 
2023  sont  repartis,  par  région   sanitaire,  comme   suit: 
 

                                                                                                                    Crédits allloués 
                                      Régions Sanitaires                                                                                      Part en % 
                                                                                                                        (En MDH) 

 Casablanca-Settat                                                                                            47,600                         36 %

 Rabat-Salé-Kenitra                                                                                           47,300                         36%

 Marrakech-Safi                                                                                                   19,11                          15% 

 Souss-Massa                                                                                                     7,41                             6% 

 Tanger-Tétouan-AL Hoceima                                                                            4,55                             3% 

 Oriental                                                                                                               3,31                            3% 

 Drâa-Tafilalet                                                                                                      1,13                            1% 


                                                Total                                                                  130,411                       100%


2.2.6.   Fonds     spécial    pour    la  promotion       et   le  soutien     de   la  Protection       Civile 

L’évolution   des  recettes   et  des  dépenses   du  Fonds  spécial  pour   la promotion     et le  soutien   de  la 
protection   civile   (FSPSPC)  au titre  de  la périiode  2021-2023,   se présente   ccomme suit  : 
 
 
                      EVOLUTION DES RECETTES* ET DES DEPENSES DU FSPSPC AU TITRE DE LA PERIODE 2021‐22023 (EN MDH)




                                                                                                                                  3351,45


                     275,44
                                                                           2500,65
                                    217,71

                                                                                                                                                 158,66
                                                                                           145,98







                             2021                                               2022                                               2023



                                                                       Recetttes    Dépenses
                                                                                                                                                                               
(*) Compte tenu du solde reporté. 
 
En 2023,   la Protection     Civile  a  effectué   6422.241 interventions,    soit  une  moyenne    journalière   de 
1.760 interventions.    La répartition    régionale   de  ces interventions    se présente   comme   suit  : 

 
            34 

41
                                                                                                          RAPPORT  SUR  LES COMPTESS SPECIAUX  DU  TRESOR 
 
 
                            REPARTITION DES INTERVENTIONS DE LA PROTECTION CIVILE PAR REGION AU TITRE DE LL'ANNEE 2023






             153 094
              23,84%






                               78 101 75    013
                              12,16% 11,68% 68       303 66      479
                                                               10,64% 10,35% 53       836
                                                                                                 8,38% 46     194
                                                                                                                  7,19% 37    346
                                                                                                                                  5,81% 29     713
                                                                                                                                                  4,63% 16      117
                                                                                                                                                                                   11 632
                                                                                                                                                                   2,51%                       6 413
                                                                                                                                                                                    1,81%
                                                                                                                                                                                                      1%











                                                                                                                                                                                                                      
 
En   ce    qui     concerne        les    interventions           de    lutte      contre       les    feux     de    forrêts,      les    services       de    la 
Protection        Civile     ont    enregistré        345    incendies       de   forêts      en   2023,     qui    ont    ravagé      une    superficie 
totale     de   5.546,12     ha.   La   région      de   l’Oriental       occupe       le  premier       rang    aveec   environ 46%         du   total 
des   superficies       brulées. 
 
                 NOMBRE D'INCENDIE DE FORETS PAR REGION                                  SUPERFICIE BRULEEE ( en hectare)


                     Marrakech‐
                                                      Autres                                                                      Béni mellal‐           Autres 
                          Safi
                                                         21                                                                            Khénifra                66,81
                           18
                                                        6%                                                                             78,77                   1,21%
                           5%
                                                                                                                                           1,42%
       Béni mellal‐                                                                                                                                                                      Tanger‐
          Khénifra                                                                                                                                                                       Tétouan‐AL 
              35                                                             Tanger‐
                                                                                                                                                                                                Hoceima  
             10%                                                        Tétouan‐AL 
                                                                                                                                                                                                1 429,04
                                                                              Hoceima
                                                                                                                                                                                                  25,77%
                                                                                  147
                                                                                  43%
       Oriental                                                                                                   Oriental
           45                                                                                                        2 564,41 
          13%                                                                                                      46,24%


                     Rabat‐Salé‐                          Fès‐Meknès                                              Casablanca‐                Fès‐Meknès 
                        Kénitra                                        59                                                             Settat                          1 054,09
                            20                                          17%                                                             353                               19%
                           6%                                                                                                             6,36%
                                                                                                                                                                                                                    
 
Les   actions     programmées          au   titre     de   l’année     2023     et celles      prévues      pourr    l’année      2024,     dont     les 
coûts    globaux       s’élèvent,      respectivement,           à  1881,17 MDH et    200    MDH,    se  préésentent      comme      suit    :   
 
 
 
                                                                                                                                                                                                  35

42
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                                                                                                                                                                                 (En MDH) 

                                                      Actions                                                                    2023                           2024 


 Fonctionnement  de la Protection  Civile                                                                     92,99                           83,17 


 Equipement de  la Protection  Civile                                                                            39,77                          68,98 


 Construction,  rénovation et  réaménagement des bâttiments de la 
                                                                                                                                      20,13                          21,65 
 Protection  Civile 


 Lutte  contre les catastrophes                                                                                      28,22                          26,20 


 Autres dépenses                                                                                                          0,06                                - 


                                                        Total                                                                      181,17                         200 

 

2.2.7.     Fonds     national       pour     l’action        cullturelle 

Les  recettes    et   les  dépenses    effectuées     par le    Fonds    national    pour   l’action     culturelle     (FNAC)    ont 
enregistré      un   accroissement       annuel     moyenn,   respectivement, de          20,04%     et    67,97%    durant     la 
période    2021-2023.  
 
                              EVOLUTION DES RECETTES* ET DES DEPENSES DU FNAC AU TITRE DE LA PERIODE 2021‐2023 (EN  MDH)




                                                                                                                                      1 289,088
                                                                              1 210,773



                        894,59

                                                                                                                                                       769,34

                                                                                                610,87




                                        272,67





                                 2021                                                2022                                                2023



                                                                            Recettees          Dépenses

                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 
        
Les  versements      du  budget     général    au   profiit   du   FNAC   ont    atteint,    durant     la  période    2021-2023, 
un  montant    total    de  712,48   MDH.  
 


 
             36 

43
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
Durant    cette    période,    le   FNAC    a  contribué,     essentiellement,      au   financement     des   actions 
suivantes  :  
 
     -     L’organisation      des   festivals     patrimoniaux,      la   participation      aux   diverses     activités    et 
           manifestations     culturelles   organisées   au niveau   national   et  international,    la valorisation    de 
           la  richesse  culturelle   du  Maroc  et  de  sa diversité   et  l’organisation    des événements    d’attrait 
           international,     notamment      la  célébration     de   Marrakech    comme    Capitale    Culturelle     du 
           Monde   Islamique  en  2024  ; 
 
     -     L’entretien     et    la   restauration     des   monuments     historiques     et   la   mise    en   valeur    du 
           patrimoine    culturel   matériel   et immatériel    national   ; 
 
     -     La  restauration    et  la  réhabilitation    des  monuments    historiques    et  les sites   sinistrés  par  le 
           séisme  d’Al  Haouz  ; 
     -     La   réhabilitation     des   infrastructures     artistiques    ainsi   que   la  réalisation     des  projets    de 
           construction    et  d’aménagement    des  établissements    culturels   ; 
 
     -     Le  soutien    culturel   par   appels   à  projets   dans  les   domaines   de  la  musique,    du  livre,   du 
           théâtre     et   des   arts    plastiques,    ainsi    que   le   soutien    aux   associations     culturelles     et 
           artistiques    et aux  manifestations    et  festivals  culturels. 
 
Ainsi,  les  engagements    dudit   Fonds,  durant   la  période   2021-2024   (1er  semestre),   se  présentent 
comme  suit  :           
                                                                                                                                                                                                       
                                                                                                                                                                                                           (En MDH) 
                                                                                                                                                                2024 
                                   Programmes/Projets                                       2021         2022         2023            (1er 
                                                                                                                                                            semestre) 

 Etablissements à caractère culturel et artistique                              77,82        216,84      198,22        178,46    

 Versements et soutien des missions                                                 67,15      233,32      305,44          111,95     

 Programme de développement des provinces du Sud                     52,73        33,60         9,21               -       
 Musées, monuments, sites historiques et centres de recherche du 
                                                                                                           44,63        66,71         51,81         58,44    
 patrimoine 
 Organisation de manifestations culturelles                                        11,41       77,93         16,79         150,12    

 Programme LA JUNTA Andalucia                                                     7,26          0,21             -                  -       

 Encouragement à la production culturelle, littéraire et artistique       6,27         35,42        59,53            1,40     

 Production de supports culturels                                                        6,01         6,66           9,45            0,89     

 Soutien à l'édition et à la diffusion de livre                                         4,16         14,56        18,52           5,33     

 Organisation de salons du livre                                                          1,75        37,40         92,46          57,21     

 Manuscrits, collections, objets et œuvres d'art                                  0,74          2,28          3,86            0,37     


 Programme de valorisation du patrimoine archéologique dans le 
                                                                                                            0,27          6,50          5,74               -       
 cadre de la conversion de la dette Italienne 

 Reconstruction et réhabilitation des territoires sinistrés suite au 
                                                                                                              -                -                -               92,79     
 séisme d’al Haouz  

 
                                                                                                                                                               37

44
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
2.2.8.    Fonds    d’appui     à  la  protection       sociale     et   à la  cohésion      sociale 

Les recettes    et  les  dépenses   du  Fonds   d’appui   à  la protection     sociale   eet à la  cohésion   sociale 
(FAPSCS)  ont   connu   un  accroissement     annnuel moyen,   respectivement,     de  48,59   % et   56,73% 
durant  la période   2021-2023.  

 
                               EVOLUTION DES RECETTES* ET DES DEPENSSES DU FAPSCS AU TITRE DE LA PERIODE 2021‐20223  (EN MDH)



                                                                                                                                 233 603,20



                                                                           14 4463,11                                                       13 544,55
                    10 690,31

                                                                                           6 638,30
                                    5 513,61



                               2021                                              2022                                               2023

                                                                     Recettees             Dépenses
                                                                                                                                                                               
(*) Compte tenu du solde reporté. 
 
Depuis  sa  création,   le  FAPSCS  a  contribué    au  financement    de  divers  prrogrammes    sociaux  tels 
que   le   RAMED,    TAYSSIR,   l'Initiative     Royale    «   Un   million    de   cartabbles   »,   le   Programme 
d'Assistance   aux  Personnes   à Besoins   Spécifiques,   le  Programme   d'Aidees Directes   aux  Femmes 
Veuves  en  Situation    de  Précarité   (DAAM),   avant   qu’il   ne  soit  érigé  en  ssupport  de  financement 
des  deux   premiers    jalons   du  chantier    de   la  généralisation     de  la   proteection   sociale,   à  savoir 
l’Assurance  Maladie   Obligatoire   de  Base (AMO)   et  l’Aide  Sociale  Directe   (AASD). 
 
Pour la  période   de janvier  à  septembre   2024,  plus  de  27,90  MMDH ont  étéé décaissés  de ce  Fonds 
pour   financer   les  deux   jalons   précités,   ainssi que   le  programme    d'assistance    aux   personnes   à 
besoins  spécifiques. 
 
     Le   régime      de    l’Assurance       Maladiie     Obligatoire        des    personnnes     n’ayant      pas    la 
        capacité     de  s’acquitter       de  leurs    cotisations      (AMO-TADAMON): 

Dans  le  cadre   du   régime   « AMO   TADAMON   »,  l'Etat   assure   la  prise   en  charge    intégrale    des 
cotisations   et  de  la part  restante   à la  charge   de l’assuré  pour   les prestations    prodiguées   dans  les 
structures   publiques   de soins  « ticket   modérateur    ». 
 
À  cet   égard,   le   FAPSCS   a  débloqué    plus   de   15,50  MMDH   pour   couvvrir   les  cotisations    des 
personnes  immatriculées    au  titre   de ce  régime,   dont  6,70  MMDH  au titre   de  fin  septembre   2024. 
En sus,  un monntant  de  plus  de  557  MDH a  été  débloqué    dans le  cadre   de  la prise  en  charge   du 
ticket  modérateur. 
 
S’agissant   du  nombre    de   bénéficiaires    du  régime    «  AMO   TADAMON   »», l’effectif   des   assurés 
principaux    immatriculés     a  dépassé   4   millions    en  mois   d’août    2024,     couvrant    ainsi   environ             
11,30 millions de  bénéficiaires,   y  compris   leurs ayants   droits. 
 
        Le   régime    de   l’Aide    Sociale    Directe     :  

  Lancé  en  décembre   2023,  ce  programme    a bénéficié,   jusqu'à septembree   2024,   d’un  déblocage 
  de  plus  de 22  MMDH,  dont  20,46   MMDH  au titre   de  l'année  2024.  Ces  dotations    ont  été  utilisés 

 
            38 

45
                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
  pour  financer  les différentes   prestations  sservies dans le  cadre  dudit  rrégime, notamment   les 
  aides de  protection  contre   les risques liés  à l'enfance  et  l'aide forfaitaire,   incluant  la nouvelle 
  prestation  appelée aide à la rentrée scolairee. 

  En ce qui  concerne  le  nombre  de bénéficiaires  de  l'ASD, il  a atteint  près  de  3,90  millions de 
  ménages au titre du  mois d’août 2024  ;  
       Le  Programme     d’Assistance    aux  Personnes   à  Besoins  Spécifiques     :  

  un montant  de plus de 2 MMDH a été versé depuis 2015 et jusqu’à septemmbre 2024, au profit de 
  l’Entraide Nationale, dont  un montant  de 200  MDH au titre de l’année 2024. 

2.2.9.    Fonds    de    soutien     aux    services     de   la    concurrence,      du    contrôle,      de   la 
          protection      du   consommateur,      de   la   régulation     du   marché    et  des   stocks    de 
          sécurité    » 

L’évolution des recettes  et des dépenses du  Fonds de soutien aux servicees de la concurrence, du 
contrôle,  de  la  protection   du   consommateeur, de la  régulation   du  maarché et  des  stocks  de 
sécurité, durant la période  2021-2023, se présente comme suit  :

                         EVOLUTION DES RECETTES* ET DES DEPENSES DU FONDS AU TITRE DE LA PERIODE 2021‐2023 (EEN MDH)


                          15,33                                         15,33                                        15,33





                                                                                                                              5,96


                           0                                                 0

                          2021                                          2022                                          2023


                                                                   Recetttes      Dépenses
                                                                                                                                                                 
(*) Compte tenu du solde reporté. 
            
Afin  de  suivre   le  travail   des  services  de  contrôle   relevant des    divissions économiques   des 
préfectures et  provinces, les indicateurs de performance  suivants ont  été retenus  :  
 

        Le nombre de commerces  et de locaux professionnels  contrôlés ; 

        Le nombre   de commerces et    locaux  contrôlés  dans  le  milieu  rural  ainsi que  les  souks 
          hebdomadaires  ; 

        Le nombre  de  procès-verbaux  d'infractions  liés  à la protection   dees consommateurs, à la 
          concurrence  et  à l’interdiction   des sacs en matières  plastiques  étaablis par les services de 
          contrôle   et  transmis  aux  tribunaux  compétents   pour  engager  la  procédure  judiciaire   à 
          l’encontre  des contrevenants. 
 
Les réalisations   de  ces indicateurs   durant   la  période  2021-2024  (jusqu’au   31 mai  2024),  se 
présentent comme  suit: 
 
                                                                                                                                                  39

46
                                                                              
   PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
  
   
                                                                                                                                                            2024  
                             Années                                    2021                 2022                  20223 
                                                                                                                                                   (jusqu’au 31 mai) 


  Nombre de commerces et locaux contrôlés    203.850            308.543              322..316              138.610 


  Nombre de commerce et locaux contrôlés 
  dans le milieu rural et les marchés                    62.218             125.299            128.3330              54.480 
  hebdomadaires 

  Nombre de procès-verbaux déférés devant 
                                                                             6..169               9.855                12.5575                7.271 
  les tribunaux 

  

  
  
  

   Réalisations   au  titre   des années  2021,  2022   et 2023   : 
 Les  actions   financées    dans  le  cadre   dudit    Fonds   durant   la  période    2021-2023,   se  présentent 

  comme suit  : 
  
  
  
  
  
  
  
       -    En  2021 : aucune  dépense  n’a  été  engagée  au  titre  de  cette  année  ; 
  
       -    En  2022   : la  commande   de  30   véhicules   utilitaires   destinés   aux  seervices de  contrôle    des 
            Provinces   et  Préfectures   pour  un  montant   de  4,32 MDH  ;
  
       -    En  2023   : le  paiement    des  véhicules   commandés    en  2022   ainsi  que   le  versement   d'une 
            prime   aux   contrôleurs    exerçant   dans   les Préfectures    et  Provincess  du  Royaume,   pour   un 
            montant    de 1,64 MDH. 

 2.2.10.       Fonds       spécial        pour       la     gestion        de      la     pandémiie         du     Coronavirus  
            "Le    Covid-19"  

 En  2023,   les  recettes    et   les  dépenses   du   Fonds   spécial   pour   la  gestion    de   la  pandémie    du 
 Coronavirus     "Le    Covid-19"    ont    atteint,     respectivement,       3.357,59    MDH    et    1.075,19  MDH, 
 enregistrant    ainsi des  baisses  annuelles  moyennes,   respectivement,    de 47,,35% et  68,63%. 
  
                          EVOLUTION DES RECETTES* ET DES DEPENSEES DU FONDS AU TITRE DE LA PERIODE 20211‐2023 (EN MDH)


                     12 111,35
                                     10 928,35



                                                                           5 917,82


                                                                                           2 966,33                       3 3557,59

                                                                                                                                               1 075,19


                                2021                                             2022                                             2023


                                                                         Recetttes        Dépenses
                                                                                                                                                                                
 (*) Compte tenu du solde reporté. 
  

  
             40 

47
                                                                                RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
  
  
 Par ailleurs, le bilan des efforts  déployés  par l’Etat  et financés à  partir des  ressources du CAS au 
 titre  de la période  2020-2023  affiche, principalement,  le renforcement   du dispositif  médical et  le 
 lancement de la campagne  nationale de  vaccination, le soutien  des couches sociales vulnérables, 
 l’appui  à l’économie  nationale  et  la  préservation  de  l’emploi,  notamment   à travers  la  mise  en 
 œuvre  du  pacte  pour   la relance  économique   et  l’emploi,  la  consolidation   des  dispositifs   de 
 soutien à l’entreprise  et l’encouragement  de l’investissement.  
  
  Les principales  réalisations  du  Fonds au titre  des années 2022  et 2023 : 
  
   
         Prise  en charge   par  l’Etat   des  intérêts   intercalaires   afférents   aux  crédits   et  leasing 
           accordés    aux  entreprises    (agences   de   voyage   et   restaurants   classés)   ayant   des 
           activités   réglementées   sous  la  tutelle   du Ministère   du  Tourisme,  de  l’Artisanat   et  de 
           l’Economie   Sociale et  Solidaire  et  aux Entreprises  de  Transport  Touristique   (ETT)  : 
   
 En application  des dispositions du  Protocole d’accord  relatif  à la mise en place d’un moratoire  au 
 titre  des crédits  et leasing accordés  auxdites  entreprises, l’Etat  s’engage à prendre  en charge  le 
 montant  des  intérêts  intercalaires  correspondant   à  une période   maximale de  9  mois  et  demi 
 afférents   aux  crédits   et  leasing   accordés  aux   catégories   de  bénéficiaires   susmentionnées. 
 L’enveloppe  en question  est  à reverser,  en deux  tranches égales,  distinctement  à  chacune des 
 Sociétés de Financement. Cette  enveloppe ressortant  à 36,29 MDH, a été servie intégralement  au 
 titre de  l’année 2023, depuis les disponibilités  dudit  CAS, au profit des bénéficiaires  éligibles. 
  
         Prise  en  charge  par   l’Etat  des  intérêts   intercalaires    afférents   aux  crédits   bancaires 
           contractés   par  les  Etablissements  d’Hébergement    Touristiques   (EHT), Etablissements 
           de   Transport   Touristique   (ETT)   et  entreprises   exerçant   des  activités    réglementées 
           (Agences   de voyage  et  restaurants  classés)  : 
  
 Dans ce cadre un Protocole  d’accord  a été conclu, en  janvier 2022, selon lequel  l’Etat s’engage à 
 prendre  en  charge  les    intérêts  intercalaires,  sur  une  période   maximale  de  9  mois  et  demi, 
 afférents aux crédits  bancaires contractés  par les bénéficiaires susmentionnés.  
  
         Contribution   au financement   du  chantier  de généralisation   de  la protection   sociale  : 
  
 Dans le   sillage  de  la  mobilisation   des  fonds  nécessaires  au  financement   du  chantier   de  la 
 généralisation  de la protection   sociale, une enveloppe  de 1.000  MDH a été mobilisée  depuis  les 
 disponibilités  du Fonds  spécial pour  la gestion de  la pandémie  du Coronavirus "Le  Covid 19", au 
 titre de  l’année 2023, en vue de contribuer  au financement  dudit Chantier. 
  

 2.2.11.   Fonds    spécial     de   soutien     à   l’action     culturelle      et    sociale    au   profit      des 
           marocains    résidant    à  l’étranger     et  des  affaires    de  la  migration  

 L’évolution  des  recettes  et  des  dépenses du  Fonds  spécial  de  soutien  à l’action   culturelle  et 
 sociale au  profit  des  marocains  résidant  à l’étranger  et  des  affaires  de la  migration,  durant  la 
 période 2021-2023, se présente comme  suit : 








  
                                                                                                                                                   41

48
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 
                           EVOLUTION DES RECETTES* ET DES DEPENSES DU FONDS AU TITRE DE LA PERIODE 20211‐2023 (MDH)




                                                                                                                                         49,73



                                38,89
                                                                                     35,18

                                               28,71
                                                                                                                                                        24,19




                                                                                                    10,45




                                        2021                                             2022                                            2023


                                                                                 Reccettes         Dépenses
                                                                                                                                                                                                
(*) compte tenu du solde reporté. 

Le  bilan   des   programmes      réalisés    et  les  programmes financés          par   ledit   Fonds    durant     la  période 
2021-2023,    se  présente    comme    suit   :                                                                                   

                                                                                                                                                                                                          (En MDH) 

                                       Programmes réalisés                                                   2021                   2022                2023 

 Actions  de communication   relatives  à l’action  culturelle  et  sociale 
                                                                                                                           14,00                   14,00               10,00 
 en faveur des Marocains Résidant à l’Etranger (MRE)) 

 Programme de soutien  des centres culturels à l’étranger                                 6,50                    8,00                 11,00 
 Programme  de  ppartenariat avec les  associations  en  faveur  de  la 
                                                                                                                            4,00                     8,00                 6,00 
 migration 
 Programme des universités  culturelles                                                                -                          -                    6,00 

 Festivités et  cérémonies officielles                                                                      -                           -                    3,00 

 Conception    et    réalisation     d’un    dispositif     pour    faciliter     la 
 mobilisation  des  compétences  des MRE et l’accomppagnement des               -                          -                     5,73 
 porteurs  de projets 

                                      Programmes  financés                                                  2021                   2022                2023 

 Appui   à  l’action    culturelle   et  sociale   en  faveur   des   MRE par 
                                                                                                                            8,00                        -                       - 
 l’Agence Marocaine de  Coopération Internationale  (AMCI) 

2.2.12.      Fonds      spécial       pour      la   gestion        des     effets       du    tremblement            de    terre      ayant 
            touché       le  Royaume        du   Maroc 

Pour   comptabiliser       les   opérations      liées   à  la   gestion     des   effets    du   trembblement     de   terre    ayant 
touché    la   région    d’Al    haouz,    un   compte     d''affectation       spéciale    intitulé     «« Fonds   spécial    pour    la 
gestion    des  effets    du  tremblement       de  terre   aayant  touché    le  Royaume    du  MMaroc » a  été  créé   suite 
aux   Hautes    Instructions      Royales.     Etant    donné    la   nécessité     impérieuse,      dictée    par   le   caractère 
urgent     des   mesures     à  déployer      pour    la   gestion      des   effets    du    séisme    et   conformément         aux 

 
             42 

49
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
dispositions de  la loi organique  n°130-13 relative aux lois de  finances, la création  dudit  support a 
été opérée  par  voie de  décret,  lequel  a placé  ce support   budgétaire  sous la  responsabilité  de 
l'autorité  gouvernementale  chargée du  budget  en tant  qu'ordonnateur.  La  ratification  du décret 
de création précité  a été actée par  la loi de finances de l’année 2024. 
 
        Bilan des  réalisations   du Fonds  spécial  pour  la  gestion  des  effets  du  tremblement   de 
          terre  ayant  touché  le  Royaume du  Maroc  : 
 
Sur le  plan budgétaire,   la situation   dudit  Fonds  au début   octobre  de  l’année 2024,  révèle  un 
solde  créditeur   de  13.031,32 MDH résultant  d’un   total  de   recettes  de  21.979,66 MDH  et   de 
dépenses émises s’élevant à 8.948,34 MDH. 
 
Ainsi, les recettes et les dépenses du Fonds  spécial pour la gestion  des effets du  tremblement  de 
terre ayant touché  le Royaume du Maroc, se présentent  comme suit : 
 
        Recettes  : 
 
Les  efforts   déployés  pour   mobiliser   les  ressources  nécessaires  à  la  gestion   des  effets  du 
tremblement    de   terre    ont   été    couronnées   par    l’accumulation    d’un   montant    total    de           
21,98 MMDH, dont la répartition se présente comme  suit : 
 
    5,25 MMDH mobilisés à partir  des disponibilités  du Budget  de l’Etat ; 
 
    16,73 MMDH comme dons octroyés  par les partenaires  institutionnels,  les personnes morales 
       de droit  public  et privé et  les citoyens. 
 
        Dépenses : 
           
Les émissions comptabilisées  sur  ledit  Fonds ont  porté,  notamment   sur les axes d’intervention 
suivants : 
        La  signature   d'une   convention   entre   l'Etat    et  la   Caisse  Nationale   de   Retraites  et 
          d'Assurances  (CNRA), mandatée  pour  gérer  les aides directes  de l'Etat  dans  le cadre  du 
          programme   d'urgence   de   réhabilitation   et   d'aide  à  la   reconstruction   des  logements 
          détruits   dans les  zones  sinistrées suite  au  séisme ayant   touché  le Royaume  du  Maroc. 
          Cette  convention  vise à octroyer  : 
 
                         -    Des aides d'urgence mensuelles aux ménages (2.500  DH par mois) ; 
                         -    Des aides directes à la reconstruction  ou  à l'acquisition  pour les ménages dont 
                              le logement  est totalement  détruit  (140.000  DH) ; 
                         -    Des  aides   directes   au  confortement    des   maisons  inhabitables   en   l'état, 
                              destinées    aux    ménages   dont    le    logement    est    partiellement     détruit           
                              (80.000   DH). 
                               
          L’effort  budgétaire   de l’Etat,  jusqu’au 01/10/2024,  s’élève  à une enveloppe  de  4,1 MMDH. 
          Les  statistiques  des  bénéficiaires  de l’opération   d’octroi   des aides  directes  aux  familles 
          sinistrées, à fin septembre  2024, se présentent  comme suit : 
           
                         -    Aides  d’urgence  mensuelles  (2.500   DH) :  l’effectif   des  bénéficiaires  est  de 
                              63.766, avec un montant  total  des aides mensuelles versées de 1.774,93 MDH. 
                               
          En   dépit   de   la  clôture   de   l’opération    d’octroi   des   aides  d’urgence   mensuelles,   la 
          Commission  Interministérielle,  lors de sa XIIe réunion tenue  le 02 octobre  2024,  a acté, en 
          application   des  Hautes  Instructions   Royales,  la  prorogation   de  l’octroi   desdites   aides 
          d’urgence  mensuelles pour  une durée  supplémentaire  de cinq  mois  au profit  des familles 
          dont  les habitations ont  été effondrées  partiellement  ou totalement. 
           
                         -    Aides  directes  à la  reconstruction   (140.000  DH)  : l’effectif   des bénéficiaires 
                              s’élève  à  5.661 avec  un  montant   total   de  237,78  MDH  versé  au  titre  des           
                              4 tranches. 


 
                                                                                                                                                  43

50
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                           -     Aides   directes    à  la  réhabilitation      (80.000    DH)   :  l’effectif     des  bénéficiaires 
                                 s’élève   à  51.938   avec   un   montant    total    de   1.775 MDH   versé   au   titre   des            
                                 4 tranches. 
 
         La   mise   en   place    des   crédits    budgétaires     nécessaires    au   financement      des   actions 
           d'urgence    à partir   des disponibilités    dudit   Fonds,   lesdites   actions  sont   issues, notamment,  
           des   résolutions   des   réunions   de  la  Commission    Interministérielle     chargée   de   la  mise  en 
           œuvre     du     programme.      Les    crédits     mobilisés,      jusqu’au     01/10/2024,      s’élèvent     à            
           4.838,64     MDH.    Les   principales     actions     menées    par    les    Départements      Ministériels 
           concernent    notamment    : 
            
                           -     La mise  à niveau  des  routes  ; 
                           -     La  réparation   des  dégâts   subis  par  les  différents    ouvrages   hydrauliques    et  le 
                                 réseau  de distribution     de l'eau  potable   ; 
                           -     La  mise  à  niveau  et  la  reconstruction     de  centres   de  santé   prioritaires    et  des 
                                 écoles  publiques   ; 
                           -     L’appui  social  au  profit   des élèves  et  enseignants   ; 
                           -     La   reconstitution      de   la  réserve    nationale    en   matériels    d’hébergement      et 
                                 d’assistance   aux  populations   ; 
                           -     Un  programme     d’aide   aux  artisans   dont   les  ateliers    ont   été  touchés   par   le 
                                 séisme  d’Al  Haouz  ; 
                           -     La  mise  en  place  au  niveau   de  chaque   région   d’une  plateforme    de  stockage 
                                 de  réserves   de  première   nécessité   en  vue  de  contrecarrer    les  effets   néfastes 
                                 des  catastrophes   naturelles   ; 
                           -     Le renforcement    et  la restauration    des  bâtiments   historiques. 
                                  
         Le  financement    du   projet   d’électrification      à  partir   de  l’énergie    solaire   des  campements 
           provisoires    installés   au niveau   des  zones  sinistrées   par  le  séisme,  il s’agit   du  reversement 
           au  profit   de  l’Agence    Marocaine   pour  l’Energie   Durable   (MASEN)   de  la  première   tranche 
           s’élevant   à  0,8  million   de  dollars  US  sur  une  enveloppe   globale   de  1 million   de  dollars  US 
           en   application    des   dispositions    du  cadre    conventionnel    signé   entre   l’Ambassade    de   la 
           République    Coréenne   et  l’Agence   au  sujet   du  cofinancement     à hauteur   de  1,4  million   de 
           dollars   US. Le  versement   du  reliquat,   soit  0,2  million   de  dollars   US, est  prévu   au cours   de 
           l’année  2024. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 


 
           44 

51
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
SECTION               III     -   PROMOTION                     ECONOMIQUE                       ET     FINANCIERE 
 
Dix  comptes     d’affectation       spéciale    intervenaant    dans   le  domaine     de  la  promotion       économique      et 
financière,     ont   réalisé    globalement       9,64%   du   total    des   dépenses    des   CAS   en   2023.    L’évolution 
des  recettes    et  des   dépenses    desdits    CAS  se  présente     comme    suit  : 
 
                       RECETTES* ET DEPENSES REALISEES AU NIVEAU DES CCAS INTERVENANT DANS LE DOMAINE DE LA PROOMOTION ECONOMIQUE 
                                                                ET FINANCIERE AU TITRE DE L'EXCERCICE 2023  (EN MDH)



  Compte spécial des dons des pays du Conseil de Coopération du                                                                  11 565
                                         Golfe                                                 828



                                                                                                                                                      8 302
                                                 Masse des services financierrs
                                                                                                     1 200



                                                                                                                                                   7 937
                                          Fonds de solidarité des assurances
                                                                                                                            44 500



                                                                                                                                  5 503
                   Fonds d'appui au financement de l'entrepreunariaat
                                                                                                            2 226



     Fonds de gestion des risques afférents aux emprunts des tierrs                  44 505
                                   garantis par l'Etat                              2



                                                                                                                   3 165
                                Fonds de lutte contre la fraude douanièrre
                                                                                                     1 155



                                                                                                                2 810
                        Fonds pour la promotion de l'emploi des jeunes
                                                                                                        1 579



                                                                                                         1 729
                                 Fonds de promotion des iinvestissementts
                                                                                                   876



                                                                                                   787
                                    Fonds provenant des dépôts au Trésor
                                                                                                  749



  Bénéfices et pertes de conversion sur les dépenses publiques en 47
                                devises étrangères                               10



                                                                         Recettes                Dépenses
                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 
 
                                                                                                                                                                               45

52
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                                                                                                
                       EVOLUTION DES RECETTES* ET DES DEPENSES DES CAS INTERVENANT DANS LE DOMAINE DE LA PROMOTION ECONOMIQUE 
                                                            ET FINANCIERE AU TITTRE DE LA PERIODE 2021‐2023 (EN MDH)



                                                                                   46 757                                              46 3350
                          44 859















                                                                                                                                                             13 124
                                                                                                    10 049
                                             9 159






                                 2021                                                   2022                                                    2023


                                                                             Recettees           Dépenses
                                                                                                                                                                                                 
(*) Compte tenu du solde reporté. 

2.3.1.    Fonds     pour     la   promotion         de   l’emploi        des    jeunes 

En 2023,    les  recettes    du  Fonds    pour   la  promotion      de  l’emploi    des   jeunes   ((FPEJ),   compte    tenu   du 
solde   reporté,    ont   atteint    2.809,95    MDH,   contre    2.563,30    MDH   en 2022    et  744,34    MDH  en  2021. 

  
Quant    aux   dépenses,    elles    ont   atteint     1.578,65   MDH   en   2023,   contre     2.2281,36  MDH   en  2022    et  
639,30   MDH   en  2021,  enregistrant      un  accroissement       annuel   moyen    de  57,114%.  
 
 
En effet,    l’augmentation       enregistrée     au  niveau    des   recettes    et  des  dépensses   dudit    Fonds   est   due, 
principalement,       à  son  utilisation      comme    support     budgétaire      pour   le  financement       du  programme 
Awrach. 
 
Outre   le  programme      Awrach,    ce  compte     finance    aussi  bien   la  réalisation     de  certains    programmes 
actifs   de  l’emploi    ainsi   que   les  programmes      de  formation     par   apprentissage. 
 
   Domaine      de  l’emploi       : 
 
          Programmes      actifs    de  l’emploi     : 

             
Le  bilan    de   réalisation      des   programmes       actifs    de   l’emploi     financés     parr   le  FPEJ,   en   terme     de 
nombre    de  bénéficiaires,      pour   la  période    2021-2023,     se présente     comme    ssuit : 
 
 
 

 
             46 

53
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
 

                                                                                                                        Nombre de bénnéficiaires 
                                 Programmes 
                                                                                                             2021                     20222                    2023 

IDMAJ                                                                                                  97.174                 114.2236                119.863 

TAHFIZ                                                                                                15.559                  18.9973                  18.639 

                          Formation  Contractualisée pour l'Emploi                  7.073                     3.695                     14.020 

                        Formation  Qualifiante  ou de Reconverrsion               2.947                     1.3331                     693 
TAEHIL 
                       Formation  d'Appui  aux Secteurs Emergents              10.768                   8.587                      8.767 

                                                 Total  Taehil                                       20.788                    13.6613                23.480 

 
Les  réalisations     dans   le  cadre    du   programme      IDMAJ   au   titre   de   l’année   22023  s’élèvent     à 119.863 
insertions     dont     15.462    dans    le  cadre     du   placement       à  l’international,        ssoit  une    hausse    de   5% 
comparativement        à l’année    2022.   La  répartition      desdites    insertions     se préssentent    comme    suit   : 
 
 
                           REPARTITION PAR DIPLOME                                      RAPARTITION PAR SECCTEUR D'ACTIVITE

                                                                                                                              3%

                                     Autres                                                                                           5%
                                                                                                                  1%
                                       8%                                                                                    7%

                         Diplomés                                                                      1%
                      Enseignement            Diplomés                                                                                   41%
                         Supérieur                Formation 
                           22%                    Professionnelle 
                                                            34%

                                                                                                                                  42%
                                 Bacheliers
                                    36%

                                                                                                      Services                  Industriee               BTP
                                                                                                      Agriculture, Pêche  Educationn              Hôtellerie
                                                                                                      Autres
                                                                                                                                                                                                
                                                                                                
                                                                             REPARTITION PAR GENRE





                                                                        Masculin                     Féminin
                                                                           52%                           48%







                                                                                                                                                                                                
                           
La  répartition      des  bénéficiaires      du  programme      Tahfiz    dédié   aux   entreprisses    nouvellement      créées 
se présente     comme    suit  : 

 
                                                                                                                                                                               47

54
                                                                                             
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 
                                 REPARTITION PAR GENRE                                                REPARTITION PAR SECCTEUR D'ACTIVITE

                                                                                                                                                                   Agriculture, 
                                                                                                                                       Education               Pêche
                                                                                                                                            3%                       2%
                                                                                                                          Hôtellerie
                                                                                                                              7%


                         Féminin
                           32%                                                                                               Industrie
                                                                                                                                     8%                                Services
                                                                                                                                                                             35%


                                                                                                                                        BTP
                                                               Masculin
                                                                                                                                       15%
                                                                   68%



                                                                                                                                                            Auttres
                                                                                                                                                             300%




                                                                                                                                                                                                                     
 
La   formation        contractualisée           pour     l’emploi        s’est    caractérisée         en   2023     par     la  signature          de    126 
conventions          triparties          de     formation,          totalisant         14.020       opportunités            de     formation          en     vue 
d’accéder        à   l’emploi.        La   répartition          sectorielle         de    ces    conventions          montre       la    dominance         du 
secteur     de   l’automobile         qui   représente        75%   des    besoins     en   formation. 
 
                                                     REPARTITION DES CONVENTIIONS DE FORMATION PAR SECTEUR D'ACTIVVITE





                                                                                   3% 3% 3% 1%
                                                                           3%

                                                                           5%
                                                                   6%



                                                                                                                    75%











          Automobile                                                     Conseil en systèmes informatiques               Educaation & Enseignement

          Services                                                         Hôtellerie et restauration                                Santéé et action sociale

          Commerce                                                     Textile
                                                                                                                                                                                                                     
 
 


 
              48 

55
                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
Au titre   du  dispositif   d’appui  aux  secteurs  émergents,  8.767 salariés  des  entreprises  opérant 
dans les secteurs émergents ont  participé  à une ou plusieurs formations  permettant  de  renforcer 
leurs compétences   managerielles  et   techniques.  Le  secteur  de  l’Offshoring   reste  le  premier 
secteur bénéficiaire, suivi de ceux  de l’automobile  et de l’aéronautique. 
 
                                               RAPARTITION DE L'EFFFECTIF ENGAGE PAR SECTEUR D'ACTIVITE


                                                                     Aérronautique
                                                                          4%



                                                                                                 Automobile
                                                                                                     43%
                                                  Offshoring
                                                      53%








                                                                                                                                                                
 
Par ailleurs, le bilan  de réalisation  des programmes  actifs  d’emploi  à fin  août  2024, se présente 
comme suit : 
 
        Le programme   «IDMAJ»  : a permis  d’insérer  86.532 bénéficiairess contre 80.456  au  titre 
          de la même  période de l’année 2023 enregistrant  ainsi une hausse de près 8% ; 
 
        Le programme   «TAHFIZ»  : a permis à 5.030  entreprises  de bénéfficier de  ce programme 
          avec  une  insertion  de  13.016 personnes contre  11.746 bénéficiairees au titre de  la  même 
          période  de l’année 2023, soit une augmentation   de près 11% ; 
 
        Le programme   «TAEHIL»  : a permis  à  11.633 chercheurs d’emploi de  suivre un  cycle de 
          formation  pour  faciliter  leur insertion  dans le marché de ttravail, contre  17.373 bénéficiaires 
          au titre  de la même période  de l’année 2023, soit une  baisse de 33%. 
 
  Domaine  de la formation   par apprentissage  : 
            
La  formation   par  apprentissage   est  un   mode  de   formation   institué   et  organisé   par  la  loi          
n° 12-00, promulguée  le 19 mai 2000,  basé sur une formation   pratique en  entreprise à  raison de 
80% au moins  de  sa durée  globale  et, complétée   pour  10% au moins de  cette  durée,  par  une 
formation  générale  et technologique   organisée, dans le  cadre de  convenntions conclues avec le 
département  de la formation  professionnelle, par : 
 
        Les chambres ou organisations professionnelles  ; 
        Les entreprises publiques ou privées  ;; 
        Les associations créées conformément  à la législation en vigueur  ; 
        Les établissements de  formation  proffessionnelle relevant de l’Etat  ou  agréés par lui, à cet 
          effet. 
           
Ce mode de formation  a pour objectifs  de :
 
 
                                                                                                                                                  49

56
                                                                              
   PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
  
          Faire  acquérir   aux  jeunes   un  savoir-faire   par   l’exercice   d’une   activité   professionnelle    leur 
             permettant    d’avoir  une  qualification    favorisant   leur  insertion   dans  le marché   de travail   ; 
          Contribuer    à  l’amélioration     de   l’encadrement     du  tissu   économique    des   PME/Petites    et 
             Moyennes  Industries   (PMI)  ; 
          Contribuer   à la  sauvegarde   des métiers   de  l’artisanat   ;  
          Assurer  aux  jeunes  ruraux  une  formation   adaptée   aux  spécificités   de  leur  milieu. 
  
 Ainsi,  pour  le  développement     de la  formation    par  apprentissage,   l’Etat   accorde   une  contribution 
 aux  frais  de  formation    des  jeunes  bénéficiaires    de  la formation    par  apprentissage    dans  le  cadre 
 du Fonds   de la promotion    de  l’emploi   des jeunes. 
  
 Par ailleurs,  le  bilan  physique   du dispositif    de formation    par  apprentissage    au titre   de 2023-2024, 
 se présente   comme  suit  : 
  

                                                                                                      Effectif des apprentis 
                                   Type de formateur                                                                                          En % 
                                                                                                              2023/2024 

  Artisanat                                                                                                  9.791                               31,9% 

  Centre de formation intra-entreprise                                                       7.905                               25,7% 

  Agriculture                                                                                               4.168                               13,6% 

  Entraide nationale                                                                                   3.748                               12,2% 

  Organisation non gouvernementale                                                        3.617                               11,8% 

  Autres (pêche maritime, AREF, Chambre de commerce…)                   1.467                               4,8% 


                                             Total                                                            30.696                              100 % 


 2.3.2.    Fonds    de  promotion       des   investissements  

 A   compter    du   1er janvier   2023,   le   CAS   intitulé    Fonds   de   développement      industriel     et  des 
 investissements    (FDII),   a été   modifié   pour   devenir   le  Fonds   de  promotion    des  investissements 
 (FPI)  selon  les  dispositions    de  l’article   14  de  la loi  de   finance  n°  50-22   pour   l’année  budgétaire 
 2023,  promulguée    par le  Dahir  n°  1-22-75 du  18 joumada  I  1444 (13 décembre    2022)  et  ce, en  vue 
 de permettre    la comptabilisation      des opérations    afférentes   à la prise  en  charge  par  l’Etat  du  coût 
 des   avantages     accordés     aux    investisseurs     dans    le   cadre     des   dispositifs      de   soutien     à 
 l’investissement     ainsi  que  la  prise  en charge   de  toutes   autres  dépenses   relatives   au soutien   et  à 
 la promotion    des  investissements. 

  
 Les recettes    réalisées  par  le  Fonds  de  promotion    des  investissements    en  2023,  compte   tenu   du 
 solde  reporté,   s’élèvent   à  1.728,81 MDH  contre   2.677,17 MDH  en  2022  et  2.798,56   MDH  en  2021, 
 enregistrant    ainsi une  baisse  annuelle  moyenne   de 21,40%.  

 Quant   aux  dépenses,   elles  ont   atteint    876,05   MDH  en  2023,   contre   2.301,36  MDH  en  2022   et 
 1.701,39 MDH en 2021,  enregistrant   ainsi  une  baisse annuelle   moyenne   de 28,24%. 

  

   Bilan   des  programmes     réalisés   et  des   projets   financés    à  travers   le   FPI  durant   les  années 
     2022   et  2023  : 
 Le Ministère   de  l’Investissement,    de  la Convergence    et  de l’Evaluation    des Politiques    Publiques  a 
 procédé   au  titre   des  années   2022  et  2023   au  déboursement,    des   primes  à  l’investissement     au 
 titre  des  projets   cités  ci-après  : 
       -    Primes   d’investissement      versées   au titre    de l’année   budgétaire     2022   : 


  
             50 

57
                                                                                        RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
  
  
                                                                                                                                                                 (En MDH) 

                                                                                 Montant total de la prime à        Montant du déboursement 
                            Bénéficiaires 
                                                                                   l’investissement accordé           au titre  de l’année 2022 


  RIVA INDUSTRIE                                                                     60                                              60 

  MEDZ                                                                                     36,50                                           7,16 

  KAPSET OFFICE                                                                      15                                            10,86 

  ESPACE LADID                                                                       6,13                                           0,19 

  PROVIDENCE VERTE                                                            5,37                                           2,58 

                                  Total                                                       123,00                                        80,79 

  
 D’autre   part,   un  montant    global   de  2.020,58   MDH  a  été  déboursé    à  partir   du  FDII  au  titre    de 
 l’année  2022,   il  concerne   notamment    les  primes   à  l’investissement    accordée   dans   le cadre   des 
 écosystèmes     industrielles     (565,97    MDH),    le   renforcement      des    infrastructures      industrielles 
 (454,36    MDH),    l’appui    à   la   compétitivité       des   entreprises     (295    MDH)    et   le    soutien    aux 
 investissements    industriels   d’envergure   et  à l’émergence   de  champions   nationaux   (600,11  MDH). 
  
       -    Primes   d’investissement      versées   au titre    de l’année   budgétaire     2023   : 

 Au  titre  de  l’année  2023,   il a été  procédé   au  déboursement    d’un  montant    global   de 876,05   MDH 
 au profit    de  77 projets   d’investissement     bénéficiaires    de  l’appui   de l’Etat   dont   5 projets    réalisés 
 dans   le   cadre    de   l’ancienne    charte    (loi   cadre    n°   18-95)   pour    une   somme    déboursée     de           
 69.74  MDH, et  72  projets  réalisés  dans  le  cadre  du Plan  d’Accélération    Industrielle    (PAI)  pour  une 
 somme  déboursée   de  806,31 MDH. 

   Plan d’action    du  Fonds  de  promotion    des  investissements    au  titre   de l’année   2024   : 
      
 Le  financement     des  projets    d’investissement     est   cadré   par   les   conventions    d’investissement 
 signées  entre   l’Etat  et  les  entreprises   choisies   pour  bénéficier    des  aides  à l’investissement     selon 
 les critères   arrêtés  par  les  textes  d’application     de la  charte  de  l’investissement.    Le déboursement 
 des primes   à l’investissement,    qui  suit  la réalisation   physique   du  projet,   se fait  suite  à la  demande 
 des investisseurs   eux-mêmes. 
 Il  convient     de   noter    que   les   dotations     budgétaires     allouées    au  Fonds    de   promotion     des 
 investissements    au titre   de l’année   2024  s’élèvent   à 3.353  MDH,  dont  2.000   MDH  sont  consacrés 
 aux  projets    relevant    de  la   charte   d’investissement     et   1.353  MDH  sont   consacrés   aux   projets 
 exécutés   dans  le  cadre  des  écosystèmes    industriels   relevant    du  Plan  d’Accélération    Industrielle 
 (PAI). 
 Le  total   des  versements   opérés   au  titre   du  1er semestre  de  l’année  2024,   s’élève  à  344,18  MDH 
 réalisés   dans    le   cadre   des    projets    relevant    de    l’ancienne    charte    d’investissement      et   des 
 écosystèmes   industriels,   soit  un  taux  d’exécution   de  10% du budget   consacré   auxdits   projets. 

 2.3.3.    Fonds    de  solidarité       des   assurances  

 Le  Fonds  de  solidarité    des assurances   (FSA)   a été   créé  en  vue  de  comptabiliser    les  opérations 
 afférentes   à : 
  
          l’attribution    d’aides   aux  entreprises   d’assurance    destinées   à pallier   le déséquilibre    de  leur 
            situation    financière    résultant   de  l’exercice    d'une   ou  de  plusieurs   catégories    d'opérations 
            d'assurances   obligatoires    pour  lesquelles   elles  sont  agréées  ; 
  
                                                                                                                                                                 51

58
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
        l’octroi    de  subventions   aux  entreprises    d’assurance   en état   de liquidation    afin  de  combler 
           l’insuffisance    d’actifs  afférents   aux  catégories   d’opérations    d’assurances   obligatoires    ; 

        l’octroi     des  subventions    aux   entreprises    d’assurance    cessionnaires    en  cas   du  transfert 
           d’office    d’un   portefeuille     des  contrats    en  cours   et   des  sinistres,   pour   combler    tout    ou 
           partie     de    l'insuffisance      d'actif     de     l'entreprise      cédante     en    considération      de    ses 
           engagements    réels. 
 
Le  FSA    est   financé,    essentiellement,     par   la   part    du   produit     de   la   taxe    sur   les   contrats 
d’assurances    conclus     par    les   entreprises     d’assurance,     le    produit     de    la   contribution    des 
entreprises    d’assurance,   de  réassurance    et   de  capitalisation     agréées,   ainsi  que   les  excédents 
d’actif  résultant   de  la liquidation    des  entreprises   d’assurance  et  de  réassurance. 
 
En   2023,   les    recettes    dudit     Fonds    se   sont    établies,    compte     tenu    du   solde    reporté,     à           
7.936,85  MDH  contre   8.132,91 MDH  et  9.436,13  MDH,  respectivement,     en  2022  et  2021,  soit  une 
baisse  annuelle  moyenne    d’environ   8,29%.  Quant  aux  dépenses,   elles  ont  atteint    4.500   MDH  en 
2023,  contre   1.000  MDH en  2022  et  2.000   MDH  en 2021,  soit  un  accroissement    annuel  moyenne 
d’environ   50%.  

2.3.4.    Masse   des   services     financiers 

En  2023,  les  recettes    du  compte    Masse  des  services   financiers    (MSF),  compte    tenu   du  solde 
reporté,   ont   atteint    8.302,21   MDH  contre    7.849,35    MDH  en  2022    et  7.385,49    MDH  en   2021, 
enregistrant    ainsi   un  accroissement    annuel   moyen    de  6,02%.  Quant    aux  dépenses,   elles   sont 
passées  de 970,73   MDH  en  2021 à 1.199,64  MDH en  2023,  avec   un accroissement    annuel   moyen 
de 11,17%. 
 
Les  principales     dépenses    imputées     sur   ce   compte,    au   titre    de   la   période     2021-2023,    se 
présentent   comme   suit :                                                                            
                                                                                                                                                                                                   
 
                                                                                                                                                                                                  (En MDH) 


                                                 Rubriques                                                      2021            2022            2023 



  Remboursements, dégrèvements et restitutions fiscaux                              70,13          41,76           58,52 


  Charges immobilières                                                                                  50,79           54,32           56,90 


  Frais de communication                                                                               20,84           20,85           19,97 


  Projets de construction, d’aménagement, d’installation et d’équipement     13,03          40,72           74,51 


  Projets informatiques                                                                                     6,71            11,88          13,74 



  Achat de fournitures                                                                                      5,29             8,14            8,63 

 
Au titre   de  la période   2024-2027,    le  recours  audit   compte   se  poursuivra   pour   la prise  en  charge 
des principales   actions   suivantes    : 
 


 
            52 

59
                                                                                      RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
     -     Remboursements,    dégrèvements    et  restitutions   fiscaux   ; 
     -     Frais  de recouvrement    ; 
     -     Dépenses  liées  au bon  fonctionnement     des  services  de  la Direction   Générale  des  Impôts   ; 
     -     Actions   liées à  la modernisation    de  l’administration    fiscale  se  rapportant    notamment    aux :  
   
           projets    de   construction,      d’aménagement      et   d’équipement      vissant  l’amélioration     des 
              conditions   de  travail  et  d’accueil   des contribuables    ; 
                          
           projets   informatiques     visant   une  meilleure    mobilisation    des   receettes  fiscales,  ainsi   que 
              l’amélioration    de la  qualité  de  service  rendu  aux  usagers  et  aux paartenaires. 

2.3.5.   Fonds    de   lutte    contre     la  fraude     douanière  

L’évolution   des  recettes   et  des dépenses   du  Fonds  de  lutte  contre   la  fraude  douanière,   durant   la 
période  2021-2023,   se présente   comme  suit : 
 
            
                     EVOLUTION DES RECETTES* ET DES DEPENSES DU FONDS DE LUTTE CONTRE LA FRAUDE DOOUANIERE AU TITRE 
                                                                 DE LA PERIIODE 2021‐2023 (EN MDH)





                                                                                                                                 3 164,99
                 3 042,36                                          3 0066,25








                                                                                                                                                 1 154,94
                                  995,91                                             942,26





                           2021                                                2022                                                2023

                                                                        Recetttes      Dépenses
                                                                                                                                                                               
(*) Compte tenu du solde reporté. 
 
Les principales   opérations    financées  par  ce Fonds,  se  présentent   comme   ssuit : 
  
    Rétributions    contentieuses   et  indemnités   dans  le cadre   de la lutte   contre   la fraude  ; 

    Diverses  dépenses  liées  à la  lutte  contre   les fraudes   douanières  ;  

    Action   sociale  ; 

    Versement    au   budget     général    de   la   part    du   Trésor    dans   le   prroduit    des   réparations 
      contentieuses    ; 

 
                                                                                                                                                               53

60
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
   Optimisation  de l’action  en recouvrement  des créances publiques  ; 

   Support  et pilotage. 

2.3.6.  Fonds   provenant     des  dépôts    au Trésor  

En 2023, les recettes du Fonds provenant  des dépôts  au trésor ont  atteint, compte  tenu  du solde 
reporté,  786,72  MDH  contre  733,27  MDH  en  2022  et  767,43  MDH  en  2021. Concernant   les 
dépenses, elles ont  atteint  748,54  MDH en 2023  contre  724,26 MDH en 2022  et  741,21 MDH en 
2021.  
 
Les principales natures de dépenses programmées  entre 2021 et 2023, autres que  celles liées aux 
indemnités du personnel, se présentent  comme suit  : 
 

   Frais  de  surveillance   des locaux   administratifs    ;  

   Entretien   et  réparation   des  bâtiments   administratifs     ; 

   Taxes  postales  et  frais  d'affranchissement     ; 

   Fournitures    de bureau,   produits   d’impression,   papeterie   et  imprimés   ; 

   Achat   de fournitures    pour  le  matériel  informatique     ; 

   Frais  de  formation   et  de stage   ; 

   Maintenance   des  logiciels,   progiciels   et solutions   informatiques. 

L’exécution des dépenses effectuées  dans le cadre de ce Fonds se présentent  comme suit : 
                                                                                                                                                 (En MDH) 


                                           2021                           2022                          2023               Au 15 mai 2024 




Crédits ouverts                  753,75                        727,78                       755,16                   398,17 



Engagements                   745,05                         727,01                       753,95                   394,01 



Emissions                          741,21                       724,26                       748,54                   375,06 


 

2.3.7.  Compte    spécial   des  dons   des  pays  du  Conseil    de  Coopération     du  Golfe  

L’évolution  des recettes  et  des dépenses  du Compte  spécial  des dons  des pays  du Conseil  de 
Coopération du  Golfe, durant la période  2021-2023, se présente comme suit :  



 
           54 

61
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
                      EVOLUTION DES RECETTES* ET DES DEPENSES DU COMPTE SPECIAL DES DONS DES PAYS DUU CONSEIL DE 
                                              COOPERATION GOLFE AU TITRE DE LA PERIODE 2021‐2023 (EN MDH)



                  12 068,85
                                                                               11 237,40                                            11 5565,02








                                     1 211,23
                                                                                                   456,26                                                  828,14


                              2021                                                     2022                                                     2023


                                                                         Recettess            Dépenses
                                                                                                                                                                                                 
(*) Compte tenu du solde reporté. 
 
En termes    d’engagement,       les  dons   des  pays   du  Conseil    de  Coopération      du   Golfe   ont  été   engagés 
en  totalité.     Ainsi,    à  fin   juin   2024,    la  répartittion      sectorielle     des projets       bénéficiant de        ces   dons, 
comme    le  montre     le  graphe     ci-après,    fait    ressortir     une   prédominance       dees secteurs     sociaux    qui 
représentent      près   de  57%  des   financements,      ce  qui   indique    la  préférence      des  donateurs     pour    les 
projets    à vocation     sociale.  
 
                                                RÉPARTITION DES DOTATIONS DU DON ARABE PAR SECTEURS

                                                                                                       Secteurs productifs
                                                                                                                10%






                                                                                                                                                   Secteurs de l'infrastructure
                                                                                                                                                                 33%

                      Secteurs sociaux
                              57%





                                                                                                                                                                                                 
 
 
L’éducation,      la  formation     professionnelle       et   la  santé    bénéficient     de   61% des   dotations      réservées 
aux   secteurs    sociaux.     Le   reste   est   affecté     à   l’habitat     social    (21%)   et  au   développement         social 
(INDH   et  développement       rural)    (18%). 
 
Concernant      les   dotations      dédiées     aux    secteurs     de   l’infrastructure        (33%),     elles   sont    réparties 
entre    les   projets     de   transport      (68%),    les   barrages     (17%)   et   les   projetss    d’alimentation        en  eau 
potable,     en  électricité      et  à l’assainissement      (15%). 

Pour   les  secteurs    productifs      (10%),   les  dépenses     effectuées     ont   financéess,   à  hauteur    de  86%,   les 
projets    d’agriculture      et,  à  hauteur    14%, ceux de    la  pêche   maritime. 


 
                                                                                                                                                                               55

62
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
En termes de  tirages réalisés à fin  juin 2024,  les montants  des dons Koweitien  et  Qatari ont  été 
décaissés en totalité  (soit  1.250 millions de dollars  US chacun). Quant  aux dons  des autres pays 
donateurs, les décaissements réalisés ont  atteints  1.209 millions de  dollars US sur le  don Emirati 
et 1.190 millions de dollars US sur  le don Saoudien. Le  reliquat, s’élevant  à 95 millions  de dollars 
US, sera décaissé durant  l’année 2025, en  fonction  de  l’état  d’avancement  des projets  financés 
en cours d’exécution, ainsi qu’avec  le redéploiement  des reliquats des projets  achevés. 

2.3.8.  Fonds   d’appui    au  financement     de  l’entrepreneuriat 

Le Fonds  d’appui  au  financement   de l’entrepreneuriat   (FAFE)   a été  créé  conformément   aux 
dispositions de l’article  15 de la loi de finances pour l’année budgétaire  2020.  
 
Ce Fonds a été mis en place dans le  cadre du programme  intégré  d’appui  et de financement  des 
entreprises   (PIAFE).   Ce   programme    ambitionne    d’apporter     une   solution    globale    à   la 
problématique   d’accès  au  financement   notamment   des  jeunes  porteurs   de  projet   des  Très 
Petites Entreprises (TPE). Ce programme  devrait, non seulement  créer de nouvelles opportunités 
pour les  jeunes porteurs  de  projets,  mais  également, contribuer   à améliorer  les  indicateurs  de 
développement   de  notre   pays  aussi  bien  en  termes  d’emploi,   de  résorption   des  disparités 
territoriales  que d’inclusion socio-économique. 
 
Le FAFE a été doté  d’une enveloppe  de 8 MMDH, dont 3 MMDH provenant  du budget  général  et 
3 MMDH comme   contribution   du  secteur  bancaire. A  cette   enveloppe  s’ajoutent  2  MMDH du 
Fonds Hassan II pour le développement  économique et  social destiné au monde rural. 
 
Par  ailleurs,  la   mise  en   œuvre   du  volet   financement    du  PIAFE   a  été   possible   grâce  à 
l’opérationnalisation  de  nouveaux produits   de garantie  offerts  par  la SNGFE (Ex-CCG) aux TPE 
et jeunes porteurs de  projets, suivants : 
           
    -  ‘’DAMANE  INTELAK’’  : Produit  de  garantie  ciblant  les auto-entrepreneurs,   les porteurs  de 
      projet  et les TPE; 

    -  ‘’DAMANE   INTELAK   AL  MOUSTATMIR  AL   QARAWI’’  : Produit   de  garantie   ciblant  les 
      petites  exploitations  agricoles,  les TPE, les porteurs  de projets  et  les auto-entrepreneurs  du 
      monde rural  ; 

    - ‘’START-TPE’’ : Produit  de financement  sous la forme  d’une avance  remboursable après une 
      franchise de 5  ans, sans intérêts et sans exigence de  sûretés, à destination  des TPE, porteurs 
      de projet  et auto-entrepreneurs. 
En  2023,  les   recettes  réalisées   par  le   FAFE,  compte   tenu   du  solde   reporté,   ont   atteint           
5.503,42 MDH contre  6.075,92  MDH et  4.268,84 MDH, respectivement,  en  2022 et  2021. Quant 
aux dépenses, elles ont atteint  2.226,19 MDH en 2023, contre 1.202,70 MDH en 2022 et 880  MDH 
en 2021. 
A fin  juin  2024, le  nombre  de crédits  accordés  dans  le cadre  du programme   « Intelaka  » s’est 
établi  à 42.570  prêts  pour  un volume  de  crédits  de 10 MMDH  et un  volume  d’engagement  de           
8 MMDH. Ces financements  devraient  permettre   à plus  de  33.900  entreprises  bénéficiaires  de 
créer plus de 124.400 emplois. 
 
Concernant  les  dotations   Start  TPE  versées  aux  banques,  à fin   juin  2024,  elles  s’élèvent  à           
190,6 MDH pour un nombre de crédit  de 6.660.  
 
 
 
 
 



 
           56 

63
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
SECTION               IV     -   RENFORCEMENT                          DES        INFRASTRUCTURES 
 
Les  dépenses    des  comptes     d’affectation       spéciale    intervenant     dans   le  domaine    des   infrastructures 
représentent      environ    8,44%   du  total    des  dépenses    effectuées     en  2023   parr  l’ensemble     des  CAS.  
 
L’évolution     des   recettes    et  des  dépenses     desdits    CAS  se  présente    commee  suit   : 

 

 

                          RECETTES*ET DEPENSES REALISEES AU NIVEAU DESS CAS INTERVENANT DANS LE DOMAINE DE L'INFRRASTRUCTURE AU TITRE 
                                                                                DE L''EXCERCICE 2023 (EN MDH)




                                                                                                                                                                                6 935
                                                                    Fonds spécial rooutier
                                                                                                                                     3 198



                                                                                                                                                                          6 392
                                         Fonds national de développement du sport
                                                                                                                                                4 138



         Fonds d'accompagnement des réformes du transport routier urbaain et                                4 932
                                            interurbain                                                    1 339



                                                                                                                                                4 153
                                 Fonds de service universel de télécommunicaations
                                                                                                      384



                                                                                                                                         3 553
                      Fonds de lutte contre les effets des catastrophes naturelles
                                                                                                                   1 541



     Fonds d'assainissement liquide et solide et d'épuration des eaux uséées et 2 041
                                      leur réutilisation                                     204



 Fonds national pour la protection  de l'environnement et du développement 2 016
                                          durable                                              229



                                                                                                           826
                                               Fonds de développement énergéétique
                                                                                                       443



  Fonds de délimitation, de préservation et de valorisation du domaine public 166
                                  maritime et portuaire                               13



                                                                              Recetttes           Dépenses
                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 
 
 
 
                                                                                                                                                                               57

64
                                                                                             
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 
                          EVOLUTION DES RECETTES* ET DES DEPENSES DES CAS INTERVENANT DANS LE DOMAINE DE L'INFRASSTRUCTURE AU TITRE DE 
                                                                                       LA PERIODE 2021‐2023 (EN MDH)




                                                                                                                                                           31 0014

                                                                                            26 780

                              23 151





                                                                                                              10 862                                                    11 489
                                                    7 481






                                     2021                                                         2022                                                          2023

                                                                                          Recettes           Dépenses
                                                                                                                                                                                                                     
(*) Compte tenu du solde reporté. 

2.4.1.      Fonds       spécial        routier  

L’évolution        des    recettes       et   des    dépenses       du   Fonds     spécial      routier      (FSR)),    au   titre     de   la   période 
2021-2023,       se  présente      comme      suit    : 
 
                                EVOLUTION DES RECETTES* ET DES DEPENSES DU FSR AU TITRE DE LA PERIODE 2021‐22023 (EN MDH)







                                                                                                                                                           6 9335,15
                                                                                            6 6676,72
                              6 130,64




                                                                                                              3 392,22                                                 3 197,86
                                                2 984,51







                                         2021                                                       2022                                                      2023




                                                                                       Recetttes          Dépenses
                                                                                                                                                                                                                     
(*) Compte tenu du solde reporté. 
 
Les   crédits      programmés          dans    le   cadre     du    FFSR au    titre     de   la   période      2021-2023,        se   présentent 
comme     suit    : 
                                                                                                                                                                                                                     
                                                                                                                                                                                                                     

 
              58 

65
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
                                                                                                                                                                              
                                                                                                                                                                 (En MDH) 

                                         Programmes                                                   2021                 2022              2023 


 Versement                                                                                             2.500                  3.111            3.090 


 Maintenance et conservation du patrimoine routier                              733,60              851,40           982,20 


 Exploitation                                                                                           283,80              293,40            293,80 


 Parc et Atelier                                                                                        131,80              231,20           160,50 


 Routes dans le monde rurale                                                                   99                     67                  40 


 Études routières                                                                                     8,70                  10,70               10 


 Soutien aux Missions                                                                              1,20                  2,50               2,50 


                                               Total                                                       3.758,10           4.567,20          4.579 

 
Le bilan  des  réalisations   dudit  Fonds  au  titre  de  la même  période,   se présente   comme   suit  : 
 
          Maintenance   des  Ouvrages   d’Art   (OA)   : 
            
Durant   la  période    2021-2023,   le  FSR   et  le  budget    général    ont   contribué    au  financement     de 
projets   d’entretien,    de réparation    et  de  reconstruction     des  OA  en  vue  de  garantir   la  sécurité   et 
assurer  un bon  niveau  de  services  aux  usagers  de la  route.  
 
De ce  fait,   cette   période   a été   caractérisée   par  l’achèvement    des  travaux    de  reconstruction     de 
118 OA d’un  montant    d’environ    1.400  MDH.  L’année  2023   a connu   le  lancement   des  travaux   de 
reconstruction    de  91 OA d’un  montant   d’environ    473 MDH.  
 
          Maintenance   routière    et  adaptation    du   réseau  routier   : 
      
En  vue   de  conserver    l’état    du   réseau   routier    et  son   adaptation     à  l’évolution     du  trafic,    des 
opérations    de  maintenance    et   de  mise   à  niveau   de   3.565  km   dudit   réseau   ont   été   réalisées 
durant  la période   2021-2023,   soit  une moyenne   annuelle   de 1.188 km.  
 
Durant   la  même   période,   la  contribution      du  FSR  au  financement     de  ces  opérations    a  atteint 
5.702  MDH.  
 
          Sécurité   routière   : 
 
                  Traitement    des axes  routiers   accidentogénes     : 
 
Dans le cadre   de la  politique   générale   du gouvernement     en matière   du  transport,   visant  à assurer 
un haut  degré   de sécurité   du  système   des transports    au  profit   des usagers   de la  route  et  réduire 
le  nombre    de   décès   dus  aux   accidents    de   la  circulation     à  50%   d’ici   2026,   le   Ministère    de 


 
                                                                                                                                                               59

66
                                                                       
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
  
 l’Equipement et  de l’Eau s’est engagé à la réalisation  d’un programme  spécial pour  l’amélioration 
 de la sécurité routière  qui s’articule  autour de deux axes à savoir : 
  
         Le traitement  des axes stratégiques accidentogénes  suivantes : 
              ‐   La route  nationale reliant Marrakech  à Ouarzazate via Tichka sur 177 km; 
              ‐   La route  rapide reliant Meknès à Souk Laarba sur 88,5 km. 
  
         Traitement  des  points  noirs répartis  sur  le  reste du  réseau routier   représentant  un  taux 
           d’accidents  important. 
            
 Le volume  d’investissement du  FSR durant la  période 2021-2023  a atteint  un montant  d’environ 
 1.335 MDH (CP et CE). 
  
                 Signalisation  : 
  
 Au cours de la même  période, le FSR a contribué  au financement  des opérations de  signalisation 
 routière d’un  linéaire d’environ 13.000  km, avec un montant  global de 696  MDH. 
  
          Programme  de réduction  des disparités  territoriales   et  sociales : 
 
 Au cours de la  période 2021-2023, un montant  de 2.331 MDH, a été versé pour le financement  du 
 programme  de lutte contre  les disparités territoriales  et  sociales dans le monde rural. 
  
  
  Opérations  programmées  au titre  de  l’année 2024  :  
    
 Les principales actions programmées  en 2024, dans le cadre  du FSR, se présentent comme suit: 
  
  

                                                                                                                                            Montant 
                                                  Nature des opérations 
                                                                                                                                           (En MDH) 


  Maintenance des routes 
                                                                                                                                             2.206,5 
   


  Versement                                                                                                                           1.970 


  Maintenance des OA                                                                                                            300 


  Exploitation et sécurité routière                                                                                           266,8 


 2.4.2.   Fonds   de  délimitation,      de  préservation      et  de  valorisation      du  domaine    public 
           maritime     et  portuaire  

 L’évolution   des  recettes  et   des  dépenses  du  Fonds  de  délimitation,   de  préservation   et   de 
 valorisation  du domaine  public  maritime  et  portuaire  durant  la  période  2021-2023, se présente 
 comme suit : 


  
            60 

67
                                                                                      RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
                        EVOLUTION DES RECETTES* ET DES DEPENSES DU FONDS AU TITRE DE LA PERIODE 2021‐‐2023 (EN MDH)



                        175,85                                          1174,98
                                                                                                                                  1165,76








                                        23,38                                            20,16
                                                                                                                                                  13,19


                                 2021                                             2022                                             2023


                                                                      Recettes             Dépenses

(*) Compte tenu du solde reporté. 
 
L’exécution    des   dépenses    programmées     dans   le   cadre   dudit    Fonds,    y  compris    les   crédits 
reportés,    au  titre    de   la   période    2021-2023,    a  permis    le  lancement     des   principales    actions 
suivantes  : 
 
             Travaux   de  consolidation    du  trait   de côtes    et  de plages,    rechargement        : 55,68 MDH ;
               des  plages  en  sable et  petits   ouvrages 

             Etudes  et  travaux   de  délimitation     et  de  préservation    du domaine    public      :  22,00 MDH ;
               maritime    et portuaire    (DPMP)  

             Etudes  de  suivi du  trait   de côte                                                                                 :  19,14  MDH ; 

             Etudes  générales  et  honoraires   d’avocat                                                                  : 12,95 MDH ;

             Surveillance   et entretien    du domaine   public   maritime   (DPM)                             :  9,08 MDH ;

             Valorisation   du  DPM                                                                                                   :  6,19   MDH ;

             Etudes  d’élaboration    des  plans d’aménagement     des ports   et des  plages         :  0,53 MDH.

 
Les principales   actions   prévues  en  2024,  se présentent    comme  suit  : 
 
          Etudes   et  travaux    de  délimitation     et  de  redélimitation     du  DPM  eet de  sa 
                                                                                                                                                          : 5,76  MDH  ; 
             protection 
          Soutien   aux missions                                                                                                         :  4,10   MDH ;
          Etudes   de suivi  du  trait  de  côte                                                                                      : 3,76  MDH ; 

          Etudes   hydro-sédimentaires     et  de protection    du  DPM  
                                                                                                                                                          : 1,25  MDH. 

 

2.4.3.   Fonds     national     du   développement         du   sport 

Les  recettes    et    les  dépenses    du   Fonds national       du   développement      du   sport   (FNDS)    ont 
enregistré   un  accroissement    annuel  moyen,   respectivement,    de  48,66%  eet de 60,31%  au titre   de 
la période   2021-2023.  

 
                                                                                                                                                               61

68
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                       EVOLUTION DES RECETTES* ET DES DEPENSESS DU FNDS AU TITRE DE LA PRIODE 2021‐20023 (EN MDH) 


                                                                                                                          6 392,233




                                                                                                                                        4 137,92
                                                                           3 4422,34
                            2 892,60


                                         1 610,22                                  1 611,93




                                     2021                                       2022                                       2023


                                                                   Recettes                 Dépenses
                                                                                                                                                                               
(*) Compte tenu du solde reporté. 
 
Les  crédits    alloués   au   FNDS   pour   l'année   2023,    ont   été   répartis    de   manière   à  couvrir    les 
opérations   suivantes  : 
 
   Financement    des fédérations    et   des  associations    sportives : 
      
Au titre   de l’année  2023,   un montant   de  515,,71 MDH a été réservé  au financement    des  fédérations 
et des  associations    sportives   au  titre  des  contrats-objectifs      qui  ont  été  ssignés entre   le Ministère 
de  l'Education     Nationale,     du   Préscolaire    et   des   Sports    (MENPS)   et   les   Fédérations     Royal 
Marocaine  du  Sport  (FRMS)  et  des  conventions    de partenariat    nécessaires   au fonctionnement     de 
ces fédérations. 
 
Il  importe    de   noter   que   les   subventions    accordées    par   le   MENPS  aux   FRMS  demeurent     la 
principale   source  de  financement   de  leurs  activités. 
 
   Organisation,    préparation    et  participation     aux  manifestations     sportivves  :  
      
Dans le  cadre  de  sa politique   proactive    en matière   d’organisation    de  grands   événements   sportifs 
internationaux,     le  Maroc   s'est   affirmé    comme   une   destination     privilégiée     pour   accueillir    des 
compétitions     de   grande    envergure,     grâce   à   des   infrastructures     de   qqualité,   un  savoir-faire 
éprouvé   et   une  organisation     efficace,   soutenus   par   l'appui   financier    ett  technique    du  MENPS. 
Ainsi,   le   budget     alloué   à   l'organisation      de   ces   événements     pour    l’’année   2023   s'élève    à           
371,21 MDH. 
 
   Renforcement    de  l’infrastructure     sportive    de  proximité    : 
Les  infrastructures     sportives    de  proximité    sont   cruciales    pour  le   développement     du   sport   au 
Maroc.   En    offrant     des   équipements      adaptés    à   proximité      des   zones    résidentielles,      elles 
encouragent   la  pratique   régulière  d'activités    physiques   pour  tous  les  citoyyens. 

Dans cette   optique,    le MENPS  a décidé   d'éllargir   le programme    de  consttruction    de  800   terrains 
de  proximité     pour   mieux    répondre    aux  besoins    en  infrastructures      sportives    dans   les  zones 
défavorisées.   L’élargissement     dudit   programmme  a  permis   d’atteindre    environ    1.855  terrains   au 
31/12/2023,   répartis    dans  différentes    communes    du   Royaume   par   le  biais   de  conventions     de 
partenariat    avec  les  collectivités     territoriales.    Cela  permet   de  renforcer    l'offre    d'infrastructures 
sportives   de proximité    et d'en  faciliter   l'accès   pour  les populations    localess. 
 


 
            62 

69
                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
  Mise à  niveau  de l’infrastructure    footballistique    nationale  pour  l’organisation   de  la  Coupe 
     d'Afrique  des  Nations 2025  et la coupe  du monde  2030  : 
 
 
Dans le cadre  de  la modernisation,  du  réaménagement  et  de  la mise  à  niveau des  principales 
infrastructures  sportives  du Royaume, le  MENPS a lancé en 2023 les travvaux y afférents  en vue 
de la candidature  du Maroc pour  la co-organisation  de  la Coupe du Monde  2030  avec l'Espagne 
et  le  Portugal  et  l’organisation   de  la  Coupe  d'Afrique   des  Nations  dee football  en  2025.  Un 
montant  de   2  MMDH a  été   alloué  à  ces  projets  pour   l'année  2023,  visant   à  améliorer  les 
infrastructures   afin  de   se  conformer   aux  normes   et  exigences   internationales   de  la  FIFA, 
garantissant ainsi le succès de ces deux grands événements  sportifs. 

2.4.4.   Fonds  de  service    universel    de  télécommunications   

L’évolution     des    recettes     et     des    dépenses     du    Fonds     de    sservice   universel     de 
télécommunications   (FSUT) durant la périodde 2021-2023, se présente comme suit :  

                      EVOLUTION DES RECETTES* ET DES DEPENSES DU FSUT AU TITRE DE LA PERIODE 2021‐22023 (EN MDH)



                            4 409                               4 405,44
                                                                                                               4 152,6











                                                                                 676,03
                                       424,85                                                                          384,38


                                  2021                                  2022                                   22023


                                                                  Recetttes    Dépenses

  
(*) Compte tenu du solde reporté. 
 
Les programmes réalisés dans le cadre de ce Fonds, se déclinent  comme ssuit : 
 

        Projets dde connexion à Internet de  certains  localités/sites  via  des liaisons  par satellites  : 
Ces projets visent  à doter  certaines  localités/entités  de  stations par  sateellite, aux fins de fournir 
des services de télécommunications,  notamment  les services voix et internnet. 
Le FSUT contribue à la mise  en œuvre de ces projets par  un  montant esttimé à 70 MDH étalé  sur 
la période 2018-2024. Un montant  d’environ  60 MDH a déjà été payé. 

        Projet du  Registre national  de la  population  : 
L’objectif  de ce  projet  est la  mise en place  d’un Registre  National de  la Population.  Le Fonds  a 
contribué au financement  de ce projet  par un montant  d’environ  300 MDH.  
 
                                                                                                                                                  63

70
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
        Feuille de route  pour  la transformation   digitale  :  
Dans le cadre  de la transformation   digitale,  une feuille  de  route  a été validée  par  le Comité  de 
Gestion   du   Service   Universel   des   Télécommunications    (CGSUT),   pour   un   montant    de           
400  MDH à partir  du FSUT, 60% de  ce montant  a déjà été  versé à l’Agence  de Développement 
du Digital (ADD). 

        Rénovation  des services des appels  d’urgence  :  
Des projets  visant  la  rénovation  des  services  des appels  vers  les numéros  d’urgence   ont  été 
examinés  par le CGSUT. Le FSUT contribue à ces projets par un montant  de 150 MDH, 67% de ce 
montant a déjà été  versé par ledit Fonds. 

        Développement  d’un  réseau sécurisé à haut débit  : 
Le CGSUT a retenu, comme  relevant du  service universel,  la mise en place  d’un réseau  sécurisé 
et a décidé de contribuer  à son financement,  à partir du  FSUT, à hauteur de 380 MDH. 

        Portail National  de  l’Administration   : 
Ce projet  vise  à  simplifier  et  digitaliser  les  démarches  administratives.  Il  nécessite la  mise  en 
place d’une organisation  et des outils  digitaux  à destination  des fonctionnaires  et des usagers de 
l’Administration.  Vu l’intérêt  de  ce projet, le  CGSUT a décidé de contribuer  au financement  de la 
mise en œuvre  de  ce projet   à hauteur  de  120 MDH dont  un  montant  de  43,6 MDH a  déjà été 
versé. 

        Programme  de  couverture  4G  au  titre  de  la  2ème année  du  Plan National   du  Haut et 
          Très Haut Débits  (PNHD 1) : 
A fin  mai 2024, plus  de 10.623 localités  ont été  déclarées couvertes  par  les services 2G/3G/4G. 
Au titre  des  dernières années et celui  en cours, la réalisation du  PNHD 1 s’accompagnerait par le 
paiement, à partir  du  FSUT, d’une partie du  montant  de la  subvention accordée  par  le CGSUT à 
ce programme. Le montant  de cette  subvention  s’établit actuellement  à 634 MDH. 
       
        PNHD 2 : Nouveau programme  de couverture   4G : 
       
Ce programme  permet  la couverture  des  localités non  couvertes  en 4G, qui  s’élèvent à environ 
2.000  localités.   Le  coût   global  de   ce  projet   est  d’environ   350  MDH,  étalé   sur  la  période           
2024-2026. 
 
        PNHD 3 : Développement  du Très Haut Débit  : 
           
L’objectif  de  ce  projet  est  de  permettre  un  déploiement   progressif  des  services du  très  haut 
débit sur  plusieurs villes  du Royaume. La  mise en place  de ce projet  serait  prévue  sur plusieurs 
années dès 2024, avec un budget prévisionnel  de 500  MDH.  
 
  
        PNHD 4 : Initiative  VSAT : 
 
Dans le cadre de la mise en œuvre  du (PNHD), le CGSUT a décidé de mettre  en œuvre  un projet 
baptisé  ‘’Initiative   VSAT‘’,  dont  l’objectif   est  de   permettre   aux  usagers  dans  les  zones non 
couvertes  par  internet   en  technologies  terrestres,   d’accéder  au  service  internet   par  satellite 
(VSAT) moyennant  une subvention  allouée  par le biais  du FSUT. Cette subvention  est accordée 
pour tout  abonnement  d’une période comprise  entre un et  deux ans et correspond  à 50% du prix 
total de  l’abonnement.  Il est plafonné  à 2.500  DH TTC par station.  Le nombre  de bénéficiaires  a 
été augmenté  par  le CGSUT de 1.000  à 4.000   bénéficiaires  par an,  avec un  budget  annuel de           
10 MDH.  

 
          64 

71
                                                                                      RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
 
         Connexion   des  sites  publics   à Internet    : 
  
Ce projet    vise  à  raccorder   les  représentations     des  services   publics   à  internet    en  fibre   optique 
avec  un  débit   minimum    de  20   MB/s   par  site.   Il  s’agit  de   plus  de  12.000   points/sites     pour   un 
budget   annuel  de 30  MDH.  
  
         Programme   GENIE  :  
 
Le programme    GENIE, lancé  en  2006,  a  pour  objectif   de  généraliser   l’usagge des Technologies    de 
l’Information    et de  la  Communication    (TIC)  dans  l’enseignement    public.  Il  est  financé  par  le FSUT 
pour   un  montant     global   de   1.128 MDH.  La   totalité    de   ce   montant    esst déjà   programmée     et 
déléguée  aux  Académies   Régionales   d'Éducation   et  de  Formation   (AREF)). 
 
         Campus  Connecté   : 
 
Ce projet   a  pour  objectif    de mettre    en place   les infrastructures     de  conneectivité  WiFi   et  Internet 
aux établissements    universitaires   ainsi  qu'aux   cités  universitaires.   Le budget    alloué  à ce projet   est 
estimé   à  314  MDH  sur   une  période    de  5   années.  Près   de  100%  des   ssites prévues   sont   déjà 
achevés  et connectés.  

2.4.5.     Fonds      d’accompagnement            des     réformes       du    transporrt       routier       urbain      et 
           interurbain 

L’évolution     des   recettes    et   des   dépenses    du   Fonds    d’accompagnement       des   réformes    du 
transport   routier   urbain   et  interurbain    (FART)   durant   la période   2021-2023,   se  présente   comme 
suit :  

                              EVOLUTION DES RECETTES* ET DES DEPENSEES DU FART AU TITRE DE LA PERIODE 2021‐2023 (EEN MDH)




                                                                          4 8883,82                                       4  932,32

                  3 996,74



                                                                                          2 152,86

                                                                                                                                                 1 338,74
                                   913,43



                            2021                                                2022                                               2023


                                                                       Recetttes        Dépenses 
(*) Compte tenu du solde reporté. 
 
   Composante    liée  au transport    urbain   par  autobus:	
             
Le  bilan  des  réalisations    des  programmes     financés   par  le  FART  au  titree  de  cette   composante 
durant  la période   2021-2023,   se présente   comme  suit : 
 
         Transport    urbain   par  autobus   : 
      
Les sociétés  concessionnaires    et  délégataires   ont  bénéficié   d’un  montant    total  de  298,70  MDH.  
 
                                                                                                                                                               65

72
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 
         Etudes,  enquêtes    et  audit   : 

Le projet   d’étude   de restructuration     du  réseau  du périmètre    de la  gestion  déléguée   du  service  de 
transport    urbain   de  Marrakech   a  été  réalisé   par  la  société   de   développement     local   « Bus  City 
Motajadida   »  pour   un   montant    d’environ    3  MDH,  au   titre   de   l’année   2021.  Aussi,   une   étude 
d’accompagnement     technique    et  juridique   du  service   de  transport    collectif   par  autobus   au  sein 
du  périmètre    de   la  gestion   déléguée    du  Marrakech    a  été  réalisée   par   ladite   société   pour   un 
montant   d’environ   0,30  MDH,  au titre   de l’année  2022. 

 
   Composante   liée   au transport    par  Tramway   :	
 
     Les  projets   du  transport     par  tramway    financés   par   le FART  : 
 
Les réalisations    des  programmes    d’investissement     durant   la  période    2021-2023   concernant    les 
projets   de  tramway    et  tout   autre  moyen   de  transport    collectif    urbain   sont   synthétisées   via  les 
indicateurs   suivants  : 
   

    AVANCEMENT DES INDICATEURS              2021                            2022                            2023 


 I- REALISATION  D’UN  SYSTEME  MODERNE  DE  TRANSPORT  EN  SITE  PROPRE  A  CASABLANCA 

 Projet de la ligne T2 extension T1 


 Taux d’engagement                                          100%                           100%                              100% 


 Avancement  physique                                     100%                            100%                             100% 


 Taux de règlement                                            96%                              97%                               98% 


 Projet des lignes T3 et T4		


 Taux d’engagement                                          97%                              94%                                97% 

 Avancement  physique                                      25%                              56%                               79% 

 Taux de règlement                                             15%                             37%                               57% 

 Projet des lignes du Bus à Haut Niveau de Service (BHNS) L5 et L6		

 Taux d’engagement                                          95%                              104%                             108% 

 Avancement  physique                                      43%                              81%                               98% 

 Taux de règlement                                             17%                             50%                               78% 

 Projet de mise à niveau du réseau de bus au sein du territoire de l’Etablissement de coopération intercommunale 
 (ECI)	

 Taux d’engagement                                          115%                            115%                             115% 

 Avancement physique                                       98%                              99%                               99% 

 Taux de règlement                                            76%                              87%                               88% 



 
            66 

73
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 

 II- EXTENSION DU RESEAU DE  TRAMWAY  POUR  L’AGGLOMERATION  DE  RABAT-SALE-TEMARA	

 Projet d’extension de 7 km de la ligne du Tramway L2 	

 Taux d’engagement                                          108%                            106%                             106% 

 Avancement  physique                                      94%                              99%                               99% 

 Taux de règlement                                            89%                              95%                               96% 

 Etudes de développement du réseau de Tramway de l’agglomération Rabat-Salé		


 Taux d’engagement                                          70%                             100%                              100% 

 Avancement physique                                       38%                             100%                              90% 

 Taux de règlement                                             13%                             66%                               83% 

 III- DEVELOPPEMENT  URBAIN  DE  LA  VILLE  D’AGADIR  (2020-2024)	


 Projet de réalisation de la ligne L1 du BHNS	

 Taux d’engagement                                          29%                              113%                             127% 

 Avancement  physique                                      12%                              38%                               64% 

 Taux de règlement                                             4%                               19%                               44% 

  
 IV - MARRAKECH –BCM  
  

 Les études relatives au projet de réalisation des lignes de BHNS 

 Taux d’engagement                                           0%                                0%                                 68% 

 Avancement  physique                                       0%                                0%                                 0% 

 Taux de règlement                                             0%                                0%                                 0% 

 
   Composante   liée   à la mise  à niveau   du  parc  des  taxis  : 
 
Le programme     d’appui   au  renouvellement     des  taxis,  financé   dans  le  cadre   du  FART,  a  permis, 
depuis    son   lancement,     de   renouveler     plus    de   61.650   taxis    de    1ère  et    2ème   catégories 
correspondant    à 80%  du  parc  des  taxis  en  exploitation,    se  traduisant   par  une  nette   amélioration 
du parc  des  taxis  au niveau  de  l’ensemble   des préfectures    et  provinces. 
 
Suite   à  l’expiration,     à  fin   2021,   du   délai   de   dépôt    des  demandes     d’octroi    de   la  prime    de 
renouvellement     des  taxis   de   1ère  et  2ème   catégories,    deux   arrêtés   conjoints    du   Ministre   de 
l’Intérieur   et  du Ministre   Délégué   auprès  de  la Ministre   de  l’Economie   et  des  Finances,  chargé   du 
Budget,  ont  été  signés  en  2022  en vue  de  proroger   la  durée  de  ce programme    pour  deux  années 
supplémentaires    jusqu’à  fin  2023. 
          
Les réalisations   de  ce programme    jusqu’au  31/12/2023,   se présentent   comme   suit  : 
 
 
                                                                                                                                                               67

74
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 

                                                   Taxi 1ère catégorie                       Taxi 2ème catégorie  
                                                       (Grand Taxi)                                   (Petit Taxi) 
                                                                                                                                                 Crédits délégués 
                                                                                                                                                     /  besoin de 
           Années 
                                                                                              nombre de                                     financement 
                                   nombre de taxis       % du parc                                     % du parc 
                                                                                                  taxis                                               (MDH) 
                                       renouvelés           renouvelé                                      renouvelé 
                                                                                              renouvelés 
                                         (cumul)                (cumul)                                          (cumul)  
                                                                                                (cumul)  

                                                                                                                                                          4.185
                                                                                                                                                               
       Réalisations                                                                                                                       (avec utilisation 
          jusqu’au                  33.000                   74%                  25.000                  77%             des crédits non 
        31/12/2022                                                                                                                         consommés au 
                                                                                                                                                  titre des années 
                                                                                                                                                    précédentes) 

                                                                                                                                                               
                                                                                                                                                   Utilisation des 
       Réalisations 
                                                                                                                                                     crédits non 
          jusqu’au                  33.900                   76%                  27.650                  85% 
                                                                                                                                                   consommés au 
        31/12/2023 
                                                                                                                                                  titre des années 
                                                                                                                                                    précédentes 


2.4.6.    Fonds     d’assainissement          liquide      et   solide     et   d’épuration        des    eaux    usées    et 
           leur   réutilisation 

En 2023,  les  recettes   réalisées  par  le  Fonds  d’assainissement    liquide   et solide   et  d’épuration    des 
eaux   usées   et   leur    réutilisation     (FALSEEUR),    compte     tenu    du   solde    reporté,    ont    atteint             
2.041,07  MDH  contre   1.594,60  MDH  en 2022   et  1.241,17 MDH en 2021. Quant   aux  dépenses,   elles 
ont  atteint   un montant    de  203,80  MDH  en  2023  contre   1.053,53 MDH  en 2022   et 646,57   MDH  en 
2021. 

Ainsi,   les    dotations     budgétaires     affectées     à   ce    Fonds    sont    mobilisées    pour     contribuer, 
principalement,    au financement    du  Programme   National   d’Assainissement    liquide   Mutualisé  et  de 
réutilisation    des   eaux   usées   traitées    (PNAM).   Les   principaux    objectifs     de  ce   programme,     à 
l’horizon  2040,   sont  : 
 
     L’augmentation     en  milieu   urbain   du   taux   de  raccordement     à  plus  de   90%  et   du  taux   de 
        dépollution    à 80%  au niveau  des  centres  concernés   par  le PNAM  ; 
     L’équipement    en  milieu  rural  de  1.207 centres   chefs-lieux   des  communes,   pour  augmenter    le 
        taux  de raccordement     à 80%  et le  taux  de dépollution    à 60%  ; 
     La   réutilisation     des   eaux    usées   traitées,    avec   comme     objectif    d’atteindre      un   volume 
        potentiel   annuel  de  573 millions   de  m3 des eaux  usées  traitées. 
         
Aussi,   ce   Fonds    permet    d’appuyer     les   projets     d’assainissement     solide    dans   le   cadre    du 
Programme     National     de    Valorisation     des    Déchets    Ménagers     et    assimilés    (PNVDM).     Ce 
programme   étalé  sur  la période   2023-2026    envisage  d’assurer   la continuité    des projets   convenus 
dans  le  cadre  du   Programme   National    des  Déchets   Ménagers   (PNDM),   de  mettre   en  œuvre   le 
protocole    d’accord    relatif   à  la  valorisation     des  Déchets   Ménagers    et  assimilés   signé   avec  les 
cimentiers   et de  traiter   la problématique     du lixiviat. 
 
Les  dotations    budgétaires    allouées   au  FALSEEUR,   par   département    ministériel,    au   titre   de  la 
période  2021-2023,   se présentent   comme   suit  :  

                                                                                                                                                                                                                                                   


 
            68 

75
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
                                                                                                                                                               (En MDH) 

                                                Dotations                                                        2021              2022            2023  

 Part du Ministère de l'Intérieur                                                                       714                800             1.000 

 Part du Département de l’Eau                                                                        130               200               500 

                                                    Total                                                            844              1.000            1.500 

 
       Réalisations    au titre   des  années   2023  et  2024   : 
La  situation    de   l’assainissement     liquide    en  milieu    urbain,   à  fin   2023,    s’est   caractérisée    par 
l’amélioration    des indicateurs   suivants   : 

        Le  raccordement    au réseau  d’assainissement    liquide   a atteint   un taux  de  83,5% contre 
           82,5% en  2021 et  70% en  2006   ; 
       
        Le  niveau  d’épuration    des eaux  usées  autour  de  57,5% contre   56,2  % en 2021 et  7% en 
           2006   ; 
       
        Le  nombre   des stations   d’épuration    (STEP), en  état  de  fonctionnement,    a  atteint   168, 
           contre   165 en 2021 et  27 en  2006. 
                                                                     
Au  titre   de   l’année   2024,   les  dotations    prévisionnelles     du  budget    général   aux   recettes   dudit 
Fonds    s’élève    à     1.700    MDH.    Ces    crédits     sont    destinés     au    financement      des    projets 
d’assainissement   liquide   et  solide  et  de réutilisations    des  eaux  usées traitées,   en  partenariat   avec 
l’ONEE,  les   régies,   les   autorités    délégantes    et   les   collectivités     territoriales.     Ils  sont   répartis 
comme  suit  : 
                                                                                                                                                                              
                                                                                                                                                                 (En MDH) 

                                                     Bénéficiaires                                                                 Prévisions 2024             

       Programme national d’assainissement liquide mutualisé et de réutilisation des eaux usées traitées 

Versement aux régies de distribution d'eau et d'électricité                                                       348 

Versement aux Collectivités Territoriales                                                                                  331 

Versement à l’ONEE                                                                                                                 144 

Crédits non programmés                                                                                                          477  

                                           Contribution aux projets d’assainissement solide 

Versement aux Collectivités Territoriales                                                                                400 

Etudes, assistance technique et conseils                                                                                  -            

                                                           Total                                                                              1.700 

                                                                                                                                                                                                                                                                 

2.4.7.    Fonds    national      pour    la   protection       de   l’environnement          et   du   développement 
           durable 

Durant  la  période   2021-2023,   les  recettes   et  les  dépenses   du  Fonds  national   pour   la  protection 
de  l’environnement     et  du   développement     durable   (FNPEDD)    ont  enregistré    un  accroissement 
annuel  moyen,  respectivement,    de  15,72% et de  3,87%. 
 
                                                                                                                                                               69

76
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                       EVOLUTION DES REECETTES* ET DES DEPENSES DU FNPEDD AU TITRE DE LA PERIODE 2021‐22023 (EN MDH)




                                                                                                                                              2 015,72
                                                                                 1 7991,93

                     1 505,38







                                       212,08                                                                                                               228,82
                                                                                                     52,34

                               2021                                                     2022                                                     2023

                                                                             Recettes        Dépenses

(*) Compte tenu du solde reporté. 

                                                                                                
Le  FNPEDD    contribue      au   financement      des   projets     qui   s’inscrivent      dans   le   cadre   de   la  mise    en 
œuvre    du   Programme      National     des   Déchets     Ménagers    et   ceux    de  la   Lutte    Contre     la  Pollution 
Industrielle. 
 
          Programme     National     des   Déchets    Ménagers     (PNDM)    :  
 
La mise   en  œuvre    du  PNDM   a permis    à fin   2022   :        
      
                 L’augmentation         du   taux   de   collecte     professionnalisée         à 96%   contre     44%   en  2008     ; 
                 L’augmentation           du    taux      de    mise     en    CEV     pour     atteindre        66,6%      des    déchets 
                    ménagers     produits,      contre     10%  avant    2008    ; 
                 La  mise    en  place    de  29  décharges      contrôlées       et  CEV   ;  
                 L’achèvement        de   la  réhabilitation         de   67  décharges      non    contrôlées       dont    44   ont    été 
                    fermées     et  23  décharges      aménagées. 
              
Le  bilan    des    réalisations      financières      du   PNDM    au   titre    de   la   période     22021-2023,   se   présente 
comme    suit  :                        
                                                                                                                                                                                                          (En MDH)   


                                                       Projets                                                               2021                2022               2023  



 Mise en place des Centres d'Enfouissement et de  Valorisation (CEV) des 
                                                                                                                                 112,12             24,30              42,69 
 déchets 



 Réhabilitation  et fermeture  des décharges sauvages                                          58,50                    -                      -



                                                        Total                                                                170,62              24,30              42,69 





 
             70 

77
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
                                                                                                                                                                        
      Projets  de Valorisation   des Déchets : 
 
Ces projets de  Valorisation  des Déchets représentent  une  continuité  logique  des réalisations du 
PNDM qui s’est fixé  comme objectif  de  tri-recyclage  des déchets,  un taux  de l’ordre  de 20%. En 
outre, le  développement  des filières  de valorisation   des déchets  constitue  le premier  pas d’une 
stratégie  de  sortie  à  moyen  et  long  terme   de  l’option  de  mise  en  décharge  et  un  pas  vers 
l’application  des concepts de l’économie  circulaire.  
 
Ainsi, le  bilan  des réalisations  financières  de  ces projets,  au  titre  de  la  période  2021-2023, se 
présente comme suit  : 
                                                                                                                                                     (En MDH) 

                                            Projets                                                    2021            2022           2023 



 Etudes relatives au projet de tri à la source et à la construction de 
                                                                                                           0,47                -                0,12 
 l’écocentre de Marrakech 



 Mise en place du centre de tri d’Oum Azza à Rabat                           -                   -                150 



 Mise à niveau du centre de tri des déchets de Sidi Bernoussi            -                   -               2,50 

 
La mise en œuvre de ces projets a permis  à fin 2023 :  
       Le  suivi  de la  réalisation  des projets  de  mise en  place  des centres  de  tri  subventionnés 
          durant  les quatre dernières années ; 
       La  réalisation des  principales  activités  du plan  d’action  relatif  à la filière  de gestion  et  de 
          valorisation  des véhicules en fin de vie  (VFV) ; 
      La  mise en œuvre de la convention  signée  avec le secteur privé  relative à l’organisation  de 
         la filière  de valorisation des déchets  d’équipements  électriques et  électroniques (DEEE) ; 
      La  réalisation de  l’étude relative  à l’application   de la Responsabilité  Elargie du  Producteur 
         (REP) aux bouteilles  en Polyéthylène Téréphtalate  (PET). 
      Programme  de Prévention  et  de Lutte  Contre la  Pollution  Industrielle  : 
  
     -    Mécanisme  volontaire   de dépollution   industrielle   hydrique   (MVDIH)  :  
                          
      
Le mécanisme volontaire  de dépollution   industrielle hydrique  mis  en place en 2011 dans le cadre 
du FNEDD, doté  d’une  enveloppe  budgétaire  de  105 MDH pour  le  financement  des projets   de 
traitement  des  rejets  industriels  liquides,  a permis  à  ce jour  d’appuyer   29 projets   de mise  en 
place de stations de traitement   des rejets liquides industriels. 
 
     -    Mise à niveau  environnementale   du  secteur  de la  poterie  : 
 
      
Dans  ce   cadre,  une   enveloppe   budgétaire    de   7,32  MDH  a   été   allouée   aux  projets    de 
remplacement  de  fours  traditionnels   polluants   par  des  fours  à  gaz  modernes,  au  profit   des 
potiers de Zagora, Salé et Marrakech. 
 
 
                                                                                                                                                  71

78
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
     -    Mise à niveau  environnementale   de  l’activité   oléicole  : 
 
      
Dans ce  cadre,  une convention   de  partenariat   a été  signée  en  2020  afin  d’appuyer  tous   les 
projets  relatifs  à  la  collecte,  le  traitement   et/ou  la  valorisation   des déchets   issus du  secteur 
oléicole et de  définir les contributions   de tous  les départements  concernés au titre  de la période  
2020-2024. 
 
Le bilan des réalisations  du programme  de prévention   et de lutte  contre  la pollution  industrielle, 
au titre de la période  2021-2023, se présente comme suit  : 
                                                                                                                                                                                                 (En MDH) 

                                              Projets                                                    2021           2022           2023 


Traitement des rejets industriels liquides (Ouled Taima, Ain Chegag, 
                                                                                                               30               12               20 
Bouknadel et Jouhara) 


Mise à niveau environnementale de l’activité oléicole (Ouazzane et Beni 
                                                                                                              3,15              -                 12 
Mellal) et le plan d’urgence de dépollution du Sebou 



Mise à niveau environnementale du secteur de la poterie (Oulja, Tamgrout 
                                                                                                              1,32           11,60             - 
et Agafay) 


2.4.8.   Fonds  de  lutte    contre   les  effets    des  catastrophes     naturelles                                    

Les recettes   mobilisées  par  le  Fonds  de   lutte  contre   les  effets  des  catastrophes   naturelles 
(FLCN) en 2023,  compte  tenu du  solde reporté,  s’élèvent  à 3.552,79 MDH contre  2.659,32 MDH 
en 2022 et 1.583,27 MDH en 2021. Quant aux dépenses réalisées, elles ont atteint 1.541,36 MDH en 
2023 contre 1.551,93 MDH en 2022 et 614,56 MDH en 2021. 
 
  Les projets   cofinancés  par  le FLCN  dans le  cadre du  programme   de Gestion  Intégrée  des 
     Risques Catastrophiques  Naturelles  et de  la Résilience (PGIR) :  
 
Jusqu’à fin 2023,  le FLCN a  cofinancé 324  projets,  d’un montant  global  de  4,69 MMDH, dont  la 
part du FLCN s’élève à 1,65 MMDH. Ces projets sont répartis comme suit : 

        247  projets  concernant   la  prévention   contre  les  inondations,   d’un  montant   global  de            

          3,8 MMDH, dont la contribution   du FLCN est de 1,27 MMDH ; 

        48 projets  concernant  la prévention  contre  des risques  multiples, d’un  montant  global  de 

          334,19 MDH, dont la contribution  du  FLCN est de 193,86 MDH ; 

        13 projets  concernant  la  prévention   contre  le  Tsunami,  d’un  montant  global   de  196,29 

          MDH, dont  la contribution  du FLCN est de 75,22 MDH ; 

        10 projets   concernant  la  prévention   contre   les  glissements  de  terrains,  d’un   montant 

          global  de 316,80 MDH, dont la contribution  du  FLCN est de 81,40 MDH ; 

        6 projets  concernant  la prévention  contre  les tremblements  de terre,  d’un montant  global 

          de 45,27 MDH, dont  la contribution  du FLCN est de 27,70 MDH. 

 
           72 

79
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
  Les projets  d’urgences  pour  la sécurisation  de l’approvisionnement   en  eau potable  : 
 
En plus des projets  cofinancés  dans le cadre  PGIR et suite à la  situation  de sécheresse actuelle, 
un montant  global  de  2.255 MDH a été  programmé   dans le cadre  du  FLCN au titre   de l’année 
2024 pour  le financement  des projets d’urgences  pour  la sécurisation de l’approvisionnement   en 
eau potable, notamment,  les conventions et  programmes suivants  : 

        Conventions de  partenariat  pour  le financement  et   la réalisation  des actions  urgentes  et 

          structurantes  au niveau des bassins de Moulouya, Tensift  et Oum Errabia ; 

        Convention de partenariat  pour  la réalisation des actions  urgentes et  structurantes  dans le 

          secteur  de l’eau au niveau de la Région Drâa-Tafilalet  ; 

        Convention  relative  à  la  réalisation  du  renouvellement   de  la  conduite   d’amenée d’eau 

          potable  alimentant  la zone d’Oujda-Taourirt  ; 

        Programme de réalisation  des petits barrages  et lacs collinaires ; 

        Programme de réalisation  des stations monoblocs  ; 

        Conventions relative  à la réalisation du plan d’urgence  de dépollution  industrielle  ; 

        Convention relative  à la mise à niveau et à l’extension du  programme « Al  Ghait ». 


  Projets  prévisionnels  pour  l’année 2024  dans la cadre  du PGIR : 
 
En plus des projets en cours  de réalisation, de nouveaux  projets feront  l’objet  de la procédure  de 
sélection  au titre  de  l’appel  à  projet  en  2024.  Dans ce  cadre, 157 dossiers  de projets   ont  été 
présentés  par  les  départements   ministériels,  les  collectivités    territoriales,  les  établissements 
publics et les associations  et qui sont  en cours d’étude  par la Commission Nationale  de Sélection 
(CNS). 

Les prévisions de financement  des projets au titre  de l’année 2024, se présente comme  suit : 

                                                                                                                                                   (En MDH) 
                                                                                                                            Réalisations au premier 
                                   Rubriques                                             Prévisions 2024 
                                                                                                                                  trimestre 2024 

  
 Programme  de     Gestion   Intégrée   des    Risques 
 Catastrophiques Naturelles et de la Résilience                       588,20                           104,21 



 Dépenses du Ministère de l’Intérieur au titre des actions de 
                                                                                                  30,00                             30,00 
 secours et d’assistance aux populations sinistrées 


 Crédits non programmés                                                          153,50                              - 


2.4.9.   Fonds  de  développement       énergétique  

Les recettes  du  Fonds  de développement   énergétique  (FDE),  constituées  essentiellement  des 
soldes reportés  des années précédentes,  s’élèvent  à 826,26 MDH  en 2023  contre  1.170,99 MDH 


 
                                                                                                                                                  73

80
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
en 2022  et  1.216,33 MDH en  2021. Quant  aux  dépenses,  elles  ont  atteint   443  MDH  en  2023  contre 
350,50  MDH  en 2022  et  51,11 MDH en 2021. 
 
Les dépenses  effectuées    dans le  cadre  dudit   Fonds,  depuis  sa création   en  2009   jusqu’au  mois  de 
septembre     2024,   ont    atteint     un   montant     total    d’environ     5.242,71   MDH.   Pour    la   période             
2017-2024,  les  versements   effectués   dans le  cadre  du  FDE se présentent    comme  suit  :  
                                                                                                                                                                                                 
                                                                                                                                                                            
                                                                                                                                                                (En MDH) 

                 Bénéficiaires                     2017        2018      2019      2020      2021      2022       2023        2024 

 L’Office National de l’Électricité 
                                                          132,50         -             -            -             -             -         400,00          - 
 et de l’Eau potable (ONEE) 
 L’Institut de Recherche en 
 Energie Solaire et Energies             25,00       63,00      51,00    49,89      51,11    38 ,00     33,00       44,00 
 Nouvelles (IRESEN) 
 L’Agence Marocaine pour 
                                                              -               -        312,50       -             -         312,50        -               - 
 l’Energie Durable (MASEN) 

 La Société d'Ingénierie 
                                                              -               -            -             -             -             -          10,00           - 
 Énergétique (SIE)  

 La Société Financière 
                                                              -               -            -             -             -             -              -            3,19 
 Internationale (IFC) 
 
 
Au titre   des neuf  premiers   mois  de  l’année  2024,  les réalisations   du  Fonds  ont  porté   sur : 
 
 
     -     Le  versement   au  profit   de  la Société   Financière   Internationale    d’un  montant    de  3,19 MDH, 
           au   titre   de   son  assistance    pour   la  mise   en   œuvre   d’une   solution    technologique      pour 
           l’import    par  voie   maritime   et   regazéification    du   Gaz  Naturel   Liquéfié   (GNL)   ainsi  que  sa 
           distribution. 
 
     -     Le  versement   à l’IRESEN   d’un  montant    global   de 44  MDH  dans  le  cadre  de  la convention 
           signée  entre   l’Etat  et  l’IRESEN, au  titre  de  la période   2017-2026,  telle   qu’elle  a été  modifiée 
           et   complétée     par   l’avenant   n°2.   L’objectif     est  d’appuyer     l’action    de  l’IRESEN   pour   le 
           développement     de la  recherche   dans le  domaine   des énergies   renouvelables. 

                                                                     
 

 

 

 

 

 

 

 

 

 

 


 
            74 

81
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
SECTION               V    –   DEVELOPPEMENT                            RURAL,             AGRIICOLE                 ET      DE 
LA      PECHE 
 
Sept    comptes      d’affectation        spéciale     intervenant        dans    le   domaine      du   développement         rural, 

 agricole   et  de  la  pêche,   ont   réalisé   globalement       5,54  % du   total   des  dépenses     des  CAS  en  2023. 
L’évolution     des   recettes    et  des  dépenses     desdits    CAS  se  présente    commee  suit   : 
                                                                                               
                            RECETTES*ET DEPENSES REALISEES AU NIVEAU DES CAS INTERVENANT DANS LE DOMAINE DU DEVVELOPPEMENT RURAL, 
                                                           AGRICOLE ET DE LA PECCHE AU TITRE DE L'EXCERCICE 2023 (EN MDH)






                                                                                                                                                                             6 986
           Fonds pour le développement rural et des zones de
                                    montagne
                                                                                                           2 192




                                                                                                                                                                     6 450
                                Fonds de développement agricole
                                                                                                                                           4 5444




                                                                                                                    2 827
                                            Fonds national forestier
                                                                                    5000




                                                                                            1 083
             Fonds spécial des prélèvements sur le pari mutuel
                                                                                194




                                                                                        748
                                        Fonds de la réforme agraire
                                                                             0




                                                                                  3600
                 Fonds de la chasse et de la pêche continentale
                                                                              30




                                                                                 265
                Fonds de développement de la pêche maritime
                                                                              80





                                                                          Recettes            Dépenses
                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 
 
                                                                                                                                                                               75

82
                                                                                             
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
 
                           EVOLUTION DES RECETTES* ET DES DEPENSES DES CAAS INTERVENANT DANS LE DOMAINE DU DEVELOOPPEMENT RURAL, 
                                                         AGRICOLE ET DE LA PECHE AU TITRE DE LA PERIODE 2021‐2023 (EN MDH)




                                                                                                                                                           18 7718

                               15 925                                                   166 310





                                                       8 310                                                7 882                                                     7 540







                                      2021                                                          2022                                                          2023


                                                                                       Recetttes Dépenses
                                                                                                                                                                                                                     
(*) Compte tenu du solde reporté. 

2.5.1.     Fonds        de   développement                 agricole  

Les    recettes       et    les    dépenses       du    Fonds      de    développement            agricole       (FDA)       ont     enregistré        un 
accroissement         annuel     moyen,      respectivement,           de   13,15%  et   0,63%    durant      lla période      2021-2023.  
 
L’évolution         des     recettes        et    des     dépenses        effectuées         par     le FDA        durrant      ladite      période,        se 
présente      comme      suit   : 
 
                               EVOLUTION DES RECETTES* ET DES DEPENSEES DU FDA AU TITRE DE LA PERIODE 2021‐20023 (EN MDH)




                                                                                                                                                       6 449,,69
                                                                                           5 808,32

                              5 038,02
                                                4 487,38                                              4 684,91                                               4 544,05












                                          2021                                                    2022                                                     2023


                                                                                          Recettes          Dépenses 
(*) Compte tenu du solde reporté. 
 
La   ventilation         des    dépenses        du    FDA,    par     rubrique,        durant      la   période       22021-2023,      se    présente 
comme     suit    :       
 

 
              76 

83
                                                                                      RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
                                                                                                                                                               (En MDH) 

                                       Rubriques                                                    2021               2022                 2023 


  Aides et  incitations                                                                           4.000              3.800               3.500 
       - Aménagements hydro-agricoles                                                 2.473               2.127              2.100 
       - Matériel agricole                                                                           377                 358                  332 
       - Promotion des exportations agricoles                                          341                 336                   171 
       - Production animale                                                                       215                453                   301 
       - Plantations fruitières                                                                     135                  78                   124 
       - Unités de valorisation                                                                    82                  116                   90 
       - Autres                                                                                           377                 332                  382 

  Assurance agricole                                                                             369                  381                  519 

  Mise à niveau  des filières                                                                   46                   166                  179 

  Programme  d’achat  de  plants  de Palmier  Dattier                           40                   25                    44 

  Autres                                                                                                   32                  312                  302 

                                           Total                                                         4.487                4.684               4.544 

 
L’analyse   des  réalisations    au  titre    des  aides   et  incitations    accordées,    au  cours   de   la  période  
2021-2023,  met  en exergue   les éléments   suivants   : 
 
      -     Les  subventions    destinées   aux  aménagements    hydro-agricoles     ont   connu   une  baisse  de 
            14% et  1%, respectivement,   au titre   des années  2022  et  2023  ; 
      -     Les  subventions    destinées   à l’équipement    des  exploitations     ont  connu   une  baisse  de  5% 
            et  7%, respectivement,    au  titre  des  années  2022  et 2023  ; 
      -     Les  subventions   accordées   au titre   de  l’intensification    de  la production    animale   ont  connu  
            une  forte  hausse  de  111% en 2022 contre  une baisse  de  34% en  2023  ; 
      -     Les  subventions    accordées    aux  plantations     fruitières    ont  connu   une   baisse  de   42%  en 
            2022  contre   une  hausse de  59% en  2023  ; 
      -     Les  subventions    accordées    aux  unités   de  valorisation    ont  connu   une  hausse   de  41% en 
            2022  contre   une  baisse  de 22% en  2023  ; 
      -     Les  subventions    accordées   aux   exportations    agricoles   ont   connu   une  légère   diminution 
            de  1% en 2022, suivi  d’une  baisse  de  49% en  2023. 
 
Les principales   réalisations   physiques   du  FDA,  au titre  de  l’année  2023,  ont  porté    sur : 
 
      -     L’équipement    de  près   de  43.449   ha en  systèmes   d’irrigation    localisée   et  l’aménagement 
            du  foncier   sur 5.229  ha ;  
      -     L’acquisition    de 5.640   unités  de  matériel  agricole   dont   près  de 1.226 tracteurs   ; 
      -     La  plantation    de   5.588  ha  d’oliviers,    2.485   ha  de  rosacées   et  autres   espèces   fruitières,     
            251 ha d’agrumes   et  505  ha de  canne  à sucre; 
      -     La   production     de   249.975    reproducteurs     ovins    et   bovins   de   races   pures,    de   6.388 
            reproducteurs     caprins  ; 
      -     La construction     de 517 unités  de  bâtiments   d’élevage   ; 
      -     La construction     et l’équipement    de  21 unités  de valorisation    des produits    agricoles  ;  
      -     La   promotion      des    exportations      agricoles     de   plus    de    250.218   Tonnes    d’agrumes,             
            3.132 Tonnes   des  fruits   et  légumes   par  voie   aérienne   et  plus  de  6.402   Tonnes  de  l’huile 
 
                                                                                                                                                               77

84
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
           d’olive,  18.648 Tonnes de  produits  valorisés  et  1.473 Tonnes des produits   avicoles frais.
                                              

2.5.2.  Fonds   de  la  réforme    agraire 

En 2023, les recettes  du Fonds  de la réforme  agraire  (FRA), compte  tenu  du solde  reporté,  ont 
atteint  748,40  MDH, contre  746,03  MDH en 2022  et  746,17 MDH en 2021, enregistrant  ainsi un 
accroissement annuel moyen de  0,15%. 
 
Quant aux  dépenses,  elles ont  atteint   0,45  MDH en  2021, contre  0,06   MDH en  2022  et  sans 
aucune dépense en 2023, enregistrant  une baisse annuelle moyenne de 100%.  
Les dépenses dudit compte  sont mobilisées pour  le règlement  : 

        Des indemnisations dans le cadre  des procédures d'expropriation   prévues  par le code des 
          investissements  agricoles ; 
        Des créances  hypothécaires  grevant   les immeubles   domaniaux  notamment   les terrains 
          agricoles  ayant appartenu  à des étrangers  et transférés à l'Etat  en application  du  dahir du 
          2 mars 1973 ; 
        Des remboursements mis à la charge de l'Etat  dans le cadre de la réforme  agraire ; 
        Des décisions judiciaires et administratives. 

2.5.3.  Fonds   national    forestier 

Les recettes   réalisées par  le  Fonds  national  forestier   (FNF)  en  2023,  compte  tenu  du  solde 
reporté,  s’élèvent  à  2.826,94  MDH contre   2.507,04  MDH  en  2022  et  2.408,27  MDH en  2021 
enregistrant  ainsi un  accroissement  annuel moyen  de 8,34%. Les dépenses  effectuées  en 2023 
ont  atteint  500,10  MDH contre  671,78 MDH en  2022  et  913,84 MDH en  2021, avec une  baisse 
annuelle moyenne de 26,02%. 
 
L’état  d’exécution  des principales  composantes  des  programmes  financés dans  le cadre  de  ce 
Fonds pour l’année 2023, se présente comme  suit :  
 
  Protection    et sécurisation   du  domaine  forestier    : 

La  sécurisation  du   patrimoine   forestier   national  a  atteint   88%,  représentant   une  superficie 
délimitée  et  homologuée   d’environ   8  millions  d'hectares,   dont  6,75  millions  d'hectares   sont 
immatriculés.  Les superficies  en cours  de délimitation   définitive  sont  de  0,6  million  d'hectares, 
tandis que 0,4 million  d'hectares  sont en phase de délimitation  provisoire. 
 
  Infrastructures    et  Mesures d’accompagnement     au profit   des  usagers : 
Durant l’année 2023,  220 projets  à caractère  social ont été  réalisés dans le domaine  forestier  au 
profit  des  populations   riveraines  dans  un  cadre  conventionnel   avec  les  communes.  Il  s’agit, 
notamment,  de   l'ouverture   et  l'entretien   de  432   km  de  pistes,  l'approvisionnement    en  eau 
potable et  en électricité  des douars, ainsi que la construction  de terrains de sport  de proximité. 
  Aménagement   et  développement    forestier   : 
 
    -     Reconstitution   des écosystèmes  forestiers  : 
 
Pour la campagne  2023-2024, le  programme  de reboisement  réalisé porte  sur une superficie  de 
9.412 ha, en plus des actions  de regarnissage  et d'entretien   des plantations  anciennes sur  1.487 
ha, ainsi que des travaux  de régénération  naturelle  protégés  par clôture  sur 220  ha. Par ailleurs, 
les travaux de  sylviculture  et de gestion  des peuplements  (dépressage, élagage  et éclaircie)  ont 
porté sur une superficie  de 12.417 ha, dont 7.000 ha ont déjà été achevés. 
 


 
           78 

85
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 
    -     Compensation  des mises en défens  : 
En 2023, le programme  de  compensation  pour la mise  en défens a impliqué  189 associations de 
gestion  sylvopastorale,   regroupant   18.000   adhérents,  chargées  de  surveiller   84.000   ha   de 
périmètres de reboisement  mis en défens.  
    -     Animation  territoriale   : 
Depuis 2020,  76 Agents  de  Développement  de Partenariat  (ADP)  ont  été  recrutés et  déployés 
au niveau de plus de 90 communes  territoriales  et 20 Organismes  de Développements  Forestiers 
(ODF) ont été  constitués et  44 autres sont  en cours de constitution.  Ces ADP et ODF constituent 
une interface entre  l’administration  forestière  et  la population  locale dont  le rôle  principal  est de 
faire rapprocher   la population   des projets  forestiers  et  son  implication  directe  dans  la gestion 
participative  dans  un cadre  d’intérêts  communs.  Aussi, 37  Plans de  Développement  Forestiers 
Communaux Participatifs  (PDFCP) ont  été  élaborés dont  24 sont  validés au niveau  des conseils 
communaux concernés. 
 
  Lutte  contre  l’ensablement  : 
      
En 2023, plusieurs actions  de lutte  contre  l’ensablement  ont  été menées, notamment   la fixation 
mécanique et  biologique  de 470  hectares  de dunes  en mouvement  et  la protection   de la route 
nationale n°1 traversant  la région  de  Laâyoune-Sakia-El Hamra, dans  le cadre  d'une convention 
de partenariat  avec le Ministère de l'Équipement  et  de l’Eau. Le coût total  de ce projet  est évalué 
à 48,05   MDH, dont   34,10 MDH  ont  été  financés  par  l'Agence  Nationale   des  Eaux et  Forêts 
(ANEF) et le reste par  le Ministère de l'Équipement  et de l’Eau. 
  
  Prévention  contre  les incendies  et surveillance  sanitaire  : 
 
    -     Gestion  des risques climatiques  : 
 
Durant l’année 2023,  466 incendies  de forêts  ont été  enregistrées à l’échelle  nationale, touchant 
une superficie de 6.421 ha constituée  de 4.158 ha de formations arborées  (65 %) et environ  2.263 
ha  d’essences  secondaires   et   de  formations    herbacées   (35  %).  Malgré   les   températures 
caniculaires et  la  sècheresse  enregistrée  en  2023, la  superficie  brûlée   reste  beaucoup  moins 
élevée que celle de l'année 2022, enregistrant  une baisse de plus de 70 %.  
 
Pour  assurer  la  surveillance  et   l’alerte  précoce   des  feux   de  forêts,   l’ANEF  a  recruté   1.291 
guetteurs au cours de  cette campagne. 
 
  Santé des forêts   : 
 
La lutte contre  les défoliateurs  forestiers a été  menée en 2023 sur une superficie  totale  d'environ 
22.538 ha, ciblant principalement  la processionnaire  du pin, le bombyx  disparate, les catocales  et 
la tordeuse du cèdre. 
 
L’année 2023  a  également   été  marquée  par  l'extension  du   réseau systématique   8x8  km  de 
surveillance et  de suivi de  la santé des  forêts, au niveau  de la région  de  Marrakech-Safi, avec la 
matérialisation    de   53   placettes    définitives.   Aussi,   une   opération    d'inter-calibration     des 
animateurs régionaux  de  la  santé des  forêts  a été  réalisée pour  la  notation  des  530  placettes 
permanentes. 

2.5.4.  Fonds   de  la  chasse   et  de  la pêche   continentale   

L’évolution  des  recettes  et  des dépenses  du  Fonds  de la  chasse et  de  la  pêche continentale 
(FCPC) durant la période  2021-2023, se présente comme suit : 
 

 
                                                                                                                                                  79

86
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                      EVOLUTION DES RECETTES* ET DES DEPENSES DU FCPC AU TITRE DE LA PERIODE 2021‐20223 (EN MDH)




                                                                                                                                3559,84
                                                                         335,,18
                   312,24










                                   23,92                                              21,19                                             30,00


                            2021                                              2022                                               2023

                                                                   Recettes         Dépenses
                                                                                                                                                                              
(*) Compte tenu du solde reporté. 
 
Les principales    actions   réalisées   en  2023  pour   la  conservation    des  ressoources  cynégétiques    et 
piscicoles,   se présentent    comme   suit : 
 
   Chasse  et  cynégétique      : 
 
Durant  l’année  2023,  la  valorisation   durable   de la  grande  faune  sauvage   protégée   a été  renforcée 
grâce  à des expériences    pilotes  de  chasse  au mouflon   à  manchettes   dans  les enclos  d’Iguer   et  de 
Tafoughalt,   utilisant   des  armes  à feu  ou des  arcs.  Au total,   23 mouflons   ont   été  tirés, dont   11 dans 
la région  de  Marrakech-Safi   et  12 dans la  région  de  l’Oriental. 
 
Cette  année   a  également   été   marquée   par  la  signature    d'une  convention     de  partenariat    entre 
l'ANEF   et  la   Fédération    Royale   Marocaine    de   Chasse  (FRMC),   visant    à  établir    un  cadre    de 
coopération     pour   le   développement     cynégétique      sur  la   période    2023-2027.     Par  ailleurs,   le 
nombre   d’amodiations     du  droit    de  chasse   a atteint    1.490  lots,   s’étalantt   sur  une  superficie    de 
3.915.000  ha, répartis   entre  92  sociétés  de  chasse  touristique    et 1.251 associations  de  chasse. 
 
   Pêche  et  aquaculture      continentale     :  
 
En 2023,   dans  le  cadre  des  actions   de  valorisation    piscicole   des  milieux   aquatiques,   plus   de  27 
millions  d’alevins   ont  été  déversés   dans  26  cours  d'eau,  19 lacs  naturels   eet plans d’eau,  ainsi  que 
44   retenues    de   barrages.   Ces   opérations     visaient    à  préserver    la   biodiversité     aquatique,     à 
renforcer   la  productivité     piscicole,   à  développer    la  pêche   de  loisir   et  commerciale,    à  encadrer 
des associations   et  des coopératives    de  pêches  et  l’octroi   de 2.559  permiss de  pêche  sportive. 

2.5.5.   Fonds    pour    le  développement          rural    et  des   zones    de  monttagne 

Les recettes   et  les  dépenses   du  Fonds  pour   le  développement     rural  et  des  zones  de  montagne 
(FDRZM)  ont   atteint,   respectivement,    6.986,05    MDH  et 2.191,52 MDH  en  2023.  L’évolution    sur  la 
période  2021-2023   se présente   comme  suit  ::  




 
           80 

87
                                                                                                RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
  
  
                         EVOLUTION DES RECETTES* ET DES DEPENSES DU FDRZM AU TITRE DE LA PERIODE 2021‐22023 (EN MDH)


                                                                                                                                               6 9986,05
                       6 178,49
                                                                                   5 572,01




                                        2 637,59
                                                                                                    2 165,09                                              2 191,52





                                  2021                                                    2022                                                    2023

                                                                               Recetttes         Dépenses
                                                                                                                                                                                                  
  (*) Compte tenu du solde reporté. 
  
 Durant    la  période    2021-2023,     l’essentiel     des  recettes     réalisées    par  le  FDRZM,    environ    92%,    a  été 
 affecté    au  Programme     de   Réduction     des  Disparités     Territoriales et       Socialees  (PRDTS).  
  
                                         REPARTITION PAR PROGRAMME DES DEPENSES DU FDRZM AU TITRE DE LA PERIODE 20221‐2023


                                                      Conventions et 
                                                        partenariat
                                                              8%









                                                                                            PRDTS
                                                                                             92%




                                                                                                                                                                                                  
                                                                                                  
  
 Les   principales       actions     réalisées     et   financées      dans    le   cadre    dudit     Fonds     durant     la   période               
 2017-2023    se  résument     comme    suit: 
  
   Programme      de  Réduction      des   Disparités     Territoriales       et  Sociales    : 
  
 Les  principales     réalisations     physiques     de  ce  programme      à  fin  2023,   se  préésentent    comme    suit  : 
  
-     Routes    et  pistes     rurales    : 

                        L’achèvement       des    travaux     de   construction        et   d’aménagement         des   routes     et   des 
                        pistes    rurales   sur   9.315  Km   et   la  poursuite     de   l’exécution      de   2.127  Km,  en   plus   de  la 
                        réalisation     de  149  ouvrages    d’art. 



  
                                                                                                                                                                                 81

88
                                                                       
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
  
-    Education  : 
                 L’achèvement   des  travaux  de   construction,   de  reconstruction   ou  d’extension   au 
                    niveau de 2.246 infrastructures  scolaires ; 
                 L’achèvement   des   travaux    d’entretien   et    de  réhabilitation     au  niveau   de   516  
                    infrastructures  scolaires ; 
                 L’équipement  de  42 établissements  scolaires et  l’acquisition  de 436  minibus  pour le 
                    transport  scolaire. 

-    Santé : 

                 L’achèvement   des  travaux  de   construction,   de  reconstruction   ou  d’extension   au 
                    niveau de 425 infrastructures  de santé ; 
                 L’achèvement   des   travaux   d’entretien    et   de   réhabilitation    au  niveau   de   280 
                    infrastructures  de santé ; 
                 L’équipement    de  442   autres   établissements   de   santé   et   l’acquisition   de   278 
                    ambulances et unités mobiles. 

-     Adduction   Eau Potable  (AEP)  : 
                    La  réalisation  de  33  systèmes  d’AEP, 207  branchements   par  bornes  fontaines   et 
                    l’extension du réseau sur 41 Km. 

-    Electricité   : 
                    L’achèvement  des travaux  d’électrification   pour  15 villages  et  l’extension du  réseau 
                    sur environ 22 Km.   

   Autres  programmes  : 
  
 Les réalisations en dehors du  PRDTS ont porté  sur l’assainissement des reliquats d’engagements 
 pris dans le cadre des conventions  de partenariats  pour  environ 8% des dépenses du CAS durant 
 la  période   2021-2023,  notamment   dans  le  cadre   des conventions   de  partenariats   avec  les 
 Collectivités  Territoriales   et  les acteurs  de  la  société  civile  et  de  l’économie  sociale,  portant, 
 essentiellement, sur le  désenclavement par  la réalisation  d’environ  400  Km des pistes  rurales et 
 la mise à niveau  de l’infrastructure   de certaine  Collectivités  Territoriales  (Abattoirs,   marchés de 
 gros, mise à niveau de centres de communes  …).                                                                                           

 2.5.6.   Fonds  de  développement       de  la  pêche   maritime  

 L’évolution  des  recettes  et  des  dépenses du  Fonds  de  développement   de  la pêche  maritime 
 (FDPM), au titre de la période  2021-2023, se présente comme suit  : 
  








  
            82 

89
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
                           EVOLUTION DES RECETTES* ET DES DEPENSEES DU FDPM AU TITRE DE LA PERIODE 2021‐‐2023 (EN MDH)



                                                                                     3313,65
                         275,39                                                                                                             264,51




                                                                                                      111,32
                                                                                                                                                                   80,42
                                           30,85


                                   2021                                                    2022                                                    2023


                                                                             Recetttes              Dépenses
                                                                                                                                                                                                
(*) Compte tenu du solde reporté. 

Les  principales     actions    réalisées    en 2023    dans   le cadre    dudit   Fonds,   se  préésentent    comme    suit  : 
                                             

          Financement      de  la construction       d’un   centre    Méditerranéen      de  mer   àà la ville  d’AL   Hoceima    ; 

          Maintenance      de   matériel     et   de    logiciels     de   sécurité     informatiquees      au   profit     du   service 
            central    et  des   Délégations     des   Pêches   Maritimes    du   Ministère    de  l’Agriculture       ; 

          Accompagnement        des   marins   pêcheurs     victimes    de  l'attaque     du  grrand   dauphin    "NEGRO"    ; 

          Financement       de    la   construction        d'un     nouveau      poste     électrique       60/22      KV    au   point 
            kilométrique       40  à  Dakhla. 

 
Les  principales     actions    programmées      pour    l’’année  2024,    se présentent      comme    suit   : 

  
                                                                                                                                                                                         (En MDH) 

                                                                 Actions                                                                                    Crédits  2024 


 Construction  du Point de Débarquement  Aménagé (PDA) IFRI IFOUNASSEN                                         38,50 

 Acquisition   des  sennes  tournantes   renforcées   contre   les  attaques   du  grand   daupphin 
                                                                                                                                                                       27,00 
 (NEGRO) en Méditerranée au profit  des armateurs 

 Organisation de la 7ème édition  du salon halieutis                                                                                     25,00 


 Construction  du marché de gros de poisson à Nadorr                                                                                 22,50 


 Construction  du PDA de SAADIA                                                                                                                20,00 

 

 

 

 


 
                                                                                                                                                                               83

90
                                                                                             
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 


 SECTION                  VI      -    AUTRES                   DOMAINES 

Les   comptes       d’affectation           spéciale      intervenant         dans    les    autres     domainees      représentent         22,66     % 
du  total     des   dépenses       effectuées       en   2023    par    l’ensemble       des   CAS    . 

                                      RECETTES* ET DEPENSES REALISEES AU NIVEEAU DES CAS INTERVENANT DANS LES AUTRES DOOMAINES 
                                                                              AU TITRE DE LL'EXCERCICE 2023 (EN MDH) 





                                                                                                                                                                                                      61 818
                                                                   Fonds de remploi domanial
                                                                                                                                                   26 403



                                                                                                                 2 539
                                                     Fonds de soutien à la sûreté natiionale
                                                                                                              428



  Fonds de participation des Forces Armées Royales  aux missions de paix, aux 2 508
   actions humanitaires et de soutien au titre de la coopération intérnatioonale 1 229



      Fonds spécial pour la mise en place des titres identitaires électroniquues et 2 335
                                         des titres de voyage                                    284



                                                                                                                2 008
                                            Fonds spécial pour le soutien des juridicctions
                                                                                                              710




  Fonds de modernisatioon de l'administration publique, d'appui à la transition 1 415
                         numérique et à l'utilisation de l'amazighe                    357



                                                                                                               1 189
                                                 Fonds de soutien à la gendarmerie rroyale
                                                                                                             72



           Fond spécial pour le soutien de l'administration et des établissements 1 140
                                                pénitentiaires                                         776



         Fonds pour la promotion du paysage audiovisuel et des annoncess et de 713
                                             l'édition publique                                      508



    Fonds national de soutien à la recherche scientifique et au développeement 484
                                            technologique                                           101



                                                                                            Recettes         Dépenses
                                                                                                                                                                                                                     
(*) Compte tenu du solde reporté. 

 
              84 

91
                                                                                                          RAPPORT  SUR  LES COMPTESS SPECIAUX  DU  TRESOR 
 
 
                                          EVOLUTION DES RECETTES* ET DES DEPEENSES DES CAS INTERVENANT DANS LES AUTRES DDOMAINES 
                                                                              AU TITRE DE LLA PERIODE 2021‐2023 (EN MDH))




                                                                                                                                                      76 150

                                                                                            65 779



                                   43 340

                                                                                                                                                                        30 867
                                                                                                             21 991

                                                    8 490





                                            2021                                                  2022                                                  2023


                                                                                        Recetttes         Dépenses
                                                                                                                                                                                                                     
(*) Compte tenu du solde reporté. 

2.6.1.     Fonds        de    remploi         domanial 

L’évolution        des   recettes       et   des   dépenses      du    Fonds     de   remploi      domanial       ((FRD)    durant     la   période 
2021-2023,       se  présente      comme      suit    :  
 
                              EVOLUTION DES RECETTES* ET DES DEPENSES DU FRD AU TITRE DE LA PERIODE 2021‐20023 (EN MDH)




                                                                                                                                                             611 817,78

                                                                                           53 595,29




                         32 263,92
                                                                                                                                                                                26 402,78

                                                                                                              18 947,08


                                             5 415,56


                                      2021                                                           2022                                                          2023




                                                                                            Reecettes Dépenses
                                                                                                                                                                                                                     
(*) Compte tenu du solde reporté. 
 
    Réalisation        au   titre     de   la  période       2021-2023        : 
 
Les   dépenses        effectuées        au    cours     de    la   péériode     2021-2023,        dont     le   montant        global      s’élève      à 
environ     50.765      MDH,    ont   servi,    essentiellement,           à  : 
 
 
                                                                                                                                                                                                  85

92
                                                                      
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
     -    L’acquisition  de terrains et  bâtiments pour  satisfaire les besoins des administrations  ; 

     -    L’accompagnement  des établissements  publics pour  la réalisation  des projets structurants 

          dans un cadre  conventionnel  ; 

     -    La  contribution   au  financement  du  programme   de  relogement   des ménages  issus des 

          bidonvilles  de la  Préfecture  de Skhirat-Témara ;   

     -    Les réalisations immobilières  à l’étranger  ; 

     -    La   réalisation   de  travaux    topographiques    des  immeubles   pour   l’établissement    des 

          règlements  de copropriété  en vue de la vente  de logements  domaniaux ; 

     -    L’appui  aux programmes de développement   régionaux ;               

     -    Le paiement  des dépenses relatives à la gestion active  du domaine privé  de l’Etat. 

      
             Mobilisation   du foncier   en appui  à l’investissement   : 
           
Les réserves foncières mobilisées  durant  la période  2021-2023, s’élèvent à environ  1.620.087 ha, 
pour   un   investissement    projeté   de   près    de   903.163  MDH,   permettant    la   création    de           
101.382 emplois dans divers secteurs économiques. 
 
             Ventilation   par  secteur  d'activité   : 
 
La ventilation par  secteur d’activité,  au titre  de la période 2021-2023, se présente comme  suit : 
 
        Energie:  1.600.142 ha  ont   été  mobilisés  dans  le  cadre  de  la  promotion    des  énergies 
          renouvelables  pour  la réalisation  de  24 projets  devant  drainer  un  investissement  projeté 
          de l’ordre  de 808.116 MDH et la création à termes de 27.393 emplois escomptés; 
 
        Mines : 9.074  ha ont  été  mobilisés pour  105 projets  relevant  du  secteur des  Mines et  un 
          investissement   projeté   de  l’ordre   de  19.639  MDH  et  la  génération   de  2.284  emplois 
          escomptés  ; 
                                                               
        Agro-industrie   : 165 projets d’une  superficie globale  de 2.131 ha ont été approuvés, devant 
          drainer  un  investissement   projeté  de  l’ordre  de  4.419  MDH et  la  création  à  termes  de           
          12.757 emplois escomptés ; 
 
        Habitat:   84  projets   d’une  superficie  globale   de  1.961 ha  ont  été  approuvés,   pour  un 
          investissement  projeté  de l’ordre de 10.154 MDH; 
 
         Industrie  : 1.188 ha ont été mobilisés pour 235 projets  relevant  du secteur de l’industrie  et 
          un  investissement  projeté  de  l’ordre  de 10.562 MDH  et la  génération  de  26.487 emplois 
          escomptés  ; 
                                                               
        Tourisme  : 318 projets   d’une  superficie  globale  de  559  ha ont  été  approuvés,  pour   un 
          investissement   projeté   de  l’ordre  de  14.302  MDH  et  la  génération   de  13.906 emplois 
          escomptés. 
                                                               
                                                               

 
           86 

93
                                                                                        RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
  
  
  
                Déclinaison    Régionale   : 
  
 Au  titre   de la  période   2021-2023,   les  trois  régions   de  Dakhla-Oued   Eddaahab, Laâyoune-Sakia    El 
 Hamra   et  Guelmim-Oued     Noun   s’accaparent    99,8%   de  la   superficie   mobilisée.    En   termes   de 
 nombre   de  projets   réalisés,  plus  de  75% des  projets   sont   concentrés   au  niveau   de deux   régions 
 (Dakhla-Oued   Eddahab   et  Laâyoune-Sakia   El Hamra).         
  
                            PARTS DES REGIONS DANS LA SUPERFICIE TOTALE MOBILISEE AU TITRE DE LA PERIODDE 2021‐2023







                                                                             Auutres régions 
                                                                                   0,2%


                        Laayoune‐Sakia EL Hamra
                                    23%






                                                                                                                                Dakkhla‐Oued Eddahab
                                                                                                                                         50,7%





                         Guelmim‐Oued Noun 
                                  26,1%






                                                                                                                                                                                

                Ventes   de  logements    à leurs  occupants     : 
               
 Durant  la  période   2021-2023,    1.803 unités  ont   été cédées   à leurs  occupannts pour   une enveloppe 
 globale  de  105,56  MDH.  
  
   Réalisation   au  titre   de l’année   2024  : 
             
                Appui   du  FRD  aux  programmes     de  développement     régionaux     : 

 Le   Fond   de    remploi    domanial    intervient,,     également,    dans l’accompagnement         des   projets 
 structurants    dans un  cadre  conventionnel.    Il  s’agit  notamment   de  :  
  



  
                                                                                                                                                                87

94
                                                                                      
    PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
   
                                                                                                                                                                                (En MDH) 

                                                                                                                                                            Contribution  
                                           Conventions                                                  Contributions   du FRD       effective  au     Reliquat 
                                                                                                                                                             31 mai 2024 

                                                                                                                                550 
                                                                                                                      (conventionnel) 
                                                                                                                                    
                                                                                                                              6.500 
Convention relative  à la création de la société  d'aménagement 
                                                                                                                 (estimé sur la base des           526,77         5.973,23 
de la vallée de l'Oued Martil 
                                                                                                                           jugements 
                                                                                                                       d'expropriation 
                                                                                                                          prononcés) 
                                                                                                                                    
                                                                                                                                400
                                                                                                                      (conventionnel) 
                                                                                                                               1.600 
Convention relative  au programme de développement   intégré,           (estimé sur la base des 
                                                                                                                                                                1.515,52          84,48 
équilibré et  inclusif baptisé Tanger Métropole  (2013-2017)                            jugements 
                                                                                                                       d'expropriation 
                                                                                                                          prononcés) 
                                                                                                                                    

Convention pour le  financement de l'opération  d'acquisition   des 
                                                                                                                             2.338,61                     1.932,36        406,25 
actions de la Société Wessal Bouregreg S.A 


Convention relative  au financement du programme  de 
relogement des ménages issus des bidonvilles de  la préfecture                       2.081,25                     1.706,25            375 
de Skhirate-Témara et son avenant signé en Juillet  2023 

Convention relative  au financement et réalisation  des zones 
d'activités  économiques dédiées aux unités de production 
                                                                                                                                800                             780                 20 
identifiées à risque et  nécessitant une délocalisation  (Rabat, 
Casablanca et Tanger) 
Convention relative  au programme intégré  de développement 
urbain de la ville de Rabat (2014-2018)  (Rabat ville lumières                               400                            183,66          216,34 
capitale culturelle  du Maroc) 

Convention de partenariat  relative  à la réhabilitation  et la 
                                                                                                                                100                            10,69             89,31 
valorisation de l'ancienne  médina de Tanger 

Convention de partenariat  relative  au programme de 
                                                                                                                                100                            16,80             83,20 
réhabilitation  de la Médina de Fès 



                                                 Total                                                                   13.919,86                   6.672,05        7.247,81 



  2.6.2.     Fonds      spécial      pour     le   soutien      des    juridictions   

  Les   recettes      réalisées    en   2023     par   le   Fonds    spécial     pour    le   soutien     des   juridictions       (FSSJ), 
  compte    tenu   du   solde   reporté,    s’élève    à 2.008,01    MDH   contre    2.040,28     MDH  en  2022   et   2.046,23 
  MDH  en  2021,   soit  une   baisse   annuelle    moyenne     de  0,94%.   En  ce  qui   concerne    les  dépenses,     elles 
  sont   passées    de  705   MDH   en   2021  à  737,52   MDH   en  2022    et  710,05    MDH   en  2023,   enregistrant 
  ainsi  un   accroissement      annuel   moyen    de  0,36%. 

  Le   bilan    des    réalisations      dudit     Fonds,    par    programme       et   par    projet,     au   titre     de   la   période              
  2021-2023,    se  présente     comme    suit  : 
                                                                                                                                                                                      
                                                                                                                                                                         
                                                                                                                                                                              

   
               88 

95
                                                                                               RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
                                                                                                                                                                                (En MDH) 
                                                                                                                          Dépenses au     Dépenses       Dépenses 
                                                                                                                              titre  de          au titre  de      au titre  de 
             Programmes                                            Projets 
                                                                                                                              l’année             l’année           l’année  
                                                                                                                                 2021               2022               2023 
                                                                                                                                                             
                                                  Construction,  extension, et                                                                                       
                                                  réaménagement des juridictions                         420,97              279,69            354,14 

                                                  Gestion des ressources                                       122,22              135,41            119,84
 Soutien  et pilotage 
                                                                                                                                                             
                                                  Equipement des juridictions                                  14,28               78,01              46,81 
                                                                                                                                                             
                                                                                                                                                                                    
                                                  Formation                                                              0,16                   7,11               8,88 

                                                  Performance des tribunaux  en matière                                             
 Performance  de                      civile                                                                      62,60               69,20              69,02 
 l’administration   judiciaire        Performance des tribunaux  en matière                                             
                                                  pénale                                                                   32,70                41,15             38,02 

 Modernisation  du système                                                                                                                 
                                                  Tribunal numérique 
 judiciaire  et juridique                                                                                             25,46               72,94              50,86 

                                                       Total                                                               678,39              683,51            687,57 
 
Les  dépenses     réalisées     au   premier     trimestrre    de   l’année     2024    concerneent,    essentiellement,        les 
dépenses    de   fonctionnement         courant    des   jjuridictions,      notamment       les  dépenses     afférentes aux 
marchés     reconductibles        de    surveillance,      de    nettoyage      et    de   l’entretieen     de   bâtiments      et    du 
matériel    ainsi   que   les  dépenses    courantes     établis    à  travers    des  bons   de  coommandes.    Le  montant 
global   de  ces   dépenses    a atteint     environ    212 MDH. 

2.6.3.      Fonds       spécial       pour       le    soutien        de    l’administration               et     des     établissements 
pénitentiaires   

Au  titre   de  la  période    2021-2023,     les  recettes    et   les  dépenses    du  Fonds   spécial    pour   le  soutien    de 
l’administration        et    des   établissements        pénitentiaires        (FSSAEP)     ont    connu     un    accroissement 
annuel   moyen,    respectivement,       de  4,25%   et  13,74%.  
                                                                                                                                                            
                         EVOLUTION DES RECETTES* ET DES DEPENSES DU FSSAEP AU TITRE DE LA PERIODE 2021‐‐2023 (EN MDH) 


                                                                              1 258,,61
                                                                                                                                         1 1400,43
                   1 049,33

                                                                                                883,66
                                                                                                                                                           775,94

                                     599,83







                              2021                                                   2022                                                   2023

                                                                              Recetttes Dépenses 
(*) Compte tenu du solde reporté. 
 
                                                                                                                                                                               89

96
                                                                            
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
Les  dépenses    du   Fonds    spécial   pour    le   soutien    de   l’administration      et   des   établissements 
pénitentiaires,    au titre   de  la  période   2021-2023,  ont   concerné,   principalement,    les  constructions, 
l’extension     et   l’aménagement      desdits     établissements      ainsi    que   l’achat     des    équipements 
logistiques,   techniques   et  sécuritaires. 
 
Les réalisations    des  programmes    financés   par  le  Fonds,  au  titre   de  l’année  2023,   se présentent 
comme  suit  : 

        Hébergement    des  détenus                                                                                        : 454,57  MDH  ; 
        Soutien,   fonctionnement     et logistique                                                                      : 212,80  MDH  ; 
        Sûreté   et sécurité   des établissements    pénitentiaires                                             : 33,76   MDH  ; 
        Réinsertion    des détenus                                                                                            : 27,51  MDH  ; 
        Formation    du  personnel                                                                                             : 24,97   MDH;   
        Délocalisation    des  établissements    pénitentiaires   enclavés   dans  le milieu    : 22,34   MDH. 
           urbain                                                                                                                                    
 
Pour  l’année   2024,    les  actions    programmées     dans  le   cadre   dudit    Fonds,   sont   ventilées    par 
programme   comme   suit  :  
                                                                                                                                                                                         

   
                                                            Programmes                                                             Montant (En MDH) 



  Hébergement des détenus                                                                                                          236,65 



  Soutien, fonctionnement et logistique                                                                                             76 


  Formation du personnel                                                                                                                14,78 


  Programme de délocalisation des établissements pénitentiaires enclavés dans le milieu    
                                                                                                                                                        12,36 
   urbain  


  Sûreté et sécurité au sein des établissements pénitentiaires                                                       10,45 



  Réinsertion des détenues                                                                                                              3,22 


                                                                 Total                                                                              353,46 


2.6.4.     Fonds     pour    la    promotion        du   paysage      audiovisuel        et    des   annonces       et   de 
l’édition      publique               

Les  recettes    et   les   dépenses   du   Fonds    pour   la   promotion     du   paysage   audiovisuel     et   des 
annonces  et  de  l’édition    publique   ont   enregistré   une  baisse   annuelle  moyenne,   respectivement, 
de 11,88% et 5,75% durant   la période   2021-2023. 
 
 
 


 
           90 

97
                                                                                                  RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
    
    
                              EVOLUTION DES RECETTES* ET DES DEPENSEES DU FONDS AU TITRE DE LA PERIODE 20211‐2023 (EN MDH) 





                          918,79
                                                                                      7499,49                                               7713,48
                                           571,31
                                                                                                                                                                    507,54
                                                                                                       401,95





                                   2021                                                     2022                                                    2023



                                                                                     Reccettes Dépenses
                                                                                                                                                                                                    
   (*) Compte tenu du solde reporté. 
    
   Au   titre   de   la  période     2021-2024     (1èr semestre),      les  subventions      accordéées    par   ledit   Fonds aux 
   organismes     bénéficiaires,      sont   ventilées    comme    suit   : 
    
    
                                                                                                                            Subventions acccordées  (En MDH) 

                              Organismes bénéficiaires  
                                                                                                                                                                               1èr semestre 
                                                                                                               2021                2022               2023 
                                                                                                                                                                                     2024 


Société Nationale de Radiodiffusion  et de Télévision  (S.N.R.T)           316                  120                 150                 120 


Centre Cinématographique  Marocain (C.C.M)                                    229,68                271                 316                 100 


Agence Maghreb Arabe Presse (M.A.P)                                               25,63                   6                   6,51                  -


Compagnes de Communication                                                                -                    3,45                9,24                0,99 


Etudes générales                                                                                      -                     1,49               0,79                0,20 


Versement au budget général                                                                   -                       -                    25                     -


                                               Total                                                       571,31            401,94            507,54             221,19 

    

   2.6.5.     Fonds      national        de    soutien       à  la    recherche        scientifique           ett   au   développement 
               technollogique  

   Les   recettes     du    Fonds    national     de   soutien      à  la   recherche      scientifiquee    et    au  développement 
   technologique,       compte      tenu   du   solde    reporté,     s’élèvent     à  483,91   MDH    en  2023    contre     564,97 
   MDH  en  2022    et  599,71  MDH   en  2021.  Quant    aux   dépenses,    elles  ont   atteint     100,64   MDH   en  2023 
   contre    157,84  MDH   en  2022   et  130,25  MDH   en  2021. 

   Les  principales     actions     financées    par   ledit   Fonds,    au  titre   de   l’année   2023,    se  présentent     comme 
   suit  :                                                                                                                                                                                      
    
                                                                                                                                                                                   91

98
                                                                                             
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
                                                                                                                                                                                                   (En MDH) 

                                                                                                                                                                                              Montant   de 
        Projets   et programmes                                                                                            Actions   réalisées  au  titre                 la 
                                                                          Objectifs    du programme 
                     financés                                                                                                                de l’année   2023                subvention 
                                                                                                                                                                                                  allouée  



                                                             Le  CNRST contracte  des abonnements  en 
                                                             consortium   pour  favoriser  des  économies 
 Abonnements  aux   ressources  et     d’échelles   importantes.     Le    consortium 
 ouvrages électroniques                       concerne  toutes  les  universités  publiques     Abonnement     de     l’exercice 
  (Subvention   au  Centre  National     nationales.    L’utilisation      de    l’accès    à                                                                34,53 
                                                                                                                                        2023 
 pour  la Recherche Scientifique   et    distance      aux     différentes      ressources 
 Technique (CNRST))                          documentaires   sont  fourni   par  le  CNRST 
                                                             aux universités  à travers  la plateforme  «E-
                                                             ressources». 



                                                                                                                                        -  Octroi     de    la     deuxième 
                                                                                                                                        tranche  aux   projets   relevant 
                                                                                                                                        des appels à  projets n°  1, 2 et 
                                                                                                                                        3      dont      le      rapport      à   
                                                                                                                                        mi-parcours a été validé  ; 
                                                             Renforcer  la coopération   dans le domaine 
                                                             de  la recherche et  de l'innovation  dans les     - Octroi      de     la     première 
                                                             pays  méditerranéens   afin  de   développer     tranche   aux  projets   retenus 
                                                             des   solutions   innovantes  permettant    de    dans   le  cadre   de   l’appel   à 
 Partnership    for    Research    and 
                                                             contribuer     aux     défis     de    production      projets n° 5 ; 
 Innovation   in  the   Mediterranean                                                                                                                                           21,22 
                                                             alimentaire  durable  et  de  sécurité  en eau 
 Area « PRIMA »                                                                                                             -  Lancement du sixième appel 
                                                             dans       la       région       méditerranéenne. 
                                                                                                                                        à projets PRIMA ; 
                                                             (programme    financé   conjointement     par 
                                                             l’Union     Européenne          et     les     Pays    - Evaluation         des         pré-
                                                             participants)                                                       propositions    reçues  dans   le 
                                                                                                                                        cadre de l’appel à projets  ; 

                                                                                                                                        -  Signature   des  conventions 
                                                                                                                                        des    projets     retenus    pour 
                                                                                                                                        financement (20  projets). 






                                                             Encourager les brillants  étudiants, titulaires 
                                                             d’un  Master ou  d’un diplôme  équivalent,  à 
                                                                                                                                        Tranches      accordées      aux 
 Bourses d’Excellence                          poursuivre  des  études  doctorales  en  vue                                                                16,70 
                                                                                                                                        différentes éditions 
                                                             de     la     promotion     de     la     recherche 
                                                             scientifique  au niveau national 






                                                             -  Préparer   un  capital   humain   avec   des 
                                                             compétences    en   Intelligence   Artificielle 
                                                             (IA)  dont le  pays a besoin pour développer 
                                                             une    économie   prospère    basée   sur   la 
                                                             transformation   digitale   et   l’économie   du 
                                                             savoir ; 

 Programme    de     recherche     Al    -  Soutenir  une recherche  appliquée  en  IA    Octroi  de la deuxième tranche 
 Khawarizmi                                          visant  à   améliorer   la   compétitivité    des    aux  projets  dont  le  rapport  à           7,34 
                                                             entreprises marocaines ;                                   mi-parcours  a été validé  

                                                             -  Favoriser   la  mise  à   niveau  d’un   tissu 
                                                             productif   innovant  capable  de  tirer  profit 
                                                             des             différentes              opportunités 
                                                             socioéconomiques   que  l’IA  offre   tant   au 
                                                             niveau national  qu’au niveau international. 




 
              92 

99
                                                                                                          RAPPORT  SUR  LES COMPTES   SPECIAUX  DU  TRESOR 
 
 


                                                             Mettre  à  la disposition  de  la  communauté 
 Les analyses des Unités d’Appui 
                                                             scientifique   et   à  l’ensemble  des   acteurs 
 Techniques à la Recherche 
                                                             économiques  un  parc  d’instrumentation   à 
 Scientifique (UATRS) (Subvention                                                                                Contribution      de     l’exercice 
                                                             la fine  pointe  de la technologie  offrant  des                                                                4,00 
 au CNRST)                                                                                                                    2023 
                                                             prestations      analytiques     couvrant     les 
                                                             domaines  de  la  chimie,  de  la  biologie  et 
                                                             des matériaux 




                                                             Soutenir    des   projets    de   recherche   et 
                                                             développement  structurants  répondant aux 
                                                             enjeux   économiques  et   sociétaux   visant    Versement   de    la   deuxième 
 Programme de coopération 
                                                             notamment  des retombées économiques et     tranche  aux   projets   dont   le 
 scientifique Maroco-Tunisienne                                                                                                                                                  3,28 
                                                             technologiques  directes pour  le Maroc et la    rapport   à  mi-parcours   à  été 
 (PR&D LMMT) 
                                                             Tunisie   en  termes   de   valeurs   ajoutées,    validé 
                                                             d’emplois,  ou  d'anticipation   de  mutations 
                                                             économiques 





                                                             Mettre   en   synergie   les   moyens   et   les 
 Coopération Maroco-Canadienne 
                                                             efforts  des Parties  pour  créer un cadre  de    Octroi      de     la     subvention 
     (Subvention au CNRST)                                                                                                                                                        3,00 
                                                             coopération   dans différents  domaines  liés    annuelle 
  
                                                             à la recherche scientifique  et technique 






 Appel à projets dans les domaines     Promouvoir   et  renforcer   les  activités   de    Déblocage  des  deuxièmes ou 
 prioritaires de  la recherche                 recherche dans les domaines prioritaires de    des   troisièmes   tranches  aux 
                                                                                                                                                                                                    2,87 
 scientifique et du  développement       la      recherche      scientifique       et       du    projets   dont  le  rapport  à  mi-
 technologique                                      développement  technologique                         parcours  a été validé 





                                                             Appui    à   la    recherche   scientifique     en 
                                                             Sciences       Humaines,       Sociales        et    Versement    de   la   deuxième 
                                                             Economiques,    en   lien    avec    l’Intégrité     tranche   aux  projets   dont   le 
 Programme de recherche SHSE                                                                                                                                                2,29 
                                                             Territoriale,   les  Provinces  du   Sud  et  les    rapport   à  mi-parcours   a  été 
                                                             Conséquences     de     la     pandémie     de    validé 
                                                             Coronavirus (COVID-19) 





                                                                                                                                        Octroi  de la  première  tranche 
 Long-term Europe Africa                     Renforcer   la   coopération    entre   l'Union     des    subventions    accordées 
 Partnership on Renewable Energy     Africaine   et   l'Union  Européenne  dans  le     aux    projets     de    recherche           1,96 
 « LEAP-RE »                                       domaine des énergies renouvelables                retenus   dans   le    cadre   de 
                                                                                                                                        l’appel à projets  n° 2 







                                                             Permet     l’analyse     scientifique     de     la 
 Abonnement Anti-plagiat 
                                                             production      scientifique      encours     des    Abonnement      de    l’exercice 
                                                                                                                                                                                                     1,70 
 (Subvention au CNRST)                                                                                                2023 
                                                             enseignants chercheurs et doctorants 





 
                                                                                                                                                                                                  93

100
                                                                                             
  PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 



                                                             Développer  des propositions de nouveaux 
                                                             projets  conjoints ou à connecter des                Octroi  de la première tranche 
 Programme de coopération 
                                                             projets  qui sont actuellement  financés             aux projets retenus dans le                 0,80 
 scientifique Maroc - Suisse 
                                                             séparément, dans le but de les transformer      cadre de ce programme 
                                                             en collaborations  de longue durée 





                                                             un programme  de bourses de recherche 
 Bourses de recherche dans le            dans le domaine des technologies 
                                                                                                                                        Tranches accordées aux 
 domaine des technologies                  spatiales, destiné aux doctorants  impliqués                                                                  0,55 
                                                                                                                                        différentes éditions 
 spatiales                                              dans la réalisation de nano-satellites 
                                                             universitaires 





                                                                                                                                        Restitution au profit  de 
                                                                                                                                        l'Agence Nationale de 
                                                             Dépenses destinées à restituer des crédits       Réglementation des 
 Restitution des crédits  reçus à tort                                                                                                                                             0,19 
                                                             reçus à tort  des exploitants du réseau              Télécommunications (ANRT) 
                                                                                                                                        suite au versement à tort  de 
                                                                                                                                        WANA 






                                                             Bourses dans le cadre des accords 
 Bourses CIFRE Maroc                        industriels  de formation par voie  de                                         -                                    0,13 
                                                             recherche 







                                                                                                                                        Evaluation de l’appel à projet 
                                                             Financement de l’évaluation  des projets          lancé dans le cadre du 
 Evaluation des projets                                                                                                                                                                0,04 
                                                             soumis dans le cadre des programmes             programme de coopération 
                                                                                                                                        Maroc - Hongrie 




Les    prévisions        budgétaires          des    principaux         programmes          financés       par    ledit      Fonds,      au    titre     de 
l’année     2024,    se   présentent        comme      suit   : 

                                                                                                                                                                                                (En MDH) 
                                                                                                                                                   Budget   prévisionnel    pour  l’année 
                                                          Programmes 
                                                                                                                                                                            2024 


 Programme National d’Appui  à la R&D et à l’Innovation PNARDI                                                                   100,00 


 Partnership for Research and Innovation in the Mediterranean Area (PRIMA)                                                  33,16 


 Mise en place des cités d’innovation                                                                                                                  30,00 

                                                                                                                                                                                  
  
                                                                                                                                                                            30,00  
 Abonnements aux ressources et ouvrages électroniques 
                                                                                                                                                                                  

 Bourses d’excellence                                                                                                                                          12,94 



 
              94 

101
                                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 

Centre de calcul quantique                                                                                                                10,00 


Programme de coopération Maroco–Tunisien (PR&D LMMT)                                                           6,44 
                                                                                                                                                                
Programme de coopération Maroco–Allemande                                                                                 6,12 

Long-term Europe Africa Partnership on Renewable Energy « LEAP-RE »                                       6,11 


Appel à projets en partenariat avec l’ONEE                                                                                       6,00 


Programme de coopération Maroc-Hongrie                                                                                        4,66 


Programme de coopération Maroco-Canadienne                                                                               3,00 


Programme de recherche Open Science                                                                                            3,00 


Programme de recherche Fosc                                                                                                           2,97 


Programme de recherche Fosc-Susfood                                                                                            2,06 


Programme de coopération Maroc–Suisse                                                                                         2,00 


Abonnement Anti-plagiat                                                                                                                     2,00 


Programme Prioritaire de la Recherche (PPR)                                                                                   2,00 


Programme de recherche Cor-organic                                                                                                1,62 


Programme de recherche ClimGenOlive                                                                                            1,40 


Programme de recherche BIODIVERSA                                                                                             1,20 


Bourse de recherche dans le domaine des technologies spatiales                                                     1,18 


Points de Contact Nationaux Thématiques « l’Horizon Europe »                                                       0,90 


Programme de recherche BIODIVERSTORE                                                                                     0,78 


Bourses CIFRE                                                                                                                                   0,17 


2.6.6.     Fonds      spécial       pour     la    mise    en    place      des    titres      identitaires           électroniques           et 
des   titres      de   voyage  

En  2023,   les   recettes    réalisées     par  le   Fonds   spécial    pour    la  mise   en  place    des   titres    identitaires 
électroniques      et   des   titres    de  voyage,     compte    tenu    du   solde   reporté,     ont   atteint     2.335,43    MDH 
contre    1.994,37   MDH   en  2022    et  1.841,51 MDH   en  2021.   Quant    aux  dépenses,     elles   ont   enregistré 
une  baisse   annuelle    moyenne     de   27,35%   passant   de   538,95   MDH   en  2021   à 345,27    MDH   en  2022 
et  284,49    MDH  en  2023. 



 
                                                                                                                                                                               95

102
                                                                                    
 PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
 
Les  principaux     projets    financés     par  ledit   Fonds,    au  titre   de   la période     20221-2024,   se  représentent 
comme    suit  : 

                                                                                                                                                                            (En MDH) 
                                                                                                                                                                             2024 
                                                projets                                                       2021          2022           2023           (En cours 
                                                                                                                                                                       d’exécution) 

 Acquisition   d'une solution  complète   relative à  la nouvelle  carte 
 d’identité   électronique  CNIE.2 au profit  de la Directtion Générale 
                                                                                                                258,54       237,61         214,88           233,70 
 de   la  Sûreté  Nationale   (DGSN)  en  plus   d’une  plateforme   y 
 afférente         


 Acquisition   et installation  d'une  plateforme  PKI pour le  système 
                                                                                                                 60,57         85,93          85,93               28,15
 de  production  dees titres identitaires au profit de la DGSN 


 Mise   à    niveau   et    maintenance   du    système   automatique 
 d'identification    par  empreintes  digitales  «AFIS» ett du  système      27,02         27,02          54,04              16,85
 de  reconnaissance faciale «FRS» au profit de la DGSN                     


 Entretien    et   maintenance   (pièce    et   main   d'œuvre)   de   la 
 plateforme   Datacenter  au  profit   du Centre  Informatique   de  la      12,00         12,00          12,00               6,20
 DGSN 


 Maintenance    de    la   plateforme     de    gestion    de    l'identité 
                                                                                                                     -                 -              23,38              23,38
 numérique  de la carte d'identité   nationale au profit  dde la DGSN

 

2.6.7.     Fonds     de   soutien       à  la   sûreté      nationale                    

Les  recettes    et   les  dépenses    du   Fonds   de   soutien    à  la  sûreté   nationale     (FSSN)    ont   enregistré     un 
accroissement      annuel   moyen,    respectivement,        de  12,25% et   21,52% durant     la période    2021-2023. 
 
 
                               EVOLUTION DES RECETTES* ET DES DEPENNSES DU FSSN AU TITRE DE LA PERIODE 20221‐2023 (EN MDH)




                                                                                                                                              2 539,30

                                                                                        2 231,45
                                 2 015,37








                                                                                                                                                               428,18
                                                  289,96                                            245,17


                                            2021                                              2022                                               2023

                                                                                   Recettes       Dépenses
                                                                                                                                                                                                 
(*) Compte tenu du solde reporté. 
 


 
             96 

103
                                                                                      RAPPORT SUR LES COMPTESS SPECIAUX DU TRESOR 
 
 
Les principales   dépenses   effectuées   dans  le cadre   du FSSN, au  titre  de  la  période  2021-2023,   ont 
porté  sur  les opérations   suivantes   :                   

                                                                                                                                                                            (En MDH) 
                                                                                

                                                      Actions                                                             2021           2022        2023 

 Acquisition de matériel de prévention, cartouches ett accessoires d’armements  18,71       130,53      251,13 

 Acquisition des effets, équipements, accessoires d'habillement, chaussures et 
                                                                                                                              150,,27      241,90       65,84 
 bottes et ceinturons 
 Fourniture d’équipements d’infrastructure, système d’information, installation, 
                                                                                                                             758,,90        205,15    240,68 
 services et mise en service de réseau de transmission  

 Achat de véhicules et motos                                                                                61,999       130,96       117,19 

 
                                                           

2.6.8.    Fonds    de   modernisation        de   l’administration          publique,       d’’appui     à  la  transition 
           numérique       et  à  l’utilisation        de  l’amazighe  

Les  recettes    et   les  dépenses    effectuées    par   le   Fonds   de   modernisattion    de   l’administration 
publique,    d’appui     à   la   transition      numériique    et    à   l’utilisation     de    l’’amazighe    ont    atteint, 
respectivement,    1.414,78 MDH  et  357  MDH  au  titre   de  l’année   2023.  L’évvolution   des recettes    et 
des dépenses  dudit   Fonds  sur  la période   2021-2023   se présente  comme   suit  :  
 
 
                        EVOLUTION DES RECETTES* ET DES DEPENSEES DU FONDS AU TITRE DE LA PERIODE 20211‐2023 (EN MDH)


       (Recettes)                                                                                                                                 (Dépenses)
           1600                                                                                                                                               400
                                                                                                                                   11 414,78
           1400                                                                                                                                               350
           1200                                                                                                                    357                     300
           1000                                                                                                                                               250
            800                                                                                                                                                200
            600                                                                                                                                                150
            400                                                                 307,74
                                                                                                    72,47                                                     100
            200                    107,83 0,08                                                                                                         50
               0                                                                                                                                                 0
                                        2021                                      2022                                       2023


                                                                        Recetttes         Dépenses
                                                                                                                                                                               
(*) Compte tenu du solde reporté. 
 
   Dépenses  effectuées    au titre   des  années  2021  et  2022: 
 
Les  dépenses   du  Fonds   de  modernisation     de  l’administration     publique,    d’appui    à la  transition 
numérique   et à  l’utilisation   de  l’amazighe   sont  effectuées   selon  deux  niveaaux : 
 
-  Projets      transverses        :  financement    en  totalité   des  opérations    portaant sur  la  modernisation 
des services  publics. 
  
-  Projets      sectoriels        :  versement   au  profit    des  départements    ministéériels  de  dotations    pour 
contribuer    aux  dépenses    afférentes   aux   opérations    de  modernisation     des   services   publics   ou 


 
                                                                                                                                                               97

104
                                                                                 
      PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
     
    versement      au    profit      des    institutions      internationales       pour     réaliser     des    opérations      de 
    modernisations    des  services  publics. 
     
     
    La  répartition   des  dépenses,  ordonnancées,    par  projet  se  présente  comme   suit  : 
                                                                                                                                                                                        (En MDH)                   

                                                                   Projets                                                                     2021          2022 

     Versement au profit des institutions internationales pour réaliser des opérations de 
                                                                                                                                                      -                70 
     modernisations des services publics 

     Réalisation d’études portant sur la modernisation de l’administration publique                   0,08               - 

     Contribution au profit des départements ministériels au titre des opérations de 
                                                                                                                                                      -               2,47 
     modernisation de l’Administration publique 


                                                                    Total                                                                       0,08           72,47 

          
      Les  projets   transverses   : 
     
     Durant  les  années  2021 et  2022, un  projet   financé  a été  achevé,  il  s’agit  de  : 
                                                                                                             
               Refonte     du    portail     national      de   l’Emploi     Public     «   www.emploi-            : 1,40 MDH.
                  public.ma    » et  de son  application     mobile 
     
      Les  projets   sectoriels   : 
     

     Durant  la même  période,   ledit  Fonds  a  contribué   au réalisation   des  projets   sectoriels   suivants  : 


             Modernisation     et  amélioration     de  la visite   des  familles   des  détenus 
                                                                                                                                                         : 1,90 MDH ; 
                des  établissements     pénitentiaires-Prison       local  d’Ain   Sbaâ 


             Mise  en  place  d’un   Système   National   d’Information      sur  l’eau                          : 1,22 MDH ; 


             Appui    et  accompagnement      de  40   communes    dans   la mise   en  œuvre 
                                                                                                                                                        : 0,95  MDH  ; 
                de  la fonction    d’audit    interne 


             Développement      d’un   système   intégré    de  suivi   du  travail   législatif,    du 
                contrôle       de    l’action      gouvernementale         et     de     l’évaluation       des 
                                                                                                                                                         : 0,91 MDH ; 
                politiques      publiques       du    Ministère     délégué      auprès     du    chef     du 
                gouvernement     chargé   des  relations    avec  le  parlement 


             Elaboration       du     bilan     de     compétences       des     cadres      du    Haut-
                Commissariat     au  Plan   et  mise   en  place    de  la  Gestion    Prévisionnelle         : 0,80  MDH  ; 
                des  Emplois   et  Compétences 





     
                98 

105
                                                                               RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 
 

        Dématérialisation    de  la  gestion   des  documents   via  un  système   de 
          Gestion     Electronique      des     Documents      (GED)    au     profit      du     : 0,60  MDH ; 
          Département   de  l’Environnement 

        Elaboration    d’un    système   de   gestion    des    études   d’impact     sur 
          l’environnement      et   des    autorisations     pour    le   Département     de      : 0,53 MDH ; 
          l’Environnement 

        Appui   à   l’amélioration     de   l’accueil   au   niveau   de   10  communes 
          bénéficiaires   du programme   de  promotion   de la  gestion  de proximité 
                                                                                                                                        : 0,09 MDH. 
          dans   les  communes    pour   la   Direction   Générale   des   Collectivités 
          Territoriales 
      
  Dépenses effectuées  au titre  de  l’années 2023 : 
      
Concernant   les   dépenses   dudit    Fonds   au  titre    de  l’année   2023,   elles   sont   exécutées 
conformément   au nouveau  cadre  juridique  comme  suit  : 
      
    -     Le programme   de  modernisation   des services  publics,  comprend  les axes suivants : 
           
                -    l’amélioration   de la qualité   des services rendus  au public  ; 
                -    la consécration   de l’intégrité   et  la transparence  dans  le service public   ; 
                -    l’appui  à la déconcentration    administrative   ; 
                -    l’adopter   des  méthodes   et  des  procédés   efficaces  et  efficients   en  matière   de 
                     gestion  des  ressources humaines  ; 
                -    le  renforcement    de  l’efficience   des   services  publics   dans  la  gestion   de  leurs 
                     ressources.  
           
    -     Le programme   de  transition  numérique,   comprend les axes suivants :  
                      
                -    L’administration   électronique   ; 
                -    La    simplification     de    la    numérisation     des   procédures     et    des    parcours 
                     administratifs   ; 
                -    L’offshoring   ; 
                -    Les entreprises  œuvrant   dans les domaines  de  la transformation   numérique   ; 
                -    La numérisation   des entreprises  du  secteur  privé  ; 
                -    L’inclusion  numérique   ; 
                -    Le soutien  de l’encadrement,  de  la formation   et du  renforcement  des capacités  et 
                     des compétences. 
 
    -     Le programme   de  l’utilisation   de l’amazighe,  comprend  les axes suivants : 
 
                -    Le système  de l’éducation   et de  la formation   ; 
                -    La législation   et la réglementation    ; 
                -    L’information   et  la communication   ; 
                -    La créativité   culturelle  et  artistique  ; 
                -    Le recours  à la justice. 

 
                                                                                                                                                  99

106
                                                                              
   PROJET DE LOI DE FINANCES POUR L’ANNEE  2025 
  
  
 La répartition    des  dépenses,  ordonnancées,   par  projet   se présente   comme   suit  : 
                                                                                                                                                                                                          (En MDH) 

                                                                         Projets                                                                             2023 


   Dépenses liées au développement de l’économie numérique                                                            259,02 


   Versement au profit des institutions internationales                                                                               40 


   Dépenses liées à l’utilisation de l’Amazighe dans l’administration publique                                        20,25 


   Versement au profit des établissements publics pour contribuer aux dépenses liées à la promotion de 
                                                                                                                                                                 18,70 
   l’inclusion numérique 

   Versement au profit des collectivités territoriales pour contribuer aux dépenses liées à la promotion 
                                                                                                                                                                   15 
   de l’inclusion numérique 

   Versement au profit  des  institutions internationales afin  de  contribuer aux  dépenses liées au 
                                                                                                                                                                  3,70 
   développement de l’administration numérique 


   Réalisation d’opérations portant sur la modernisation des services publics                                         0,34 


                                                                          Total                                                                              357,01 

        
 Au   cours   de   l’année    2023,   ledit    Fonds    a  contribué     à   la  réalisation     des   projets    suivants, 
 repartis   par  programme     : 
        
   Le programme    de  modernisation     des  services  publics   : 
  
            Projet    complet      de   services     électroniques       pour    les   familles     des        : 0,34   MDH.
              détenus    et  les  relier   à l’environnement      carcéral    interne   pour   faciliter 
              la  réinsertion    des  détenus   » 
  
   Le programme    de  transition    numérique    : 
  

          Création    et   gestion     des   centres    de   programmation       et   de   codage 
                                                                                                                                                    : 15 MDH  ; 
             informatique     dans  la  région   de l’oriental    « Youcode    » 

          Financement     du  projet    d’équipement     de  l’établissement      universitaire 
             « Ecole   Nationale    de  l’Intelligence     Artificielle     et  de   la Numérisation     »      : 10 MDH  ; 
             à la ville   de  Berkane 

          Mise  en  œuvre   de  la  phase  pilote    du  projet    «JobInTech»    au  profit   de 
                                                                                                                                                     : 8,70  MDH ; 
             la Caisse  de  Dépôts   et  de  Gestion   (CDG) 

          Numérisation       du    Centre      Culturel     Marocain      Bayt     Al-Maghrib       à  
             AL  QODS   et  sa  liaison    avec  les   services   décentralisés     de  l’AGENCE         : 3,70  MDH. 
             BAYT  MAL  AL  QODS   ACHARIF 


  
            100 

107
                                                                                RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
  
  
  Le programme  de  l’utilisation   de l’amazighe  : 
  

         Programme   des Nations  Unies  pour  le  Développement   (PNUD)  pour 
           contribuer     à   la  mise   en   œuvre    et   au  pilotage    du   chantier    de      : 40 MDH ; 
           l’utilisation   de  l’amazighe 

         Mise en  œuvre  du  caractère  officiel   de la  langue  amazighe  dans  son 
                                                                                                                                        : 20 MDH ; 
           volet  culturel 

         Mise en  place d’une  plateforme   pour   l’apprentissage   de l’amazighe  à 
                                                                                                                                         : 0,25 MDH. 
           distance   au profit  des étudiantes   et étudiants                                                                   
                                                                  
                                                                  
                                                                  
                                         ANNEXES 
 
 
 
        SITUATION   DES RECETTES  ET DES DEPENSES DES  COMPTES 
     D’AFFECTATION    SPECIALE  PAR  DOMAINE  D’INTERVENTION    AU 
                                  TITRE  DE LA  PERIODE  2021-2023 
          
                                                                       
 
 
 

110
 

111
                                                                                                                                                                                         RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
        

                             SITUATION   DES RECETTES ET  DES DEPENSES DES COMPTES  D'AFFECTATION    SPECIALE  PAR DOMAINE   D'INTERVENTION  
                                                                                                             AU TITRE  DE LA  PERIODE  2021-2023 


                                                                                                                                                                                                                                                                                       


I- DOMAINE DU DEVELOPPEMENT TERRITORIAL  
                                                                                                                                                                                                                                                                                       


                                                                                                                                  RECETTES (En MDH)                                                   DEPENSES (En MDH) 
                                                                                                                                                                                           TAUX                                                                             TAUX 
                                    INTITULE DU COMPTE 
                                                                                                                                                                                         MOYEN                                                                          MOYEN 
                                                                                                                         2021               2022              2023                                     2021               2022            2023 



Parts des collectivités  territoriales  dans le produit  de la T.V.A                 38.222,03       47.008,37      54.214,45        19,10%         28.428,91      32.020,26     33.346,79       8,30% 


Fonds spécial relatif au produit  des parts  d'impôts  affectées aux 
                                                                                                                     10.808,13       10.720,32      10.426,88        -1,78%          9.093,68         9.293,45       8.793,53       -1,66% 
régions 


Fonds de solidarité Interrégionale                                                                 2.338,38         3.329,22       4.324,89         36,00%             3,28                 4,32         1.009,09      1653,49% 



Fonds de mise à niveau sociale                                                                      39,00              49,00             59,00           23,00%             0,00                0,00              0,00           0,00% 



                                                TOTAL_I                                                      51.407,54        61.106,91     69.025,22        15,88%         37.525,87       41.318,03    43.149,40       7,23% 



                                           Evolution  /  an                                                    21,83%           18,87%          12,96%              -                  11,14%           10,11%        4,43%              - 

        
                                                           

        
                                                                                                                                                                                                                                                                              105 
                                                                                                                                                                                                                                                           

112
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025                            
      

     II- DOMAINE DU DEVELOPPEMENT HUMAIN ET SOCIAL  
                                                                                                                                                                                                                                                                             

                                   INTITULE DU COMPTE                                                RECETTES (En MDH)                    TAUX                   DEPENSES (En MDH)                    TAUX 
                                                                                                                                                                                MOYEN                                                                         MOYEN 
                                                                                                                2021               2022               2023                                 2021             2022             2023 
     Fonds de soutien à l'initiative  nationale  pour le 
                                                                                                             9.437,01         10.381,24       10.163,55       3,78%       3.344,34        4.730,78        4.316,93          13,61% 
     développement  humain 
     Fonds de soutien aux services de la concurrence, du 
     contrôle, de la protection   du consommateur, de la                          15,33              15,33              15,33          0,00%            0,00              0,00               5,96                  - 
     régulation  du marché et des stocks de sécurité 
     Fonds d'entraide  familiale                                                              1.203,54          1.289,53         1.351,79        5,98%          110,01          130,00        1.050,06         208,95% 
     Fonds de soutien à l'action  culturelle  et sociale au profit 
     des marocains résidants à l'étranger  et des affaires de la               38,89               35,18             49,73          13,09%          28,71             10,45            24,19            -8,22% 
     migration 
     Fonds spécial pour la promotion  et  le soutien de la 
                                                                                                               275,44           250,65             351,45         12,96%         217,71          145,98          158,66           -14,63% 
     protection  civile 
     Financement des dépenses d'équipement  et  de la lutte 
                                                                                                             2.624,53          2.882,11        3.223,58        10,83%       1.887,53        2.018,23      2.000,61           2,95% 
     contre le chômage 
     Fonds spécial pour la promotion  du  système d’éducation  et 
                                                                                                              256,00             344,10            299,10         8,09%            0,00             45,00             0,00                   - 
     de formation  et l’amélioration  de sa qualité 
     Fonds spécial de la pharmacie centrale                                         4.499,99          4.049,15        4.062,44        -4,99%        2.945,64       2.574,20        1.710,76         -23,79% 
     Fonds spécial du produit  des loteries                                              286,15            381,38            488,89         30,71%         27,20              35,16            32,11            8,64% 
     Fonds de soutien des prix  de certains produits  alimentaires         524,94             601,55           764,60         20,69%         300,84           301,00          301,00            0,03% 
     Fonds d'appui à la protection   sociale et à la cohésion 
                                                                                                             10.690,31       14.463,11      23.603,20      48,59%        5.513,61       6.638,30       13.544,55        56,73% 
     sociale 
     Fonds spécial pour la gestion  de la pandémie du 
                                                                                                              12.111,35       5.917,82        3.357,59       -47,35%      10.928,35      2.966,33        1.075,19        -68,63% 
     Coronavirus "Le Covid-19" 
     Fonds spécial pour la gestion  des effets du tremblement  de 
                                                                                                                0,00                0,00             19.709,12           -                0,00              0,00           2.387,68               - 
     terre ayant touché  le Royaume du Maroc 

     Fonds national pour  l'action culturelle                                             894,59            1.210,73        1.289,08       20,04%         272,67           610,87         769,34            67,97% 

     Fonds solidarité pour  le soutien au logement,  d'habitat  et 
                                                                                                              7.195,56        7.010,88          6.277,17       -6,60%        2.399,12       2.912,39       2.644,88           5,00% 
     intégration  urbaine 

                                             TOTAL _II                                              50.053,64       48.832,76       75.006,62       22,41%      27.975,73      23.118,69     30.021,91         3,59% 

                                          Evolution  /  an                                            -24,10%          -2,44%           53,60%              -             -35,46%         -17,36%        29,86%               - 

                                  
             106 
      

113
                                                                                                                                                                                  RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 

 III-  DOMAINE DE LA PROMOTION ECONOMIQUE ET FINANCIERE  
                                                                                                                                                                                                                                                                         

                                                                                                                 RECETTES (En MDH)                                                     DEPENSES (En MDH) 
                                                                                                                                                                           TAUX                                                                              TAUX 
                            INTITULE DU COMPTE 
                                                                                                                                                                          MOYEN                                                                          MOYEN 
                                                                                                       2021                2022               2023                                   2021               2022              2023 

 Fonds pour la promotion   de l'emploi  des jeunes                      744,34            2.563,30        2.809,95         94,30%          639,30           2.281,36        1.578,65        57,14% 

 Fonds de promotion  des investissements                                 2.798,56          2.677,17          1.728,81       -21,40%        1.701,39         2.301,36         876,05         -28,24% 

 Masse des services financiers                                                   7.385,49          7.849,35         8.302,21          6,02%          970,73           1.089,58         1.199,64         11,17% 

 Bénéfices et pertes  de conversion sur les dépenses 
                                                                                                      82,00                76,72              46,93          -24,35%           14,09             48,43              10,36          -14,24% 
 publiques  en devises étrangères 

 Fonds de solidarité  des assurances                                          9.436,13          8.132,91         7.936,85         -8,29%        2.000,00         1.000,00        4.500,00        50,00% 

 Fonds de gestion  des risques afférents aux emprunts 
                                                                                                    4.265,36          4.404,42         4.505,15          2,77%             5,16                2,69                1,51          -45,93% 
 des tiers garantis  par l'Etat 

 Compte spécial  des dons des pays du Conseil de 
                                                                                                   12.068,85         11.237,40       11.565,02        -2,11%         1.211,23         456,26            828,14          -17,31% 
 Coopération  du Golfe 

 Fonds de lutte  contre la fraude  douanière                               3.042,36          3.006,25          3.164,99         2,00%           995,91            942,26          1.154,94         7,69% 

 Fonds provenant  des dépôts au Trésor                                     767,43              733,27            786,72           1,25%           741,21            724,26           748,54          0,49% 

 Fonds d'appui  au financement de l'entreprenariat                    4.268,84          6.075,92         5.503,42         13,54%         880,00           1.202,70         2.226,19       59,05% 


                                     TOTAL _ III                                           44.859,37        46.756,72       46.350,04          1,65%         9.159,02       10.048,89       13.124,03       19,70% 


                                   Evolution  /  an                                          -25,84%            4,23%            -0,87%               -               -61,42%           9,72%           30,60%              - 

 
 
 

 
                                                                                                                                                                                                                                                                       107 
                                                                                                                                                                                                                                                    

114
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025                            
      

        IV- DOMAINE  DE L'INFRASTRUCTURE  
                                                                                                                                                                                                                                                                          

                                                                                                                           RECETTES (En MDH)                                             DEPENSES (En MDH) 
                                                                                                                                                                                TAUX                                                                          TAUX 
                                       INTITULE DU COMPTE 
                                                                                                                                                                               MOYEN                                                                      MOYEN 
                                                                                                                   2021             2022             2023                                2021            2022            2023 


        Fonds d'accompagnement  des réformes du  transport 
                                                                                                                3.996,74       4.883,82       4.932,32        11,09%       913,43        2.152,86       1.338,74          21,06% 
        routier  urbain et interurbain 


         Fonds de service universel de  télécommunications                     4.409,00       4.405,44        4.152,60       -2,95%        424,85         676,03          384,38            -4,88% 


        Fonds d'assainissement liquide  et solide et d'épuration   des 
                                                                                                                 1.241,17       1.594,60      2.041,07       28,24%        646,57        1.053,53        203,80           -43,86% 
        eaux usées et leur réutilisation 


        Fonds de lutte  contre les effets  des catastrophes naturelles        1.583,27       2.659,32       3.552,79       49,80%        614,56        1.551,93       1.541,36         58,37% 


        Fonds spécial routier                                                                       6.130,64       6.676,72       6.935,15        6,36%       2.984,51      3.392,22       3.197,86            3,51% 


        Fonds de délimitation,  de préservation  et de  valorisation du 
                                                                                                                  175,85          174,98          165,76         -2,91%         23,38           20,16            13,19            -24,88% 
        domaine public  maritime  et portuaire 


        Fonds national de  développement  du sport                                  2.892,60       3.422,34       6.392,23       48,66%       1.610,22       1.611,93      4.137,92          60,31% 


        Fonds national pour  la protection   de l'environnement  et  du 
                                                                                                                 1.505,38       1.791,93       2.015,72      15,72%        212,08          52,34           228,82             3,87% 
        développement  durable 


        Fonds de développement  énergétique                                           1.216,33       1.170,99        826,26        -17,58%         51,11         350,50          443,00           194,42% 


                                                 TOTAL _V                                             23.150,98     26.780,14      31.013,89     15,74%      7.480,71      10.861,50     11.489,06        23,93% 


                                             Evolution  /  an                                             11,25%         15,68%         15,81%            -             -5,08%         45,19%          5,78%                 - 

      

                                  
             108 
      

115
                                                                                                                                                                                  RAPPORT SUR LES COMPTES SPECIAUX DU TRESOR 
 

V-  DOMAINE DE DEVELOPPEMENT RURAL, AGRICOLE ET DE LA PECHE 
                                                                                                                                                                                                                                                                      


                                                                                                               RECETTES (En MDH)                                                    DEPENSES (En MDH) 
                                                                                                                                                                        TAUX                                                                               TAUX 
                            INTITULE DU COMPTE 
                                                                                                                                                                       MOYEN                                                                           MOYEN 
                                                                                                      2021              2022               2023                                  2021            2022               2023 


Fonds spécial des prélèvements  sur le pari mutuel                   966,73          1.027,69         1.082,98          5,84%          215,52        227,56             194,32             -5,05% 


Fonds de la réforme  agraire                                                       746,17           746,03            748,40            0,15%           0,45             0,06                0,00              -100,00% 


Fonds de développement   agricole                                          5.038,02         5.808,32         6.449,69          13,15%      4.487,38      4.684,91         4.544,05             0,63% 


Fonds de développement   de la pêche maritime                       275,39            313,65            264,51           -1,99%         30,85           111,32            80,42               61,47% 


Fonds de développement   rural et des zones de 
                                                                                                   6.178,49         5.572,01        6.986,05          6,33%        2.637,59      2.165,09          2.191,52            -8,85% 
montagne 


Fonds national  forestier                                                            2.408,27         2.507,04         2.826,94         8,34%          913,84         671,78            500,10             -26,02% 


Fonds de la chasse et de la pêche continentale                         312,24            335,18           359,84            7,35%          23,92            21,19             30,00                11,98% 


                                     TOTAL _IV                                           15.925,32       16.309,91       18.718,43        8,42%        8.309,56      7.881,89         7.540,41            -4,74% 


                                  Evolution  /  an                                          -3,91%             2,41%           14,77%               -               1,03%         -5,15%           -4,33%                   - 

 
 
 
 
 
 
 
                                                                                                                                                                                                                                                                       109 
                                                                                                                                                                                                                                                    

116
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025                            
      
      
        VI- AUTRES  DOMAINES  

                                                                                                                    RECETTES (En MDH)                       TAUX                      DEPENSES (En MDH)                   TAUX 
                                INTITULE DU COMPTE 
                                                                                                                                                                              MOYEN                                                                          MOYEN 
                                                                                                          2021                 2022               2023                                    2021              2022               2023 

        Fonds spécial pour le soutien  des juridictions                      2.046,23           2.040,28          2.008,01         -0,94%          705,00            737,52            710,05         0,36% 

        Fonds de soutien à la sûreté nationale                                  2.015,37            2.231,45        2.539,30          12,25%         289,96            245,17           428,18          21,52% 

        Fonds spécial pour la mise en place des titres 
                                                                                                        1.841,51           1.994,37        2.335,43          12,62%         538,95            345,27           284,49         -27,35% 
        identitaires  électroniques et  des titres de voyage 
        Fonds national de soutien  à la recherche scientifique 
                                                                                                         599,71              564,97            483,91          -10,17%         130,25            157,84           100,64         -12,10% 
        et au développement  technologique 

        Fonds de remploi  domanial                                                  32.263,92         53.595,29        61.817,78       38,42%        5.415,56        18.947,08      26.402,78      120,80% 

        Fonds pour la promotion  du  paysage audiovisuel et 
                                                                                                         918,79              749,49            713,48          -11,88%          571,31           401,95           507,54         -5,75% 
        des annonces et de l'édition  publique 
        Fonds de modernisation  de l'administration 
        publique, d'appui  à la transition  numérique et à                    107,83              307,74           1.414,78        262,22%          0,08               72,47            357,00        6419,25% 
        l'utilisation  de l'amazighe 
        Fonds de participation  des Forces Armées Royales  
        aux missions de paix, aux actions humanitaires et  de          1.864,75            2.151,42        2.507,58         15,96%          179,20            147,78          1.228,87       161,87% 
        soutien au titre  de la coopération  internationale 

        Fonds de soutien à la gendarmerie  royale                             632,82               885,22           1.188,99        37,07%           59,91              52,52             71,59           9,31% 
        Fond spécial pour le  soutien de l’administration  et
                                                                                                       1.049,33            1.258,61         1.140,43         4,25%           599,83            883,66           775,94          13,74% 
        des établissements pénitentiaires 

                                          TOTAL _VI                                         43.340,26          65.778,84       76.149,70        32,55%        8.490,06         21.991,25     30.867,08       90,67% 

                                       Evolution  /  an                                          8,22%               51,77%           15,77%              -               -39,72%         159,02%         40,36%             - 

                 TOTAL GENERAL DES RECETTES ET DES 
               DEPENSES DES COMPTES D'AFFECTATION          228.737,09       265.565,28     316.263,90       17,59%       98.940,95       115.220,24    136.191,89     17,32% 
                                           SPECIALE 

                                       Evolution  /  an                                         -7, 04%              16,10%          19,09%               -              -24,49%           16,45%           18,20               - 

      
                                  
              110 
      

117
 


    
    
"""
    conversation_history = StreamlitChatMessageHistory()  # Créez l'instance pour l'historique

    st.header("PLF2025: Explorez le rapport sur les comptes speciaux du trésor à travers notre chatbot 💬")
    
    # Load the document
    #docx = 'PLF2025-Rapport-FoncierPublic_Fr.docx'
    
    #if docx is not None:
        # Lire le texte du document
        #text = docx2txt.process(docx)
        #with open("so.txt", "w", encoding="utf-8") as fichier:
            #fichier.write(text)

        # Afficher toujours la barre de saisie
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)
    selected_questions = st.sidebar.radio("****Choisir :****", questions)
        # Afficher toujours la barre de saisie
    query_input = st.text_input("", key="text_input_query", placeholder="Posez votre question ici...", help="Posez votre question ici...")
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)

    if query_input and query_input not in st.session_state.previous_question:
        query = query_input
        st.session_state.previous_question.append(query_input)
    elif selected_questions:
        query = selected_questions
    else:
        query = ""

    if query :
        st.session_state.conversation_history.add_user_message(query) 
        if "Donnez-moi un résumé du rapport" in query:
            summary="""Le rapport sur les Comptes Spéciaux du Trésor (CST) pour le Projet de Loi de Finances 2025 analyse leur rôle dans la gestion budgétaire, leur impact sur le développement social et économique, ainsi que leur contribution aux politiques d’urgence, comme pour la pandémie de Covid-19 et le séisme d’Al Haouz. Ce document détaille l’évolution des ressources et des dépenses des CST, les recettes mobilisées, et leur affectation par domaine : protection sociale, justice spatiale, investissement, et transition numérique. En 2023, les recettes ont atteint 316,26 milliards de dirhams, dont une grande partie a été affectée à des fonds sociaux, régionaux et de soutien aux infrastructures, en ligne avec les objectifs du nouveau modèle de l’État social."""
            st.session_state.conversation_history.add_ai_message(summary) 

        else:
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"{query}. Répondre à la question d'apeés ce texte repondre justement à partir de texte ne donne pas des autre information voila le texte donnee des réponse significatif et bien formé essayer de ne pas dire que information nest pas mentionné dans le texte si tu ne trouve pas essayer de repondre dapres votre connaissance ms focaliser sur ce texte en premier: {text} "
                    )
                }
            ]

            # Appeler l'API OpenAI pour obtenir le résumé
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # Récupérer le contenu de la réponse

            summary = response['choices'][0]['message']['content']
           
                # Votre logique pour traiter les réponses
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(response)
            st.session_state.conversation_history.add_ai_message(summary)  # Ajouter à l'historique
            
            # Afficher la question et le résumé de l'assistant
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(summary)

            # Format et afficher les messages comme précédemment
                
            # Format et afficher les messages comme précédemment
        formatted_messages = []
        previous_role = None 
        if st.session_state.conversation_history.messages: # Variable pour stocker le rôle du message précédent
                for msg in conversation_history.messages:
                    role = "user" if msg.type == "human" else "assistant"
                    avatar = "🧑" if role == "user" else "🤖"
                    css_class = "user-message" if role == "user" else "assistant-message"

                    if role == "user" and previous_role == "assistant":
                        message_div = f'<div class="{css_class}" style="margin-top: 25px;">{msg.content}</div>'
                    else:
                        message_div = f'<div class="{css_class}">{msg.content}</div>'

                    avatar_div = f'<div class="avatar">{avatar}</div>'
                
                    if role == "user":
                        formatted_message = f'<div class="message-container user"><div class="message-avatar">{avatar_div}</div><div class="message-content">{message_div}</div></div>'
                    else:
                        formatted_message = f'<div class="message-container assistant"><div class="message-content">{message_div}</div><div class="message-avatar">{avatar_div}</div></div>'
                
                    formatted_messages.append(formatted_message)
                    previous_role = role  # Mettre à jour le rôle du message précédent

                messages_html = "\n".join(formatted_messages)
                st.markdown(messages_html, unsafe_allow_html=True)
if __name__ == '__main__':
    main()
