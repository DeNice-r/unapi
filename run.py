import logging
import uvicorn
import ssl
from dotenv import load_dotenv


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    load_dotenv()
    uvicorn.run('main:app',
                host='0.0.0.0',
                port=443,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_keyfile='key.pem',
                ssl_certfile='cert.pem',
                log_level='info',
                reload=True
                )
