#!/usr/bin/env python3
"""
SNP Detection Pipeline using Snippy
Python script alternative to Snakemake for batch running Snippy SNP detection
"""

import os
import subprocess
import glob
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('snippy_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SnippyAnalysis:
    def __init__(self, base_path, output_base_dir, ref_genome_path, cpu_cores=16):
        """
        Initialize Snippy analysis pipeline
        
        Args:
            base_path (str): Base path where FASTQ files are stored
            output_base_dir (str): Base directory for output results
            ref_genome_path (str): Reference genome file path
            cpu_cores (int): Number of CPU cores to use
        """
        self.base_path = base_path
        self.output_base_dir = output_base_dir
        self.ref_genome_path = ref_genome_path
        self.cpu_cores = cpu_cores
        
        # Supported strains
        self.strains = [
            "Acinetobacterbaumannii",
            "Pseudomonasaeruginosa", 
            "Staphylococcusaureus", 
            "Klebsiellapneumoniae"
        ]
        
        # Create output directory
        os.makedirs(self.output_base_dir, exist_ok=True)
    
    def get_samples(self):
        """
        Get all samples that need to be analyzed
        
        Returns:
            list: List of tuples containing (strain, sample_name)
        """
        samples = []
        
        if not os.path.exists(self.base_path):
            logger.error(f"Base path does not exist: {self.base_path}")
            return samples
        
        for strain in self.strains:
            strain_path = os.path.join(self.base_path, strain)
            
            if not os.path.exists(strain_path):
                logger.warning(f"Strain path does not exist: {strain_path}")
                continue
                
            for item in os.listdir(strain_path):
                item_path = os.path.join(strain_path, item)
                if os.path.isdir(item_path) and item.startswith("MCR_CVU_"):
                    samples.append((strain, item))
                    logger.info(f"Found sample: {strain}/{item}")
        
        logger.info(f"Total samples found: {len(samples)}")
        return samples
    
    def get_fastq_files(self, strain, sample):
        """
        Get FASTQ file paths for specified sample
        
        Args:
            strain (str): Strain name
            sample (str): Sample name
            
        Returns:
            tuple: (R1_file_path, R2_file_path)
        """
        sample_path = os.path.join(self.base_path, strain, sample, "ILLUMINA_DATA")
        
        if not os.path.exists(sample_path):
            raise FileNotFoundError(f"Sample path does not exist: {sample_path}")
        
        R1_files = []
        R2_files = []
        
        for file in os.listdir(sample_path):
            file_path = os.path.join(sample_path, file)
            if file.endswith("R1_trimmed.fastq"):
                R1_files.append(file_path)
            elif file.endswith("R2_trimmed.fastq"):
                R2_files.append(file_path)
        
        R1_files = sorted(R1_files)
        R2_files = sorted(R2_files)
        
        if not R1_files or not R2_files:
            raise FileNotFoundError(f"No matching FASTQ files found for: {strain}/{sample}")
        
        logger.info(f"Found FASTQ files for: {strain}/{sample}")
        logger.info(f"  R1: {os.path.basename(R1_files[0])}")
        logger.info(f"  R2: {os.path.basename(R2_files[0])}")
        
        return R1_files[0], R2_files[0]
    
    def run_snippy(self, strain, sample, R1_file, R2_file):
        """
        Run Snippy for a single sample
        
        Args:
            strain (str): Strain name
            sample (str): Sample name
            R1_file (str): R1 FASTQ file path
            R2_file (str): R2 FASTQ file path
            
        Returns:
            bool: True if successful, False if failed
        """
        # Create output directory
        output_dir = os.path.join(self.output_base_dir, strain, f"{sample}_mysnps")
        os.makedirs(output_dir, exist_ok=True)
        
        # Build Snippy command
        cmd = [
            "snippy",
            "--cpu", str(self.cpu_cores),
            "--outdir", output_dir,
            "--ref", self.ref_genome_path,
            "--R1", R1_file,
            "--R2", R2_file
        ]
        
        logger.info(f"Starting Snippy analysis: {strain}/{sample}")
        logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            # Run Snippy
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Snippy completed successfully: {strain}/{sample}")
            logger.info(f"Output directory: {output_dir}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Snippy failed for: {strain}/{sample}")
            logger.error(f"Return code: {e.returncode}")
            logger.error(f"Error message: {e.stderr}")
            return False
        
        except FileNotFoundError:
            logger.error("Snippy command not found. Please ensure Snippy is properly installed")
            return False
    
    def validate_inputs(self):
        """
        Validate input files and paths
        
        Returns:
            bool: True if validation passes
        """
        # Check base path
        if not os.path.exists(self.base_path):
            logger.error(f"Base path does not exist: {self.base_path}")
            return False
        
        # Check reference genome
        if not os.path.exists(self.ref_genome_path):
            logger.error(f"Reference genome file does not exist: {self.ref_genome_path}")
            return False
        
        # Check if snippy is available
        try:
            subprocess.run(["snippy", "--version"], capture_output=True, check=True)
            logger.info("Snippy tool validation successful")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Snippy command not found or version check failed")
            return False
        
        return True
    
    def run_analysis(self):
        """
        Run the complete SNP analysis workflow
        """
        logger.info("Starting SNP analysis workflow")
        
        # Validate inputs
        if not self.validate_inputs():
            logger.error("Input validation failed, exiting analysis")
            return
        
        # Get all samples
        samples = self.get_samples()
        
        if not samples:
            logger.error("No samples found, exiting analysis")
            return
        
        # Statistics variables
        success_count = 0
        failed_count = 0
        
        # Process each sample
        for strain, sample in samples:
            try:
                # Get FASTQ files
                R1_file, R2_file = self.get_fastq_files(strain, sample)
                
                # Run Snippy
                if self.run_snippy(strain, sample, R1_file, R2_file):
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to process sample {strain}/{sample}: {str(e)}")
                failed_count += 1
        
        # Output summary
        logger.info("=" * 60)
        logger.info("Analysis completed!")
        logger.info(f"Successfully processed: {success_count} samples")
        logger.info(f"Failed samples: {failed_count} samples")
        logger.info(f"Total samples: {len(samples)} samples")
        logger.info(f"Results saved in: {self.output_base_dir}")
        logger.info("=" * 60)


def get_user_inputs():
    """
    Get configuration parameters from user input
    
    Returns:
        dict: Dictionary containing all configuration parameters
    """
    print("SNP Detection Pipeline using Snippy")
    print("=" * 60)
    print("Please provide the following configuration:")
    print()
    
    # Get base path
    while True:
        base_path = input("Base path for FASTQ files: ").strip()
        if base_path and os.path.exists(base_path):
            break
        print("Error: Path does not exist or is empty. Try again.")
    
    # Get output directory
    output_dir = input("Output directory: ").strip()
    if not output_dir:
        output_dir = "./snippy_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get reference genome path
    while True:
        ref_genome = input("Reference genome file: ").strip()
        if ref_genome and os.path.exists(ref_genome):
            break
        print("Error: File does not exist or is empty. Try again.")
    
    # Get CPU cores
    cpu_input = input("CPU cores [16]: ").strip()
    cpu_cores = int(cpu_input) if cpu_input.isdigit() else 16
    
    print()
    print("Configuration:")
    print(f"  Base path: {base_path}")
    print(f"  Output: {output_dir}")
    print(f"  Reference: {ref_genome}")
    print(f"  CPU cores: {cpu_cores}")
    print()
    
    return {
        'base_path': base_path,
        'output_dir': output_dir,
        'ref_genome': ref_genome,
        'cpu_cores': cpu_cores
    }


def main():
    """
    Main function - Get configuration and run analysis
    """
    try:
        # Get configuration from user input
        config = get_user_inputs()
        
        # Create and run analysis
        analysis = SnippyAnalysis(
            base_path=config['base_path'],
            output_base_dir=config['output_dir'],
            ref_genome_path=config['ref_genome'],
            cpu_cores=config['cpu_cores']
        )
        
        analysis.run_analysis()
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
