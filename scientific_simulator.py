#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
과학적으로 정확한 항생제 내성 진화 시뮬레이터
Samsung Innovation Challenge 2025

Based on:
- Mouton et al. (2008) Pharmacokinetic/Pharmacodynamic modelling
- Nielsen et al. (2011) Pharmacodynamic modeling of antibiotics
- Regoes et al. (2004) Pharmacodynamic functions
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 백엔드 이슈 해결
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

@dataclass
class PatientProfile:
    """환자 프로필 - 개인화된 약동학 파라미터"""
    weight: float = 70.0  # kg
    age: float = 35.0     # years
    creatinine_clearance: float = 120.0  # mL/min
    albumin: float = 4.0  # g/dL
    
    # 유전적 다형성 (CYP2D6 등)
    cyp2d6_activity: float = 1.0  # 정상 활성 = 1.0
    
    def get_clearance_adjustment(self) -> float:
        """신장 기능에 따른 청소율 조정"""
        # Cockcroft-Gault 공식 기반
        normal_cl = 120.0
        return self.creatinine_clearance / normal_cl
    
    def get_volume_adjustment(self) -> float:
        """체중과 나이에 따른 분포용적 조정"""
        # 표준 70kg 성인 기준
        weight_factor = self.weight / 70.0
        age_factor = 1.0 - (self.age - 35.0) * 0.005  # 나이당 0.5% 감소
        return weight_factor * max(0.5, age_factor)

@dataclass
class DrugProperties:
    """항생제 약물 특성 - FDA/EMA 승인 문헌 기반 정확한 파라미터"""
    name: str = "Ciprofloxacin"
    
    # 약동학 파라미터 (FDA Label & Clinical Pharmacology)
    # Reference: Bayer Pharmaceuticals, FDA Label 2016
    bioavailability: float = 0.78  # 경구 생체이용률 (70-85%, 평균 78%)
    protein_binding: float = 0.25  # 단백결합률 (20-30%, 평균 25%)
    half_life: float = 4.1         # 반감기 (3.5-4.6시간, 평균 4.1시간)
    vd_base: float = 2.1          # 기본 분포용적 (1.9-2.3 L/kg, 평균 2.1)
    clearance_renal: float = 0.75  # 신장 청소율 비율 (75%)
    
    # 약력학 파라미터 (CLSI 2023, EUCAST 2023)
    mic_breakpoint_susceptible: float = 1.0    # CLSI/EUCAST breakpoint (≤1 mg/L)
    mic_breakpoint_resistant: float = 4.0      # CLSI/EUCAST breakpoint (≥4 mg/L)
    pAUC_target: float = 125       # AUC24/MIC 목표값 (≥125 for efficacy)
    pAUC_resistance: float = 250   # 내성 억제 목표값 (≥250)
    
    # Hill 계수 (Quinolone 농도-효과 관계)
    # Reference: Mueller et al., AAC 2004
    hill_coefficient: float = 2.2  # Ciprofloxacin Hill coefficient (1.8-2.6)
    
    # 추가 임상 파라미터
    mpc: float = 4.0              # Mutant Prevention Concentration
    pac: float = 0.125            # Post-Antibiotic Effect concentration
    
    def get_elimination_constant(self, patient: PatientProfile) -> float:
        """개인화된 제거상수 계산"""
        ke_base = 0.693 / self.half_life
        clearance_adj = patient.get_clearance_adjustment()
        cyp_adj = patient.cyp2d6_activity
        return ke_base * clearance_adj * cyp_adj
    
    def get_distribution_volume(self, patient: PatientProfile) -> float:
        """개인화된 분포용적 계산"""
        vd_total = self.vd_base * patient.weight
        return vd_total * patient.get_volume_adjustment()

