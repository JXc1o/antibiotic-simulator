# 🧬 완벽한 항생제 내성 진화 AI 시뮬레이터

## Samsung Innovation Challenge 2025

---

## 🎯 개요

이 프로젝트는 **과학적으로 정확하고 포괄적인 항생제 내성 진화 시뮬레이터**입니다. 
- 📊 **다중 언어 지원**: Python, JavaScript, R, MATLAB
- 🌐 **웹 인터페이스**: 사용자 친화적인 웹 허브
- 📈 **실시간 시각화**: 동적 그래프와 애니메이션
- 🔬 **과학적 정확성**: 문헌 기반의 정확한 모델링

---

## 🚀 빠른 시작

### 1️⃣ 모든 시뮬레이터 한 번에 실행

```bash
cd "antibiotic simulator"
source antibiotic_env/bin/activate
python launch_all.py
```

### 2️⃣ 웹 허브만 실행

```bash
cd "antibiotic simulator"
source antibiotic_env/bin/activate
streamlit run web_hub.py
```

웹 브라우저에서 **http://localhost:8501** 접속

---

## 📁 주요 파일 설명

### 🐍 Python 시뮬레이터

| 파일명 | 설명 | 특징 |
|--------|------|------|
| `scientific_simulator.py` | 과학적으로 정확한 모델 | 📚 문헌 기반, 개인화 약동학 |
| `antibiotic_simulator_clean.py` | 기본 데모 버전 | 🎯 간단한 실행, 교육용 |
| `antibiotic_simulator_full.py` | 고급 기능 포함 | 🤖 AI 최적화, 네트워크 모델 |
| `antibiotic_main.py` | 통합 메인 프로그램 | 🎨 비선형 모델, 한글 지원 |

### ⚡ 다른 언어

| 파일명 | 언어 | 실행 방법 |
|--------|------|-----------|
| `antibiotic_simulator.js` | JavaScript | `node antibiotic_simulator.js` |
| `antibiotic_simulator.R` | R | `Rscript antibiotic_simulator.R` |
| `antibiotic_simulator.m` | MATLAB | `matlab -batch antibiotic_simulator` |

### 🌐 웹 인터페이스

| 파일명 | 설명 | 접속 방법 |
|--------|------|-----------|
| `web_hub.py` | 통합 웹 허브 | http://localhost:8501 |
| `launch_all.py` | 전체 시스템 런처 | 모든 시뮬레이터 통합 실행 |

### 📊 시각화

| 파일명 | 설명 | 특징 |
|--------|------|------|
| `realtime_visualizer.py` | 실시간 시각화 | 🔄 인터랙티브 GUI |
| `animated_visualizer.py` | 애니메이션 시각화 | 🎬 동적 애니메이션 |

---

## 🔧 환경 설정

### 필수 도구

✅ **Python 3.8+** (필수)
✅ **Node.js** (JavaScript 시뮬레이터용)
⚪ **R** (R 시뮬레이터용, 선택사항)
⚪ **MATLAB** (MATLAB 시뮬레이터용, 선택사항)

### Python 패키지 설치

```bash
# 가상환경 활성화
source antibiotic_env/bin/activate

# 필요한 패키지들이 이미 설치되어 있습니다
# numpy, pandas, matplotlib, plotly, streamlit, flask, dash 등
```

---

## 💡 사용법

### 🌐 웹 허브 사용법

1. **웹 허브 실행**
   ```bash
   streamlit run web_hub.py
   ```

2. **브라우저 접속**: http://localhost:8501

3. **시뮬레이터 선택**: 사이드바에서 원하는 시뮬레이터 선택

4. **파라미터 설정**:
   - 👤 환자 정보: 체중, 나이, 신장 기능
   - 💊 투약 설정: 용량, 간격, 치료 기간
   - 🦠 세균 설정: 초기 집단 크기

5. **실행 및 결과 확인**: 실시간 그래프와 통계 확인

### 🐍 개별 Python 시뮬레이터 실행

