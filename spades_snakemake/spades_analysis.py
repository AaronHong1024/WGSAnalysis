#!/usr/bin/env python3
"""
Genome Assembly Pipeline using SPAdes
Python script alternative to Snakemake for batch running SPAdes genome assembly
"""

import os
import subprocess
import gzip
import shutil
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spades_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SpadesAnalysis:
    def __init__(self, base_input_dir, base_output_dir, cpu_cores=16):
        """
        Initialize SPAdes analysis pipeline
        
        Args:
            base_input_dir (str): Base input directory containing FASTQ files
            base_output_dir (str): Base output directory for assembly results
            cpu_cores (int): Number of CPU cores to use
        """
        self.base_input_dir = base_input_dir
        self.base_output_dir = base_output_dir
        self.cpu_cores = cpu_cores
        
        # Create output directory
        os.makedirs(self.base_output_dir, exist_ok=True)
    
    def get_samples(self):
        """
        Get all samples that need to be assembled
        
        Returns:
            list: List of sample paths for assembly
        """
        samples = []
        
        if not os.path.exists(self.base_input_dir):
            logger.error(f"Base input directory does not exist: {self.base_input_dir}")
            return samples
        
        # Get all directories in the input directory
        directories = [d for d in os.listdir(self.base_input_dir) 
                      if os.path.isdir(os.path.join(self.base_input_dir, d))]
        
        for directory in directories:
            input_dir = os.path.join(self.base_input_dir, directory, "ILLUMINA_DATA")
            
            if not os.path.exists(input_dir):
                logger.warning(f"ILLUMINA_DATA directory not found: {input_dir}")
                continue
            
            # Find R1 files
            r1_files = [f for f in os.listdir(input_dir) 
                       if f.endswith("R1_trimmed.fastq.gz")]
            
            for r1_file in r1_files:
                r2_file = r1_file.replace("_R1_trimmed.fastq.gz", "_R2_trimmed.fastq.gz")
                r2_path = os.path.join(input_dir, r2_file)
                
                if os.path.exists(r2_path):
                    sample_name = r1_file.replace("_R1_trimmed.fastq.gz", "")
                    sample_path = os.path.join(directory, "ILLUMINA_DATA", sample_name)
                    samples.append(sample_path)
                    logger.info(f"Found sample: {sample_path}")
                else:
                    logger.warning(f"Missing R2 file for {r1_file}: {r2_path}")
        
        logger.info(f"Total samples found: {len(samples)}")
        return samples
    
    def decompress_fastq(self, sample_path):
        """
        Decompress FASTQ.gz files to FASTQ files
        
        Args:
            sample_path (str): Sample path (relative to base input directory)
            
        Returns:
            tuple: (R1_decompressed_path, R2_decompressed_path)
        """
        # Build file paths
        r1_gz = os.path.join(self.base_input_dir, f"{sample_path}_R1_trimmed.fastq.gz")
        r2_gz = os.path.join(self.base_input_dir, f"{sample_path}_R2_trimmed.fastq.gz")
        r1_fastq = os.path.join(self.base_input_dir, f"{sample_path}_R1_trimmed.fastq")
        r2_fastq = os.path.join(self.base_input_dir, f"{sample_path}_R2_trimmed.fastq")
        
        logger.info(f"Decompressing FASTQ files for: {sample_path}")
        
        # Check if already decompressed
        if os.path.exists(r1_fastq) and os.path.exists(r2_fastq):
            logger.info(f"FASTQ files already decompressed: {sample_path}")
            return r1_fastq, r2_fastq
        
        # Decompress R1
        if os.path.exists(r1_gz):
            try:
                with gzip.open(r1_gz, 'rb') as f_in:
                    with open(r1_fastq, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                logger.info(f"Decompressed R1: {os.path.basename(r1_gz)}")
            except Exception as e:
                logger.error(f"Failed to decompress {r1_gz}: {e}")
                raise
        else:
            raise FileNotFoundError(f"R1 file not found: {r1_gz}")
        
        # Decompress R2
        if os.path.exists(r2_gz):
            try:
                with gzip.open(r2_gz, 'rb') as f_in:
                    with open(r2_fastq, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                logger.info(f"Decompressed R2: {os.path.basename(r2_gz)}")
            except Exception as e:
                logger.error(f"Failed to decompress {r2_gz}: {e}")
                raise
        else:
            raise FileNotFoundError(f"R2 file not found: {r2_gz}")
        
        return r1_fastq, r2_fastq
    
    def run_spades(self, sample_path, r1_file, r2_file):
        """
        Run SPAdes assembly for a single sample
        
        Args:
            sample_path (str): Sample path identifier
            r1_file (str): R1 FASTQ file path
            r2_file (str): R2 FASTQ file path
            
        Returns:
            bool: True if successful, False if failed
        """
        # Create output directory for this sample
        assembly_dir = os.path.join(self.base_output_dir, f"{os.path.basename(sample_path)}_assembly")
        
        # Build SPAdes command
        cmd = [
            "spades.py",
            "--threads", str(self.cpu_cores),
            "-o", assembly_dir,
            "-1", r1_file,
            "-2", r2_file
        ]
        
        logger.info(f"Starting SPAdes assembly: {sample_path}")
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info(f"Output directory: {assembly_dir}")
        
        try:
            # Run SPAdes
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"SPAdes assembly completed successfully: {sample_path}")
            
            # Check if contigs.fasta was generated
            contigs_file = os.path.join(assembly_dir, "contigs.fasta")
            if os.path.exists(contigs_file):
                logger.info(f"Contigs file generated: {contigs_file}")
            else:
                logger.warning(f"Contigs file not found: {contigs_file}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"SPAdes assembly failed for: {sample_path}")
            logger.error(f"Return code: {e.returncode}")
            logger.error(f"Error message: {e.stderr}")
            return False
        
        except FileNotFoundError:
            logger.error("SPAdes command not found. Please ensure SPAdes is properly installed")
            return False
    
    def validate_inputs(self):
        """
        Validate input directories and tools
        
        Returns:
            bool: True if validation passes
        """
        # Check input directory
        if not os.path.exists(self.base_input_dir):
            logger.error(f"Base input directory does not exist: {self.base_input_dir}")
            return False
        
        # Check if SPAdes is available
        try:
            subprocess.run(["spades.py", "--version"], capture_output=True, check=True)
            logger.info("SPAdes tool validation successful")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("SPAdes command not found or version check failed")
            return False
        
        return True
    
    def run_assembly(self):
        """
        Run the complete genome assembly workflow
        """
        logger.info("Starting genome assembly workflow")
        
        # Validate inputs
        if not self.validate_inputs():
            logger.error("Input validation failed, exiting assembly")
            return
        
        # Get all samples
        samples = self.get_samples()
        
        if not samples:
            logger.error("No samples found, exiting assembly")
            return
        
        # Statistics variables
        success_count = 0
        failed_count = 0
        
        # Process each sample
        for sample_path in samples:
            try:
                logger.info(f"Processing sample: {sample_path}")
                
                # Decompress FASTQ files
                r1_file, r2_file = self.decompress_fastq(sample_path)
                
                # Run SPAdes assembly
                if self.run_spades(sample_path, r1_file, r2_file):
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to process sample {sample_path}: {str(e)}")
                failed_count += 1
        
        # Output summary
        logger.info("=" * 60)
        logger.info("Assembly workflow completed!")
        logger.info(f"Successfully assembled: {success_count} samples")
        logger.info(f"Failed assemblies: {failed_count} samples")
        logger.info(f"Total samples: {len(samples)} samples")
        logger.info(f"Results saved in: {self.base_output_dir}")
        logger.info("=" * 60)


def get_user_inputs():
    """
    Get configuration parameters from user input
    
    Returns:
        dict: Dictionary containing all configuration parameters
    """
    print("Genome Assembly Pipeline using SPAdes")
    print("=" * 60)
    print("Please provide the following configuration:")
    print()
    
    # Get input directory
    while True:
        input_dir = input("Base path for input directories: ").strip()
        if input_dir and os.path.exists(input_dir):
            break
        print("Error: Directory does not exist or is empty. Try again.")
    
    # Get output directory
    output_dir = input("Output directory: ").strip()
    if not output_dir:
        output_dir = "./spades_assemblies"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get CPU cores
    cpu_input = input("CPU cores [16]: ").strip()
    cpu_cores = int(cpu_input) if cpu_input.isdigit() else 16
    
    print()
    print("Configuration:")
    print(f"  Input directory: {input_dir}")
    print(f"  Output directory: {output_dir}")
    print(f"  CPU cores: {cpu_cores}")
    print()
    
    return {
        'input_dir': input_dir,
        'output_dir': output_dir,
        'cpu_cores': cpu_cores
    }


def main():
    """
    Main function - Get configuration and run assembly
    """
    try:
        # Get configuration from user input
        config = get_user_inputs()
        
        # Create and run analysis
        analysis = SpadesAnalysis(
            base_input_dir=config['input_dir'],
            base_output_dir=config['output_dir'],
            cpu_cores=config['cpu_cores']
        )
        
        analysis.run_assembly()
        
    except KeyboardInterrupt:
        print("\nAssembly interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
