def main():
    from rocket_optimizer import cli
    cli.app()


if __name__ == "__main__":
    import os
    os.chdir("../..")
    print(os.getcwd())

    from rocket_optimizer import cli
    cli.app()
