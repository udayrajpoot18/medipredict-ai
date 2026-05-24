// ============================================
//   MEDIPREDICT AI - ENHANCED ANIMATED JS
// ============================================

let currentDisease = null;

// ===== PAGE LOADER =====
window.addEventListener('load', () => {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('hidden');
            setTimeout(() => loader.remove(), 500);
        }, 800);
    }
    initScrollReveal();
    initCursorGlow();
    initParticles();
    initCounterAnimations();
    initNavbarScroll();
});

// ===== NAVBAR SCROLL EFFECT =====
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 60) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ===== CURSOR GLOW =====
function initCursorGlow() {
    const cursor = document.createElement('div');
    cursor.className = 'cursor-glow';
    document.body.appendChild(cursor);
    
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });
}

// ===== PARTICLES BACKGROUND =====
function initParticles() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particles-canvas';
    document.body.prepend(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const PARTICLE_COUNT = 60;
    
    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2 + 0.5,
            speedX: (Math.random() - 0.5) * 0.4,
            speedY: (Math.random() - 0.5) * 0.4,
            opacity: Math.random() * 0.5 + 0.1,
            color: Math.random() > 0.5 ? '0, 230, 118' : '0, 188, 212'
        });
    }
    
    // Connection lines
    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 230, 118, ${0.08 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        drawConnections();
        
        particles.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            
            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${p.color}, ${p.opacity})`;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// ===== SCROLL REVEAL =====
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });
    
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale').forEach(el => {
        observer.observe(el);
    });
}

// ===== COUNTER ANIMATIONS =====
function initCounterAnimations() {
    // Animate stat numbers if any exist
    const counters = document.querySelectorAll('[data-count]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    counters.forEach(c => observer.observe(c));
}

function animateCounter(el) {
    const target = parseInt(el.dataset.count);
    const duration = 1800;
    const start = performance.now();
    const update = (time) => {
        const elapsed = time - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target);
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = target;
    };
    requestAnimationFrame(update);
}

// ===== NAV RIPPLE EFFECT =====
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            const rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
});

// ===== HAMBURGER MENU =====
function initializeHamburgerMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    if (!hamburger) return;
    
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    navMenu.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    document.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !hamburger.contains(e.target) && navMenu.classList.contains('active')) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        }
    });
}

// ===== TOAST NOTIFICATION =====
function showToast(message, type = 'success') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// ===== SMOOTH SCROLL =====
function scrollServices() {
    document.getElementById('services').scrollIntoView({ behavior: 'smooth' });
}

// ===== OPEN FORM =====
function openForm(type) {
    const formSection = document.getElementById('form-section');
    formSection.classList.add('active');
    document.body.style.overflow = 'hidden';
    currentDisease = type;
    document.getElementById('disease').value = type;

    const diseaseNames = {
        diabetes: 'Diabetes Risk', heart: 'Heart Disease', lung: 'Lung Cancer',
        parkinsons: "Parkinson's Disease", thyroid: 'Thyroid Disorder'
    };
    
    // Update form title
    const formTitle = formSection.querySelector('.form-container h2');
    if (formTitle && diseaseNames[type]) formTitle.textContent = diseaseNames[type];
    
    let html = '';
    if (type === 'diabetes') {
        html = `
            <input type="number" name="f1" placeholder="Glucose Level (70-200 mg/dL)" step="0.1" required>
            <input type="number" name="f2" placeholder="Blood Pressure (40-120 mmHg)" step="0.1" required>
            <input type="number" name="f3" placeholder="BMI (15-50)" step="0.1" required>
            <input type="number" name="f4" placeholder="Age (0-100 years)" step="1" required>
        `;
    } else if (type === 'heart') {
        html = `
            <input type="number" name="f1" placeholder="Age (20-80 years)" step="1" required>
            <input type="number" name="f2" placeholder="Cholesterol (100-400 mg/dL)" step="1" required>
            <input type="number" name="f3" placeholder="Blood Pressure (80-180 mmHg)" step="1" required>
            <input type="number" name="f4" placeholder="Max Heart Rate (60-200 bpm)" step="1" required>
        `;
    } else if (type === 'lung') {
        html = `
            <input type="number" name="f1" placeholder="Smoking Status (0=No, 1=Yes)" min="0" max="1" step="1" required>
            <input type="number" name="f2" placeholder="Age (20-80 years)" step="1" required>
            <input type="number" name="f3" placeholder="Cough Symptoms (0=No, 1=Yes)" min="0" max="1" step="1" required>
            <input type="number" name="f4" placeholder="Fatigue Level (0=No, 1=Yes)" min="0" max="1" step="1" required>
        `;
    } else if (type === 'parkinsons') {
        html = `
            <input type="number" name="f1" placeholder="Voice Tremor (0-1)" step="0.01" required>
            <input type="number" name="f2" placeholder="Pitch (50-300 Hz)" step="0.1" required>
            <input type="number" name="f3" placeholder="Jitter (0-1)" step="0.0001" required>
            <input type="number" name="f4" placeholder="Shimmer (0-1)" step="0.0001" required>
        `;
    } else if (type === 'thyroid') {
        html = `
            <input type="number" name="f1" placeholder="TSH Level (0.4-4.0 mIU/L)" step="0.01" required>
            <input type="number" name="f2" placeholder="T3 Level (80-200 ng/dL)" step="0.1" required>
            <input type="number" name="f3" placeholder="T4 Level (5-12 µg/dL)" step="0.1" required>
            <input type="number" name="f4" placeholder="Age (10-80 years)" step="1" required>
        `;
    }
    document.getElementById('inputs').innerHTML = html;
    
    // Animate inputs with stagger
    const inputs = document.querySelectorAll('#inputs input');
    inputs.forEach((input, i) => {
        input.style.opacity = '0';
        input.style.transform = 'translateY(20px)';
        setTimeout(() => {
            input.style.transition = 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
            input.style.opacity = '1';
            input.style.transform = 'translateY(0)';
        }, i * 80 + 100);
    });
}

// ===== CLOSE FORM =====
function closeForm() {
    const formSection = document.getElementById('form-section');
    formSection.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// ===== PRECAUTION MODAL =====
const diseaseInfo = {
    diabetes: {
        icon: '🩺', name: 'Diabetes Mellitus',
        description: 'Diabetes is a chronic metabolic disorder characterized by high blood sugar levels. It occurs when the pancreas cannot produce enough insulin or when the body cannot effectively use the insulin produced. Type 2 diabetes is the most common form, accounting for 90% of all cases.',
        precautions: ['Monitor blood sugar levels regularly (fasting and random)', 'Maintain a balanced diet low in refined sugars and high in fiber', 'Engage in at least 150 minutes of moderate physical activity per week', 'Keep your weight within a healthy BMI range (18.5-24.9)', 'Limit alcohol consumption', 'Get regular health check-ups and eye examinations', 'Manage stress through meditation and yoga', 'Quit smoking if you smoke', 'Stay hydrated and drink plenty of water', 'Take medications as prescribed by your doctor']
    },
    heart: {
        icon: '❤️', name: 'Heart Disease',
        description: 'Heart disease encompasses various conditions affecting the heart and blood vessels, including coronary artery disease, arrhythmias, and heart failure. It remains the leading cause of death globally.',
        precautions: ['Maintain healthy blood pressure (below 120/80 mmHg)', 'Keep cholesterol levels in check through diet and exercise', 'Avoid smoking and secondhand smoke exposure', 'Exercise regularly (at least 30 minutes, 5 days a week)', 'Follow a heart-healthy diet (Mediterranean or DASH diet)', 'Manage stress with relaxation techniques', 'Maintain a healthy weight', 'Limit sodium intake to less than 2,300mg per day', 'Get adequate sleep (7-9 hours per night)', 'Have regular cardiovascular health check-ups']
    },
    lung: {
        icon: '🫁', name: 'Lung Cancer',
        description: 'Lung cancer is a malignant tumor that develops in the tissues of the lungs. It is the leading cause of cancer deaths worldwide. Smoking is the primary risk factor, but non-smokers can also develop lung cancer.',
        precautions: ['Do not smoke or use tobacco products', 'Avoid secondhand smoke and air pollution', 'Test your home for radon gas and reduce exposure if necessary', 'Work in a safe environment with proper ventilation', 'Avoid asbestos exposure', 'Maintain a healthy diet rich in fruits and vegetables', 'Exercise regularly to keep lungs healthy', 'Get annual screening if you are at high risk', 'Avoid exposure to occupational hazards', 'Report persistent cough or respiratory symptoms to your doctor']
    },
    parkinsons: {
        icon: '🧠', name: "Parkinson's Disease",
        description: "Parkinson's disease is a progressive neurological disorder that affects movement control. It occurs due to the loss of nerve cells that produce dopamine in the brain. While there is no cure, treatments can help manage symptoms.",
        precautions: ['Stay physically active with regular exercise (walking, swimming, dancing)', 'Practice balance and coordination exercises', 'Engage in occupational and speech therapy when recommended', 'Maintain cognitive health through mental exercises and puzzles', 'Get adequate sleep and maintain a regular sleep schedule', 'Manage stress through relaxation and meditation', 'Follow a balanced, nutritious diet', 'Stay socially connected and maintain relationships', 'Take medications exactly as prescribed', 'Attend regular neurological check-ups and follow medical advice']
    },
    thyroid: {
        icon: '🦋', name: 'Thyroid Disorder',
        description: "Thyroid disorders affect the thyroid gland, which controls metabolism. The main types are hypothyroidism (underactive thyroid), hyperthyroidism (overactive thyroid), and thyroid nodules. Early detection is crucial for proper management.",
        precautions: ['Get regular thyroid function tests (TSH, T3, T4)', 'Consume adequate iodine through diet (seafood, dairy, eggs)', 'Maintain a balanced diet with selenium and zinc', 'Manage stress levels effectively', 'Exercise regularly for metabolic health', 'Maintain a healthy weight', 'Avoid excessive iodine supplementation', 'If diagnosed, take thyroid medication as prescribed', 'Get thyroid checked if you have family history of thyroid disease', 'Report symptoms like fatigue, weight changes, or mood swings to your doctor']
    }
};

function openPrecaution(diseaseType) {
    const modal = document.getElementById('precautionModal');
    const detailDiv = document.getElementById('precautionDetail');
    const disease = diseaseInfo[diseaseType];
    if (!disease) return;
    
    const precautionsList = disease.precautions.map((p, i) => 
        `<li style="animation-delay:${i * 0.04}s; animation: fadeInUp 0.4s ease both;">${p}</li>`
    ).join('');
    
    detailDiv.innerHTML = `
        <h2>
            <span class="disease-icon">${disease.icon}</span>
            ${disease.name}
        </h2>
        <div class="description">${disease.description}</div>
        <h3>Prevention & Precautions</h3>
        <ul>${precautionsList}</ul>
    `;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closePrecaution() {
    const modal = document.getElementById('precautionModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// ===== RETAKE / GO HOME =====
function retakeAssessment() {
    const resultCard = document.getElementById('resultCard');
    resultCard.style.display = 'none';
    if (currentDisease) openForm(currentDisease);
}

function goHome() {
    document.getElementById('resultCard').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== DOM READY =====
document.addEventListener('DOMContentLoaded', () => {
    initializeHamburgerMenu();
    
    // Form click outside close
    document.getElementById('form-section').addEventListener('click', (e) => {
        if (e.target === document.getElementById('form-section')) closeForm();
    });
    
    // Precaution modal click outside close
    document.getElementById('precautionModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('precautionModal')) closePrecaution();
    });
    
    // Smooth nav scroll
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // AJAX form submission with loading state
    const form = document.getElementById('assessmentForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const inputs = form.querySelectorAll("input[type='number']");
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value) {
                    isValid = false;
                    input.style.borderColor = '#ef4444';
                    input.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.15)';
                    input.addEventListener('input', () => {
                        input.style.borderColor = '';
                        input.style.boxShadow = '';
                    }, { once: true });
                }
            });
            
            if (!isValid) {
                showToast('Please fill all required fields', 'error');
                return;
            }
            
            const submitBtn = form.querySelector('.submit-btn');
            submitBtn.classList.add('loading');
            submitBtn.innerHTML = `<span style="display:inline-flex;align-items:center;gap:8px"><span style="width:16px;height:16px;border:2px solid rgba(0,230,118,0.3);border-top-color:var(--accent-green);border-radius:50%;animation:rotate-slow 0.8s linear infinite;display:inline-block"></span> Analyzing...</span>`;
            
            const formData = new FormData(form);
            fetch('/predict', { method: 'POST', body: formData })
                .then(r => r.text())
                .then(html => {
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    const resultTitle = doc.querySelector('#resultTitle');
                    if (resultTitle) {
                        document.getElementById('resultTitle').innerHTML = resultTitle.innerHTML;
                        const resultCard = document.getElementById('resultCard');
                        resultCard.style.display = 'block';
                        closeForm();
                        setTimeout(() => resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' }), 150);
                        showToast('Analysis complete! Results ready.', 'success');
                    }
                })
                .catch(() => showToast('Error occurred. Please try again.', 'error'))
                .finally(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = 'Analyze Results';
                });
        });
    }
    
    // Card hover tilt effect
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `translateY(-16px) scale(1.02) rotateX(${-y * 6}deg) rotateY(${x * 6}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.transition = 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
        });
    });
    
    // Precaution cards hover tilt
    document.querySelectorAll('.precaution-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `translateY(-12px) scale(1.04) rotateX(${-y * 8}deg) rotateY(${x * 8}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
    
    // Escape key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { closeForm(); closePrecaution(); }
    });
    
    // Add reveal classes to sections
    const sections = document.querySelectorAll('.hero-left, .hero-right, .about-left, .about-right, .services-header, .card, .precaution-card, .disclaimer-container');
    sections.forEach((el, i) => {
        if (!el.classList.contains('reveal') && !el.classList.contains('reveal-left') && !el.classList.contains('reveal-right')) {
            el.classList.add('reveal');
            if (i % 3 === 0) el.classList.add('stagger-1');
            else if (i % 3 === 1) el.classList.add('stagger-2');
            else el.classList.add('stagger-3');
        }
    });
    initScrollReveal();
});

// ===== SHOW PDF BUTTON AFTER PREDICTION =====
// Flask injects latest_pred_id into a meta tag; JS reads it
function checkPdfButton() {
    const meta = document.getElementById('latestPredId');
    const btn  = document.getElementById('pdfDownloadBtn');
    if (meta && btn && meta.value) {
        btn.href = '/report/' + meta.value + '/pdf';
        btn.style.display = 'inline-flex';
    }
}
document.addEventListener('DOMContentLoaded', checkPdfButton);