class PharmacokineticModel:
    """정확한 약동학 모델"""
    
    def __init__(self, drug: DrugProperties, patient: PatientProfile):
        self.drug = drug
        self.patient = patient
        self.ke = drug.get_elimination_constant(patient)
        self.vd = drug.get_distribution_volume(patient)
        
    def calculate_concentration(self, time: float, dose_times: List[float], 
                             dose_amounts: List[float]) -> float:
        """다회 투여 후 혈중농도 계산 (정확한 중첩 원리)"""
        total_conc = 0.0
        
        for dose_time, dose_amount in zip(dose_times, dose_amounts):
            if time >= dose_time:
                # 투여 후 경과시간
                t_elapsed = time - dose_time
                
                # 생체이용률 고려한 실제 흡수량
                bioavailable_dose = dose_amount * self.drug.bioavailability
                
                # 유리 약물 농도 (단백결합 고려)
                free_fraction = 1.0 - self.drug.protein_binding
                
                # 1차 제거동역학
                conc_contribution = (bioavailable_dose / self.vd) * \
                                  np.exp(-self.ke * t_elapsed) * free_fraction
                
                total_conc += conc_contribution
        
        return max(0.0, total_conc)

class BacterialDynamicsModel:
    """과학적으로 정확한 세균 동역학 모델"""
    
    def __init__(self):
        # 세균 성장 파라미터 (문헌값)
        self.growth_rate_sensitive = 0.693  # E.coli doubling time ~1h
        self.growth_rate_resistant = 0.623  # 10% fitness cost
        
        # 환경 수용력
        self.carrying_capacity = 1e12  # CFU/mL (in vitro 최대)
        
        # 돌연변이율 (실험적 측정값)
        self.mutation_rate = 1e-8  # per cell division
        
        # 경쟁 계수
        self.competition_coefficient = 0.1
    
    def sigmoid_kill_curve(self, concentration: float, mic: float, 
                          emax: float = 4.0, hill: float = 2.5) -> float:
        """Sigmoid Emax 모델 (Hill equation)"""
        if concentration <= 0:
            return 0.0
        
        # EC50 = MIC (일반적 가정)
        ec50 = mic
        
        # Hill equation
        effect = emax * (concentration ** hill) / (ec50 ** hill + concentration ** hill)
        
        return effect
    
    def calculate_bacterial_change(self, S: float, R: float, 
                                 drug_concentration: float,
                                 mic_sensitive: float = 0.5,
                                 mic_resistant: float = 8.0) -> Tuple[float, float]:
        """세균 집단 변화율 계산 (ODE 시스템)"""
        
        # 현재 총 세균 수
        total_bacteria = S + R
        
        # 환경 제한 요인 (로지스틱 성장)
        growth_limitation = max(0, 1 - total_bacteria / self.carrying_capacity)
        
        # 약물에 의한 살균 효과
        kill_rate_S = self.sigmoid_kill_curve(drug_concentration, mic_sensitive)
        kill_rate_R = self.sigmoid_kill_curve(drug_concentration, mic_resistant)
        
        # 경쟁 효과
        competition_S = self.competition_coefficient * R / total_bacteria if total_bacteria > 0 else 0
        competition_R = self.competition_coefficient * S / total_bacteria if total_bacteria > 0 else 0
        
        # 감수성균 변화율
        dS_dt = (self.growth_rate_sensitive * growth_limitation - 
                kill_rate_S - competition_S) * S - self.mutation_rate * S
        
        # 내성균 변화율 (돌연변이 유입 포함)
        dR_dt = (self.growth_rate_resistant * growth_limitation - 
                kill_rate_R - competition_R) * R + self.mutation_rate * S
        
        return dS_dt, dR_dt

