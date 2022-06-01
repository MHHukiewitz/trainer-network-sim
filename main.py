import random

from network import Network, TreeType
from node import random_nodes


def main(tree_type: TreeType = TreeType.ordered_ltor):
    net = create_network(200, tree_type=tree_type)
    simulate_time(net, tree_type)


def create_network(nodes: int, tree_type: TreeType = TreeType.ordered_ltor):
    net = Network(tree_type=tree_type)
    net.add_nodes(random_nodes(nodes, 1, to="2001-01-01"))
    return net


def simulate_time(net, tree_type):
    dataset = net.get_all_dataset_names()[0]
    print(f"\nSimulating distribution of dataset {dataset} with tree building algorithm {tree_type}")
    net.distribute_dataset(dataset)
    for i in range(90 * 24):
        if i % 24 == 23:
            print(f"Iterated {i+1} hours with {len(net.nodes)} nodes...")
        if i % 24 * 14 == 0:
            net.add_nodes(random_nodes(3, 1))
        # if random.randint(0, 24) == 0:
        #    nodes = list(net.nodes.keys())
        #    nodes.remove(dataset[:-2])
        #    net.remove_node(random.choice(nodes))
        net.tick()
        if i % 8 == 0:
            net.distribute_dataset(dataset)
    net.print_dataset_distribution(dataset)
    print(f"Average amount of ticks observed: {net.avg_observations(dataset): 2f} of {len(net.get_dataset(dataset))} ({100*net.avg_observations(dataset)/len(net.get_dataset(dataset)): .1f} %)")
    # TODO: Get distribution of all intervals and the amount of copies in the network


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #main(TreeType.ordered_ltor)
    #main(TreeType.ordered_rtol)
    main(TreeType.balanced_ltor)
    #main(TreeType.balanced_rtol)
    #main(TreeType.balanced_random)
