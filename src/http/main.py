from src.http.routes import router
from src.http.server import Server
from loguru import logger

server: Server = Server(router)

if __name__ == "__main__":
    try:
        logger.info("Server Started")
        server.run()
    finally:
        logger.info("Server Shutdown")
        server.shutdown()
