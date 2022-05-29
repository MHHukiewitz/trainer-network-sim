from data import create_dataset
from network import Network
from node import random_nodes


def main():
    net = Network()
    net.add_nodes(random_nodes(1, 1))

    dataset = net.get_all_dataset_names()[0]
    print(f"Simulating distribution of dataset {dataset}")
    net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)
    for i in range(6):
        if i % 50 == 0:
            print(f"Iterated {i} days with {len(net.nodes)} nodes...")
        if i % 1 == 0:
            net.add_nodes(random_nodes(1, 1))
        net.distribute_dataset(dataset)
        net.tick()
    net.print_dataset_distribution(dataset)

    print(net.tree)
    print(net.tree.left_to_right)
    print(net.get_all_dataset_names())

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
