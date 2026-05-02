#!/usr/bin/env python3
"""
포트폴리오 분석 스크립트
"""

import json
import math

def load_portfolio_data(filepath):
    """포트폴리오 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_portfolio(portfolio_data):
    """포트폴리오 분석 수행"""
    
    print("=" * 60)
    print("포트폴리오 분석 리포트")
    print("=" * 60)
    
    # 기본 정보
    print(f"\n📊 기본 정보")
    print(f"포트폴리오 이름: {portfolio_data.get('portfolio_name', 'N/A')}")
    print(f"기준일: {portfolio_data.get('as_of_date', 'N/A')}")
    print(f"총 자산 가치: {portfolio_data.get('total_value', 0):,.0f} {portfolio_data.get('currency', 'KRW')}")
    
    # 자산 현황
    print(f"\n📈 자산 현황")
    assets = portfolio_data.get('assets', [])
    total_value = portfolio_data.get('total_value', 0)
    
    if total_value == 0:
        print("총 자산 가치가 0입니다. 데이터를 확인해주세요.")
        return
    
    print(f"{'자산명':<20} {'현재가치':>15} {'비율':>10} {'수익률':>10}")
    print("-" * 60)
    
    for asset in assets:
        name = asset.get('name', 'Unknown')
        current_value = asset.get('current_value', 0)
        pnl_pct = asset.get('unrealized_pnl_pct', 0)
        ratio = (current_value / total_value) * 100
        
        print(f"{name:<20} {current_value:>15,.0f} {ratio:>9.1f}% {pnl_pct:>9.1f}%")
    
    # 자산 클래스별 분석
    print(f"\n🏦 자산 클래스별 배분")
    strategic_allocation = portfolio_data.get('strategic_allocation', {})
    
    print(f"{'자산클래스':<15} {'현재비율':>10} {'목표비율':>10} {'편차':>10}")
    print("-" * 45)
    
    for asset_class, allocation in strategic_allocation.items():
        current = allocation.get('current', 0) * 100
        target = allocation.get('target', 0) * 100
        tolerance = allocation.get('tolerance', 0) * 100
        deviation = current - target
        
        status = "✅ 적정" if abs(deviation) <= tolerance else "⚠️ 조정필요"
        
        print(f"{asset_class:<15} {current:>9.1f}% {target:>9.1f}% {deviation:>9.1f}% {status}")
    
    # 리스크 분석
    print(f"\n⚠️ 리스크 분석")
    risk_params = portfolio_data.get('risk_parameters', {})
    perf_metrics = portfolio_data.get('performance_metrics', {})
    
    print(f"리스크 허용도: {risk_params.get('risk_tolerance', 'N/A')}")
    print(f"기대수익률: {risk_params.get('expected_return', 0)*100:.1f}%")
    print(f"최대 변동성: {risk_params.get('max_volatility', 0)*100:.1f}%")
    print(f"실제 변동성: {perf_metrics.get('volatility_annualized', 0)*100:.1f}%")
    print(f"샤프 비율: {perf_metrics.get('sharpe_ratio', 0):.2f}")
    print(f"최대 손실: {perf_metrics.get('max_drawdown', 0)*100:.1f}%")
    
    # 투자 성과
    print(f"\n📊 투자 성과")
    print(f"YTD 수익률: {perf_metrics.get('ytd_return', 0)*100:.1f}%")
    print(f"1년 수익률: {perf_metrics.get('one_year_return', 0)*100:.1f}%")
    print(f"3년 연평균: {perf_metrics.get('three_year_annualized', 0)*100:.1f}%")
    
    # 리밸런싱 권고사항
    print(f"\n💡 리밸런싱 권고사항")
    
    recommendations = []
    
    # 현금 비중이 너무 높음
    cash_current = strategic_allocation.get('Cash', {}).get('current', 0) * 100
    cash_target = strategic_allocation.get('Cash', {}).get('target', 0) * 100
    cash_tolerance = strategic_allocation.get('Cash', {}).get('tolerance', 0) * 100
    
    if cash_current - cash_target > cash_tolerance:
        excess_cash = (cash_current - cash_target - cash_tolerance) / 100 * total_value
        recommendations.append(f"현금 비중이 목표보다 {cash_current - cash_target:.1f}% 높습니다. 약 {excess_cash:,.0f} {portfolio_data.get('currency', 'KRW')}를 다른 자산에 투자할 것을 권장합니다.")
    
    # 주식 자산이 없음
    equity_current = strategic_allocation.get('Equity', {}).get('current', 0) * 100
    equity_target = strategic_allocation.get('Equity', {}).get('target', 0) * 100
    
    if equity_current == 0 and equity_target > 0:
        equity_amount = equity_target / 100 * total_value
        recommendations.append(f"주식 자산이 전혀 없습니다. 목표 비중 {equity_target:.1f}%에 따라 약 {equity_amount:,.0f} {portfolio_data.get('currency', 'KRW')}를 주식에 투자할 것을 권장합니다.")
    
    # 부동산 자산이 없음
    real_estate_current = strategic_allocation.get('Real Estate', {}).get('current', 0) * 100
    real_estate_target = strategic_allocation.get('Real Estate', {}).get('target', 0) * 100
    
    if real_estate_current == 0 and real_estate_target > 0:
        real_estate_amount = real_estate_target / 100 * total_value
        recommendations.append(f"부동산 자산이 전혀 없습니다. 목표 비중 {real_estate_target:.1f}%에 따라 약 {real_estate_amount:,.0f} {portfolio_data.get('currency', 'KRW')}를 부동산(REIT 등)에 투자할 것을 권장합니다.")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("현재 포트폴리오가 목표 배분에 잘 맞추어져 있습니다.")
    
    # 장기 목표
    print(f"\n🎯 장기 목표 (5년 후)")
    investment_horizon = risk_params.get('investment_horizon_years', 5)
    expected_return = risk_params.get('expected_return', 0.045)
    
    future_value = total_value * (1 + expected_return) ** investment_horizon
    print(f"현재 자산: {total_value:,.0f} {portfolio_data.get('currency', 'KRW')}")
    print(f"예상 수익률: {expected_return*100:.1f}% 연복리")
    print(f"투자 기간: {investment_horizon}년")
    print(f"예상 미래 가치: {future_value:,.0f} {portfolio_data.get('currency', 'KRW')}")
    
    print("\n" + "=" * 60)

def main():
    """메인 함수"""
    try:
        portfolio_data = load_portfolio_data('/mnt/samba/Documents/Investment/user_portfolio_data.json')
        analyze_portfolio(portfolio_data)
    except FileNotFoundError:
        print("포트폴리오 데이터 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print("포트폴리오 데이터 파일 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()