from typing import List, Dict, Any
import logging

from ..models.shipment import Shipment
from ..interfaces import ShipmentRepository

logger = logging.getLogger(__name__)

class ShipmentAnalyticsService:
    """Domain service for shipment analytics and business intelligence"""
    
    def __init__(self, repository: ShipmentRepository):
        self.repository = repository
    
    def analyze_profitability_by_route(self, shipments: List[Shipment]) -> Dict[str, Dict[str, float]]:
        """
        Analyze profitability by shipping route
        
        Args:
            shipments: List of Shipment objects to analyze
            
        Returns:
            Dictionary with route as key and metrics as values
        """
        logger.info(f"Analyzing profitability for {len(shipments)} shipments across routes")
        
        route_metrics = {}
        
        for shipment in shipments:
            route = shipment.route
            if route not in route_metrics:
                route_metrics[route] = {
                    'total_shipments': 0,
                    'total_profit': 0,
                    'total_revenue': 0,
                    'total_cost': 0,
                    'avg_profit_margin': 0,
                    'avg_duration': 0
                }
            
            metrics = route_metrics[route]
            metrics['total_shipments'] += 1
            metrics['total_profit'] += shipment.profit or 0
            metrics['total_revenue'] += shipment.revenue or 0
            metrics['total_cost'] += shipment.cost or 0
            
        # Calculate averages
        for route, metrics in route_metrics.items():
            if metrics['total_shipments'] > 0:
                route_shipments = [s for s in shipments if s.route == route]
                
                # Calculate average profit margin
                profit_margins = [s.profit_margin for s in route_shipments if s.profit_margin is not None]
                metrics['avg_profit_margin'] = sum(profit_margins) / len(profit_margins) if profit_margins else 0
                
                # Calculate average duration
                durations = [s.shipping_duration_days for s in route_shipments if s.shipping_duration_days is not None]
                metrics['avg_duration'] = sum(durations) / len(durations) if durations else 0
                
                # Round for readability
                metrics['avg_profit_margin'] = round(metrics['avg_profit_margin'], 2)
                metrics['avg_duration'] = round(metrics['avg_duration'], 2)
        
        logger.info(f"Analyzed {len(route_metrics)} unique routes")
        return route_metrics
    
    def analyze_temporal_trends(self, shipments: List[Shipment]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze shipment trends over time (monthly, quarterly)
        
        Args:
            shipments: List of Shipment objects to analyze
            
        Returns:
            Dictionary with temporal analysis
        """
        logger.info("Analyzing temporal trends")
        
        monthly_metrics = {}
        quarterly_metrics = {}
        
        for shipment in shipments:
            if not shipment.shipping_date:
                continue
                
            # Monthly analysis
            month_key = f"{shipment.year}-{shipment.month:02d}"
            if month_key not in monthly_metrics:
                monthly_metrics[month_key] = {
                    'shipments': 0,
                    'total_revenue': 0,
                    'total_cost': 0,
                    'total_profit': 0,
                    'avg_profit_margin': 0,
                    'profitable_shipments': 0
                }
            
            month_metrics = monthly_metrics[month_key]
            month_metrics['shipments'] += 1
            month_metrics['total_revenue'] += shipment.revenue or 0
            month_metrics['total_cost'] += shipment.cost or 0
            month_metrics['total_profit'] += shipment.profit or 0
            if shipment.is_profitable:
                month_metrics['profitable_shipments'] += 1
            
            # Quarterly analysis
            quarter_key = f"{shipment.year}-Q{shipment.quarter}"
            if quarter_key not in quarterly_metrics:
                quarterly_metrics[quarter_key] = {
                    'shipments': 0,
                    'total_revenue': 0,
                    'total_cost': 0,
                    'total_profit': 0,
                    'avg_profit_margin': 0,
                    'profitable_shipments': 0
                }
            
            quarter_metrics = quarterly_metrics[quarter_key]
            quarter_metrics['shipments'] += 1
            quarter_metrics['total_revenue'] += shipment.revenue or 0
            quarter_metrics['total_cost'] += shipment.cost or 0
            quarter_metrics['total_profit'] += shipment.profit or 0
            if shipment.is_profitable:
                quarter_metrics['profitable_shipments'] += 1
        
        # Calculate averages
        for metrics in monthly_metrics.values():
            if metrics['shipments'] > 0:
                metrics['avg_profit_margin'] = round((metrics['total_profit'] / metrics['total_revenue'] * 100) if metrics['total_revenue'] > 0 else 0, 2)
                metrics['profitability_rate'] = round((metrics['profitable_shipments'] / metrics['shipments'] * 100), 2)
        
        for metrics in quarterly_metrics.values():
            if metrics['shipments'] > 0:
                metrics['avg_profit_margin'] = round((metrics['total_profit'] / metrics['total_revenue'] * 100) if metrics['total_revenue'] > 0 else 0, 2)
                metrics['profitability_rate'] = round((metrics['profitable_shipments'] / metrics['shipments'] * 100), 2)
        
        return {
            'monthly': monthly_metrics,
            'quarterly': quarterly_metrics
        }
    
    def identify_optimization_opportunities(self, shipments: List[Shipment]) -> Dict[str, Any]:
        """
        Identify business optimization opportunities based on shipment analysis
        
        Args:
            shipments: List of Shipment objects to analyze
            
        Returns:
            Dictionary with optimization recommendations
        """
        logger.info("Identifying optimization opportunities")
        
        opportunities = {
            'cost_reduction_routes': [],
            'price_increase_candidates': [],
            'process_improvement_needed': [],
            'high_performers': [],
            'summary': {}
        }
        
        route_metrics = self.analyze_profitability_by_route(shipments)
        
        low_margin_routes = []
        high_performing_routes = []
        slow_routes = []
        
        for route, metrics in route_metrics.items():
            # Low margin routes might need cost reduction
            if metrics['avg_profit_margin'] < 10:
                opportunities['cost_reduction_routes'].append({
                    'route': route,
                    'profit_margin': metrics['avg_profit_margin'],
                    'total_shipments': metrics['total_shipments'],
                    'total_profit': metrics['total_profit']
                })
                low_margin_routes.append(route)
            
            # High-performing routes might support price increases
            if metrics['avg_profit_margin'] > 30 and metrics['avg_duration'] < 20:
                opportunities['price_increase_candidates'].append({
                    'route': route,
                    'profit_margin': metrics['avg_profit_margin'],
                    'avg_duration': metrics['avg_duration'],
                    'total_revenue': metrics['total_revenue']
                })
                high_performing_routes.append(route)
            
            # Long duration routes need process improvement
            if metrics['avg_duration'] > 45:
                opportunities['process_improvement_needed'].append({
                    'route': route,
                    'avg_duration': metrics['avg_duration'],
                    'total_shipments': metrics['total_shipments'],
                    'profit_margin': metrics['avg_profit_margin']
                })
                slow_routes.append(route)
            
            # Identify consistently high performers
            if (metrics['avg_profit_margin'] > 25 and 
                metrics['avg_duration'] < 30 and 
                metrics['total_shipments'] >= 3):
                opportunities['high_performers'].append({
                    'route': route,
                    'profit_margin': metrics['avg_profit_margin'],
                    'avg_duration': metrics['avg_duration'],
                    'total_shipments': metrics['total_shipments']
                })
        
        # Generate summary insights
        opportunities['summary'] = {
            'total_routes_analyzed': len(route_metrics),
            'low_margin_routes_count': len(low_margin_routes),
            'high_performing_routes_count': len(high_performing_routes),
            'slow_routes_count': len(slow_routes),
            'optimization_potential': len(low_margin_routes) + len(slow_routes),
            'recommendations_priority': self._prioritize_recommendations(opportunities)
        }
        
        logger.info(f"Identified {opportunities['summary']['optimization_potential']} optimization opportunities")
        return opportunities
    
    def generate_business_insights(self, shipments: List[Shipment]) -> Dict[str, Any]:
        """
        Generate comprehensive business insights report
        
        Args:
            shipments: List of Shipment objects to analyze
            
        Returns:
            Comprehensive business insights dictionary
        """
        logger.info("Generating comprehensive business insights")
        
        route_analysis = self.analyze_profitability_by_route(shipments)
        temporal_analysis = self.analyze_temporal_trends(shipments)
        optimization_opportunities = self.identify_optimization_opportunities(shipments)
        
        # Calculate overall business health metrics
        total_shipments = len(shipments)
        profitable_count = sum(1 for s in shipments if s.is_profitable)
        high_margin_count = sum(1 for s in shipments if s.is_high_margin)
        delayed_count = sum(1 for s in shipments if s.is_delayed)
        
        business_health = {
            'profitability_score': round((profitable_count / total_shipments * 100), 2) if total_shipments > 0 else 0,
            'efficiency_score': round(((total_shipments - delayed_count) / total_shipments * 100), 2) if total_shipments > 0 else 0,
            'margin_quality_score': round((high_margin_count / total_shipments * 100), 2) if total_shipments > 0 else 0
        }
        
        # Overall business health score (weighted average)
        business_health['overall_score'] = round(
            (business_health['profitability_score'] * 0.4 +
             business_health['efficiency_score'] * 0.3 +
             business_health['margin_quality_score'] * 0.3), 2
        )
        
        insights = {
            'business_health': business_health,
            'route_analysis': route_analysis,
            'temporal_analysis': temporal_analysis,
            'optimization_opportunities': optimization_opportunities,
            'key_insights': self._generate_key_insights(shipments, route_analysis, business_health)
        }
        
        logger.info("Business insights report generated successfully")
        return insights
    
    def _prioritize_recommendations(self, opportunities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prioritize optimization recommendations based on impact potential"""
        recommendations = []
        
        # High impact: Cost reduction on high-volume low-margin routes
        high_volume_low_margin = [r for r in opportunities['cost_reduction_routes'] 
                                if r['total_shipments'] >= 5]
        if high_volume_low_margin:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Cost Reduction',
                'description': f"Focus on {len(high_volume_low_margin)} high-volume, low-margin routes",
                'impact': 'High revenue impact potential'
            })
        
        # Medium impact: Process improvement for delayed routes
        if opportunities['process_improvement_needed']:
            recommendations.append({
                'priority': 'MEDIUM', 
                'action': 'Process Improvement',
                'description': f"Improve {len(opportunities['process_improvement_needed'])} slow routes",
                'impact': 'Customer satisfaction and efficiency gains'
            })
        
        # Low impact: Price increases on high performers
        if opportunities['price_increase_candidates']:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Price Optimization',
                'description': f"Consider price increases on {len(opportunities['price_increase_candidates'])} high-performing routes",
                'impact': 'Margin improvement with low risk'
            })
        
        return recommendations
    
    def _generate_key_insights(self, shipments: List[Shipment], route_analysis: Dict, business_health: Dict) -> List[str]:
        """Generate key business insights from the analysis"""
        insights = []
        
        # Profitability insight
        if business_health['profitability_score'] > 80:
            insights.append("🟢 Strong profitability across shipments - business is performing well")
        elif business_health['profitability_score'] > 60:
            insights.append("🟡 Moderate profitability - some room for improvement")
        else:
            insights.append("🔴 Low profitability - urgent attention needed on cost structure")
        
        # Route performance insight
        if route_analysis:
            best_route = max(route_analysis.items(), key=lambda x: x[1]['avg_profit_margin'])
            worst_route = min(route_analysis.items(), key=lambda x: x[1]['avg_profit_margin'])
            
            insights.append(f"🏆 Best performing route: {best_route[0]} ({best_route[1]['avg_profit_margin']:.1f}% margin)")
            insights.append(f"⚠️ Worst performing route: {worst_route[0]} ({worst_route[1]['avg_profit_margin']:.1f}% margin)")
        
        # Efficiency insight
        if business_health['efficiency_score'] > 85:
            insights.append("⚡ Excellent shipping efficiency - most deliveries are on time")
        elif business_health['efficiency_score'] > 70:
            insights.append("📈 Good shipping efficiency with room for improvement")
        else:
            insights.append("🐌 Shipping delays are impacting business - process review needed")
        
        return insights
