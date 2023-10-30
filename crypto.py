import argparse
import requests
import sqlite3

def get_bitcoin_price():
    url = f'https://rest.coinapi.io/v1/exchangerate/BTC/USD'
    headers = {'X-CoinAPI-Key': '53A77F27-DB93-4117-9FBC-E4AF9E158289'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        price = data['rate']
        return price
    else:
        print("Erreur lors de la récupération des données de prix de Bitcoin depuis CoinAPI.")
        return None

def create_alert(cryptocurrency, price_threshold):
    conn = sqlite3.connect('crypto_alerts.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO alerts (cryptocurrency, price_threshold) VALUES (?, ?)",
                   (cryptocurrency, price_threshold))

    conn.commit()
    conn.close()
    print("Alerte créée avec succès.")

def list_alerts(cryptocurrency):
    conn = sqlite3.connect('crypto_alerts.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts WHERE cryptocurrency = ?", (cryptocurrency,))
    alerts = cursor.fetchall()

    conn.close()

    if not alerts:
        print("Aucune alerte trouvée pour", cryptocurrency)
    else:
        print(f"Liste des alertes pour {cryptocurrency}:")
        for alert in alerts:
            print(f"ID: {alert[0]}, Seuil de prix: {alert[2]}")

def update_alert(alert_id, price_threshold):
    conn = sqlite3.connect('crypto_alerts.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE alerts SET price_threshold = ? WHERE id = ?",
                   (price_threshold, alert_id))

    conn.commit()
    conn.close()
    print(f"Alerte {alert_id} mise à jour avec succès.")

def delete_alert(alert_id):
    conn = sqlite3.connect('crypto_alerts.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))

    conn.commit()
    conn.close()
    print(f"Alerte {alert_id} supprimée avec succès.")

def check_alerts():
    conn = sqlite3.connect('crypto_alerts.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts")
    alerts = cursor.fetchall()

    current_price = get_bitcoin_price()

    for alert in alerts:
        alert_id, cryptocurrency, price_threshold = alert
        if cryptocurrency == 'BTC':
            if current_price <= price_threshold:
                print(f"Alerte pour BTC : Prix en dessous de {price_threshold}")

    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Application de gestion d'alertes de crypto-monnaies")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Créer une nouvelle alerte")
    create_parser.add_argument("cryptocurrency", type=str, help="Symbole de la crypto-monnaie")
    create_parser.add_argument("price_threshold", type=float, help="Seuil de prix de l'alerte")

    list_parser = subparsers.add_parser("list", help="Lister toutes les alertes pour une crypto-monnaie")
    list_parser.add_argument("cryptocurrency", type=str, help="Symbole de la crypto-monnaie")

    update_parser = subparsers.add_parser("update", help="Mettre à jour une alerte existante")
    update_parser.add_argument("alert_id", type=int, help="ID de l'alerte à mettre à jour")
    update_parser.add_argument("--price-threshold", type=float, help="Nouveau seuil de prix de l'alerte")

    delete_parser = subparsers.add_parser("delete", help="Supprimer une alerte")
    delete_parser.add_argument("alert_id", type=int, help="ID de l'alerte à supprimer")

    args = parser.parse_args()

    if args.command == "create":
        create_alert(args.cryptocurrency, args.price_threshold)
    elif args.command == "list":
        list_alerts(args.cryptocurrency)
    elif args.command == "update":
        update_alert(args.alert_id, args.price_threshold)
    elif args.command == "delete":
        delete_alert(args.alert_id)
    elif args.command is None:
        check_alerts()