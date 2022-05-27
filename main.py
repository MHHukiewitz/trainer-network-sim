from data import create_dataset, TimeSeries
from network import Network
from node import Node


def main():
    comfy = create_dataset(columns=["comfy"], start="1999-12-01", end="2000-02-01")
    nice = create_dataset(columns=["nice"], start="2000-01-01", end="2000-02-01")
    c = Node(comfy)
    n = Node(nice)
    net = Network()
    net.add_node(c)
    net.add_node(n)
    net.print_nodes()
    c.receive_data(n.own_data)
    net.tick()
    net.print_nodes()
    c.receive_data(n.own_data)
    net.print_nodes()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
