"""
Machine Learning Engine for Pattern Tracking System
Provides anomaly detection, trend analysis, and pattern recognition
"""
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class MLEngine:
    """Machine Learning analysis engine"""
    
    def __init__(self, threshold: float = 2.0):
        self.anomaly_threshold = threshold
    
    def detect_anomalies(self, daily_counts: Dict[str, int]) -> Dict[str, any]:
        """
        Detect anomalies in daily report counts using statistical methods
        
        Returns:
            Dict with anomaly information
        """
        if len(daily_counts) < 5:
            return {
                'anomalies_detected': False,
                'reason': 'Insufficient data (need at least 5 days)',
                'anomalous_dates': []
            }
        
        counts = list(daily_counts.values())
        mean = np.mean(counts)
        std = np.std(counts)
        
        if std == 0:
            return {
                'anomalies_detected': False,
                'reason': 'No variation in data',
                'anomalous_dates': [],
                'statistics': {
                    'mean': float(mean),
                    'std': float(std)
                }
            }
        
        # Detect anomalies (values > mean + threshold * std)
        threshold_value = mean + (self.anomaly_threshold * std)
        anomalies = []
        
        for date, count in daily_counts.items():
            if count > threshold_value:
                anomalies.append({
                    'date': date,
                    'count': count,
                    'expected_range': f"{mean:.1f} ± {std:.1f}",
                    'severity': 'high' if count > (mean + 3 * std) else 'moderate'
                })
        
        return {
            'anomalies_detected': len(anomalies) > 0,
            'anomalous_dates': anomalies,
            'statistics': {
                'mean': float(mean),
                'std': float(std),
                'threshold': float(threshold_value)
            },
            'total_anomalies': len(anomalies)
        }
    
    def analyze_trends(self, daily_counts: Dict[str, int]) -> Dict[str, any]:
        """
        Analyze trends in report submissions over time
        
        Returns:
            Dict with trend analysis
        """
        if len(daily_counts) < 3:
            return {
                'trend': 'insufficient_data',
                'direction': 'unknown'
            }
        
        # Sort by date
        sorted_data = sorted(daily_counts.items())
        dates = [item[0] for item in sorted_data]
        counts = [item[1] for item in sorted_data]
        
        # Calculate linear regression slope
        x = np.arange(len(counts))
        y = np.array(counts)
        
        # Simple linear regression
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
        else:
            slope = 0
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend = 'stable'
            direction = 'no significant change'
        elif slope > 0:
            trend = 'increasing'
            direction = 'upward'
        else:
            trend = 'decreasing'
            direction = 'downward'
        
        # Calculate rate of change
        if len(counts) >= 2:
            recent_avg = np.mean(counts[-3:]) if len(counts) >= 3 else counts[-1]
            earlier_avg = np.mean(counts[:3]) if len(counts) >= 3 else counts[0]
            
            if earlier_avg > 0:
                change_rate = ((recent_avg - earlier_avg) / earlier_avg) * 100
            else:
                change_rate = 0
        else:
            change_rate = 0
        
        return {
            'trend': trend,
            'direction': direction,
            'slope': float(slope),
            'change_rate_percent': float(change_rate),
            'recent_average': float(np.mean(counts[-3:])) if len(counts) >= 3 else float(counts[-1]),
            'overall_average': float(np.mean(counts))
        }
    
    def identify_symptom_patterns(self, symptom_counts: Dict[str, int]) -> Dict[str, any]:
        """
        Identify patterns in symptom co-occurrence
        
        Returns:
            Dict with pattern analysis
        """
        total_symptoms = sum(symptom_counts.values())
        
        if total_symptoms == 0:
            return {
                'patterns_found': False,
                'dominant_symptoms': [],
                'rare_symptoms': []
            }
        
        # Calculate percentages
        symptom_percentages = {
            symptom: (count / total_symptoms) * 100 
            for symptom, count in symptom_counts.items()
        }
        
        # Sort by frequency
        sorted_symptoms = sorted(
            symptom_percentages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Identify dominant symptoms (>20% of total)
        dominant = [
            {'symptom': s, 'percentage': p, 'count': symptom_counts[s]}
            for s, p in sorted_symptoms if p > 20
        ]
        
        # Identify rare symptoms (<5% of total)
        rare = [
            {'symptom': s, 'percentage': p, 'count': symptom_counts[s]}
            for s, p in sorted_symptoms if p < 5 and symptom_counts[s] > 0
        ]
        
        return {
            'patterns_found': True,
            'dominant_symptoms': dominant,
            'rare_symptoms': rare,
            'most_common': sorted_symptoms[0][0] if sorted_symptoms else None,
            'distribution': [
                {'symptom': s, 'percentage': round(p, 2), 'count': symptom_counts[s]}
                for s, p in sorted_symptoms
            ]
        }
    
    def location_risk_analysis(self, location_counts: Dict[str, int]) -> Dict[str, any]:
        """
        Analyze risk levels by location
        
        Returns:
            Dict with location risk analysis
        """
        if not location_counts:
            return {
                'risk_levels': {},
                'high_risk_locations': [],
                'low_risk_locations': []
            }
        
        total_reports = sum(location_counts.values())
        counts = list(location_counts.values())
        mean = np.mean(counts)
        std = np.std(counts)
        
        risk_levels = {}
        high_risk = []
        low_risk = []
        
        for location, count in location_counts.items():
            percentage = (count / total_reports) * 100
            
            # Determine risk level
            if count > mean + std:
                risk = 'high'
                high_risk.append({'location': location, 'count': count, 'percentage': round(percentage, 2)})
            elif count < mean - std:
                risk = 'low'
                low_risk.append({'location': location, 'count': count, 'percentage': round(percentage, 2)})
            else:
                risk = 'moderate'
            
            risk_levels[location] = {
                'risk_level': risk,
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return {
            'risk_levels': risk_levels,
            'high_risk_locations': sorted(high_risk, key=lambda x: x['count'], reverse=True),
            'low_risk_locations': sorted(low_risk, key=lambda x: x['count']),
            'statistics': {
                'mean': float(mean),
                'std': float(std)
            }
        }
    
    def severity_analysis(self, severity_counts: Dict[str, int]) -> Dict[str, any]:
        """
        Analyze severity distribution
        
        Returns:
            Dict with severity analysis
        """
        total = sum(severity_counts.values())
        
        if total == 0:
            return {
                'alert_level': 'none',
                'distribution': {}
            }
        
        percentages = {
            severity: (count / total) * 100 
            for severity, count in severity_counts.items()
        }
        
        # Determine alert level
        severe_percentage = percentages.get('Severe', 0)
        moderate_percentage = percentages.get('Moderate', 0)
        
        if severe_percentage > 30:
            alert_level = 'critical'
        elif severe_percentage > 15 or moderate_percentage > 50:
            alert_level = 'warning'
        else:
            alert_level = 'normal'
        
        return {
            'alert_level': alert_level,
            'distribution': {
                severity: {
                    'count': count,
                    'percentage': round(percentages.get(severity, 0), 2)
                }
                for severity, count in severity_counts.items()
            },
            'recommendations': self._get_severity_recommendations(alert_level)
        }
    
    def _get_severity_recommendations(self, alert_level: str) -> List[str]:
        """Get recommendations based on severity alert level"""
        recommendations = {
            'critical': [
                'Immediate attention required',
                'Consider alerting health authorities',
                'Increase monitoring frequency',
                'Prepare emergency response protocols'
            ],
            'warning': [
                'Enhanced monitoring recommended',
                'Review reported symptoms for patterns',
                'Consider preventive health measures',
                'Keep medical resources available'
            ],
            'normal': [
                'Continue regular monitoring',
                'Maintain current health protocols',
                'Encourage preventive care'
            ]
        }
        return recommendations.get(alert_level, recommendations['normal'])
    
    def comprehensive_analysis(self, 
                               daily_counts: Dict[str, int],
                               symptom_counts: Dict[str, int],
                               location_counts: Dict[str, int],
                               severity_counts: Dict[str, int]) -> Dict[str, any]:
        """
        Perform comprehensive ML analysis
        
        Returns:
            Dict with all analysis results
        """
        return {
            'anomaly_detection': self.detect_anomalies(daily_counts),
            'trend_analysis': self.analyze_trends(daily_counts),
            'symptom_patterns': self.identify_symptom_patterns(symptom_counts),
            'location_risk': self.location_risk_analysis(location_counts),
            'severity_analysis': self.severity_analysis(severity_counts),
            'timestamp': datetime.now().isoformat()
        }
