"""Professional multi-factor stock analysis with clear recommendations."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import analysis rules
from ..utils.analysis_rules import ANALYSIS_STYLE, TECHNICAL_RULES, FACTOR_WEIGHTS, DECISION_THRESHOLDS


def generate_professional_analysis_report(symbol: str) -> Dict[str, Any]:
    """Generate professional analysis report with clear buy/sell recommendation.
    
    Args:
        symbol: Stock code to analyze
        
    Returns:
        Complete professional analysis report with clear recommendation
    """
    from .market_data_simple import get_realtime_quotes_simple
    from .corrected_akshare import calculate_technical_indicators_corrected
    from .news import get_market_news
    
    try:
        # Get real-time market data
        market_data = get_realtime_quotes_simple(symbol)
        current_price = market_data['price']
        change_percent = market_data['change_percent']
        
        # Get technical indicators
        tech_indicators = calculate_technical_indicators_corrected(symbol)
        
        # Get news for fundamental/policy analysis
        news_data = get_market_news(symbol, max_results=5)
        
        # Perform multi-factor analysis
        analysis_result = {
            'symbol': symbol,
            'name': market_data['name'],
            'current_price': current_price,
            'change_percent': change_percent,
            'timestamp': datetime.now().isoformat(),
            'technical_analysis': _analyze_technical(market_data, tech_indicators),
            'fundamental_policy_analysis': _analyze_fundamental_policy(news_data, market_data),
            'market_sentiment_analysis': _analyze_market_sentiment(market_data, tech_indicators),
            'risk_assessment': _assess_risk(market_data, tech_indicators),
            'final_recommendation': None,
            'price_targets': None
        }
        
        # Generate final recommendation
        final_decision = _generate_final_recommendation(analysis_result)
        analysis_result['final_recommendation'] = final_decision
        
        # Add price targets based on recommendation
        price_targets = _calculate_price_targets(
            current_price, 
            tech_indicators, 
            final_decision['recommendation']
        )
        analysis_result['price_targets'] = price_targets
        
        logger.info(f"Professional analysis completed for {symbol}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in professional analysis for {symbol}: {str(e)}")
        raise ValueError(f"Failed to generate professional analysis: {str(e)}")


def _analyze_technical(market_data: Dict[str, Any], tech_indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze technical factors."""
    current_price = market_data['price']
    ma5 = tech_indicators['ma5']
    ma10 = tech_indicators['ma10']
    ma20 = tech_indicators['ma20']
    ma30 = tech_indicators['ma30']
    rsi = tech_indicators['rsi']
    
    # Determine technical signal
    if current_price < ma5 and ma5 < ma10 and ma10 < ma20:
        tech_signal = '强烈卖出'
        tech_score = -4.0
    elif current_price < ma5 and ma5 < ma10:
        tech_signal = '卖出'
        tech_score = -2.0
    elif current_price > ma5 and ma5 > ma10 and ma10 > ma20:
        tech_signal = '强烈买入'
        tech_score = 4.0
    elif current_price > ma5 and ma5 > ma10:
        tech_signal = '买入'
        tech_score = 2.0
    else:
        tech_signal = '观望'
        tech_score = 0.0
    
    # RSI analysis
    if rsi > 70:
        rsi_status = '超买'
    elif rsi < 30:
        rsi_status = '超卖'
    else:
        rsi_status = '中性'
    
    return {
        'signal': tech_signal,
        'score': tech_score,
        'moving_averages': {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ma30': ma30
        },
        'rsi': rsi,
        'rsi_status': rsi_status,
        'price_vs_ma30_pct': (current_price - ma30) / ma30 * 100
    }


