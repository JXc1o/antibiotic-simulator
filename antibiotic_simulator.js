#!/usr/bin/env node
/**
 * 항생제 내성 진화 시뮬레이터 - JavaScript 버전
 * Samsung Innovation Challenge 2025
 * 
 * 실행: node antibiotic_simulator.js
 */

console.log(`
╔══════════════════════════════════════════════════════════════╗
║        항생제 내성 진화 AI 시뮬레이터 v1.0 - JS 버전         ║
║               Samsung Innovation Challenge 2025               ║
╚══════════════════════════════════════════════════════════════╝
`);

class PatientProfile {
    constructor(age, weight, creatinineClearance, infectionSeverity) {
        this.age = age;
        this.weight = weight;
        this.creatinineClearance = creatinineClearance;
        this.infectionSeverity = infectionSeverity;
        this.geneticMarkers = {
            cypActivity: 1.0,
            mdr1Activity: 1.0
        };
        this.comorbidities = [];
    }
}

class DrugProperties {
    constructor(name, micSensitive, micResistant, mpc, halfLife) {
        this.name = name;
        this.micSensitive = micSensitive;
        this.micResistant = micResistant;
        this.mpc = mpc;
        this.halfLife = halfLife;
        this.volumeDistribution = 2.5;
        this.emax = 4.0;
        this.hillCoefficient = 2.0;
    }
}

class PharmacokineticModel {
    constructor(drug, patient) {
        this.drug = drug;
        this.patient = patient;
        this.ke = this.calculateEliminationRate();
        this.vd = this.calculateVolumeDistribution();
    }

    calculateEliminationRate() {
        const baseKe = 0.693 / this.drug.halfLife;
        const renalFactor = this.patient.creatinineClearance / 120.0;
        const geneticFactor = this.patient.geneticMarkers.cypActivity;
        const ageFactor = this.patient.age > 30 ? 
            1.0 - (this.patient.age - 30) * 0.01 : 1.0;
        
        return baseKe * renalFactor * geneticFactor * ageFactor;
    }

    calculateVolumeDistribution() {
        return this.drug.volumeDistribution * this.patient.weight;
    }

    concentrationTimeCourse(doses, times) {
        const concentrations = new Array(times.length).fill(0);
        
        for (let i = 0; i < times.length; i++) {
            let totalConc = 0;
            const t = times[i];
            
            for (let j = 0; j < doses.length; j++) {
                const doseTime = j * 12; // 12시간 간격
                if (t >= doseTime) {
                    const timeSinceDose = t - doseTime;
                    const doseConc = (doses[j] / this.vd) * Math.exp(-this.ke * timeSinceDose);
                    totalConc += doseConc;
                }
            }
            concentrations[i] = totalConc;
        }
        
        return concentrations;
    }
}

class BacterialPopulationModel {
    constructor() {
        this.initialS = 1e8;
        this.initialR = 1e4;
        this.growthRateS = 0.693;
        this.growthRateR = 0.623;
        this.mutationRate = 1e-8;
    }

    pharmacodynamicEffect(concentration, mic, emax = 4.0, hill = 2.0) {
        if (concentration <= 0) return 0;
        return emax * Math.pow(concentration, hill) / 
               (Math.pow(mic, hill) + Math.pow(concentration, hill));
    }

    simulate(concentrations, times, drug) {
        const sTrajectory = [this.initialS];
        const rTrajectory = [this.initialR];
        
        for (let i = 1; i < times.length; i++) {
            const dt = times[i] - times[i-1];
            const C = concentrations[i];
            
            const S = sTrajectory[i-1];
            const R = rTrajectory[i-1];
            
            const killRateS = this.pharmacodynamicEffect(C, drug.micSensitive, drug.emax, drug.hillCoefficient);
            const killRateR = this.pharmacodynamicEffect(C, drug.micResistant, drug.emax, drug.hillCoefficient);
            
            const dS = (this.growthRateS - killRateS) * S * dt - this.mutationRate * S * dt;
            const dR = (this.growthRateR - killRateR) * R * dt + this.mutationRate * S * dt;
            
            sTrajectory.push(Math.max(0, S + dS));
            rTrajectory.push(Math.max(0, R + dR));
        }
        
        return { sensitive: sTrajectory, resistant: rTrajectory };
    }
}

class AntibioticSimulator {
    constructor() {
        this.pkModel = null;
        this.bacterialModel = new BacterialPopulationModel();
    }

