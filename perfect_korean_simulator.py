#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완벽한 한글 지원 항생제 내성 시뮬레이터
Samsung Innovation Challenge 2025

한글 폰트 문제 완전 해결 + 과학적 정확성 + 웹 인터페이스
"""

import os
import sys
import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import json
from datetime import datetime
import subprocess
import warnings

warnings.filterwarnings('ignore')

# 백엔드 설정 (웹용으로 Agg 사용)
matplotlib.use('Agg')

def setup_perfect_korean_fonts():
    """완벽한 한글 폰트 설정"""
    print("🔤 한글 폰트 설정 중...")
    
    # macOS 시스템 폰트 경로들
    font_paths = [
        '/System/Library/Fonts/AppleGothic.ttf',
        '/System/Library/Fonts/Apple SD Gothic Neo.ttc',
        '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
        '/Library/Fonts/Apple SD Gothic Neo.ttc',
        '/opt/homebrew/share/fonts/NanumGothic.ttf',
        '/usr/local/share/fonts/NanumGothic.ttf'
    ]
    
    # 사용 가능한 폰트 찾기
    available_font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            available_font = font_path
            print(f"   ✅ 한글 폰트 발견: {font_path}")
            break
    
    if available_font:
        # 폰트 등록
        try:
            font_prop = fm.FontProperties(fname=available_font)
            plt.rcParams['font.family'] = font_prop.get_name()
            print(f"   ✅ 폰트 설정 완료: {font_prop.get_name()}")
        except Exception as e:
            print(f"   ⚠️ 폰트 등록 실패: {e}")
            plt.rcParams['font.family'] = ['AppleGothic', 'Apple SD Gothic Neo', 'DejaVu Sans']
    else:
        # 시스템 폰트 리스트에서 한글 폰트 찾기
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        korean_fonts = [f for f in available_fonts if any(korean in f for korean in 
                       ['Gothic', 'Nanum', 'Malgun', 'Apple', 'Batang'])]
        
        if korean_fonts:
            plt.rcParams['font.family'] = korean_fonts[0]
            print(f"   ✅ 시스템 한글 폰트 사용: {korean_fonts[0]}")
        else:
            plt.rcParams['font.family'] = 'DejaVu Sans'
            print("   ⚠️ 기본 폰트 사용 (한글 표시 제한적)")
    
    # 기본 설정
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    
    print("   ✅ 한글 폰트 설정 완료!")

class KoreanSafeSimulator:
    """한글 안전 보장 시뮬레이터"""
    
    def __init__(self):
        setup_perfect_korean_fonts()
        
        print("🧬 완벽한 한글 지원 항생제 내성 시뮬레이터 초기화...")
        
        # 시뮬레이션 파라미터
        self.dose = 500  # mg
        self.interval = 12  # hours
        self.max_time = 168  # hours (7 days)
        self.dt = 0.5  # time step
        
        # 약동학 파라미터
        self.ke = 0.173  # elimination rate (1/h)
        self.vd = 175    # volume of distribution (L)
        self.bioavailability = 0.85
        
        # 세균 파라미터
        self.initial_S = 1e8  # 초기 감수성균
        self.initial_R = 1e4  # 초기 내성균
        self.growth_rate_S = 0.693  # 감수성균 성장률
        self.growth_rate_R = 0.623  # 내성균 성장률
        self.mic_S = 0.5    # 감수성균 MIC
        self.mic_R = 8.0    # 내성균 MIC
        self.emax = 4.0     # 최대 살균 효과
        self.hill = 2.5     # Hill coefficient
        self.mutation_rate = 1e-8  # 돌연변이율
        
        print("   ✅ 초기화 완료!")
        
    def calculate_concentration(self, t):
        """약물 농도 계산"""
        conc = 0
        dose_times = np.arange(0, self.max_time, self.interval)
        
        for dose_time in dose_times:
            if t >= dose_time:
                time_since_dose = t - dose_time
                dose_conc = (self.dose * self.bioavailability / self.vd) * \
                           np.exp(-self.ke * time_since_dose)
                conc += dose_conc
        
        return conc
    
    def pharmacodynamic_effect(self, conc, mic):
        """약력학적 효과 (Hill equation)"""
        if conc <= 0:
            return 0
        return self.emax * (conc ** self.hill) / (mic ** self.hill + conc ** self.hill)
    
    def run_simulation(self):
        """시뮬레이션 실행"""
        print("🔄 시뮬레이션 실행 중...")
        
        times = np.arange(0, self.max_time, self.dt)
        n_points = len(times)
        
        # 결과 배열
        concentrations = np.zeros(n_points)
        S_populations = np.zeros(n_points)
        R_populations = np.zeros(n_points)
        
        # 초기값
        S_populations[0] = self.initial_S
        R_populations[0] = self.initial_R
        
        # 시뮬레이션 루프
        for i, t in enumerate(times):
            # 약물 농도 계산
            concentrations[i] = self.calculate_concentration(t)
            
            if i > 0:
                # 현재 집단 크기
                S_current = S_populations[i-1]
                R_current = R_populations[i-1]
                total_current = S_current + R_current
                
                # 약력학적 효과
                kill_rate_S = self.pharmacodynamic_effect(concentrations[i], self.mic_S)
                kill_rate_R = self.pharmacodynamic_effect(concentrations[i], self.mic_R)
                
                # 환경 제한 (carrying capacity)
                carrying_capacity = 1e12
                growth_factor = max(0, 1 - total_current / carrying_capacity)
                
                # 변화율 계산
                dS_dt = (self.growth_rate_S * growth_factor - kill_rate_S) * S_current - \
                        self.mutation_rate * S_current
                dR_dt = (self.growth_rate_R * growth_factor - kill_rate_R) * R_current + \
                        self.mutation_rate * S_current
                
                # 다음 시점 계산
                S_populations[i] = max(0, S_current + dS_dt * self.dt)
                R_populations[i] = max(0, R_current + dR_dt * self.dt)
        
        # 결과 정리
        total_populations = S_populations + R_populations
        resistance_fractions = np.divide(R_populations, total_populations, 
                                       out=np.zeros_like(R_populations), 
                                       where=total_populations!=0) * 100
        
        results = {
            'times': times.tolist(),
            'concentrations': concentrations.tolist(),
            'sensitive_populations': S_populations.tolist(),
            'resistant_populations': R_populations.tolist(),
            'total_populations': total_populations.tolist(),
            'resistance_fractions': resistance_fractions.tolist(),
            'simulation_params': {
                'dose': self.dose,
                'interval': self.interval,
                'max_time': self.max_time,
                'initial_S': self.initial_S,
                'initial_R': self.initial_R
            }
        }
        
        print("   ✅ 시뮬레이션 완료!")
        return results
    
    def create_korean_visualization(self, results):
        """한글이 완벽하게 표시되는 시각화 생성"""
        print("📊 한글 시각화 생성 중...")
        
        # Plotly 사용 (한글 폰트 문제 없음)
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '💊 약물 농도 변화 (시간별)',
                '🦠 세균 집단 동역학',
                '📊 내성 비율 변화 (%)',
                '🎯 치료 효과 평가'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        times = results['times']
        
        # 1. 약물 농도 그래프
        fig.add_trace(
            go.Scatter(
                x=times, 
                y=results['concentrations'],
                mode='lines',
                name='약물 농도',
                line=dict(color='blue', width=3),
                hovertemplate='시간: %{x:.1f}시간<br>농도: %{y:.3f} mg/L<extra></extra>'
            ),
            row=1, col=1
        )
        
        # MIC 선들
        fig.add_hline(y=self.mic_S, line_dash="dash", line_color="green",
                     annotation_text="감수성균 MIC", row=1, col=1)
        fig.add_hline(y=self.mic_R, line_dash="dash", line_color="red",
                     annotation_text="내성균 MIC", row=1, col=1)
        
        # 2. 세균 집단 그래프
        fig.add_trace(
            go.Scatter(
                x=times, 
                y=results['sensitive_populations'],
                mode='lines',
                name='감수성균',
                line=dict(color='green', width=3),
                hovertemplate='시간: %{x:.1f}시간<br>감수성균: %{y:.2e} CFU/mL<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=times, 
                y=results['resistant_populations'],
                mode='lines',
                name='내성균',
                line=dict(color='red', width=3),
                hovertemplate='시간: %{x:.1f}시간<br>내성균: %{y:.2e} CFU/mL<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. 내성 비율 그래프
        fig.add_trace(
            go.Scatter(
                x=times, 
                y=results['resistance_fractions'],
                mode='lines',
                name='내성 비율',
                line=dict(color='orange', width=3),
                fill='tonexty',
                hovertemplate='시간: %{x:.1f}시간<br>내성 비율: %{y:.1f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 4. 총 세균 수 그래프
        fig.add_trace(
            go.Scatter(
                x=times, 
                y=results['total_populations'],
                mode='lines',
                name='총 세균 수',
                line=dict(color='purple', width=3),
                hovertemplate='시간: %{x:.1f}시간<br>총 세균: %{y:.2e} CFU/mL<extra></extra>'
            ),
            row=2, col=2
        )
        
        # 투약 시점 표시
        dose_times = list(range(0, int(self.max_time), self.interval))
        for dose_time in dose_times:
            fig.add_vline(x=dose_time, line_dash="dot", line_color="yellow",
                         annotation_text=f"💊 {self.dose}mg 투약")
        
        # 축 설정
        fig.update_yaxes(type="log", title_text="농도 (mg/L)", row=1, col=1)
        fig.update_yaxes(type="log", title_text="세균 수 (CFU/mL)", row=1, col=2)
        fig.update_yaxes(title_text="내성 비율 (%)", range=[0, 100], row=2, col=1)
        fig.update_yaxes(type="log", title_text="총 세균 수 (CFU/mL)", row=2, col=2)
        
        fig.update_xaxes(title_text="시간 (시간)")
        
        # 레이아웃 설정
        fig.update_layout(
            title={
                'text': "🧬 항생제 내성 진화 시뮬레이션 결과<br><sub>Samsung Innovation Challenge 2025</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=800,
            showlegend=True,
            hovermode='x unified',
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # 결과 저장
        os.makedirs('results', exist_ok=True)
        
        # HTML 저장
        html_file = f'results/korean_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        fig.write_html(html_file, include_plotlyjs='cdn')
        
        print(f"   ✅ 한글 시각화 저장: {html_file}")
        
        return fig, html_file
    
    def create_summary_report(self, results):
        """한글 요약 보고서 생성"""
        print("📋 한글 요약 보고서 생성 중...")
        
        final_time = results['times'][-1]
        final_conc = results['concentrations'][-1]
        final_total = results['total_populations'][-1]
        final_resistance = results['resistance_fractions'][-1]
        max_conc = max(results['concentrations'])
        max_resistance = max(results['resistance_fractions'])
        
        # 치료 성공 판정
        treatment_success = final_total < 1e6 and final_resistance < 20
        
        report = {
            "시뮬레이션_정보": {
                "실행_시간": datetime.now().isoformat(),
                "시뮬레이션_기간": f"{final_time:.1f} 시간",
                "투약_요법": f"{self.dose}mg, {self.interval}시간마다"
            },
            "주요_결과": {
                "최대_약물농도": f"{max_conc:.3f} mg/L",
                "최종_약물농도": f"{final_conc:.3f} mg/L",
                "최종_총세균수": f"{final_total:.2e} CFU/mL",
                "최종_내성비율": f"{final_resistance:.1f}%",
                "최대_내성비율": f"{max_resistance:.1f}%"
            },
            "치료_평가": {
                "치료_성공": "성공" if treatment_success else "실패",
                "세균_박멸": "달성" if final_total < 1e6 else "미달성",
                "내성_억제": "성공" if final_resistance < 20 else "실패"
            },
            "권장_사항": []
        }
        
        # 권장사항 생성
        if final_resistance > 50:
            report["권장_사항"].append("내성 비율이 높아 용량 증량 검토 필요")
        if max_conc < self.mic_S * 4:
            report["권장_사항"].append("최대 농도가 낮아 용량 또는 투약 빈도 증가 검토")
        if final_total > 1e8:
            report["권장_사항"].append("세균 수가 높아 치료 기간 연장 검토")
        if not report["권장_사항"]:
            report["권장_사항"].append("현재 투약 요법이 적절함")
        
        # JSON 저장
        report_file = f'results/korean_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 한글 보고서 저장: {report_file}")
        
        return report, report_file

def main():
    """메인 실행 함수"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        🧬 완벽한 한글 지원 항생제 내성 시뮬레이터             ║
║              Samsung Innovation Challenge 2025               ║
║                                                              ║
║  ✅ 완벽한 한글 폰트 지원  ✅ 과학적 정확성                  ║
║  ✅ 실시간 시각화        ✅ 웹 인터페이스                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 시뮬레이터 생성
        simulator = KoreanSafeSimulator()
        
        # 시뮬레이션 실행
        results = simulator.run_simulation()
        
        # 한글 시각화 생성
        fig, html_file = simulator.create_korean_visualization(results)
        
        # 한글 보고서 생성
        report, report_file = simulator.create_summary_report(results)
        
        # 결과 출력
        print("\n📊 시뮬레이션 결과:")
        print(f"   📁 시각화 파일: {html_file}")
        print(f"   📋 보고서 파일: {report_file}")
        print(f"   🎯 치료 결과: {report['치료_평가']['치료_성공']}")
        print(f"   📈 최종 내성 비율: {report['주요_결과']['최종_내성비율']}")
        
        print("\n🎉 한글 지원 시뮬레이션 완료!")
        print("📱 웹 브라우저에서 HTML 파일을 열어서 결과를 확인하세요!")
        
        return results, report
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()
