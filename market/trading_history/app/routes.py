from flask import Blueprint, jsonify, request, current_app
from .models import db,AuctionTransactions,UserTransactionHistory
from datetime import datetime
import requests

trading_history = Blueprint('trading_history', __name__)

def dbm_url(path):
    return current_app.config['DBM_URL'] + path

# Endpoint: GET /market/transaction_history
@trading_history.route('/market/transaction_history', methods=['GET'])
def get_transaction_history():
    user_id = request.args.get("user_id")

    # Valida user_id
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid User ID format"}), 400

    transaction_history = UserTransactionHistory.query.filter_by(user_id=user_id).all()
    if not transaction_history:
        return jsonify({"transactions": [], "message": "No transactions found for this user"}), 200

    result = [
        {
            "auction_id": t.auction_id,
            "transaction_type": t.transaction_type,
            "amount": t.amount,
            "transaction_time": t.transaction_time
        }
        for t in transaction_history
    ]

    return jsonify({"transactions": result}), 200

# Endpoint POST /market/transaction
@trading_history.route('/market/transaction', methods=['POST'])
def record_transaction():
    data = request.get_json()
    auction_id = data.get('auction_id')
    buyer_id = data.get('buyer_id')
    seller_id = data.get('seller_id')
    final_price = data.get('final_price')

    if not all([auction_id, buyer_id, seller_id, final_price]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        auction_id = int(auction_id)
        buyer_id = int(buyer_id)
        seller_id = int(seller_id)
        final_price = int(final_price)
        if final_price <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid input format or negative price"}), 400

    try:
        # Chiamata al db-manager per registrare la transazione
        response = requests.post(dbm_url("/market/transaction"), json={
            "auction_id": auction_id,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "final_price": final_price
        })

        if response.status_code != 200:
            return jsonify({"error": response.json().get("error", "Unknown error")}), response.status_code

        result = response.json()
        if not result["success"]:
            return jsonify({"error": result["message"]}), 500

        return jsonify({"message": "Transaction recorded successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Transaction failed: {str(e)}"}), 500

# Endpoint POST /market/refund
@trading_history.route('/market/refund', methods=['POST'])
def process_refund():
    data = request.get_json()
    user_id = data.get("user_id")
    auction_id = data.get("auction_id")
    amount = data.get("amount")

    if not all([user_id, auction_id, amount]):
        return jsonify({"error": "Invalid data"}), 400
    
    try:
        user_id = int(user_id)
        auction_id = int(auction_id)
        amount = int(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid input format or negative amount"}), 400

    try:
        refund_transaction = UserTransactionHistory(
            user_id=user_id,
            auction_id=auction_id,
            transaction_type="refund",
            amount=amount
        )
        db.session.add(refund_transaction)
        db.session.commit()

        return jsonify({"message": "Refund processed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Refund failed: {str(e)}"}), 500