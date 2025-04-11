from typing import List
from cards import Card

def get_hand_rank(hand: List[Card]) -> str:
    """
    评估手牌等级
    返回: 手牌等级描述
    """
    # TODO: 实现手牌评估逻辑
    return "高牌"

def suggest_action(win_rate: float, pot_odds: float, ev: float) -> str:
    """
    根据当前情况给出行动建议
    """
    if win_rate > 0.7:
        return "🔥 加注 - 你有很大优势！"
    elif win_rate > 0.5:
        return "✅ 跟注 - 形势不错"
    elif pot_odds > 4 and ev > 0:
        return "🔄 跟注 - 赔率合适"
    else:
        return "❌ 弃牌 - 形势不利"

def format_currency(amount: int) -> str:
    """
    格式化金额显示
    """
    return f"${amount:,}" 