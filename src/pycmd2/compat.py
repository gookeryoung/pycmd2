try:
    import tomllib  # type: ignore[import]
except ModuleNotFoundError:
    # Python < 3.11时使用tomli作为替代
    import tomli as tomllib  # noqa: F401
