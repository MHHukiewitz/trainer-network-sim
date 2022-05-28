from data import create_dataset
from network import Network
from node import random_nodes


def main():
    net = Network()
    net.add_nodes(random_nodes(7, 1))

    print(net.tree)
    print(net.tree.left_to_right)

    net.tick()
    net.print_nodes()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
