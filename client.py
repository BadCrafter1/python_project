import socket
import ssl

def main():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect(("127.0.0.1", 12345))

    # Wrap the socket with an SSL context
    client_socket = ssl.wrap_socket(client_socket,
                                   cert_reqs=ssl.CERT_REQUIRED,
                                   ca_certs="server.crt")

    # Send the login credentials
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    client_socket.sendall(username.encode())
    client_socket.sendall(password.encode())

    # Receive the login response
    response = client_socket.read(1024).decode()
    if response != "Welcome!":
        print(response)
        client_socket.close()
        return

    # Start the chat loop
    while True:
        # Send a message
        message = input("Enter your message: ")
        client_socket.sendall(message.encode())

        # Exit the chat if the message is "exit"
        if message == "exit":
            client_socket.close()
            break

        # Receive and print messages from other clients
        while True:
            try:
                message = client_socket.read(1024).decode()
                print(message)
            except socket.timeout:
                # Exit the inner loop if there are no more messages
                break

if __name__ == "__main__":
    main()
