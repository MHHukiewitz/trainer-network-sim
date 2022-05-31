# trainer-network-sim
A simulation on sharing time series datasets in distributed (federated learning) networks.

This repository is for testing different slicing schemes of time series datasets. It can simulate:
- A network consisting of an arbitrary amount of nodes
- Nodes' ownership of datasets
- Joining/leaving nodes and datasets over time
- Operations to share them across the network, such that the entire dataset can be reconstructed by help of the entire network
- Visualization of dataset distribution over time

# TODO
- [ ] Recursively balanced tree building for less data knowledge drift _(as proposed)_
- [ ] Simulation of adversary nodes trying to undermine privacy guarantees
  - [ ] Simulate colluding node sets
  - [ ] Simulate identity switching nodes
  - [ ] Fuzzy exploration of random strategies
  - [ ] Deterministic attack algorithms
- [ ] Calculation of minimal node set having distributed knowledge of a dataset
- [ ] Finding satisfactory privacy guarantees under certain network conditions
- [ ] Finding strategies to enforce privacy-preserving network conditions
