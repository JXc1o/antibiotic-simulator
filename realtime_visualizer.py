#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 항생제 내성 시뮬레이션 시각화
Samsung Innovation Challenge 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
import seaborn as sns
import time
import threading
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 스타일 설정
plt.style.use('dark_background')
sns.set_palette("husl")

class RealtimeAntibioticSimulator:
    def __init__(self):
        self.running = False
        self.paused = False
        self.current_time = 0
        self.max_time = 168  # 7일 = 168시간
        self.dt = 0.1  # 시간 단계
        
        # 시뮬레이션 파라미터
        self.dose = 500  # mg
        self.interval = 12  # hours
        self.patient_weight = 70  # kg
        self.ke = 0.173  # elimination rate
        self.vd = 175   # volume of distribution
        
        # 세균 파라미터
        self.S = 1e8  # 감수성균
        self.R = 1e4  # 내성균
        self.growth_rate_s = 0.693
        self.growth_rate_r = 0.623
        self.mutation_rate = 1e-8
        self.mic_s = 0.5
        self.mic_r = 8.0
        self.emax = 4.0
        self.hill = 2.0
        
        # 데이터 저장
        self.times = []
        self.concentrations = []
        self.s_populations = []
        self.r_populations = []
        self.resistance_fractions = []
        self.doses_given = []
        
        self.setup_figure()
        
    def setup_figure(self):
        """실시간 시각화 figure 설정"""
        self.fig = plt.figure(figsize=(16, 12))
        self.fig.suptitle('🧬 실시간 항생제 내성 진화 시뮬레이터', fontsize=16, fontweight='bold')
        
        # 서브플롯 생성
        gs = self.fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 약물 농도 그래프
        self.ax1 = self.fig.add_subplot(gs[0, :2])
        self.ax1.set_title('💊 실시간 약물 농도', fontweight='bold')
        self.ax1.set_xlabel('시간 (시간)')
        self.ax1.set_ylabel('농도 (mg/L)')
        self.ax1.set_yscale('log')
        self.ax1.grid(True, alpha=0.3)
        
        # 2. 세균 집단 그래프
        self.ax2 = self.fig.add_subplot(gs[1, :2])
        self.ax2.set_title('🦠 실시간 세균 집단 동역학', fontweight='bold')
        self.ax2.set_xlabel('시간 (시간)')
        self.ax2.set_ylabel('세균 수 (CFU/mL)')
        self.ax2.set_yscale('log')
        self.ax2.grid(True, alpha=0.3)
        
        # 3. 내성 비율 그래프
        self.ax3 = self.fig.add_subplot(gs[2, :2])
        self.ax3.set_title('📊 내성 비율 변화', fontweight='bold')
        self.ax3.set_xlabel('시간 (시간)')
        self.ax3.set_ylabel('내성 비율 (%)')
        self.ax3.grid(True, alpha=0.3)
        
        # 4. 현재 상태 표시
        self.ax4 = self.fig.add_subplot(gs[0, 2])
        self.ax4.set_title('📋 현재 상태', fontweight='bold')
        self.ax4.axis('off')
        
        # 5. 컨트롤 패널
        self.ax5 = self.fig.add_subplot(gs[1, 2])
        self.ax5.set_title('🎛️ 제어판', fontweight='bold')
        self.ax5.axis('off')
        
        # 6. 통계 패널
        self.ax6 = self.fig.add_subplot(gs[2, 2])
        self.ax6.set_title('📈 실시간 통계', fontweight='bold')
        self.ax6.axis('off')
        
        # 선 객체 초기화
        self.line_conc, = self.ax1.plot([], [], 'cyan', linewidth=2, label='농도')
        self.line_mic_s = self.ax1.axhline(y=self.mic_s, color='green', linestyle='--', alpha=0.7, label='MIC (감수성)')
        self.line_mic_r = self.ax1.axhline(y=self.mic_r, color='red', linestyle='--', alpha=0.7, label='MIC (내성)')
        
        self.line_s, = self.ax2.plot([], [], 'green', linewidth=2, label='감수성균')
        self.line_r, = self.ax2.plot([], [], 'red', linewidth=2, label='내성균')
        self.line_total, = self.ax2.plot([], [], 'white', linewidth=1, linestyle='--', label='총합')
        
        self.line_resistance, = self.ax3.plot([], [], 'orange', linewidth=2, label='내성 비율')
        
        # 범례 추가
        self.ax1.legend(loc='upper right')
        self.ax2.legend(loc='upper right')
        self.ax3.legend(loc='upper right')
        
        # 슬라이더 추가
        self.add_controls()
        
    def add_controls(self):
        """컨트롤 슬라이더 및 버튼 추가"""
        # 용량 슬라이더
        ax_dose = plt.axes([0.7, 0.85, 0.25, 0.03])
        self.slider_dose = Slider(ax_dose, '용량 (mg)', 100, 2000, valinit=self.dose, valfmt='%0.0f')
        self.slider_dose.on_changed(self.update_dose)
        
        # 간격 슬라이더
        ax_interval = plt.axes([0.7, 0.8, 0.25, 0.03])
        self.slider_interval = Slider(ax_interval, '간격 (h)', 6, 24, valinit=self.interval, valfmt='%0.0f')
        self.slider_interval.on_changed(self.update_interval)
        
        # 시작/정지 버튼
        ax_start = plt.axes([0.7, 0.75, 0.1, 0.04])
        self.btn_start = Button(ax_start, '시작')
        self.btn_start.on_clicked(self.toggle_simulation)
        
        # 리셋 버튼
        ax_reset = plt.axes([0.85, 0.75, 0.1, 0.04])
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
        else:
            self.running = True
            self.btn_start.label.set_text('정지')
            self.run_simulation()
            
    def reset_simulation(self, event):
        self.running = False
        self.current_time = 0
        self.S = 1e8
        self.R = 1e4
        self.times = []
        self.concentrations = []
        self.s_populations = []
        self.r_populations = []
        self.resistance_fractions = []
        self.doses_given = []
        self.btn_start.label.set_text('시작')
        self.update_plots()
        
    def calculate_concentration(self, t):
        """현재 시점의 약물 농도 계산"""
        conc = 0
        # 지금까지 투여된 모든 용량의 효과 합산
        for dose_time in self.doses_given:
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
        
    def should_give_dose(self, t):
        """투약 시점인지 확인"""
        if not self.doses_given:
            return True  # 첫 투약
        last_dose_time = self.doses_given[-1]
        return (t - last_dose_time) >= self.interval
        
    def update_simulation_step(self):
        """시뮬레이션 한 단계 업데이트"""
        t = self.current_time
        
        # 투약 시점 확인
        if self.should_give_dose(t):
            self.doses_given.append(t)
            
        # 현재 농도 계산
        conc = self.calculate_concentration(t)
        
        # 약력학적 효과
        kill_rate_s = self.pharmacodynamic_effect(conc, self.mic_s)
        kill_rate_r = self.pharmacodynamic_effect(conc, self.mic_r)
        
        # 세균 집단 업데이트 (Euler method)
        total_pop = self.S + self.R
        carrying_capacity = 1e12
        growth_factor = max(0, 1 - total_pop / carrying_capacity)
        
        dS_dt = (self.growth_rate_s * growth_factor - kill_rate_s) * self.S - self.mutation_rate * self.S
        dR_dt = (self.growth_rate_r * growth_factor - kill_rate_r) * self.R + self.mutation_rate * self.S
        
        self.S = max(0, self.S + dS_dt * self.dt)
        self.R = max(0, self.R + dR_dt * self.dt)
        
        # 데이터 저장
        self.times.append(t)
        self.concentrations.append(conc)
        self.s_populations.append(self.S)
        self.r_populations.append(self.R)
        
        total = self.S + self.R
        if total > 0:
            resistance_frac = self.R / total * 100
        else:
            resistance_frac = 0
        self.resistance_fractions.append(resistance_frac)
        
        self.current_time += self.dt
        
    def update_plots(self):
        """그래프 업데이트"""
        if not self.times:
            return
            
        # 농도 그래프 업데이트
        self.line_conc.set_data(self.times, self.concentrations)
        self.ax1.relim()
        self.ax1.autoscale_view()
        
        # 세균 집단 그래프 업데이트
        self.line_s.set_data(self.times, self.s_populations)
        self.line_r.set_data(self.times, self.r_populations)
        total_pops = [s + r for s, r in zip(self.s_populations, self.r_populations)]
        self.line_total.set_data(self.times, total_pops)
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        # 내성 비율 그래프 업데이트
        self.line_resistance.set_data(self.times, self.resistance_fractions)
        self.ax3.relim()
        self.ax3.autoscale_view()
        
        # 현재 상태 텍스트 업데이트
        self.ax4.clear()
        self.ax4.set_title('📋 현재 상태', fontweight='bold')
        self.ax4.axis('off')
        
        if self.times:
            current_conc = self.concentrations[-1]
            current_s = self.s_populations[-1]
            current_r = self.r_populations[-1]
            current_resistance = self.resistance_fractions[-1]
            
            status_text = f"""
시간: {self.current_time:.1f}h
농도: {current_conc:.2f} mg/L
감수성균: {current_s:.2e}
내성균: {current_r:.2e}
내성비율: {current_resistance:.1f}%
총 투약: {len(self.doses_given)}회
            """
            self.ax4.text(0.05, 0.95, status_text, transform=self.ax4.transAxes, 
                         fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        # 통계 패널 업데이트
        self.ax6.clear()
        self.ax6.set_title('📈 실시간 통계', fontweight='bold')
        self.ax6.axis('off')
        
        if len(self.concentrations) > 10:
            max_conc = max(self.concentrations)
            min_conc = min([c for c in self.concentrations if c > 0]) if any(c > 0 for c in self.concentrations) else 0
            avg_resistance = np.mean(self.resistance_fractions[-100:]) if len(self.resistance_fractions) > 100 else np.mean(self.resistance_fractions)
            
            # 치료 성공 예측
            current_total = self.s_populations[-1] + self.r_populations[-1] if self.s_populations else 0
            treatment_success = current_total < 1e6 and self.resistance_fractions[-1] < 10 if self.resistance_fractions else False
            
            stats_text = f"""
최대농도: {max_conc:.2f} mg/L
최소농도: {min_conc:.2f} mg/L
평균내성: {avg_resistance:.1f}%
치료성공: {'✅' if treatment_success else '❌'}
MIC 상회: {'✅' if current_conc > self.mic_s else '❌'}
            """
            self.ax6.text(0.05, 0.95, stats_text, transform=self.ax6.transAxes,
                         fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        # 투약 시점 표시
        for dose_time in self.doses_given:
            if dose_time <= self.current_time:
                self.ax1.axvline(x=dose_time, color='yellow', alpha=0.5, linestyle=':', linewidth=1)
                self.ax2.axvline(x=dose_time, color='yellow', alpha=0.5, linestyle=':', linewidth=1)
                self.ax3.axvline(x=dose_time, color='yellow', alpha=0.5, linestyle=':', linewidth=1)
        
        plt.draw()
        
    def run_simulation(self):
        """시뮬레이션 실행"""
        while self.running and self.current_time < self.max_time:
            self.update_simulation_step()
            self.update_plots()
            plt.pause(0.01)  # 실시간 업데이트를 위한 짧은 대기
            
        if self.current_time >= self.max_time:
            self.running = False
            self.btn_start.label.set_text('완료')
            self.save_results()
            
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
                'final_concentration': self.concentrations[-1] if self.concentrations else 0,
                'final_sensitive': self.s_populations[-1] if self.s_populations else 0,
                'final_resistant': self.r_populations[-1] if self.r_populations else 0,
                'final_resistance_fraction': self.resistance_fractions[-1] if self.resistance_fractions else 0,
                'total_doses': len(self.doses_given)
            },
            'time_series': {
                'times': self.times,
                'concentrations': self.concentrations,
                'sensitive_populations': self.s_populations,
                'resistant_populations': self.r_populations,
                'resistance_fractions': self.resistance_fractions
            }
        }
        
        with open('results/realtime_simulation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print("\n✅ 실시간 시뮬레이션 완료!")
        print(f"📊 결과 저장: results/realtime_simulation_results.json")
        
    def start(self):
        """시각화 시작"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║            🧬 실시간 항생제 내성 시뮬레이터 v1.0             ║
║                Samsung Innovation Challenge 2025              ║
╚══════════════════════════════════════════════════════════════╝

💡 사용법:
   - '시작' 버튼: 시뮬레이션 시작/정지
   - '리셋' 버튼: 시뮬레이션 초기화
   - 슬라이더: 실시간으로 용량과 간격 조정
   - 그래프: 실시간 데이터 모니터링

🎯 주요 기능:
   ✅ 실시간 약물 농도 모니터링
   ✅ 세균 집단 동역학 실시간 추적
   ✅ 내성 발생 실시간 예측
   ✅ 투약 시점 자동 표시
   ✅ 치료 성공률 실시간 평가
        """)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    simulator = RealtimeAntibioticSimulator()
    simulator.start()
