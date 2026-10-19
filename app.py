
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="Atelier PVC Pro",
    page_icon="🪟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prototype : stockage JSON local
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CLIENTS_FILE = DATA_DIR / "clients.json"
QUOTES_FILE = DATA_DIR / "devis.json"


def charger_json(fichier):
    if not fichier.exists():
        return []
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            donnees = json.load(f)
        return donnees if isinstance(donnees, list) else []
    except (json.JSONDecodeError, OSError):
        st.error(
            f"Impossible de lire {fichier.name}. "
            "Ne remplace pas le fichier avant d'avoir vérifié les données."
        )
        return []


def sauvegarder_json(fichier, donnees):
    temporaire = fichier.with_suffix(".tmp")
    with open(temporaire, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)
    temporaire.replace(fichier)


clients = charger_json(CLIENTS_FILE)
devis = charger_json(QUOTES_FILE)

st.sidebar.title("🪟 Atelier PVC Pro")
st.sidebar.caption("Gestion commerciale et fabrication")
page = st.sidebar.radio(
    "Navigation",
    [
        "Tableau de bord",
        "Clients",
        "Devis",
        "Catalogue PVC",
        "Vitrages",
        "Accessoires",
        "Fabrication",
        "Paramètres"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Version initiale — prototype")


if page == "Tableau de bord":
    st.title("Tableau de bord")
    st.write("Bienvenue dans ton application de menuiserie PVC.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Clients", len(clients))
    c2.metric("Devis enregistrés", len(devis))
    c3.metric(
        "Montant des devis",
        f"{sum(float(d.get('total', 0)) for d in devis):,.2f} DA"
    )

    st.subheader("Derniers devis")
    if devis:
        st.dataframe(pd.DataFrame(devis), use_container_width=True)
    else:
        st.info("Aucun devis enregistré pour le moment.")


elif page == "Clients":
    st.title("Gestion des clients")

    with st.form("form_client", clear_on_submit=True):
        nom = st.text_input("Nom du client *")
        telephone = st.text_input("Téléphone")
        email = st.text_input("E-mail")
        adresse = st.text_area("Adresse")
        ajouter = st.form_submit_button("Enregistrer le client")

        if ajouter:
            if not nom.strip():
                st.error("Le nom du client est obligatoire.")
            else:
                clients.append({
                    "id": len(clients) + 1,
                    "nom": nom.strip(),
                    "telephone": telephone.strip(),
                    "email": email.strip(),
                    "adresse": adresse.strip(),
                    "date_creation": date.today().isoformat()
                })
                sauvegarder_json(CLIENTS_FILE, clients)
                st.success("Client enregistré.")
                st.rerun()

    st.subheader("Liste des clients")
    recherche = st.text_input("Rechercher un client")
    filtres = [
        c for c in clients
        if recherche.lower() in c.get("nom", "").lower()
        or recherche.lower() in c.get("telephone", "").lower()
    ]

    if filtres:
        st.dataframe(pd.DataFrame(filtres), use_container_width=True)
    else:
        st.info("Aucun client correspondant.")


elif page == "Devis":
    st.title("Gestion des devis")

    if not clients:
        st.warning("Commence par enregistrer un client.")
    else:
        with st.form("form_devis", clear_on_submit=True):
            client_noms = [c["nom"] for c in clients]
            client = st.selectbox("Client", client_noms)
            description = st.text_input(
                "Description de la menuiserie",
                placeholder="Ex. : fenêtre PVC deux vantaux"
            )
            quantite = st.number_input(
                "Quantité", min_value=1, value=1, step=1
            )
            prix_unitaire = st.number_input(
                "Prix de vente unitaire (DA)",
                min_value=0.0, value=0.0, step=100.0
            )
            date_devis = st.date_input("Date du devis", value=date.today())
            enregistrer = st.form_submit_button("Enregistrer le devis")

            if enregistrer:
                if not description.strip() or prix_unitaire <= 0:
                    st.error(
                        "Indique une description et un prix de vente valide."
                    )
                else:
                    devis.append({
                        "numero": f"DEV-{date.today().year}-{len(devis)+1:04d}",
                        "client": client,
                        "description": description.strip(),
                        "quantite": int(quantite),
                        "prix_unitaire": float(prix_unitaire),
                        "total": float(quantite * prix_unitaire),
                        "date": date_devis.isoformat(),
                        "statut": "Brouillon"
                    })
                    sauvegarder_json(QUOTES_FILE, devis)
                    st.success("Devis enregistré.")
                    st.rerun()

    st.subheader("Historique des devis")
    if devis:
        st.dataframe(pd.DataFrame(devis), use_container_width=True)
    else:
        st.info("Aucun devis enregistré.")


elif page == "Catalogue PVC":
    st.title("Catalogue des profils PVC")
    st.info(
        "Ce module accueillera les systèmes PVC, références de profils, "
        "longueurs commerciales, prix au mètre et règles de découpe."
    )


elif page == "Vitrages":
    st.title("Catalogue des vitrages")
    st.info(
        "Ce module accueillera les références de vitrage, prix au m², "
        "dimensions des vitres et calcul des surfaces."
    )


elif page == "Accessoires":
    st.title("Catalogue des accessoires")
    st.info(
        "Ce module accueillera les poignées, paumelles, serrures, "
        "crémones, roulettes et autres accessoires."
    )


elif page == "Fabrication":
    st.title("Dossier de fabrication")
    st.info(
        "Nous ajouterons ici les plans, listes de coupe, angles, "
        "calculs des barres et besoins en matériaux."
    )


elif page == "Paramètres":
    st.title("Paramètres")
    st.info(
        "Les coordonnées de l'entreprise, la numérotation, "
        "les conditions de paiement et les sauvegardes seront configurées ici."
    )

st.divider()
st.caption("Atelier PVC Pro — prototype de développement")
