from py_minecraft_server import logger
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Minecraft Servers")
    parser.add_argument("-c", "--create", type=str, help="Name of server to create")
    args = vars(parser.parse_args())
    print(args)
