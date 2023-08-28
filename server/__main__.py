import argparse
import asyncio

from . import db
from .server import Server


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-run", required=False, action="store_true")
    parser.add_argument("-init_db", required=False, action="store_true")
    parser.add_argument("-env", nargs="?", type=str, default="develop")

    return parser


async def main():
    app = Server()
    await app.start_server('127.0.0.1', 8000)


if __name__ == "__main__":
    parser = args_parser()
    namespace = parser.parse_args()

    if namespace.run:
        asyncio.run(main())

    if namespace.init_db:
        asyncio.run(db.create_tables())
