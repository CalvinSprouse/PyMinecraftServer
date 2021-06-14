from async_minecraft_server import ServerMaker, ServerLoader
import asyncio


async def main():
    with ServerMaker("training") as maker:
        await maker.make_server("Test", overwrite=True)

    with ServerLoader("training") as loader:
        await loader.load_server("Test")
        print(loader.get_property("server-ip"))


if __name__ == "__main__":
    asyncio.run(main())