    runSimulation(patient, drug, regimen, days = 7) {
        console.log(`\n🔬 시뮬레이션 시작...`);
        console.log(`환자: ${patient.age}세, ${patient.weight}kg, 신기능: ${patient.creatinineClearance}`);
        console.log(`약물: ${drug.name}, 용량: ${regimen.dose}mg, 간격: ${regimen.interval}시간`);
        
        this.pkModel = new PharmacokineticModel(drug, patient);
        
        // 시간 배열 생성
        const totalHours = days * 24;
        const timeStep = 0.25; // 15분 간격
        const times = [];
        for (let t = 0; t <= totalHours; t += timeStep) {
            times.push(t);
        }
        
        // 투약 스케줄
        const numDoses = Math.floor(totalHours / regimen.interval);
        const doses = new Array(numDoses).fill(regimen.dose);
        
        // 약물 농도 계산
        const concentrations = this.pkModel.concentrationTimeCourse(doses, times);
        
        // 세균 집단 시뮬레이션
        const bacterialResults = this.bacterialModel.simulate(concentrations, times, drug);
        
        // 결과 분석
        const finalTotal = bacterialResults.sensitive[bacterialResults.sensitive.length - 1] + 
                          bacterialResults.resistant[bacterialResults.resistant.length - 1];
        const finalResistanceFraction = bacterialResults.resistant[bacterialResults.resistant.length - 1] / finalTotal;
        const treatmentSuccess = finalTotal < 1e6 && finalResistanceFraction < 0.1;
        
        const results = {
            finalBacterialCount: finalTotal,
            resistanceFraction: finalResistanceFraction,
            treatmentSuccess: treatmentSuccess,
            maxConcentration: Math.max(...concentrations),
            minConcentration: Math.min(...concentrations.filter(c => c > 0)),
            concentrations: concentrations,
            bacterialTrajectory: bacterialResults,
            times: times
        };
        
        console.log(`\n📊 시뮬레이션 결과:`);
        console.log(`   최종 세균수: ${results.finalBacterialCount.toExponential(2)} CFU/mL`);
        console.log(`   내성 비율: ${(results.resistanceFraction * 100).toFixed(1)}%`);
        console.log(`   치료 성공: ${results.treatmentSuccess ? '✅ 성공' : '❌ 실패'}`);
        console.log(`   최대 농도: ${results.maxConcentration.toFixed(2)} mg/L`);
        
        return results;
    }

    optimizeRegimen(patient, drug) {
        console.log(`\n🤖 AI 기반 투약 최적화...`);
        
        const doseOptions = [250, 500, 750, 1000];
        const intervalOptions = [6, 8, 12, 24];
        
        let bestRegimen = null;
        let bestScore = -Infinity;
        
        for (const dose of doseOptions) {
            for (const interval of intervalOptions) {
                const regimen = { dose, interval };
                const result = this.runSimulation(patient, drug, regimen, 3); // 짧은 시뮬레이션
                
                // 성공률과 비용을 고려한 스코어
                const score = result.treatmentSuccess ? 1.0 : 0.0 - dose / 1000;
                
                if (score > bestScore) {
                    bestScore = score;
                    bestRegimen = regimen;
                }
            }
        }
        
        console.log(`\n✅ 최적 투약법:`);
        console.log(`   용량: ${bestRegimen.dose}mg`);
        console.log(`   간격: ${bestRegimen.interval}시간`);
        console.log(`   예상 성공률: ${(bestScore * 100).toFixed(1)}%`);
        
        return bestRegimen;
    }
}

// 메인 실행
function main() {
    // 샘플 환자 생성
    const patient = new PatientProfile(65, 75, 80, 0.7);
    patient.comorbidities = ['diabetes', 'hypertension'];
    
    // 샘플 약물
    const drug = new DrugProperties('Ciprofloxacin', 0.5, 8.0, 2.0, 4.0);
    
    // 시뮬레이터 생성
    const simulator = new AntibioticSimulator();
    
    // AI 최적화 실행
    const optimalRegimen = simulator.optimizeRegimen(patient, drug);
    
    // 최적 투약법으로 시뮬레이션
    const finalResults = simulator.runSimulation(patient, drug, optimalRegimen, 7);
    
    // 결과 저장
    const timestamp = new Date().toISOString();
    const report = {
        timestamp,
        patient: {
            age: patient.age,
            weight: patient.weight,
            creatinineClearance: patient.creatinineClearance,
            infectionSeverity: patient.infectionSeverity
        },
        drug: {
            name: drug.name,
            micSensitive: drug.micSensitive,
            micResistant: drug.micResistant
        },
        optimalRegimen,
        results: {
            finalBacterialCount: finalResults.finalBacterialCount,
            resistanceFraction: finalResults.resistanceFraction,
            treatmentSuccess: finalResults.treatmentSuccess
        }
    };
    
    console.log(`\n💾 결과 저장: antibiotic_simulation_js.json`);
    
    // Node.js 환경에서 파일 저장
    if (typeof require !== 'undefined') {
        const fs = require('fs');
        fs.writeFileSync('results/antibiotic_simulation_js.json', JSON.stringify(report, null, 2));
    }
    
    console.log(`\n✅ JavaScript 버전 시뮬레이션 완료!`);
    console.log(`\n🔬 사용 가능한 기능:`);
    console.log(`   ✅ 개인맞춤 약동학 모델`);
    console.log(`   ✅ 세균 집단 동역학`);
    console.log(`   ✅ AI 기반 투약 최적화`);
    console.log(`   ✅ 치료 결과 예측`);
}

// 실행
if (typeof require !== 'undefined' && require.main === module) {
    main();
}

// 모듈 내보내기 (Node.js 환경)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PatientProfile,
        DrugProperties,
        PharmacokineticModel,
        BacterialPopulationModel,
        AntibioticSimulator
    };
}
