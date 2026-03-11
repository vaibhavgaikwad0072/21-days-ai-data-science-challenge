def generate_recommendations(anomalies, df):
    """Generate cost-saving recommendations based on detected anomalies."""
    recommendations = []
    
    # Track resources we've already recommended actions for to avoid duplicates
    processed_resources = set()
    
    for anomaly in anomalies:
        res_id = anomaly['resource_id']
        if res_id in processed_resources:
            continue
            
        if anomaly['type'] == 'Idle Resource':
            recommendations.append({
                'service': anomaly['service'],
                'resource_id': res_id,
                'problem': 'Idle Instance Detected (CPU < 5%)',
                'action': 'Stop or Terminate the instance',
                'estimated_savings': anomaly.get('cost', 50.0) # Assume some savings if cost not present
            })
            processed_resources.add(res_id)
            
        elif anomaly['type'] == 'Cost Spike':
            recommendations.append({
                'service': anomaly['service'],
                'resource_id': res_id,
                'problem': 'Unexpected Cost Spike Detected',
                'action': 'Investigate usage patterns and consider Reserved Instances or Spot Instances',
                'estimated_savings': round(anomaly['cost'] * 0.3, 2) # Estimate 30% savings with optimization
            })
            processed_resources.add(res_id)

    # General S3 recommendation (if S3 costs are high)
    s3_total = df[df['service_name'] == 'S3']['monthly_cost'].sum()
    if s3_total > 100:
        recommendations.append({
            'service': 'S3',
            'resource_id': 'all-s3-buckets',
            'problem': 'High S3 Storage Costs',
            'action': 'Move older data to S3 Glacier or set up Lifecycle Policies',
            'estimated_savings': round(s3_total * 0.4, 2)
        })

    # General RDS recommendation
    rds_total = df[df['service_name'] == 'RDS']['monthly_cost'].sum()
    if rds_total > 200:
        recommendations.append({
            'service': 'RDS',
            'resource_id': 'all-rds-instances',
            'problem': 'High Database Costs',
            'action': 'Downsize over-provisioned RDS instances or use Aurora Serverless',
            'estimated_savings': round(rds_total * 0.2, 2)
        })

    return recommendations

if __name__ == "__main__":
    # Test
    mock_anomalies = [
        {'type': 'Idle Resource', 'service': 'EC2', 'resource_id': 'ec2-res-0', 'cost': 150.0},
        {'type': 'Cost Spike', 'service': 'EC2', 'resource_id': 'ec2-res-1', 'cost': 300.0}
    ]
    # Dummy DF for testing S3/RDS logic
    import pandas as pd
    df = pd.DataFrame([{'service_name': 'S3', 'monthly_cost': 150}])
    
    recs = generate_recommendations(mock_anomalies, df)
    for r in recs:
        print(f"Action: {r['action']} (Savings: ${r['estimated_savings']})")
