from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import statistics
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class QueryMetrics:
    query: str
    latency: float
    relevance_score: float
    cache_hit: bool
    error: Optional[str] = None
    user_feedback: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

class RAGMetrics:
    """Monitors and tracks RAG system performance metrics"""
    
    def __init__(self):
        self.metrics: List[QueryMetrics] = []
        self.cache_hits = 0
        self.total_queries = 0
        self.error_counts: Dict[str, int] = {}
        
    def track_query(self, 
                   query: str,
                   latency: float,
                   relevance_score: float,
                   cache_hit: bool,
                   error: Optional[str] = None,
                   user_feedback: Optional[int] = None):
        """
        Track metrics for a single query
        
        Args:
            query: The user's question
            latency: Response time in seconds
            relevance_score: Average relevance score of retrieved documents
            cache_hit: Whether response was served from cache
            error: Error message if any
            user_feedback: Optional user rating (1-5)
        """
        try:
            metrics = QueryMetrics(
                query=query,
                latency=latency,
                relevance_score=relevance_score,
                cache_hit=cache_hit,
                error=error,
                user_feedback=user_feedback
            )
            
            self.metrics.append(metrics)
            self.total_queries += 1
            
            if cache_hit:
                self.cache_hits += 1
            
            if error:
                self.error_counts[error] = self.error_counts.get(error, 0) + 1
                
            logger.info(f"Tracked metrics for query: {query}")
            
        except Exception as e:
            logger.error(f"Error tracking metrics: {str(e)}")
    
    def get_performance_stats(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Calculate performance statistics for the given time window"""
        try:
            cutoff_time = datetime.now() - time_window
            recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
            
            if not recent_metrics:
                return {"message": "No metrics available for the specified time window"}
            
            # Calculate statistics
            latencies = [m.latency for m in recent_metrics]
            relevance_scores = [m.relevance_score for m in recent_metrics]
            feedback_scores = [m.user_feedback for m in recent_metrics if m.user_feedback is not None]
            
            stats = {
                "query_count": len(recent_metrics),
                "average_latency": statistics.mean(latencies),
                "p95_latency": statistics.quantiles(latencies, n=20)[18],  # 95th percentile
                "average_relevance": statistics.mean(relevance_scores),
                "cache_hit_rate": self.cache_hits / self.total_queries if self.total_queries > 0 else 0,
                "error_rate": len([m for m in recent_metrics if m.error]) / len(recent_metrics),
                "common_errors": dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
            if feedback_scores:
                stats["average_user_rating"] = statistics.mean(feedback_scores)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating performance stats: {str(e)}")
            return {"error": str(e)}
    
    def generate_report(self, time_window: timedelta = timedelta(hours=24)) -> str:
        """Generate a human-readable performance report"""
        try:
            stats = self.get_performance_stats(time_window)
            
            report = [
                "RAG System Performance Report",
                "=" * 30,
                f"\nTime Window: Last {time_window.total_hours()} hours",
                f"Total Queries: {stats['query_count']}",
                f"\nPerformance Metrics:",
                f"- Average Latency: {stats['average_latency']:.2f}s",
                f"- 95th Percentile Latency: {stats['p95_latency']:.2f}s",
                f"- Average Relevance Score: {stats['average_relevance']:.2f}",
                f"- Cache Hit Rate: {stats['cache_hit_rate']*100:.1f}%",
                f"- Error Rate: {stats['error_rate']*100:.1f}%",
            ]
            
            if "average_user_rating" in stats:
                report.append(f"- Average User Rating: {stats['average_user_rating']:.1f}/5")
            
            if stats['common_errors']:
                report.extend([
                    "\nMost Common Errors:",
                    *[f"- {error}: {count} occurrences" 
                      for error, count in stats['common_errors'].items()]
                ])
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return f"Error generating report: {str(e)}" 