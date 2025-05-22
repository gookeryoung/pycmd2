from pycmd2.files.file_date import remove_date_prefix


def test_remove_date_prefix():
    f1 = remove_date_prefix("20220101-hello.txt")
    assert f1 == "hello.txt"

    f2 = remove_date_prefix("20191112-my-hello.txt")
    assert f2 == "my-hello.txt"
