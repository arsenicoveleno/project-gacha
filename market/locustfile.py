from locust import HttpUser, task, between, tag
import random
import datetime


class AuctionCreatorUser(HttpUser):
    #Utente che si occupa di creare aste usando POST /market.
    wait_time = between(1, 3)  # Tempo casuale tra le richieste

    @task
    def create_auction(self):
        gacha_id = random.randint(1000, 9999)  # ID casuale per il gacha
        seller_id = random.randint(1, 100)  # ID casuale del venditore
        starting_price = random.randint(10, 100)  # Prezzo iniziale casuale
        auction_end = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).isoformat()

        payload = {
            "gacha_id": gacha_id,
            "seller_id": seller_id,
            "starting_price": starting_price,
            "auction_end": auction_end
        }

        self.client.post("/auction_market/market", json=payload)


class AuctionBidderUser(HttpUser):
    
    #Utente che piazza offerte sulle aste già create usando POST /market/bid.
    
    wait_time = between(1, 2)

    @task
    def place_bid(self):
        auction_id = random.randint(1, 100)  # ID casuale dell'asta
        bidder_id = random.randint(1, 1000)  # ID casuale dell'offerente
        bid_amount = random.randint(50, 500)  # Importo casuale dell'offerta

        payload = {
            "auction_id": auction_id,
            "bidder_id": bidder_id,
            "bid_amount": bid_amount
        }

        self.client.post("/auction_market/market/bid", json=payload)


class RealisticUser(HttpUser):
    #Utente con comportamento realistico:
    #- Ottiene tutte le aste attive
    #- Crea una nuova asta
    #- Controlla lo storico delle transazioni
    #- Piazza un'offerta su un'asta attiva
    #- Ricontrolla lo storico delle transazioni
    wait_time = between(2, 5)

    @task
    @tag("realistic_flow")
    def realistic_flow(self):
        # Ottieni tutte le aste attive
        response = self.client.get("/auction_market/market")
        if response.status_code == 200:
            active_auctions = response.json()
        else:
            active_auctions = []

        # Crea una nuova asta
        gacha_id = random.randint(1000, 9999)
        seller_id = random.randint(1, 100)
        starting_price = random.randint(10, 100)
        auction_end = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).isoformat()
        self.client.post("/auction_market/market", json={
            "gacha_id": gacha_id,
            "seller_id": seller_id,
            "starting_price": starting_price,
            "auction_end": auction_end
        })

        # Controlla lo storico delle transazioni
        user_id = seller_id
        self.client.get(f"/market/transaction_history?user_id={user_id}")

        # Piazza un'offerta su un'asta attiva (se ce ne sono)
        if active_auctions:
            auction = random.choice(active_auctions)  # Scegli un'asta attiva
            bid_amount = auction['current_price'] + random.randint(1, 50)
            bidder_id = user_id
            self.client.post("/market/bid", json={
                "auction_id": auction['id'],
                "bidder_id": bidder_id,
                "bid_amount": bid_amount
            })

        # Ricontrolla lo storico delle transazioni
        self.client.get(f"/market/transaction_history?user_id={user_id}")
