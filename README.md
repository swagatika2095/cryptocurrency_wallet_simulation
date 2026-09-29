# 🪙 Cryptocurrency Wallet Simulation Using Python Blockchain

A comprehensive, full-stack **Cryptocurrency Wallet Simulation & Blockchain Engine** built with **Python (Flask)** and an interactive web dashboard. 

This project demonstrates how decentralized cryptosystems manage identities and secure transactions. It highlights **Elliptic Curve Cryptography (ECDSA secp256k1)** for key pair generation and digital signatures, **SHA-256** hashing, **Proof-of-Work (PoW)** consensus, dynamic UTXO-style balance auditing, **Mempool** transaction pooling, and an intentional **Data Tampering Attack** simulation to showcase block immutability.

---

## 🌟 Key Features

* 🔑 **Cryptographic Wallet Generation:** Generates asymmetric key pairs (Private Key & Public Key) using the `SECP256k1` curve and derives deterministic hexadecimal wallet addresses.
* ✍️ **Digital Signatures & Verification:** Authenticates outbound transactions by signing payloads with private keys and verifying signatures via public keys before adding them to the mempool.
* ⚡ **Proof-of-Work (PoW) Mining:** Simulates block mining by finding nonces that satisfy a targeted hash difficulty (e.g., leading zero patterns). Includes block rewards for miners.
* 💸 **Token Faucet & Transaction Engine:** Fund wallets via a system faucet and transfer tokens between users with real-time signature checks and dynamic balance validation.
* 🛡️ **Immutability & Tamper Detection:** Includes a `/api/tamper` endpoint to simulate a malicious historical data injection attack, demonstrating how validation audits instantly catch compromised block hashes.
* 🖥️ **Interactive Web Dashboard:** Modern dark-themed web interface to create wallets, send signed transactions, mine pending blocks, track balances, and inspect the block explorer.

---

## 🏗️ System Architecture

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                             Web Dashboard                              │
 │            (HTML5 / CSS / REST Fetch API / Real-Time Auditing)         │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP JSON Requests
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                          Flask REST API Layer                          │
 │  /api/wallet/create | /api/faucet | /api/transaction/send | /api/mine  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
 ┌───────────────────────────┐                       ┌───────────────────┐
 │   ECDSA Wallet Engine     │                       │ Blockchain Engine │
 │ - SECP256k1 Key Generation│                       │ - Genesis Block   │
 │ - Digital Message Signing │                       │ - Mempool Storage │
 │ - Public Key Verification │                       │ - PoW Mining Loop │
 └───────────────────────────┘                       │ - Chain Validator │
                                                     └───────────────────┘
```

---

## 📁 Project Structure

```text
crypto-wallet-simulation/
├── main.py                  # Core Blockchain, ECDSA Wallet Engine & Flask Endpoints
├── templates/
│   └── index.html           # Interactive Web Dashboard
└── README.md                # Project Documentation & Architectural Overview
```

---

## 🚀 Quick Start & Setup Guide

### 1. Prerequisites
Ensure you have **Python 3.8 or higher** installed on your system.

### 2. Install Dependencies
Install the required packages (`Flask` and `ecdsa`):

```bash
pip install flask ecdsa
```

### 3. Run the Server
Execute the application entry point:

```bash
python main.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 📡 REST API Reference

| Endpoint | Method | Payload / Parameters | Description |
| :--- | :---: | :--- | :--- |
| `/` | `GET` | *None* | Serves the main web dashboard. |
| `/api/wallet/create` | `POST` | *None* | Generates a new cryptographic key pair and address. |
| `/api/faucet` | `POST` | `{"address": "0x..."}` | Issues 100 test SIM tokens into the mempool for an address. |
| `/api/transaction/send` | `POST` | `{"sender": "...", "recipient": "...", "amount": 10}` | Digitally signs, verifies, and queues a new transaction. |
| `/api/mine` | `POST` | `{"miner_address": "0x..."}` | Runs Proof-of-Work puzzle solver and mines pending mempool transactions. |
| `/api/chain` | `GET` | *None* | Fetches the complete ledger history, current mempool, and chain status. |
| `/api/wallet/balance/<address>` | `GET` | `address` (URL parameter) | Returns the real-time balance calculated across all historical blocks. |
| `/api/tamper` | `POST` | *None* | **Attack Simulation:** Modifies historical data in Block #1 to invalidate the chain. |

---

## 🧪 Step-by-Step Educational Demo Workflow

### 1. Initialize Crypto Wallets
1. Launch the web dashboard at `http://127.0.0.1:5000`.
2. Click **"Generate Wallet A"** and **"Generate Wallet B"**.
3. Inspect how each wallet generates a **Private Key**, **Public Key**, and a derived **Wallet Address**.

### 2. Fund a Wallet via Faucet
1. Copy the address of **Wallet A** into the **Faucet** field.
2. Request 100 SIM tokens.
3. Observe that the transaction enters the **Pending Mempool** (it is not yet confirmed on the blockchain).

### 3. Mine the First Block
1. Enter Wallet A's address into the **Miner Address** input.
2. Click **"Mine Block"**.
3. The engine increments nonces until the block hash satisfies the difficulty target. Wallet A receives a **10 SIM Mining Reward** alongside the 100 SIM Faucet allocation (Total: 110 SIM).

### 4. Execute a Digitally Signed Transfer
1. Send 25 SIM from **Wallet A** to **Wallet B**.
2. The transaction engine formats the message payload (`WalletA->WalletB:25`), signs it with Wallet A's **Private Key**, and verifies it with Wallet A's **Public Key** prior to mempool entry.
3. Mine the pending block to confirm the transaction.
4. Verify dynamic balances: Wallet A has **85 SIM**, and Wallet B has **25 SIM**.

### 5. Simulate a Data Tampering Attack
1. Click **"Simulate Data Tampering Attack"**.
2. The endpoint alters historical transaction amounts in `Block #1` without recalculating nonces or downstream hash pointers.
3. Observe how the **Chain Validation Status** turns from `VALID` to `INVALID`, identifying the corrupted block hash.

---

## 🔐 Core Concepts Demonstrated

1. **Elliptic Curve Cryptography (`secp256k1`):** Guarantees transaction non-repudiation. Transfers can only be authorized by the holder of the matching private key.
2. **Dynamic Ledger Balance Computation:** Rather than storing static balance states, account balances are dynamically calculated by scanning block history (similar to the UTXO model).
3. **Immutability via Hash Linking:** Every block stores the SHA-256 hash of the preceding block. Changing 1 bit of historical data invalidates all subsequent block headers.
4. **Proof-of-Work (PoW):** Prevents spam and history rewriting by making block creation computationally expensive while remaining trivial to verify.

---

## 📜 License

Distributed under the **MIT License**. Intended for educational and demonstration purposes.
# cryptocurrency_wallet_simulation