class ScientificSimulator:
    """통합 과학적 시뮬레이터"""
    
    def __init__(self, patient: PatientProfile, drug: DrugProperties):
        self.patient = patient
        self.drug = drug
        self.pk_model = PharmacokineticModel(drug, patient)
        self.bacterial_model = BacterialDynamicsModel()
        
        # 시뮬레이션 설정
        self.time_step = 0.1  # 시간 단위 (시간)
        self.max_time = 168   # 7일
        
        # 초기 조건
        self.initial_S = 1e8  # 감수성균
        self.initial_R = 1e4  # 내성균
        
    def run_simulation(self, dose_schedule: List[Tuple[float, float]]) -> Dict:
        """
        시뮬레이션 실행
        dose_schedule: [(time, dose), ...] 형태의 투약 스케줄
        """
        
        # 시간 배열
        times = np.arange(0, self.max_time, self.time_step)
        n_points = len(times)
        
        # 결과 배열 초기화
        concentrations = np.zeros(n_points)
        S_populations = np.zeros(n_points)
        R_populations = np.zeros(n_points)
        
        # 초기값 설정
        S_populations[0] = self.initial_S
        R_populations[0] = self.initial_R
        
        # 투약 시간과 용량 분리
        dose_times = [dose[0] for dose in dose_schedule]
        dose_amounts = [dose[1] for dose in dose_schedule]
        
        # 시뮬레이션 루프
        for i, t in enumerate(times):
            # 약물 농도 계산
            concentrations[i] = self.pk_model.calculate_concentration(
                t, dose_times, dose_amounts)
            
            if i > 0:
                # 세균 동역학 계산
                dS_dt, dR_dt = self.bacterial_model.calculate_bacterial_change(
                    S_populations[i-1], R_populations[i-1], concentrations[i])
                
                # Euler 적분
                S_populations[i] = max(0, S_populations[i-1] + dS_dt * self.time_step)
                R_populations[i] = max(0, R_populations[i-1] + dR_dt * self.time_step)
        
        # 결과 정리
        results = {
            'times': times.tolist(),
            'concentrations': concentrations.tolist(),
            'sensitive_populations': S_populations.tolist(),
            'resistant_populations': R_populations.tolist(),
            'total_populations': (S_populations + R_populations).tolist(),
            'resistance_fractions': (R_populations / (S_populations + R_populations) * 100).tolist(),
            'dose_schedule': dose_schedule,
            'patient_info': {
                'weight': self.patient.weight,
                'age': self.patient.age,
                'creatinine_clearance': self.patient.creatinine_clearance
            },
            'drug_info': {
                'name': self.drug.name,
                'half_life': self.drug.half_life,
                'bioavailability': self.drug.bioavailability
            },
            'pharmacokinetic_parameters': {
                'elimination_constant': self.pk_model.ke,
                'distribution_volume': self.pk_model.vd,
                'clearance': self.pk_model.ke * self.pk_model.vd
            }
        }
        
        return results
    
    def create_plotly_visualization(self, results: Dict) -> str:
        """Plotly를 사용한 인터랙티브 시각화 생성"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '💊 약물 농도 vs 시간',
                '🦠 세균 집단 동역학',
                '📊 내성 비율 변화',
                '📈 약동학/약력학 관계'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": True}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        times = results['times']
        
        # 1. 약물 농도
        fig.add_trace(
            go.Scatter(x=times, y=results['concentrations'],
                      mode='lines', name='약물 농도',
                      line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # MIC 선들
        fig.add_hline(y=0.5, line_dash="dash", line_color="green",
                     annotation_text="MIC (감수성)", row=1, col=1)
        fig.add_hline(y=8.0, line_dash="dash", line_color="red",
                     annotation_text="MIC (내성)", row=1, col=1)
        
        # 2. 세균 집단
        fig.add_trace(
            go.Scatter(x=times, y=results['sensitive_populations'],
                      mode='lines', name='감수성균',
                      line=dict(color='green', width=2)),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=times, y=results['resistant_populations'],
                      mode='lines', name='내성균',
                      line=dict(color='red', width=2)),
            row=1, col=2
        )
        
        # 3. 내성 비율
        fig.add_trace(
            go.Scatter(x=times, y=results['resistance_fractions'],
                      mode='lines', name='내성 비율',
                      line=dict(color='orange', width=2)),
            row=2, col=1
        )
        
        # 4. PK/PD 관계
        fig.add_trace(
            go.Scatter(x=results['concentrations'], 
                      y=results['total_populations'],
                      mode='markers', name='PK/PD 관계',
                      marker=dict(color=results['resistance_fractions'],
                                colorscale='Viridis', size=8,
                                colorbar=dict(title="내성 비율 (%)"))),
            row=2, col=2
        )
        
        # 투약 시점 표시
        for dose_time, dose_amount in results['dose_schedule']:
            fig.add_vline(x=dose_time, line_dash="dot", line_color="yellow",
                         annotation_text=f"{dose_amount}mg")
        
        # 축 설정
        fig.update_yaxes(type="log", title_text="농도 (mg/L)", row=1, col=1)
        fig.update_yaxes(type="log", title_text="세균 수 (CFU/mL)", row=1, col=2)
        fig.update_yaxes(title_text="내성 비율 (%)", row=2, col=1)
        fig.update_yaxes(type="log", title_text="총 세균 수", row=2, col=2)
        
        fig.update_xaxes(title_text="시간 (시간)")
        
        # 레이아웃
        fig.update_layout(
            title="🧬 과학적 항생제 내성 진화 시뮬레이션",
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        # HTML로 저장
        html_content = fig.to_html(include_plotlyjs='cdn')
        
        with open('results/scientific_visualization.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_content

def create_standard_dosing_regimens() -> Dict[str, List[Tuple[float, float]]]:
    """표준 투약 요법들"""
    regimens = {
        'BID_500mg': [(i * 12, 500) for i in range(14)],  # 12시간마다 500mg, 7일
        'TID_250mg': [(i * 8, 250) for i in range(21)],   # 8시간마다 250mg, 7일
        'QD_750mg': [(i * 24, 750) for i in range(7)],    # 24시간마다 750mg, 7일
        'loading_dose': [(0, 1000)] + [(i * 12 + 12, 500) for i in range(13)]  # 로딩용량
    }
    return regimens

def main():
    """메인 실행 함수"""
    print("🧬 과학적으로 정확한 항생제 내성 시뮬레이터 시작...")
    
    # 결과 디렉토리 생성
    os.makedirs('results', exist_ok=True)
    
    # 환자 프로필들
    patients = {
        'standard': PatientProfile(),
        'elderly': PatientProfile(age=75, creatinine_clearance=60, weight=60),
        'obese': PatientProfile(weight=120, age=45),
        'renal_impaired': PatientProfile(creatinine_clearance=30)
    }
    
    # 약물 특성
    drug = DrugProperties()
    
    # 투약 요법들
    regimens = create_standard_dosing_regimens()
    
    all_results = {}
    
    # 각 환자 타입별로 시뮬레이션 실행
    for patient_type, patient in patients.items():
        print(f"👤 {patient_type} 환자 시뮬레이션...")
        
        simulator = ScientificSimulator(patient, drug)
        
        patient_results = {}
        for regimen_name, dose_schedule in regimens.items():
            print(f"   💊 {regimen_name} 요법...")
            
            results = simulator.run_simulation(dose_schedule)
            patient_results[regimen_name] = results
            
            # 개별 시각화 생성
            html_content = simulator.create_plotly_visualization(results)
            
            # 파일명 생성
            filename = f"scientific_{patient_type}_{regimen_name}.html"
            filepath = f"results/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"      ✅ 시각화 저장: {filepath}")
        
        all_results[patient_type] = patient_results
    
    # 전체 결과 JSON 저장
    with open('results/scientific_simulation_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("✅ 모든 시뮬레이션 완료!")
    print("📊 결과 파일들:")
    print("   - results/scientific_simulation_results.json")
    print("   - results/scientific_*.html (인터랙티브 시각화)")
    
    return all_results

if __name__ == "__main__":
    main()
