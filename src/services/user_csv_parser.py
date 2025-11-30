import csv
from typing import List, Dict, Any

class UserCSVParser:
    """
    Strategy for parsing User CSV files.
    
    This class is responsible for parsing the raw CSV content and returning
    a list of dictionaries representing the rows. It handles basic validation
    of the CSV structure (headers).
    """
    
    REQUIRED_COLUMNS = {'username', 'password', 'role', 'student_id', 'name', 'email'}

    def parse(self, file_stream) -> List[Dict[str, Any]]:
        """
        Parse the CSV file stream.

        Args:
            file_stream: A file-like object containing the CSV data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents a row in the CSV.

        Raises:
            ValueError: If the CSV is missing required columns.
        """
        # Reset stream position
        if hasattr(file_stream, 'seek'):
            file_stream.seek(0)
            
        reader = csv.DictReader(file_stream)
        
        # Validate headers
        if not reader.fieldnames or not self.REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing required columns. Expected: {self.REQUIRED_COLUMNS}")
            
        return [row for row in reader]
