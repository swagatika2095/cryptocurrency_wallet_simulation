import hashlib
import json
import time
from flask import Flask, render_template, request, jsonify
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

app = Flask(__name__)

# --- CRYPTOGRAPHY & WALLET ENGINE ---

class Wallet:
    def __init__(self):
        self.sk = SigningKey.generate(curve=SECP256k1, hashfunc=hashlib.sha256)
        self.vk = self.sk.verifying_key
        self.private_key_hex = self.sk.to_string().hex()
        self.public_key_hex = self.vk.to_string().hex()
        self.address = hashlib.sha256(self.vk.to_string()).hexdigest()[:32]

    def sign_transaction(self, recipient: str, amount: float) -> str:
        """Digitally sign transaction data with private key."""
        msg = f"{self.address}->{recipient}:{amount}".encode('utf-8')
        signature = self.sk.sign(msg)
        return signature.hex()

    @staticmethod
    def verify_signature(public_key_hex: str, sender: str, recipient: str, amount: float, signature_hex: str) -> bool:
        """Verify transaction signature using sender's public key."""
        try:
            vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1, hashfunc=hashlib.sha256)
            msg = f"{sender}->{recipient}:{amount}".encode('utf-8')
            return vk.verify(bytes.fromhex(signature_hex), msg)
        except (BadSignatureError, Exception):
            return False

# --- BLOCKCHAIN & PROOF OF WORK ENGINE ---

class Block:
    def __init__(self, index: int, transactions: list, previous_hash: str, nonce: int = 0, timestamp: float = None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = timestamp or time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "timestamp": self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, [{"sender": "GENESIS", "recipient": "SYSTEM", "amount": 0}], "0")
        genesis.hash = genesis.calculate_hash()
        self.chain.append(genesis)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float, pub_key: str, signature: str) -> tuple[bool, str]:
        # 1. System/Faucet bypasses signature verification
        if sender != "FAUCET":
            if not Wallet.verify_signature(pub_key, sender, recipient, amount, signature):
                return False, "Invalid Digital Signature! Transaction rejected."

            if self.get_balance(sender) < amount:
                return False, "Insufficient balance!"

        # 2. Append to mempool/pending transactions
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "signature": signature
        })
        return True, "Transaction validated and added to pending pool."

    def mine_pending_transactions(self, miner_address: str):
        """Proof of Work algorithm to mine pending transactions."""
        # Miner reward transaction
        reward_tx = {"sender": "MINING REWARD", "recipient": miner_address, "amount": 10, "signature": "SYSTEM_REWARD"}
        transactions_to_mine = [reward_tx] + self.pending_transactions

        new_block = Block(
            index=len(self.chain),
            transactions=transactions_to_mine,
            previous_hash=self.get_latest_block().hash
        )

        # Proof of work hash solver loop
        target = "0" * self.difficulty
        while not new_block.hash.startswith(target):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] == address:
                    balance -= tx["amount"]
                if tx["recipient"] == address:
                    balance += tx["amount"]
        return balance

    def is_chain_valid(self) -> tuple[bool, str]:
        """Validates hash links and block integrity."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Re-calculate current block hash
            if current.hash != current.calculate_hash():
                return False, f"Block #{current.index} hash is invalid! Data was tampered with."

            # Check chain link continuity
            if current.previous_hash != previous.hash:
                return False, f"Block #{current.index} previous_hash does not match Block #{previous.index} hash!"

        return True, "Blockchain is valid and intact."


# --- APP STATE & ROUTING ---

wallets = {}
blockchain = Blockchain(difficulty=3) # Low difficulty for quick demo mining

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/wallet/create", methods=["POST"])
def create_wallet():
    w = Wallet()
    wallets[w.address] = w
    return jsonify({
        "address": w.address,
        "public_key": w.public_key_hex,
        "private_key": w.private_key_hex
    })

@app.route("/api/faucet", methods=["POST"])
def faucet():
    data = request.json
    addr = data.get("address")
    if addr in wallets:
        blockchain.add_transaction("FAUCET", addr, 100.0, "", "FAUCET_SIG")
        return jsonify({"status": "success", "message": "100 SIM added to Pending Transactions!"})
    return jsonify({"status": "error", "message": "Wallet missing"}), 400

@app.route("/api/transaction/send", methods=["POST"])
def send_tx():
    data = request.json
    sender = data.get("sender")
    recipient = data.get("recipient")
    amount = float(data.get("amount", 0))

    if sender not in wallets:
        return jsonify({"status": "error", "message": "Sender wallet not found"}), 400

    wallet = wallets[sender]
    # Sign transaction cryptographically
    signature = wallet.sign_transaction(recipient, amount)

    success, msg = blockchain.add_transaction(
        sender=sender,
        recipient=recipient,
        amount=amount,
        pub_key=wallet.public_key_hex,
        signature=signature
    )
    return jsonify({"status": "success" if success else "error", "message": msg})

@app.route("/api/mine", methods=["POST"])
def mine():
    miner_address = request.json.get("miner_address")
    if not miner_address or miner_address not in wallets:
        return jsonify({"status": "error", "message": "Valid miner address required"}), 400

    block = blockchain.mine_pending_transactions(miner_address)
    return jsonify({
        "status": "success",
        "message": f"Block #{block.index} successfully mined!",
        "block": {
            "index": block.index,
            "nonce": block.nonce,
            "hash": block.hash,
            "previous_hash": block.previous_hash
        }
    })

@app.route("/api/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for b in blockchain.chain:
        chain_data.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "transactions": b.transactions,
            "previous_hash": b.previous_hash,
            "nonce": b.nonce,
            "hash": b.hash
        })
    valid, msg = blockchain.is_chain_valid()
    return jsonify({
        "chain": chain_data,
        "mempool": blockchain.pending_transactions,
        "is_valid": valid,
        "validation_message": msg
    })

@app.route("/api/wallet/balance/<address>", methods=["GET"])
def get_balance(address):
    return jsonify({"address": address, "balance": blockchain.get_balance(address)})

# --- DEMO ATTACK ENDPOINT ---
@app.route("/api/tamper", methods=["POST"])
def tamper_chain():
    """Simulates a malicious attack modifying historical data."""
    if len(blockchain.chain) > 1:
        # Alter transaction data in Block #1 without re-mining
        blockchain.chain[1].transactions[0]["amount"] = 999999
        return jsonify({"status": "success", "message": "Attacker modified transaction data in Block #1!"})
    return jsonify({"status": "error", "message": "Mine at least one block before testing tamper attack."}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)