import socket
import threading
from datetime import datetime

from crypto import create_key, encrypt_message, decrypt_message


HOST = "0.0.0.0"
PORT = 5555

# Pre-shared password.
# Every client must use the same password.
SHARED_PASSWORD = "EncryptedChat@2026"

AES_KEY = create_key(SHARED_PASSWORD)

clients = {}
clients_lock = threading.Lock()


def log_message(message):
    """
    Save server activity to chat.log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("chat.log", "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


def send_data(client_socket, data):
    """
    Send UTF-8 data through the socket.
    """
    try:
        client_socket.sendall(data.encode("utf-8"))
        return True
    except Exception:
        return False


def send_encrypted(client_socket, message):
    """
    Encrypt a server-generated message before sending it.
    """
    encrypted = encrypt_message(message, AES_KEY)
    return send_data(client_socket, encrypted)


def broadcast(message, exclude=None):
    """
    Send an encrypted message to all connected clients.

    exclude:
        Client socket that should not receive the message.
    """
    encrypted = encrypt_message(message, AES_KEY)

    disconnected = []

    with clients_lock:
        for client_socket in list(clients.keys()):

            if client_socket == exclude:
                continue

            try:
                client_socket.sendall(
                    encrypted.encode("utf-8")
                )
            except Exception:
                disconnected.append(client_socket)

    for client_socket in disconnected:
        remove_client(client_socket)


def private_message(sender, target, message):
    """
    Send an encrypted private message to one client.
    """
    with clients_lock:
        target_socket = None

        for client_socket, username in clients.items():
            if username.lower() == target.lower():
                target_socket = client_socket
                break

    if target_socket is None:
        return False

    full_message = f"[Private] {sender}: {message}"

    encrypted = encrypt_message(full_message, AES_KEY)

    try:
        target_socket.sendall(
            encrypted.encode("utf-8")
        )
        return True
    except Exception:
        remove_client(target_socket)
        return False


def get_online_users():
    """
    Return a list of currently connected usernames.
    """
    with clients_lock:
        return list(clients.values())


def remove_client(client_socket):
    """
    Remove a disconnected client.
    """
    username = None

    with clients_lock:
        if client_socket in clients:
            username = clients.pop(client_socket)

    try:
        client_socket.close()
    except Exception:
        pass

    if username:
        print(f"[-] {username} disconnected")
        log_message(f"{username} disconnected")

        broadcast(
            f"[Server] {username} left the chat.",
            exclude=client_socket
        )


def handle_client(client_socket, address):
    """
    Handle one connected client.
    """
    username = None

    try:
        # Receive encrypted username.
        encrypted_username = client_socket.recv(4096).decode("utf-8")

        if not encrypted_username:
            client_socket.close()
            return

        username = decrypt_message(
            encrypted_username,
            AES_KEY
        )

        if not username:
            send_encrypted(
                client_socket,
                "[Server] Authentication failed."
            )
            client_socket.close()
            return

        username = username.strip()

        if not username:
            send_encrypted(
                client_socket,
                "[Server] Invalid username."
            )
            client_socket.close()
            return

        # Check duplicate username.
        with clients_lock:
            existing_names = [
                name.lower()
                for name in clients.values()
            ]

            if username.lower() in existing_names:
                send_encrypted(
                    client_socket,
                    "[Server] Username already exists."
                )
                client_socket.close()
                return

            clients[client_socket] = username

        print(f"[+] {username} connected from {address}")
        log_message(
            f"{username} connected from {address[0]}:{address[1]}"
        )

        send_encrypted(
            client_socket,
            "[Server] Welcome to the encrypted chat."
        )

        broadcast(
            f"[Server] {username} joined the chat.",
            exclude=client_socket
        )

        while True:
            encrypted_data = client_socket.recv(65536)

            if not encrypted_data:
                break

            encrypted_data = encrypted_data.decode("utf-8")

            message = decrypt_message(
                encrypted_data,
                AES_KEY
            )

            if message is None:
                send_encrypted(
                    client_socket,
                    "[Server] Message authentication failed."
                )
                continue

            message = message.strip()

            if not message:
                continue

            # Private message.
            if message.startswith("/msg "):
                parts = message.split(" ", 2)

                if len(parts) < 3:
                    send_encrypted(
                        client_socket,
                        "[Server] Usage: /msg username message"
                    )
                    continue

                target = parts[1]
                private_text = parts[2]

                if private_message(
                    username,
                    target,
                    private_text
                ):
                    send_encrypted(
                        client_socket,
                        f"[Private to {target}] {private_text}"
                    )

                    log_message(
                        f"PRIVATE {username} -> {target}: {private_text}"
                    )
                else:
                    send_encrypted(
                        client_socket,
                        f"[Server] User '{target}' is not online."
                    )

                continue

            # Online users.
            if message == "/users":
                users = get_online_users()

                users_text = ", ".join(users)

                send_encrypted(
                    client_socket,
                    f"[Online Users] {users_text}"
                )

                continue

            # Help.
            if message == "/help":
                help_text = (
                    "[Commands]\n"
                    "/users - Show online users\n"
                    "/msg username message - Private message\n"
                    "/help - Show commands\n"
                    "/quit - Leave chat"
                )

                send_encrypted(
                    client_socket,
                    help_text
                )

                continue

            # Quit.
            if message == "/quit":
                send_encrypted(
                    client_socket,
                    "[Server] Goodbye."
                )
                break

            # Normal broadcast message.
            full_message = f"{username}: {message}"

            print(full_message)

            log_message(full_message)

            broadcast(
                full_message,
                exclude=None
            )

    except ConnectionResetError:
        pass

    except Exception as error:
        print(f"[!] Error handling {address}: {error}")
        log_message(
            f"Error handling {address}: {error}"
        )

    finally:
        remove_client(client_socket)


def start_server():
    """
    Start the TCP chat server.
    """
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(20)

        print("=" * 60)
        print("       ENCRYPTED CHAT APP - SERVER")
        print("=" * 60)
        print(f"Listening on: {HOST}:{PORT}")
        print("Encryption: AES-256-GCM")
        print("Multiple clients: Enabled")
        print("Logging: chat.log")
        print("=" * 60)

        log_message(
            f"Server started on {HOST}:{PORT}"
        )

        while True:
            client_socket, address = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )

            client_thread.start()

    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")

    except Exception as error:
        print(f"[!] Server error: {error}")

    finally:
        with clients_lock:
            for client_socket in clients:
                try:
                    client_socket.close()
                except Exception:
                    pass

            clients.clear()

        server_socket.close()

        log_message("Server stopped.")


def server_menu():
    """
    Server menu.
    """
    while True:
        print("\n" + "=" * 50)
        print("           SERVER MENU")
        print("=" * 50)
        print("1. Start Server")
        print("2. Show Configuration")
        print("3. Show Connected Users")
        print("4. Exit")
        print("=" * 50)

        choice = input("Enter choice: ").strip()

        if choice == "1":
            start_server()

        elif choice == "2":
            print("\nServer Configuration")
            print("--------------------")
            print(f"Host       : {HOST}")
            print(f"Port       : {PORT}")
            print("Encryption : AES-256-GCM")
            print("Key type   : Pre-shared password")
            print("Concurrency: Thread-based")
            print("Log file   : chat.log")

        elif choice == "3":
            users = get_online_users()

            print("\nConnected Users")
            print("----------------")

            if users:
                for number, username in enumerate(users, 1):
                    print(f"{number}. {username}")
            else:
                print("No users connected.")

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    server_menu()