def get_jar_name(version: str) -> str:
    """Normalizes the jar naming scheme, returns minecraft_server.{version}.jar"""
    return f"minecraft_server.{version}.jar"