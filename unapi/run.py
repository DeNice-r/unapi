import logging
import uvicorn
import ssl
from dotenv import load_dotenv
from os import environ

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    load_dotenv()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(environ["PORT"]),
        ssl_version=ssl.PROTOCOL_TLS,
        ssl_keyfile=environ["SSL_KEYFILE"],
        ssl_certfile=environ["SSL_CERTFILE"],
        log_level="info",
        reload=True
    )
