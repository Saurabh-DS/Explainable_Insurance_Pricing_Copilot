import os

def generate_guidelines():
    guidelines_dir = "data/guidelines"
    os.makedirs(guidelines_dir, exist_ok=True)

    guidelines = {
        "age_policy.txt": """
        Underwriting Guidelines: Age Policy
        1. Drivers under 21 are considered high risk and may face a 50% premium surcharge.
        2. Drivers aged 21-25 are medium risk with a 20% surcharge.
        3. Drivers aged 26-60 are low risk.
        4. Drivers over 60 may see a slight increase in premium due to potential medical risks.
        """,
        "postcode_risk.txt": """
        Underwriting Guidelines: Geography
        1. Postcode risk is a decimal between 0 and 1.
        2. Risk > 0.8: High-crime or accident-prone area. Surcharge applies.
        3. Risk < 0.2: Safe rural area. Discount applies.
        """,
        "vehicle_group.txt": """
        Underwriting Guidelines: Vehicle Groups
        1. Vehicle groups range from 1 to 50.
        2. Groups 1-10: Economy cars, low premium.
        3. Groups 11-30: Family cars, moderate premium.
        4. Groups 31-50: Luxury and performance cars, high premium.
        """,
        "ncb_policy.txt": """
        Underwriting Guidelines: No Claims Bonus (NCB)
        1. 0 years NCB: No discount.
        2. 1-3 years NCB: 10-20% discount.
        3. 5+ years NCB: Up to 50% discount.
        4. Any claim in the last year resets NCB for certain policies.
        """,
        "claims_count.txt": """
        Underwriting Guidelines: Claims History
        1. 0 claims: Standard base premium.
        2. 1 claim: 15% surcharge.
        3. 2+ claims: 40% surcharge or potential declinature for high-performance vehicles.
        """
    }

    for filename, content in guidelines.items():
        with open(os.path.join(guidelines_dir, filename), "w") as f:
            f.write(content.strip())
    
    print(f"Generated {len(guidelines)} guideline files in {guidelines_dir}")

if __name__ == "__main__":
    generate_guidelines()
