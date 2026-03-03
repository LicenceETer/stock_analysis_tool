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
        "use_data_driven_reasoning": True,
        "dynamic_technical_analysis": True  # 新增：动态技术分析规则
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
    },
    # 新增：动态支撑阻力位计算规则
    "dynamic_support_resistance": {
        "enable_dynamic_calculation": True,
        "current_price_priority": True,  # 当前价格优先于历史MA值
        "support_buffer_pct": 0.5,       # 支撑位缓冲百分比
        "resistance_buffer_pct": 0.5     # 阻力位缓冲百分比
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

# Price Target Calculation Rules - 新增修正规则
PRICE_TARGET_RULES = {
    "buy_scenario": {
        "target_formula": "current_price + (current_price - ma5) * 1.5",
        "stop_loss_formula": "current_price * 0.95",
        "support_formula": "min(ma20, ma30)",
        "resistance_formula": "ma5"
    },
    "sell_scenario": {
        "support_formula": "min(ma20, ma30)",
        "resistance_formula": "ma5"
    },
    # 关键修正：动态买入区间计算
    "dynamic_buy_zone": {
        "enabled": True,
        "logic": "如果当前价格 < 原支撑位，则实际理想买入区间为 [当前价格 - 缓冲, 原支撑位]",
        "buffer_pct": 1.0,  # 1%的缓冲区间
        "max_discount": 5.0  # 最大折扣不超过5%
    }
}