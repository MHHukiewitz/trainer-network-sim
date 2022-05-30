from data import create_dataset
from network import Network
from node import random_nodes


def main(tree_type: str = "ltor"):
    net = Network(tree_type=tree_type)
    net.add_nodes(random_nodes(1, 1))

    dataset = net.get_all_dataset_names()[0]
    print(f"Simulating distribution of dataset {dataset}")
    net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)
    for i in range(14):
        if i % 30 == 0:
            print(f"Iterated {i} days with {len(net.nodes)} nodes...")
        if i % 1 == 0:
            net.add_nodes(random_nodes(1, 1))
        net.tick()
        net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main("ltor")
    main("rtol")
