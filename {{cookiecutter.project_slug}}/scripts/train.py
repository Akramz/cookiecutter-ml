import yaml
from config import ExperimentConfig

def main():
    # Load config
    with open("configs/hello_world.yaml") as f:
        config_dict = yaml.safe_load(f)
    
    # Validate config
    config = ExperimentConfig(**config_dict)
    
    # Use config
    print(f"Running experiment: {config.experiment_name}")
    print(f"Input paths: {config.input_paths}")

if __name__ == "__main__":
    main()