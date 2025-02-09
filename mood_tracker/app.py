from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import hashlib
import time

# Blockchain class to manage blockchain functionalities
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='1')  # Create the genesis block

    def create_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'moods': self.transactions,  # Save the moods in the block
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
        }
        self.transactions = []  # Clear the transaction list after the block is created
        self.chain.append(block)  # Add the block to the blockchain
        return block

    def hash(self, block):
        block_string = str(block).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 1
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    def add_mode(self, mood, note):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.append({"mood": mood, "note": note, "timestamp": timestamp})

# Initialize Flask app and Blockchain
app = Flask(__name__)
blockchain = Blockchain()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the mood and note from the form
        mood = request.form.get("mood")
        note = request.form.get("note")
        
        if mood:
            # Add mood to the blockchain (transactions list)
            blockchain.add_mode(mood, note)

            # Get last proof and mine a new block
            last_block = blockchain.chain[-1]
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)
            previous_hash = blockchain.hash(last_block)

            # Create new block with the mined proof and add it to the blockchain
            blockchain.create_block(proof, previous_hash)

        return redirect(url_for("index"))

    # Render template with the mood data
    return render_template("index.html", moods=blockchain.transactions, blockchain=blockchain.chain)

if __name__ == "__main__":
    app.run(debug=True)