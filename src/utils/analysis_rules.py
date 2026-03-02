"""Analysis rules and guidelines for A-Share MCP Agent."""

# Analysis Style Guidelines
ANALYSIS_STYLE = {
    "format": "professional_direct",
    "include_disclaimer": False,
    "decision_style": "clear_actionable",
    "multi_factor_analysis": True,
    "factors_to_consider": [
        "technical_analysis",
        "fundamental_analysis", 
        "policy_analysis",
        "market_sentiment",
        "risk_assessment"
    ],
    "output_requirements": {
        "provide_clear_recommendation": True,
        "recommendation_options": ["强烈买入", "买入", "观望", "卖出", "强烈卖出"],
        "include_price_targets": True,
        "include_support_resistance": True,
        "avoid_vague_language": True,
        "use_data_driven_reasoning": True
    }
}

# Technical Analysis Rules
TECHNICAL_RULES = {
    "moving_averages": {
        "ma5_weight": 0.25,
        "ma10_weight": 0.25, 
        "ma20_weight": 0.30,
        "ma30_weight": 0.20
    },
    "rsi_thresholds": {
        "overbought": 70,
        "oversold": 30,
        "neutral_low": 40,
        "neutral_high": 60
    },
    "trend_signals": {
        "strong_buy": "price > ma5 > ma10 > ma20",
        "buy": "price > ma5 and ma5 > ma10", 
        "sell": "price < ma5 and ma5 < ma10",
        "strong_sell": "price < ma5 < ma10 < ma20"
    }
}

# Multi-Factor Weighting
FACTOR_WEIGHTS = {
    "technical_analysis": 0.40,
    "fundamental_analysis": 0.25,
    "policy_analysis": 0.20,
    "market_sentiment": 0.15
}

# Decision Thresholds
DECISION_THRESHOLDS = {
    "strong_buy_diff": 2.0,
    "buy_diff": 0.5,
    "sell_diff": 0.5, 
    "strong_sell_diff": 2.0
}