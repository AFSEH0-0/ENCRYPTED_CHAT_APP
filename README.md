# ENCRYPTED CHAT APP

A terminal-based multi-client chat application built with Python.

The application uses TCP sockets for communication and AES-256-GCM
for encrypting chat messages.

## Features

- TCP client/server communication
- AES-256-GCM encryption
- Fresh random nonce for every message
- Pre-shared encryption password
- Multiple simultaneous clients
- Thread-based concurrency
- Broadcast messaging
- Private messaging
- Online user list
- Server-side message logging
- Menu-based terminal interface
- Connection and error handling

## Project Structure

ENCRYPTED CHAT APP/
│
├── chat.log
├── client.py
├── crypto.py
├── README.md
├── requirements.txt
└── server.py

## Requirements

Python 3.9 or newer is recommended.

Install the required package:

    pip install -r requirements.txt

On Linux:

    python3 -m pip install -r requirements.txt

## Running the Server

Open a terminal inside the project directory.

Run:

    python server.py

On Linux:

    python3 server.py

Select:

    1. Start Server

The server listens on:

    0.0.0.0:5555

## Running the Client

Open another terminal.

Run:

    python client.py

On Linux:

    python3 client.py

Select:

    1. Connect to Chat Server

For testing on the same computer, use:

    127.0.0.1

Port:

    5555

Enter a unique username.

## Testing Multiple Clients

Start the server first.

Then open multiple terminals and run:

    python client.py

Example:

    Client 1 -> Ali
    Client 2 -> Ahmed
    Client 3 -> Mcki

All clients can communicate through the same server.

## Chat Menu

The client provides:

    1. Send Message
    2. Send Private Message
    3. Show Online Users
    4. Show Help
    5. Disconnect

## Chat Commands

The server also supports:

    /users

Shows currently connected users.

    /msg username message

Sends a private message.

Example:

    /msg Ahmed Hello Ahmed

    /help

Shows available commands.

    /quit

Disconnects from the server.

## Encryption

Messages are encrypted using AES-256-GCM.

The application creates a 256-bit AES key from the pre-shared password.

Every message receives a new random 12-byte nonce.

The transmitted encrypted data contains:

    nonce + ciphertext + authentication tag

The authentication tag allows AES-GCM to detect modified or corrupted
encrypted messages.

## Pre-Shared Key

The current development password is configured in both:

    server.py
    client.py

Current password:

    EncryptedChat@2026

Both sides must use the same password.

For a real deployment, the password should not be hard-coded into
source code.

## Message Logging

The server writes chat activity to:

    chat.log

The log can contain:

- User connections
- User disconnections
- Chat messages
- Private messages
- Server events
- Errors

The server does not need to store plaintext messages in the network
traffic. Messages are encrypted before transmission.

## Security Design

### AES-256-GCM

AES-GCM provides:

- Confidentiality
- Integrity
- Authentication

### Unique Nonce

A cryptographically secure random nonce is generated for every
encrypted message.

The same nonce is never intentionally reused for separate messages.

### Password to Key

The pre-shared password is converted into a 32-byte key using SHA-256.

For a production system, a password-based key derivation function such
as PBKDF2, scrypt, or Argon2 with a salt would be preferable.

## Example

Client A enters:

    Hello Ahmed!

Before transmission:

    Hello Ahmed!
          |
          v
    AES-256-GCM
          |
          v
    Random Nonce + Ciphertext + Authentication Tag
          |
          v
       TCP Socket
          |
          v
        Server
          |
          v
       TCP Socket
          |
          v
       Client B
          |
          v
    AES-256-GCM Decryption
          |
          v
    Hello Ahmed!

## Educational Purpose

This project demonstrates:

- TCP socket programming
- Client/server architecture
- Symmetric encryption
- AES-GCM
- Secure nonce generation
- Pre-shared key handling
- Multi-threading
- Concurrent client handling
- Secure message transmission
- Message logging