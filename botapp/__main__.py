import argparse

from botapp import bot


def argsParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-run", required=False, action="store_true")
    parser.add_argument("-init_db", required=False, action="store_true")
    parser.add_argument("-env", nargs="?", type=str, default="develop")

    return parser


if __name__ == "__main__":
    parser = argsParser()
    namespace = parser.parse_args()

    if namespace.init_db:
        bot.run(bot.db.create_tables())

    if namespace.run:
        bot.run()

