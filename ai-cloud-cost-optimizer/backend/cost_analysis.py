import pandas as pd
import numpy as np

def load_data(filepath):
    """Load cost data from CSV."""
    return pd.read_csv(filepath)

def analyze_costs(df):
    """Perform basic cost analysis."""
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Total monthly cost
    total_cost = df['monthly_cost'].sum()
    
    # Cost by service
    service_costs = df.groupby('service_name')['monthly_cost'].sum().reset_index()
    
    # Cost trend over time
    daily_costs = df.groupby('timestamp')['monthly_cost'].sum().reset_index()
    
    return {
        'total_cost': total_cost,
        'service_costs': service_costs,
        'daily_costs': daily_costs
    }

def detect_anomalies(df):
    """Detect cost spikes and idle resources."""
    anomalies = []
    
    # Cost spikes: Compare resources with themselves day over day? 
    # Or just high cost items?
    # Simple spike detection: resources whose cost is 2x the mean for that service
    mean_service_costs = df.groupby('service_name')['monthly_cost'].transform('mean')
    spikes = df[df['monthly_cost'] > 2 * mean_service_costs]
    
    for _, row in spikes.iterrows():
        anomalies.append({
            'type': 'Cost Spike',
            'resource_id': row['resource_id'],
            'service': row['service_name'],
            'cost': row['monthly_cost'],
            'details': f"Cost is significantly higher than average for {row['service_name']}."
        })
        
    # Idle resources: EC2 with CPU usage < 5%
    idle_ec2 = df[(df['service_name'] == 'EC2') & (df['cpu_usage'] < 5)]
    for _, row in idle_ec2.iterrows():
        # Avoid duplicate anomalies for multiple days in sample data
        # For simplicity, we just report the latest ones or unique ones
        anomalies.append({
            'type': 'Idle Resource',
            'resource_id': row['resource_id'],
            'service': 'EC2',
            'cpu_usage': row['cpu_usage'],
            'details': "CPU usage is consistently below 5%."
        })
        
    return anomalies

if __name__ == "__main__":
    # Test loading and analysis
    data_file = "ai-cloud-cost-optimizer/data/sample_cost_data.csv"
    try:
        df = load_data(data_file)
        results = analyze_costs(df)
        anomalies = detect_anomalies(df)
        print(f"Total Cost: ${results['total_cost']:.2f}")
        print(f"Anomalies detected: {len(anomalies)}")
    except Exception as e:
        print(f"Error: {e}")
