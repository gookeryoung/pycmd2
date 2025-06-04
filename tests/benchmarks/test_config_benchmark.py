def test_config_save_toml(example_config, benchmark) -> None:
    benchmark(example_config._save)
