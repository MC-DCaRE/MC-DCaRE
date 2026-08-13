import sys
from src.config_loader import ConfigLoader
from src.pcxmc_runner import PCXMCRunner

def main():
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load_config("configs/demo_config.yaml")
    
    # Create and run PCXMC simulation
    runner = PCXMCRunner(config)
    results = runner.run()
    
    # Extract the PCXMC matrix
    matrix = results['pcxmc_matrix']
    
    # Write as tab-separated values to file
    with open('pcxmc_matrix.txt', 'w') as f:
        for row in matrix:

if __name__ == "__main__":
    main()
