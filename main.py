from data import create_dataset, Dataset


def main():
    dataset = create_dataset(columns=["comfy", "nice"])
    print(dataset.features.head(15))
    print(dataset.earliest)
    print(dataset.latest)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
