import csv
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class DeviceCondition:
    condition_rating: int = 5  # On a scale of 1-10 (5 = Moderate)
    age_years: float = 5.0     # Current age in years
    expected_lifespan: float = 7.0  # Expected lifespan in years
    recyclability_percentage: float = 80.0  # Recyclability percentage

class WeightBasedEISCalculator:
    def __init__(self, csv_path: str, device_condition: DeviceCondition = None):
        """
        Initialize calculator with materials data and device condition.
        
        Args:
            csv_path: Path to CSV file containing material data
            device_condition: Device condition parameters
        """
        self.csv_path = csv_path
        self.device_condition = device_condition or DeviceCondition()
        self.materials_data = {}
        self.total_mi = 0
        self.total_weight = 0

    def calculate_material_impact_and_weight(self) -> Tuple[float, float]:
        """Calculate total Material Impact (MI) and total weight from material data."""
        try:
            with open(self.csv_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    element = row['Element']
                    impact_factor = float(row['Impact Factor (Approx.)'])
                    quantity = float(row['Quantity (gm)'])
                    
                    # Calculate material impact
                    mi = impact_factor * quantity
                    self.total_mi += mi
                    
                    # Calculate total weight
                    self.total_weight += quantity
                    
                    # Store material data
                    self.materials_data[element] = {
                        'quantity': quantity,
                        'impact_factor': impact_factor,
                        'material_impact': mi,
                        'weight_percentage': 0  # Will be calculated after total weight is known
                    }
            
            # Calculate weight percentages
            for element in self.materials_data:
                self.materials_data[element]['weight_percentage'] = (
                    (self.materials_data[element]['quantity'] / self.total_weight) * 100
                )
            
            return self.total_mi, self.total_weight

        except Exception as e:
            raise Exception(f"Error calculating Material Impact and Weight: {str(e)}")

    def calculate_condition_adjustment(self) -> float:
        """
        Calculate Condition Adjustment (CA) factor.
        CA = 1 - (condition_rating / 10)
        """
        return 1 - (self.device_condition.condition_rating / 10)

    def calculate_age_factor(self) -> float:
        """
        Calculate Age Factor (AF).
        AF = current_age / expected_lifespan
        """
        return self.device_condition.age_years / self.device_condition.expected_lifespan

    def calculate_recyclability_factor(self) -> float:
        """
        Calculate Recyclability Factor (RF).
        RF = 1 - (recyclability_percentage / 100)
        """
        return 1 - (self.device_condition.recyclability_percentage / 100)

    def calculate_eis(self) -> float:
        """
        Calculate final Environmental Impact Score using the weight-based formula:
        EIS = (total_weight × MI × CA × AF) × RF
        """
        # Calculate all factors
        mi, total_weight = self.calculate_material_impact_and_weight()
        ca = self.calculate_condition_adjustment()
        af = self.calculate_age_factor()
        rf = self.calculate_recyclability_factor()
        
        # Compute the Environmental Impact Score
        eis = (total_weight * mi * ca * af) * rf
        return eis  # Return only the numeric value of the EIS

# Example usage
if __name__ == "__main__":
    # Create a device condition object with default values
    device_condition = DeviceCondition(
        condition_rating=5,      # Moderate condition (5/10)
        age_years=5.0,          # 5 years old
        expected_lifespan=7.0,   # Expected lifespan of 7 years
        recyclability_percentage=80.0  # 80% recyclable
    )
    
    # Initialize calculator
    calculator = WeightBasedEISCalculator(
        csv_path="./smartPhone.csv",
        device_condition=device_condition
    )
    
    # Print the numeric EIS value
    print(calculator.calculate_eis())