import random

from core.network import TreeType, create_network


def main(tree_type: TreeType = TreeType.ordered_ltor):
    net = create_network(200, tree_type=tree_type)
    simulate_time(net, tree_type)


def simulate_time(net, tree_type):
    dataset = net.get_all_dataset_names()[0]
    print(f"\nSimulating distribution of dataset {dataset} with tree building algorithm {tree_type}")
    net.distribute_dataset(dataset)
    for i in range(1 * 60):
        if i % 30 == 29:
            print(f"Iterated {i+1} days with {len(net.nodes)} nodes...")
        if i % 1 == 0:
            net.create_nodes(1, 1)
        #if random.randint(0, 5) == 0:
        #    nodes = list(net.nodes.keys())
        #    nodes.remove(dataset[:-2])
        #    net.remove_node(random.choice(nodes))
        net.tick()
        if i % 1 == 0:
            net.distribute_dataset(dataset)
    net.print_dataset_intervals(dataset)
    net.print_dataset_distribution(dataset)
    print(net.tree)
    net.print_statistics(dataset)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(TreeType.ordered_ltor)
    main(TreeType.ordered_rtol)
    main(TreeType.balanced_ltor)
    main(TreeType.balanced_rtol)
    #main(TreeType.balanced_random)
