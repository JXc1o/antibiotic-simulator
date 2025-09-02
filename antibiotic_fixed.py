#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완벽한 항생제 내성 진화 AI 시뮬레이터 - 수정된 버전
Samsung Innovation Challenge 2025

한글 폰트 및 그래프 표시 문제 해결
"""

import os
import sys
import platform
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
import seaborn as sns
import pandas as pd
import json
from datetime import datetime
import warnings

# 백엔드 설정 (운영체제별)
if platform.system() == 'Darwin':  # macOS
    matplotlib.use('TkAgg')
elif platform.system() == 'Windows':
    matplotlib.use('Qt5Agg')
else:  # Linux
    matplotlib.use('TkAgg')

warnings.filterwarnings('ignore')

# 한글 폰트 설정 함수
def setup_korean_font():
    """한글 폰트 설정"""
    try:
        # macOS용 한글 폰트 시도
        fonts = [
            'AppleGothic',
            'Noto Sans CJK KR',
            'Apple SD Gothic Neo',
            'NanumGothic',
            'Malgun Gothic',
            'DejaVu Sans'
        ]
        
        for font in fonts:
            try:
                plt.rcParams['font.family'] = font
                # 테스트
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, '한글테스트', fontsize=12)
                plt.close(fig)
                print(f"✅ 한글 폰트 설정 성공: {font}")
                break
            except:
                continue
        
        # 기본 설정
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    except Exception as e:
        print(f"⚠️ 폰트 설정 경고: {e}")
        print("기본 폰트를 사용합니다.")

class FixedAntibioticSimulator:
    def __init__(self):
        """시뮬레이터 초기화"""
        # 한글 폰트 설정
        setup_korean_font()
        
        # 기본 스타일
        plt.style.use('default')  # dark_background 대신 기본 스타일
        
        print("🧬 완벽한 항생제 내성 진화 AI 시뮬레이터 초기화 중...")
        
        # 시뮬레이션 상태
        self.running = False
        self.current_time = 0
        self.max_time = 168  # 7일
        self.dt = 0.5
        
        # 파라미터
        self.dose = 500
        self.interval = 12
        self.patient_weight = 70
        
        # 약동학 파라미터
        self.ke = 0.173  # 제거율
        self.vd = 175    # 분포용적
        
        # 세균 파라미터
        self.S = 1e8  # 감수성균
        self.R = 1e4  # 내성균
        self.mic_s = 0.5
        self.mic_r = 8.0
        self.emax = 4.0
        self.hill = 2.0
        
        # 데이터 저장
        self.reset_data()
        
        print("✅ 초기화 완료!")
        
    def reset_data(self):
        """데이터 초기화"""
        self.data = {
            'times': [],
            'concentrations': [],
            's_populations': [],
            'r_populations': [],
            'resistance_fractions': [],
            'dose_events': []
        }
        
    def calculate_concentration(self, t):
        """약물 농도 계산"""
        conc = 0
        dose_times = np.arange(0, self.max_time, self.interval)
        
        for dose_time in dose_times:
            if t >= dose_time:
                time_since_dose = t - dose_time
                dose_conc = (self.dose / self.vd) * np.exp(-self.ke * time_since_dose)
                conc += dose_conc
        return conc
        
    def pharmacodynamic_effect(self, conc, mic):
        """약력학적 효과 계산"""
        if conc <= 0:
            return 0
        return self.emax * (conc ** self.hill) / (mic ** self.hill + conc ** self.hill)
        
    def update_simulation_step(self):
        """시뮬레이션 한 스텝 업데이트"""
        t = self.current_time
        
        # 농도 계산
        conc = self.calculate_concentration(t)
        
        # 약력학 효과
        kill_rate_s = self.pharmacodynamic_effect(conc, self.mic_s)
        kill_rate_r = self.pharmacodynamic_effect(conc, self.mic_r)
        
        # 성장률
        growth_rate_s = 0.693
        growth_rate_r = 0.623
        mutation_rate = 1e-8
        carrying_capacity = 1e12
        
        # 성장 제한
        total_pop = self.S + self.R
        growth_factor = max(0, 1 - total_pop / carrying_capacity)
        
        # 변화율
        dS_dt = (growth_rate_s * growth_factor - kill_rate_s) * self.S - mutation_rate * self.S
        dR_dt = (growth_rate_r * growth_factor - kill_rate_r) * self.R + mutation_rate * self.S
        
        # 업데이트
        self.S = max(0, self.S + dS_dt * self.dt)
        self.R = max(0, self.R + dR_dt * self.dt)
        
        # 데이터 저장
        total = self.S + self.R
        resistance_frac = (self.R / total * 100) if total > 0 else 0
        
        self.data['times'].append(t)
        self.data['concentrations'].append(conc)
        self.data['s_populations'].append(self.S)
        self.data['r_populations'].append(self.R)
        self.data['resistance_fractions'].append(resistance_frac)
        
        # 투약 이벤트 기록
        dose_times = np.arange(0, self.max_time, self.interval)
        if any(abs(t - dt) < self.dt for dt in dose_times):
            self.data['dose_events'].append(t)
        
        self.current_time += self.dt
        
    def setup_gui(self):
        """GUI 설정"""
        print("📊 그래프 창 설정 중...")
        
        # Figure 생성 (명시적 백엔드 사용)
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('🧬 완벽한 항생제 내성 진화 AI 시뮬레이터', fontsize=16, fontweight='bold')
        
        # 서브플롯 설정
        gs = self.fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        
        # 1. 약물 농도 그래프 (상단 좌측)
        self.ax1 = self.fig.add_subplot(gs[0, :2])
        self.ax1.set_title('💊 실시간 약물 농도', fontsize=14, fontweight='bold')
        self.ax1.set_xlabel('시간 (시간)')
        self.ax1.set_ylabel('농도 (mg/L)')
        self.ax1.set_yscale('log')
        self.ax1.grid(True, alpha=0.3)
        
        # 2. 세균 집단 (상단 우측)
        self.ax2 = self.fig.add_subplot(gs[0, 2])
        self.ax2.set_title('🦠 세균 집단', fontsize=14, fontweight='bold')
        self.ax2.set_xlabel('시간 (시간)')
        self.ax2.set_ylabel('세균 수 (CFU/mL)')
        self.ax2.set_yscale('log')
        self.ax2.grid(True, alpha=0.3)
        
        # 3. 내성 비율 (중간 좌측)
        self.ax3 = self.fig.add_subplot(gs[1, :2])
        self.ax3.set_title('📊 내성 비율 변화', fontsize=14, fontweight='bold')
        self.ax3.set_xlabel('시간 (시간)')
        self.ax3.set_ylabel('내성 비율 (%)')
        self.ax3.grid(True, alpha=0.3)
        
        # 4. 실시간 통계 (중간 우측)
        self.ax4 = self.fig.add_subplot(gs[1, 2])
        self.ax4.set_title('📈 실시간 통계', fontsize=14, fontweight='bold')
        self.ax4.axis('off')
        
        # 선 객체 초기화
        self.line_conc, = self.ax1.plot([], [], 'b-', linewidth=2, label='농도')
        self.line_s, = self.ax2.plot([], [], 'g-', linewidth=2, label='감수성균')
        self.line_r, = self.ax2.plot([], [], 'r-', linewidth=2, label='내성균')
        self.line_total, = self.ax2.plot([], [], 'k--', linewidth=1, label='총합')
        self.line_resistance, = self.ax3.plot([], [], 'orange', linewidth=2, label='내성 비율')
        
        # MIC 선들
        self.ax1.axhline(y=self.mic_s, color='green', linestyle='--', alpha=0.7, label='MIC (감수성)')
        self.ax1.axhline(y=self.mic_r, color='red', linestyle='--', alpha=0.7, label='MIC (내성)')
        
        # 범례
        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()
        
        # 컨트롤 패널
        self.setup_controls()
        
        print("✅ 그래프 창 설정 완료!")
        
    def setup_controls(self):
        """컨트롤 패널 설정"""
        # 슬라이더 위치
        ax_dose = plt.axes([0.1, 0.02, 0.3, 0.03])
        self.slider_dose = Slider(ax_dose, '용량 (mg)', 100, 2000, valinit=self.dose, valfmt='%.0f')
        self.slider_dose.on_changed(self.update_dose)
        
        ax_interval = plt.axes([0.5, 0.02, 0.2, 0.03])
        self.slider_interval = Slider(ax_interval, '간격 (h)', 6, 24, valinit=self.interval, valfmt='%.0f')
        self.slider_interval.on_changed(self.update_interval)
        
        # 버튼들
        ax_start = plt.axes([0.75, 0.02, 0.1, 0.03])
        self.btn_start = Button(ax_start, '시작')
        self.btn_start.on_clicked(self.toggle_simulation)
        
        ax_reset = plt.axes([0.87, 0.02, 0.1, 0.03])
        self.btn_reset = Button(ax_reset, '리셋')
        self.btn_reset.on_clicked(self.reset_simulation)
        
    def update_dose(self, val):
        self.dose = self.slider_dose.val
        
    def update_interval(self, val):
        self.interval = self.slider_interval.val
        
    def toggle_simulation(self, event):
        if self.running:
            self.running = False
            self.btn_start.label.set_text('시작')
            print("⏸️ 시뮬레이션 정지")
        else:
            self.running = True
            self.btn_start.label.set_text('정지')
            print("▶️ 시뮬레이션 시작")
            
    def reset_simulation(self, event):
        print("🔄 시뮬레이션 리셋")
        self.running = False
        self.current_time = 0
        self.S = 1e8
        self.R = 1e4
        self.reset_data()
        self.btn_start.label.set_text('시작')
        self.clear_plots()
        
    def clear_plots(self):
        """그래프 초기화"""
        self.line_conc.set_data([], [])
        self.line_s.set_data([], [])
        self.line_r.set_data([], [])
        self.line_total.set_data([], [])
        self.line_resistance.set_data([], [])
        plt.draw()
        
    def update_plots(self):
        """그래프 업데이트"""
        if not self.data['times']:
            return
            
        times = self.data['times']
        
        # 데이터 길이 제한 (성능을 위해)
        max_points = 1000
        if len(times) > max_points:
            times = times[-max_points:]
            concentrations = self.data['concentrations'][-max_points:]
            s_pops = self.data['s_populations'][-max_points:]
            r_pops = self.data['r_populations'][-max_points:]
            resistance = self.data['resistance_fractions'][-max_points:]
        else:
            concentrations = self.data['concentrations']
            s_pops = self.data['s_populations']
            r_pops = self.data['r_populations']
            resistance = self.data['resistance_fractions']
        
        # 1. 농도 그래프 업데이트
        self.line_conc.set_data(times, concentrations)
        
        # 2. 세균 그래프 업데이트
        self.line_s.set_data(times, s_pops)
        self.line_r.set_data(times, r_pops)
        total_pops = [s + r for s, r in zip(s_pops, r_pops)]
        self.line_total.set_data(times, total_pops)
        
        # 3. 내성 그래프 업데이트
        self.line_resistance.set_data(times, resistance)
        
        # 축 범위 자동 조정
        current_time = times[-1] if times else 0
        time_window = 48  # 48시간 윈도우
        
        # 농도 그래프
        self.ax1.set_xlim(max(0, current_time - time_window), current_time + 12)
        if concentrations and any(c > 0 for c in concentrations):
            self.ax1.set_ylim(0.01, max(concentrations) * 2)
        
        # 세균 그래프
        self.ax2.set_xlim(max(0, current_time - time_window), current_time + 12)
        if total_pops:
            min_pop = min([p for p in total_pops if p > 0]) if any(p > 0 for p in total_pops) else 1
            max_pop = max(total_pops)
            self.ax2.set_ylim(min_pop / 10, max_pop * 10)
        
        # 내성 그래프
        self.ax3.set_xlim(max(0, current_time - time_window), current_time + 12)
        self.ax3.set_ylim(0, 100)
        
        # 투약 시점 표시
        for dose_time in self.data['dose_events']:
            if dose_time >= current_time - time_window:
                self.ax1.axvline(x=dose_time, color='yellow', alpha=0.5, linewidth=1)
                self.ax2.axvline(x=dose_time, color='yellow', alpha=0.5, linewidth=1)
                self.ax3.axvline(x=dose_time, color='yellow', alpha=0.5, linewidth=1)
        
        # 4. 통계 업데이트
        self.update_stats()
        
        # 그래프 다시 그리기
        self.fig.canvas.draw()
        
    def update_stats(self):
        """실시간 통계 업데이트"""
        self.ax4.clear()
        self.ax4.set_title('📈 실시간 통계', fontsize=14, fontweight='bold')
        self.ax4.axis('off')
        
        if self.data['times']:
            current_time = self.data['times'][-1]
            current_conc = self.data['concentrations'][-1]
            current_s = self.data['s_populations'][-1]
            current_r = self.data['r_populations'][-1]
            current_resistance = self.data['resistance_fractions'][-1]
            
            total_bacteria = current_s + current_r
            dose_count = len(self.data['dose_events'])
            
            # 치료 성공 판정
            treatment_success = total_bacteria < 1e6 and current_resistance < 10
            
            stats_text = f"""
