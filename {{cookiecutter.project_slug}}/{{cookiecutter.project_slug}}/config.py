from enum import Enum
from typing import List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, field_validator

class DataSourceEnum(str, Enum):
    """Supported data sources."""
    csv = "csv"
    parquet = "parquet"
    database = "database"

class ExperimentConfig(BaseModel):
    """Base configuration for data science experiments."""
    # Project params
    experiment_name: str
    data_source: DataSourceEnum = DataSourceEnum.csv
    input_paths: Union[str, List[str]]
    output_dir: str = "outputs/"
    
    # Compute params
    random_seed: int = 42
    n_jobs: int = -1
    
    # Optional ML specific params
    batch_size: Optional[int] = None
    learning_rate: Optional[float] = None
    max_epochs: Optional[int] = None
    
    @field_validator("input_paths")
    def validate_input_paths(cls, paths):
        if isinstance(paths, str):
            paths = [paths]
        for p in paths:
            if not Path(p).exists():
                raise ValueError(f"Path does not exist: {p}")
        return paths
    
    @field_validator("output_dir")
    def validate_output_dir(cls, path):
        out_dir = Path(path)
        out_dir.mkdir(parents=True, exist_ok=True)
        return str(out_dir)