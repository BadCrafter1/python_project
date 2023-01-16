import socket
import ssl
import hashlib
import ldap

clients = []

def authenticate(client, address):
    # Receive the username and password from the client
    username = client.read(1024).decode()
    password = client.read(1024).decode()

    try:
        # Bind to the LDAP server with the provided username and password
        ldap.con.simple_bind_s(f"uid={username},ou=people,dc=example,dc=com", password)
        # If the bind is successful, return "Welcome!"
        client.write("Welcome!".encode())
    except ldap.INVALID_CREDENTIALS:
        # If the bind is not successful, return "Invalid username or password."
        client.write("Invalid username or password.".encode())
        client.close()
        return

    # Add the client to the list of connected clients
    clients.append(client)

    # Notify all other clients of the new connection
    for c in clients:
        c.write(f"{address} has joined the chat.".encode())

def handle_chat(client, address):
    while True:
        # Receive a message from the client
        message = client.read(1024).decode()

        # Check if the message is a command to add a new user
        if message.startswith("add_user"):
            add_user(message)
            continue

        # Broadcast the message to all other clients
        for c in clients:
            c.write(f"{address}: {message}".encode())

        # Exit the chat if the client sends "exit"
        if message == "exit":
            clients.remove(client)
            client.close()
            print(f"Connection from {address} has been closed.")
            break

def add_user(message):
    # Split the message into parts
    parts = message.split(" ")

    # Extract the username and password from the message
    username = parts[1]
    password = parts[2]

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Create a new user and set their attributes
    user = {
        "cn": username,
        "uid": username,
        "userPassword": hashed_password,
        "objectClass": ["top", "person", "organizationalPerson", "inetOrgPerson"]
    }

    # Add the new user to the LDAP server
    ldap.con.add_s(f"uid={username},ou=people,dc=example,dc=com", ldap.modlist.addModlist(user))
    print(f"User {username} has been added to the LDAP server.")

def main():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind(("127.0.0.1", 12345))

    # Listen for new connections
    server_socket.listen(5)

    # Connect to the LDAP server
    ldap_con = ldap.initialized("ldap://ldap.example.com")
    ldap_con.simple_bind_s("cn=admin,dc=example,dc=com", "password")
    
    while True:
        # Accept a new connection
        client, address = server_socket.accept()
        print(f"Connection from {address} has been established.")

        # Wrap the client socket with an SSL context
        client = ssl.wrap_socket(client,
                                server_side=True,
                                certfile="server.crt",
                                keyfile="server.key")

        # Authenticate the client
        authenticate(client, address)

        # Handle the chat
        handle_chat(client, address)

if __name__ == "__main__":
    main()