def _analyze_fundamental_policy(news_data: List[Dict[str, Any]], market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze fundamental and policy factors."""
    bullish_factors = 0
    bearish_factors = 0
    key_factors = []
    
    # Analyze news sentiment
    for news in news_data:
        title = news['title'].lower()
        summary = news.get('summary', '').lower()
        combined_text = title + ' ' + summary
        
        # Bullish keywords
        bullish_keywords = ['回购', '增长', '景气', '领先', '消费', '复苏', '盈利', '分红']
        bearish_keywords = ['下跌', '调整', '风险', '压力', '减持', '亏损', '监管']
        
        if any(keyword in combined_text for keyword in bullish_keywords):
            bullish_factors += 1
            key_factors.append(f"利好: {news['title'][:30]}...")
        elif any(keyword in combined_text for keyword in bearish_keywords):
            bearish_factors += 1
            key_factors.append(f"利空: {news['title'][:30]}...")
    
    # Determine policy signal
    if bullish_factors > bearish_factors:
        policy_signal = '买入'
        policy_score = 3.5
    elif bearish_factors > bullish_factors:
        policy_signal = '卖出'
        policy_score = -3.5
    else:
        policy_signal = '中性'
        policy_score = 0.0
    
    return {
        'signal': policy_signal,
        'score': policy_score,
        'bullish_factors': bullish_factors,
        'bearish_factors': bearish_factors,
        'key_factors': key_factors
    }


def _analyze_market_sentiment(market_data: Dict[str, Any], tech_indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze market sentiment."""
    current_price = market_data['price']
    ma30 = tech_indicators['ma30']
    volume = market_data['volume']
    
    # Price position analysis
    price_position_pct = (current_price - ma30) / ma30 * 100
    if price_position_pct < -5:
        sentiment = '悲观'
    elif price_position_pct > 5:
        sentiment = '乐观'
    else:
        sentiment = '中性'
    
    # Volume analysis
    if volume > 5000000:  # High volume threshold
        volume_status = '活跃'
    else:
        volume_status = '正常'
    
    # Determine emotion signal
    if sentiment == '悲观' and volume_status == '正常':
        emotion_signal = '卖出'
        emotion_score = -2.5
    elif sentiment == '乐观' and volume_status == '活跃':
        emotion_signal = '买入'
        emotion_score = 2.5
    else:
        emotion_signal = '观望'
        emotion_score = 0.0
    
    return {
        'signal': emotion_signal,
        'score': emotion_score,
        'sentiment': sentiment,
        'volume_status': volume_status,
        'price_position_pct': price_position_pct
    }


def _assess_risk(market_data: Dict[str, Any], tech_indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Assess risk factors."""
    current_price = market_data['price']
    ma5 = tech_indicators['ma5']
    ma30 = tech_indicators['ma30']
    rsi = tech_indicators['rsi']
    
    # Calculate risk metrics
    distance_to_ma5 = abs(current_price - ma5) / current_price * 100
    distance_to_ma30 = abs(current_price - ma30) / current_price * 100
    
    # Risk level assessment
    if rsi > 70 or rsi < 30:
        volatility_risk = '高'
    else:
        volatility_risk = '中'
    
    if distance_to_ma5 > 5:
        trend_risk = '高'
    else:
        trend_risk = '低'
    
    return {
        'volatility_risk': volatility_risk,
        'trend_risk': trend_risk,
        'distance_to_ma5_pct': distance_to_ma5,
        'distance_to_ma30_pct': distance_to_ma30
    }


def _generate_final_recommendation(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final recommendation based on multi-factor analysis."""
    tech_score = analysis_result['technical_analysis']['score']
    policy_score = analysis_result['fundamental_policy_analysis']['score']
    emotion_score = analysis_result['market_sentiment_analysis']['score']
    
    # Apply factor weights
    weighted_tech = tech_score * FACTOR_WEIGHTS['technical_analysis']
    weighted_policy = policy_score * FACTOR_WEIGHTS['fundamental_analysis']
    weighted_emotion = emotion_score * FACTOR_WEIGHTS['market_sentiment']
    
    total_buy_score = max(0, weighted_tech + weighted_policy + weighted_emotion)
    total_sell_score = max(0, -(weighted_tech + weighted_policy + weighted_emotion))
    
    score_diff = total_buy_score - total_sell_score
    
    if score_diff >= DECISION_THRESHOLDS['strong_buy_diff']:
        recommendation = '强烈买入'
    elif score_diff >= DECISION_THRESHOLDS['buy_diff']:
        recommendation = '买入'
    elif score_diff <= -DECISION_THRESHOLDS['strong_sell_diff']:
        recommendation = '强烈卖出'
    elif score_diff <= -DECISION_THRESHOLDS['sell_diff']:
        recommendation = '卖出'
    else:
        recommendation = '观望'
    
    return {
        'recommendation': recommendation,
        'buy_score': total_buy_score,
        'sell_score': total_sell_score,
        'score_difference': score_diff,
        'factor_scores': {
            'technical': weighted_tech,
            'fundamental_policy': weighted_policy,
            'market_sentiment': weighted_emotion
        }
    }


def _calculate_price_targets(current_price: float, tech_indicators: Dict[str, Any], 
                          recommendation: str) -> Dict[str, Any]:
    """Calculate price targets based on recommendation."""
    ma5 = tech_indicators['ma5']
    ma20 = tech_indicators['ma20']
    ma30 = tech_indicators['ma30']
    
    if recommendation in ['强烈买入', '买入']:
        # Bullish targets
        target_price = ma5 + (ma5 - current_price) * 1.5
        stop_loss = current_price * 0.95
        return {
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'support_level': round(min(ma20, ma30), 2),
            'resistance_level': round(ma5, 2)
        }
    elif recommendation in ['强烈卖出', '卖出']:
        # Bearish targets
        support_level = min(ma20, ma30)
        resistance_level = ma5
        return {
            'support_level': round(support_level, 2),
            'resistance_level': round(resistance_level, 2),
            'target_price': None,
            'stop_loss': None
        }
    else:
        # Neutral
        return {
            'support_level': round(ma30, 2),
            'resistance_level': round(ma5, 2),
            'target_price': None,
            'stop_loss': None
        }