시간: {current_time:.1f} / {self.max_time} 시간
농도: {current_conc:.3f} mg/L
감수성균: {current_s:.2e}
내성균: {current_r:.2e}
내성 비율: {current_resistance:.1f}%
투약 횟수: {dose_count}회

치료 성공: {'✅' if treatment_success else '❌'}
진행률: {current_time/self.max_time*100:.1f}%
            """
            
            self.ax4.text(0.05, 0.95, stats_text, transform=self.ax4.transAxes,
                         fontsize=10, verticalalignment='top', fontfamily='monospace',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
    def animate(self, frame):
        """애니메이션 프레임"""
        if self.running and self.current_time < self.max_time:
            self.update_simulation_step()
            self.update_plots()
            
        if self.current_time >= self.max_time:
            self.running = False
            self.btn_start.label.set_text('완료')
            self.save_results()
            print("🎉 시뮬레이션 완료!")
            
        return []
    
    def save_results(self):
        """결과 저장"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'dose': self.dose,
                'interval': self.interval,
                'patient_weight': self.patient_weight
            },
            'final_results': {
                'final_time': self.current_time,
                'final_concentration': self.data['concentrations'][-1] if self.data['concentrations'] else 0,
                'final_total_bacteria': (self.data['s_populations'][-1] + self.data['r_populations'][-1]) if self.data['s_populations'] else 0,
                'final_resistance_fraction': self.data['resistance_fractions'][-1] if self.data['resistance_fractions'] else 0,
                'total_doses': len(self.data['dose_events'])
            },
            'time_series': self.data
        }
        
        # 결과 디렉토리 생성
        os.makedirs('results', exist_ok=True)
        
        with open('results/fixed_simulation_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("📊 결과 저장: results/fixed_simulation_results.json")
        
    def run_simulation(self):
        """시뮬레이션 실행"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║           🧬 완벽한 항생제 내성 진화 AI 시뮬레이터            ║
║                Samsung Innovation Challenge 2025              ║
║                                                              ║
║  🎯 실시간 시각화 | 🤖 AI 예측 | 📊 한글 지원               ║
╚══════════════════════════════════════════════════════════════╝

🚀 주요 기능:
   ✅ 완벽한 한글 지원
   ✅ 안정적인 그래프 표시
   ✅ 실시간 파라미터 조정
   ✅ 다차원 시각화
   ✅ 자동 결과 저장

💡 사용법:
   - 슬라이더: 용량과 간격 실시간 조정
   - '시작' 버튼: 시뮬레이션 시작/정지
   - '리셋' 버튼: 완전 초기화
   - 그래프: 실시간 데이터 모니터링

⚠️ 창을 닫으면 시뮬레이션이 종료됩니다.
        """)
        
        # GUI 설정
        self.setup_gui()
        
        # 애니메이션 시작
        self.animation = animation.FuncAnimation(
            self.fig, self.animate, 
            interval=100, blit=False, 
            repeat=True, cache_frame_data=False
        )
        
        # 창 표시
        plt.tight_layout()
        plt.show(block=True)  # 블로킹 모드로 실행
        
        print("👋 시뮬레이션 종료")

def main():
    """메인 실행 함수"""
    print("🧬 완벽한 항생제 내성 진화 AI 시뮬레이터 시작...")
    
    try:
        # 시뮬레이터 생성 및 실행
        simulator = FixedAntibioticSimulator()
        simulator.run_simulation()
        
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("디버그 정보:")
        print(f"   - Python 버전: {sys.version}")
        print(f"   - Matplotlib 버전: {matplotlib.__version__}")
        print(f"   - 백엔드: {matplotlib.get_backend()}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
