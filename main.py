from network import Network, TreeType
from node import random_nodes


def main(tree_type: TreeType = TreeType.ordered_ltor):
    net = Network(tree_type=tree_type)
    net.add_nodes(random_nodes(1, 1, to="2000-03-22"))

    dataset = net.get_all_dataset_names()[0]
    print(f"Simulating distribution of dataset {dataset}")
    net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)
    for i in range(14):
        if i % 30 == 0:
            print(f"Iterated {i} days with {len(net.nodes)} nodes...")
        if i % 1 == 0:
            net.add_nodes(random_nodes(1, 1))
        #if random.randint(0, 5) == 0:
        #    nodes = list(net.nodes.keys())
        #    nodes.remove(dataset[:-2])
        #    net.remove_node(random.choice(nodes))
        #net.tick()
        net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(TreeType.ordered_ltor)
    main(TreeType.ordered_rtol)
    main(TreeType.balanced_ltor)
    main(TreeType.balanced_rtol)
    main(TreeType.balanced_random)
