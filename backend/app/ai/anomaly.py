"""
Anomaly detection for expense tracking.
Identifies unusual spending patterns using statistical methods.

Techniques:
- Z-score based detection for individual expenses
- IQR (Interquartile Range) for category-level outliers
- Contextual anomaly detection (day-of-week, time patterns)
"""

from typing import Dict, List, Optional
from collections import defaultdict
import math


def calculate_stats(values: List[float]) -> Dict:
    """Calculate mean, std deviation, median, and IQR."""
    if not values:
        return {"mean": 0, "std": 0, "median": 0, "q1": 0, "q3": 0, "iqr": 0}
    
    n = len(values)
    sorted_vals = sorted(values)
    
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / max(n - 1, 1)
    std = math.sqrt(variance)
    
    median = sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
    
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1
    
    return {
        "mean": round(mean, 2),
        "std": round(std, 2),
        "median": round(median, 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2)
    }


def detect_anomalies_zscore(
    expenses: List[Dict],
    threshold: float = 2.0
) -> List[Dict]:
    """
    Detect anomalous expenses using Z-score method.
    
    An expense is flagged if its amount is more than `threshold` 
    standard deviations from the category mean.
    
    Args:
        expenses: List of expense dicts with 'amount', 'category', 'date', 'description'
        threshold: Z-score threshold (default 2.0 = ~95% confidence)
    
    Returns:
        List of anomalous expenses with severity scores
    """
    if len(expenses) < 3:
        return []
    
    # Group by category
    category_amounts: Dict[str, List[float]] = defaultdict(list)
    for exp in expenses:
        category_amounts[exp["category"]].append(exp["amount"])
    
    # Calculate stats per category
    category_stats = {
        cat: calculate_stats(amounts) 
        for cat, amounts in category_amounts.items()
    }
    
    anomalies = []
    
    for exp in expenses:
        cat = exp["category"]
        stats = category_stats[cat]
        
        if stats["std"] == 0 or len(category_amounts[cat]) < 3:
            continue
        
        z_score = (exp["amount"] - stats["mean"]) / stats["std"]
        
        if abs(z_score) >= threshold:
            severity = "high" if abs(z_score) >= 3 else "medium"
            
            anomalies.append({
                "expense_id": exp.get("id", ""),
                "amount": exp["amount"],
                "category": cat,
                "date": exp.get("date", ""),
                "description": exp.get("description", ""),
                "z_score": round(z_score, 2),
                "category_mean": stats["mean"],
                "category_std": stats["std"],
                "severity": severity,
                "reason": f"Amount ₹{exp['amount']} is {abs(round(z_score, 1))}x standard deviations "
                         f"{'above' if z_score > 0 else 'below'} your average "
                         f"₹{stats['mean']} for {cat}"
            })
    
    # Sort by severity (high first) then z_score
    anomalies.sort(key=lambda x: (0 if x["severity"] == "high" else 1, -abs(x["z_score"])))
    
    return anomalies


def detect_anomalies_iqr(
    expenses: List[Dict],
    multiplier: float = 1.5
) -> List[Dict]:
    """
    Detect anomalies using IQR (Interquartile Range) method.
    More robust against extreme outliers than Z-score.
    
    Outlier if: amount > Q3 + multiplier * IQR
    """
    if len(expenses) < 4:
        return []
    
    category_amounts: Dict[str, List[float]] = defaultdict(list)
    for exp in expenses:
        category_amounts[exp["category"]].append(exp["amount"])
    
    category_stats = {
        cat: calculate_stats(amounts) 
        for cat, amounts in category_amounts.items()
    }
    
    anomalies = []
    
    for exp in expenses:
        cat = exp["category"]
        stats = category_stats[cat]
        
        if len(category_amounts[cat]) < 4 or stats["iqr"] == 0:
            continue
        
        upper_fence = stats["q3"] + multiplier * stats["iqr"]
        lower_fence = stats["q1"] - multiplier * stats["iqr"]
        
        if exp["amount"] > upper_fence:
            anomalies.append({
                "expense_id": exp.get("id", ""),
                "amount": exp["amount"],
                "category": cat,
                "date": exp.get("date", ""),
                "description": exp.get("description", ""),
                "upper_fence": round(upper_fence, 2),
                "severity": "high" if exp["amount"] > stats["q3"] + 3 * stats["iqr"] else "medium",
                "reason": f"Amount ₹{exp['amount']} exceeds the upper limit "
                         f"₹{round(upper_fence, 2)} for {cat} spending"
            })
    
    return anomalies


def get_spending_insights(
    expenses: List[Dict],
    budgets: Dict[str, float]
) -> List[Dict]:
    """
    Generate smart spending insights based on patterns.
    """
    insights = []
    
    if not expenses:
        return [{"type": "info", "message": "No expenses recorded yet. Start tracking to get insights!"}]
    
    # Category analysis
    category_totals: Dict[str, float] = defaultdict(float)
    category_counts: Dict[str, int] = defaultdict(int)
    
    for exp in expenses:
        category_totals[exp["category"]] += exp["amount"]
        category_counts[exp["category"]] += 1
    
    total_spent = sum(category_totals.values())
    
    # Find dominant category
    if category_totals:
        top_category = max(category_totals, key=category_totals.get)
        top_pct = round((category_totals[top_category] / total_spent) * 100, 1) if total_spent > 0 else 0
        
        if top_pct > 40:
            insights.append({
                "type": "warning",
                "category": top_category,
                "message": f"{top_category} accounts for {top_pct}% of your spending. "
                          f"Consider setting a stricter budget for this category."
            })
    
    # Budget vs actual
    for cat, budget_amount in budgets.items():
        spent = category_totals.get(cat, 0)
        if budget_amount > 0:
            usage_pct = (spent / budget_amount) * 100
            if usage_pct >= 90:
                insights.append({
                    "type": "alert",
                    "category": cat,
                    "message": f"You've used {round(usage_pct, 1)}% of your {cat} budget "
                              f"(₹{round(spent, 2)} / ₹{budget_amount})"
                })
            elif usage_pct <= 30 and spent > 0:
                insights.append({
                    "type": "positive",
                    "category": cat,
                    "message": f"Great discipline on {cat}! Only {round(usage_pct, 1)}% used."
                })
    
    # Frequency insights
    if category_counts:
        most_frequent = max(category_counts, key=category_counts.get)
        insights.append({
            "type": "info",
            "category": most_frequent,
            "message": f"Most frequent expense category: {most_frequent} "
                      f"({category_counts[most_frequent]} transactions)"
        })
    
    # Average transaction size
    avg_transaction = round(total_spent / len(expenses), 2) if expenses else 0
    insights.append({
        "type": "info",
        "message": f"Average transaction size: ₹{avg_transaction}"
    })
    
    return insights
