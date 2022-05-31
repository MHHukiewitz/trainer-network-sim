import random

from network import Network, TreeType
from node import random_nodes


def main(tree_type: TreeType = TreeType.ordered_ltor):
    net = Network(tree_type=tree_type)
    net.add_nodes(random_nodes(1, 1, to="2000-03-22"))

    dataset = net.get_all_dataset_names()[0]
    print(f"\nSimulating distribution of dataset {dataset} with tree building algorithm {tree_type}")
    net.distribute_dataset(dataset)
    for i in range(30):
        if i % 30 == 29:
            print(f"Iterated {i} days with {len(net.nodes)} nodes...")
        if i % 2 == 0:
            net.add_nodes(random_nodes(random.randint(1, 3), 1))
        if random.randint(0, 3) == 0:
            nodes = list(net.nodes.keys())
            nodes.remove(dataset[:-2])
            net.remove_node(random.choice(nodes))
        #net.tick()
        net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)
    print(f"Average amount of ticks observed: {net.avg_observations(dataset): 2f} of {len(net.get_dataset(dataset))}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(TreeType.ordered_ltor)
    main(TreeType.ordered_rtol)
    main(TreeType.balanced_ltor)
    main(TreeType.balanced_rtol)
    #main(TreeType.balanced_random)
