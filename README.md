Financial Anomaly Detection Research

1. Research Objective
This project aims to simulate cross-border financial batch processing logs 
and explore anomaly detection mechanisms in enterprise IT operations.
Based on practical observations from financial information system monitoring, 
this research focuses on identifying abnormal job execution behaviors, 
dependency failures, and operational risks in batch processing environments.
The project further attempts to analyze process relationships between jobs 
and establish a prototype framework for risk monitoring and operational diagnostics.

2. Key Features
- Synthetic financial batch log generation
- Automated anomaly classification
- Cross-branch risk analysis
- Process relationship analysis
- Visualization dashboard for operational monitoring

3. Project Architecture

Simulated Batch Logs
        ↓
Anomaly Classification
        ↓
Process Dependency Analysis
        ↓
Visualization Dashboard
        ↓
Operational Risk Monitoring

4. How to Run
1. Clone this repository
2. Run `Generate_data.py` to generate synthetic logs
3. Run `Analyze_data.py` to perform anomaly analysis and visualization

5. Future Work
- Process mining integration
- Isolation Forest anomaly detection
- Dynamic risk scoring
- Automated forensic analysis
- SIEM integration
- Real-time alert mechanisms

6. Dashboard Overview
Below is the monitoring dashboard generated from the simulated financial batch processing logs.
<img width="1900" height="985" alt="image" src="https://github.com/user-attachments/assets/b8e6d4d6-c01f-4f55-b070-e6439313bb47" />

The top section presents the total number of simulated batch operations, including a summary of network related and non network related anomalies.

The left panel displays a branch level breakdown of anomaly categories and incident counts, allowing cross branch operational risk comparison.

The bar chart on the right visualizes the distribution of anomaly events across different incident types, helping identify high-frequency operational risks and potential process bottlenecks.