```bash
# 과학적 정확도 모델
python scientific_simulator.py

# 기본 데모 버전
python antibiotic_simulator_clean.py

# 고급 기능 버전
python antibiotic_simulator_full.py

# 통합 메인 프로그램
python antibiotic_main.py
```

### ⚡ 다른 언어 실행

```bash
# JavaScript
node antibiotic_simulator.js

# R (R이 설치된 경우)
Rscript antibiotic_simulator.R

# MATLAB (MATLAB이 설치된 경우)
matlab -batch antibiotic_simulator
```

---

## 📊 결과 파일

모든 결과는 `results/` 폴더에 저장됩니다:

| 파일 형식 | 설명 | 예시 파일명 |
|-----------|------|-------------|
| `.json` | 시뮬레이션 데이터 | `scientific_simulation_results.json` |
| `.html` | 인터랙티브 그래프 | `scientific_standard_BID_500mg.html` |
| `.png/.svg` | 정적 그래프 | `simulation_results.png` |

---

## 🔬 과학적 정확성

### 📚 참고 문헌 기반 모델링

- **약동학**: Cockcroft-Gault 공식, 1차 제거동역학
- **약력학**: Sigmoid Emax 모델 (Hill equation)
- **세균 동역학**: 로지스틱 성장, 경쟁 모델
- **내성 진화**: Wright-Fisher 모델, 돌연변이율

### 🎯 주요 특징

✅ **개인화 의학**: 환자별 약동학 파라미터 조정
✅ **비선형 모델**: Michaelis-Menten, 시그모이드 곡선
✅ **실시간 적응**: 동적 파라미터 조정
✅ **통계적 검증**: 부트스트랩 신뢰구간

---

## 🛠️ 트러블슈팅

### 자주 발생하는 문제

**❓ 한글이 제대로 표시되지 않는 경우**
```bash
# 한글 폰트 설정이 자동으로 처리됩니다
# macOS: AppleGothic, Apple SD Gothic Neo
# Windows: Malgun Gothic
```

**❓ 그래프가 표시되지 않는 경우**
```bash
# 백엔드 설정이 자동으로 처리됩니다
# macOS: TkAgg
# Windows: Qt5Agg
# Linux: TkAgg
```

**❓ 웹 허브가 실행되지 않는 경우**
```bash
# 포트 충돌 확인
streamlit run web_hub.py --server.port 8502
```

**❓ Node.js 시뮬레이터 오류**
```bash
# Node.js 설치 확인
node --version

# 패키지 설치 (필요한 경우)
npm install
```

### 시스템 요구사항

- **메모리**: 최소 4GB RAM 권장
- **저장공간**: 500MB 이상
- **네트워크**: 웹 허브 사용 시 필요

---

## 🎯 주요 기능

### 🔄 실시간 시뮬레이션
- 파라미터 실시간 조정
- 즉시 결과 반영
- 인터랙티브 그래프

### 📊 다차원 시각화
- 약물 농도 vs 시간
- 세균 집단 동역학
- 내성 비율 변화
- PK/PD 관계

### 🤖 AI 기반 최적화
- 머신러닝 예측
- 개인맞춤 치료
- 자동 용량 조절

### 🌐 웹 기반 접근
- 브라우저에서 실행
- 다중 사용자 지원
- 결과 공유 기능

---

## 📞 지원

**개발팀**: AI 기반 정밀의학 연구팀
**프로젝트**: Samsung Innovation Challenge 2025
**이메일**: 문의사항은 GitHub Issues를 통해 등록해주세요

---

## 🏆 라이선스

이 프로젝트는 **교육 및 연구 목적**으로 개발되었습니다.
상업적 사용을 원하시는 경우 별도 문의 바랍니다.

---

## 🎉 시작하기

```bash
# 1. 가상환경 활성화
source antibiotic_env/bin/activate

# 2. 웹 허브 실행
streamlit run web_hub.py

# 3. 브라우저에서 http://localhost:8501 접속

# 4. 원하는 시뮬레이터 선택하고 실행!
```

**즐거운 시뮬레이션 되세요! 🧬🚀**
