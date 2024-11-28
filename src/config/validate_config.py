import os
import sys
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_setup import log_and_raise_error

class ConfigSchema(BaseModel):
    time_window: int = Field(..., ge=0, description="Time window must be 0 or a positive integer.")
    row_to_remove: Optional[str] = Field(None, description="Row to remove must be a valid datetime string or None.")
    time_column: str = Field(..., min_length=1, description="Time column must be a non-empty string.")
    mean_values: List[str] = Field(..., min_items=1, description="There must be at least one mean values.")
    conditions: Dict[str, Any] = Field(..., description="Conditions must be a dictionary with column-value pairs.")
    margins: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="Margins must contain at least one entry, with column names and margin values."
    )

    @staticmethod
    def validate_margin_entry(margin_entry: Dict[str, Any]) -> None:
        """
      This method validates an individual margin entry.
      """
        if "column" not in margin_entry or not isinstance(margin_entry["column"], str):
            raise ValueError("Each margin entry must have a 'column' key with a string value.")
        if "margin" not in margin_entry or not isinstance(margin_entry["margin"], (int, float)):
            raise ValueError("Each margin entry must have a 'margin' key with an int or float value.")
        if margin_entry["margin"] <= 0:
            raise ValueError("The 'margin' value must be greater than 0.")

    @classmethod
    def validate_margins(cls, margins: List[Dict[str, Any]]) -> None:
        """
      This method validates the entire margins list.
      """
        for margin in margins:
            cls.validate_margin_entry(margin)

    @classmethod
    def validate(cls, config: dict) -> "ConfigSchema":
        """
      This method performs custom validation for the entire config.
      """
        # validate margins
        cls.validate_margins(config.get("margins", []))
        # use BaseModel's validation for remaining fields
        return cls(**config)


def validate_config(config: dict):
    """
  This function validates the loaded configuration.
    """
    try:
        validated_config = ConfigSchema.validate(config)
        return validated_config.dict()
    except ValidationError as e:
        log_and_raise_error(f"Configuration validation failed: {e}")
    except ValueError as ve:
        log_and_raise_error(f"Configuration validation error: {ve}")