from agent.graph import run_agent

def get_user_input():
    print("\n📝 Please enter customer details:")
    try:
        age = int(input("  - Age: "))
        postcode_risk = float(input("  - Postcode Risk (0.0 to 1.0): "))
        vehicle_group = int(input("  - Vehicle Group (1 to 50): "))
        claims_count = int(input("  - Number of Claims (0 to 5): "))
        ncb_years = int(input("  - NCB Years (0 to 10): "))
        
        return {
            'age': age,
            'postcode_risk': postcode_risk,
            'vehicle_group': vehicle_group,
            'claims_count': claims_count,
            'ncb_years': ncb_years
        }
    except ValueError:
        print("❌ Invalid input. Using default sample profile.")
        return {
            'age': 25,
            'postcode_risk': 0.5,
            'vehicle_group': 15,
            'claims_count': 0,
            'ncb_years': 3
        }

def main():
    print("="*60)
    print("🚀 Explainable Insurance Pricing Copilot")
    print("="*60)
    
    # Get user input
    profile = get_user_input()
    
    print("\n🔍 Analyzing Profile:")
    for k, v in profile.items():
        print(f"  - {k}: {v}")
    
    print("\n🤖 Agent is analyzing the profile (calling ML model, RAG, and DB)...")
    
    try:
        explanation = run_agent(profile)
        print("\n" + "="*60)
        print("💡 PRECISE EXPLANATION")
        print("="*60)
        print(explanation)
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error running agent: {e}")
        print("Note: Ensure Ollama is running and 'llama3' model is pulled.")

if __name__ == "__main__":
    main()
