#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
애니메이션 시각화 - 항생제 내성 진화
Samsung Innovation Challenge 2025
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle, Circle
import matplotlib.patches as mpatches
from datetime import datetime
import json

# 스타일 설정
plt.style.use('dark_background')
sns.set_palette("husl")

class AnimatedSimulator:
    def __init__(self):
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 12))
        self.fig.suptitle('🧬 Antibiotic Resistance Evolution Simulator', fontsize=16, fontweight='bold')
        
        # 시뮬레이션 파라미터
        self.max_time = 168  # 7일
        self.dt = 0.5
        self.times = np.arange(0, self.max_time, self.dt)
        
        # 현재 상태
        self.current_frame = 0
        self.S = 1e8  # 감수성균
        self.R = 1e4  # 내성균
        
        # 데이터 저장
        self.time_data = []
        self.conc_data = []
        self.s_data = []
        self.r_data = []
        self.resistance_data = []
        
        # 투약 정보
        self.dose = 500
        self.interval = 12
        self.dose_times = np.arange(0, self.max_time, self.interval)
        
        self.setup_plots()
        
    def setup_plots(self):
        """애니메이션 플롯 설정"""
        
        # 1. 약물 농도 (좌상)
        self.ax1 = self.axes[0, 0]
        self.ax1.set_title('💊 Drug Concentration', fontweight='bold')
        self.ax1.set_xlabel('Time (hours)')
        self.ax1.set_ylabel('Concentration (mg/L)')
        self.ax1.set_yscale('log')
        self.ax1.grid(True, alpha=0.3)
        self.line1, = self.ax1.plot([], [], 'cyan', linewidth=3, label='Concentration')
        self.ax1.axhline(y=0.5, color='green', linestyle='--', alpha=0.7, label='MIC (Sensitive)')
        self.ax1.axhline(y=8.0, color='red', linestyle='--', alpha=0.7, label='MIC (Resistant)')
        self.ax1.legend()
        
        # 2. 세균 집단 (우상)
        self.ax2 = self.axes[0, 1]
        self.ax2.set_title('🦠 Bacterial Dynamics', fontweight='bold')
        self.ax2.set_xlabel('Time (hours)')
        self.ax2.set_ylabel('Bacterial Count (CFU/mL)')
        self.ax2.set_yscale('log')
        self.ax2.grid(True, alpha=0.3)
        self.line2a, = self.ax2.plot([], [], 'green', linewidth=2, label='Sensitive')
        self.line2b, = self.ax2.plot([], [], 'red', linewidth=2, label='Resistant')
        self.line2c, = self.ax2.plot([], [], 'white', linewidth=1, linestyle='--', label='Total')
        self.ax2.legend()
        
        # 3. 내성 비율 (중상)
        self.ax3 = self.axes[0, 2]
        self.ax3.set_title('📊 Resistance Ratio', fontweight='bold')
        self.ax3.set_xlabel('Time (hours)')
        self.ax3.set_ylabel('Resistance Ratio (%)')
        self.ax3.grid(True, alpha=0.3)
        self.line3, = self.ax3.plot([], [], 'orange', linewidth=3)
        self.ax3.axhline(y=10, color='red', linestyle=':', alpha=0.7, label='Danger Level')
        self.ax3.legend()
        
        # 4. 세균 시각화 (좌하) - 창의적 시각화
        self.ax4 = self.axes[1, 0]
        self.ax4.set_title('🔬 현미경 뷰', fontweight='bold')
        self.ax4.set_xlim(0, 10)
        self.ax4.set_ylim(0, 10)
        self.ax4.set_aspect('equal')
        
        # 5. 치료 효과 (우하)
        self.ax5 = self.axes[1, 1]
        self.ax5.set_title('💉 치료 효과', fontweight='bold')
        
        # 6. 실시간 통계 (중하)
        self.ax6 = self.axes[1, 2]
        self.ax6.set_title('📈 실시간 통계', fontweight='bold')
        self.ax6.axis('off')
        
        plt.tight_layout()
        
    def calculate_concentration(self, t):
        """약물 농도 계산"""
        conc = 0
        ke = 0.173  # 제거율
        vd = 175    # 분포용적
        
        for dose_time in self.dose_times:
            if t >= dose_time:
                time_since_dose = t - dose_time
                dose_conc = (self.dose / vd) * np.exp(-ke * time_since_dose)
                conc += dose_conc
        return conc
        
    def pharmacodynamic_effect(self, conc, mic, emax=4.0, hill=2.0):
        """약력학적 효과 계산"""
        if conc <= 0:
            return 0
        return emax * (conc ** hill) / (mic ** hill + conc ** hill)
        
    def update_bacteria(self, frame):
        """세균 집단 업데이트"""
        t = self.times[frame]
        conc = self.calculate_concentration(t)
        
        # 약력학적 효과
        kill_rate_s = self.pharmacodynamic_effect(conc, 0.5)
        kill_rate_r = self.pharmacodynamic_effect(conc, 8.0)
        
        # 파라미터
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
        self.time_data.append(t)
        self.conc_data.append(conc)
        self.s_data.append(self.S)
        self.r_data.append(self.R)
        
        total = self.S + self.R
        if total > 0:
            resistance_frac = self.R / total * 100
        else:
            resistance_frac = 0
        self.resistance_data.append(resistance_frac)
        
    def animate(self, frame):
        """애니메이션 프레임 업데이트"""
        if frame < len(self.times):
            self.update_bacteria(frame)
            
            # 데이터 길이 제한 (메모리 효율성)
            max_points = 500
            if len(self.time_data) > max_points:
                self.time_data = self.time_data[-max_points:]
                self.conc_data = self.conc_data[-max_points:]
                self.s_data = self.s_data[-max_points:]
                self.r_data = self.r_data[-max_points:]
                self.resistance_data = self.resistance_data[-max_points:]
            
            # 1. 농도 그래프 업데이트
            self.line1.set_data(self.time_data, self.conc_data)
            if self.time_data:
                self.ax1.set_xlim(max(0, self.time_data[-1] - 48), self.time_data[-1] + 12)
                if self.conc_data:
                    max_conc = max(self.conc_data[-100:]) if len(self.conc_data) > 100 else max(self.conc_data)
                    self.ax1.set_ylim(0.01, max_conc * 2)
            
            # 투약 시점 표시
            current_time = self.time_data[-1] if self.time_data else 0
            for dose_time in self.dose_times:
                if abs(current_time - dose_time) < 1:  # 투약 시점 근처
                    self.ax1.axvline(x=dose_time, color='yellow', alpha=0.8, linewidth=2)
            
            # 2. 세균 집단 그래프 업데이트
            self.line2a.set_data(self.time_data, self.s_data)
            self.line2b.set_data(self.time_data, self.r_data)
            total_data = [s + r for s, r in zip(self.s_data, self.r_data)]
            self.line2c.set_data(self.time_data, total_data)
            
            if self.time_data:
                self.ax2.set_xlim(max(0, self.time_data[-1] - 48), self.time_data[-1] + 12)
                if total_data:
                    max_bacteria = max(total_data[-100:]) if len(total_data) > 100 else max(total_data)
                    min_bacteria = min([x for x in total_data[-100:] if x > 0]) if len(total_data) > 100 else min([x for x in total_data if x > 0]) if total_data else 1
                    self.ax2.set_ylim(min_bacteria / 10, max_bacteria * 10)
            
            # 3. 내성 비율 그래프 업데이트
            self.line3.set_data(self.time_data, self.resistance_data)
            if self.time_data:
                self.ax3.set_xlim(max(0, self.time_data[-1] - 48), self.time_data[-1] + 12)
                self.ax3.set_ylim(0, 100)
            
            # 4. 현미경 뷰 업데이트 (창의적 시각화)
            self.ax4.clear()
            self.ax4.set_title('🔬 Microscope View', fontweight='bold')
            self.ax4.set_xlim(0, 10)
            self.ax4.set_ylim(0, 10)
            
            if self.s_data and self.r_data:
                # 세균 비율에 따른 점 표시
                total_current = self.S + self.R
                if total_current > 0:
                    s_ratio = self.S / total_current
                    r_ratio = self.R / total_current
                    
                    # 랜덤 위치에 세균 표시
                    np.random.seed(42)  # 일관된 위치
                    n_bacteria = min(100, int(np.log10(total_current)))
                    
                    for i in range(n_bacteria):
                        x = np.random.uniform(1, 9)
                        y = np.random.uniform(1, 9)
                        
                        if i < n_bacteria * s_ratio:
                            # 감수성균 (녹색 원)
                            circle = Circle((x, y), 0.2, color='green', alpha=0.7)
                            self.ax4.add_patch(circle)
                        else:
                            # 내성균 (빨간 사각형)
                            rect = Rectangle((x-0.15, y-0.15), 0.3, 0.3, color='red', alpha=0.7)
                            self.ax4.add_patch(rect)
            
            self.ax4.set_aspect('equal')
            
            # 5. 치료 효과 시각화
            self.ax5.clear()
            self.ax5.set_title('💉 Treatment Effect', fontweight='bold')
            
            if self.time_data:
                current_time = self.time_data[-1]
                current_total = total_data[-1] if total_data else 0
                current_resistance = self.resistance_data[-1] if self.resistance_data else 0
                
                # 치료 성공/실패 판정
                treatment_success = current_total < 1e6 and current_resistance < 10
                
                # 게이지 차트 스타일
                colors = ['green' if treatment_success else 'red']
                success_rate = 100 - current_resistance if treatment_success else current_resistance
                
                wedges, texts = self.ax5.pie([success_rate, 100 - success_rate], 
                                           colors=['green' if treatment_success else 'red', 'gray'],
                                           startangle=90, counterclock=False)
                
                # 중앙에 결과 표시
                self.ax5.text(0, 0, '✅ Success' if treatment_success else '❌ Failure', 
                            ha='center', va='center', fontsize=14, fontweight='bold',
                            color='white')
            
            # 6. 실시간 통계 업데이트
            self.ax6.clear()
            self.ax6.set_title('📈 Real-time Stats', fontweight='bold')
            self.ax6.axis('off')
            
            if self.time_data:
                current_time = self.time_data[-1]
                current_conc = self.conc_data[-1] if self.conc_data else 0
                current_s = self.s_data[-1] if self.s_data else 0
                current_r = self.r_data[-1] if self.r_data else 0
                current_resistance = self.resistance_data[-1] if self.resistance_data else 0
                
                stats_text = f"""
📅 Time: {current_time:.1f} / {self.max_time} hrs
💊 Concentration: {current_conc:.3f} mg/L
🦠 Sensitive: {current_s:.2e}
🔴 Resistant: {current_r:.2e}
📊 Resistance: {current_resistance:.1f}%
💉 Doses: {len([t for t in self.dose_times if t <= current_time])}

📈 Avg Resistance: {np.mean(self.resistance_data[-10:]):.1f}%
⚡ Progress: {current_time/self.max_time*100:.1f}%
                """
                
                self.ax6.text(0.05, 0.95, stats_text, transform=self.ax6.transAxes,
                            fontsize=10, verticalalignment='top', fontfamily='monospace',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="navy", alpha=0.8))
        
        return [self.line1, self.line2a, self.line2b, self.line2c, self.line3]
    
    def save_animation(self, filename='antibiotic_animation.gif'):
        """애니메이션을 GIF로 저장"""
        ani = animation.FuncAnimation(self.fig, self.animate, frames=len(self.times), 
                                     interval=50, blit=False, repeat=True)
        ani.save(f'results/{filename}', writer='pillow', fps=20)
        print(f"✅ Animation saved: results/{filename}")
        
    def run_animation(self):
        """애니메이션 실행"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║            🎬 Antibiotic Resistance Animation v1.0           ║
║                Samsung Innovation Challenge 2025              ║
╚══════════════════════════════════════════════════════════════╝

🎯 Features:
   ✅ Real-time drug concentration
   ✅ Bacterial dynamics animation
   ✅ Live resistance tracking
   ✅ Creative microscope view
   ✅ Treatment effect visualization
   ✅ Real-time statistics dashboard

⏯️  Close window to save as GIF file.
        """)
        
        ani = animation.FuncAnimation(self.fig, self.animate, frames=len(self.times),
                                     interval=100, blit=False, repeat=True)
        
        plt.show()
        
        # 애니메이션 저장
        self.save_animation()
        
        # 결과 저장
        results = {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'dose': self.dose,
                'interval': self.interval,
                'max_time': self.max_time
            },
            'final_results': {
                'final_time': self.time_data[-1] if self.time_data else 0,
                'final_concentration': self.conc_data[-1] if self.conc_data else 0,
                'final_sensitive': self.s_data[-1] if self.s_data else 0,
                'final_resistant': self.r_data[-1] if self.r_data else 0,
                'final_resistance_fraction': self.resistance_data[-1] if self.resistance_data else 0
            }
        }
        
        with open('results/animation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("📊 Results saved: results/animation_results.json")

if __name__ == "__main__":
    simulator = AnimatedSimulator()
    simulator.run_animation()
