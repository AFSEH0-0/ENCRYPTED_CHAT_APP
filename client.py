import socket
import threading
import sys

from crypto import create_key, encrypt_message, decrypt_message


DEFAULT_SERVER = "127.0.0.1"
DEFAULT_PORT = 5555

SHARED_PASSWORD = "EncryptedChat@2026"

AES_KEY = create_key(SHARED_PASSWORD)


client_socket = None
running = False
username = ""


def send_encrypted(message):
    """
    Encrypt and send a message to the server.
    """
    try:
        encrypted = encrypt_message(
            message,
            AES_KEY
        )

        client_socket.sendall(
            encrypted.encode("utf-8")
        )

        return True

    except Exception as error:
        print(f"\n[!] Send error: {error}")
        return False


def receive_messages():
    """
    Receive and decrypt messages from the server.
    """
    global running

    while running:
        try:
            encrypted_data = client_socket.recv(65536)

            if not encrypted_data:
                print("\n[!] Server disconnected.")
                running = False
                break

            encrypted_data = encrypted_data.decode("utf-8")

            message = decrypt_message(
                encrypted_data,
                AES_KEY
            )

            if message is None:
                print("\n[!] Received invalid or modified message.")
                continue

            print(f"\n{message}")
            print("> ", end="", flush=True)

        except ConnectionResetError:
            print("\n[!] Connection lost.")
            running = False
            break

        except Exception as error:
            if running:
                print(f"\n[!] Receive error: {error}")

            running = False
            break


def connect_to_server(server_ip, server_port):
    """
    Connect the client to the TCP server.
    """
    global client_socket
    global running

    try:
        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.settimeout(10)

        client_socket.connect(
            (server_ip, server_port)
        )

        client_socket.settimeout(None)

        print("\n[+] Connected to encrypted chat server.")

        running = True

        # Send username encrypted.
        if not send_encrypted(username):
            return False

        receiver_thread = threading.Thread(
            target=receive_messages,
            daemon=True
        )

        receiver_thread.start()

        return True

    except socket.timeout:
        print("[!] Connection timed out.")
        return False

    except ConnectionRefusedError:
        print("[!] Connection refused. Is the server running?")
        return False

    except Exception as error:
        print(f"[!] Connection error: {error}")
        return False


def chat_menu():
    """
    Main chat menu.
    """
    global running

    while running:

        print("\n" + "=" * 55)
        print("                 CHAT MENU")
        print("=" * 55)
        print("1. Send Message")
        print("2. Send Private Message")
        print("3. Show Online Users")
        print("4. Show Help")
        print("5. Disconnect")
        print("=" * 55)

        choice = input("Enter choice: ").strip()

        if not running:
            break

        if choice == "1":
            message = input("\nEnter message: ").strip()

            if message:
                send_encrypted(message)

        elif choice == "2":
            target = input("Enter username: ").strip()
            message = input("Enter private message: ").strip()

            if target and message:
                send_encrypted(
                    f"/msg {target} {message}"
                )

        elif choice == "3":
            send_encrypted("/users")

        elif choice == "4":
            send_encrypted("/help")

        elif choice == "5":
            send_encrypted("/quit")

            running = False
            break

        else:
            print("Invalid choice.")


def get_connection_details():
    """
    Ask the user for server information.
    """
    print("\n" + "=" * 55)
    print("             SERVER CONNECTION")
    print("=" * 55)

    server_ip = input(
        f"Server IP [{DEFAULT_SERVER}]: "
    ).strip()

    if not server_ip:
        server_ip = DEFAULT_SERVER

    port_text = input(
        f"Server Port [{DEFAULT_PORT}]: "
    ).strip()

    if port_text:
        try:
            server_port = int(port_text)
        except ValueError:
            print("Invalid port. Using default port.")
            server_port = DEFAULT_PORT
    else:
        server_port = DEFAULT_PORT

    return server_ip, server_port


def client_menu():
    """
    Main client menu.
    """
    global username

    while True:

        print("\n" + "=" * 60)
        print("             ENCRYPTED CHAT APP")
        print("=" * 60)
        print("1. Connect to Chat Server")
        print("2. Application Information")
        print("3. Exit")
        print("=" * 60)

        choice = input("Enter choice: ").strip()

        if choice == "1":

            username = input(
                "\nEnter your username: "
            ).strip()

            if not username:
                print("Username cannot be empty.")
                continue

            server_ip, server_port = get_connection_details()

            if connect_to_server(
                server_ip,
                server_port
            ):
                chat_menu()

                try:
                    client_socket.close()
                except Exception:
                    pass

                print("\nDisconnected from server.")

        elif choice == "2":
            print("\nApplication Information")
            print("-----------------------")
            print("Project      : Encrypted Chat App")
            print("Language     : Python")
            print("Protocol     : TCP")
            print("Encryption   : AES-256-GCM")
            print("Key handling : Pre-shared key")
            print("IV/Nonce     : Random 12 bytes per message")
            print("Concurrency  : Multi-threaded server")

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    try:
        client_menu()

    except KeyboardInterrupt:
        running = False

        try:
            client_socket.close()
        except Exception:
            pass

        print("\n\nClient stopped.")
        sys.exit(0)