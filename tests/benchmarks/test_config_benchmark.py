def test_config_save_toml(example_config, benchmark):
    benchmark(example_config._save)
