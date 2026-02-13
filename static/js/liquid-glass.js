/**
 * Liquid Glass Effect Library
 * Apple-inspired glass morphism with dynamic refraction and lighting
 */

class LiquidGlass {
    constructor() {
        this.mouseX = 0;
        this.mouseY = 0;
        this.elements = [];
        this.init();
    }

    init() {
        // Track mouse movement for parallax and lighting effects
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
            this.updateLighting();
        });

        // Apply glass effect to all cards and major elements
        this.applyToElements();
        
        // Add dynamic highlights
        this.addDynamicHighlights();
        
        // Initialize refraction effects
        this.initRefractionEffects();
    }

    applyToElements() {
        // Apply to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            this.enhanceElement(card);
        });

        // Apply to buttons
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            this.enhanceButton(button);
        });

        // Apply to inputs
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            this.enhanceInput(input);
        });
    }

    enhanceElement(element) {
        // Add data attribute for tracking
        element.setAttribute('data-liquid-glass', 'true');
        this.elements.push(element);

        // Remove animation after it completes (prevent retriggering)
        element.addEventListener('animationend', () => {
            element.style.animation = 'none';
        }, { once: true });

        // Add mouse move listener for parallax
        element.addEventListener('mousemove', (e) => {
            this.applyParallax(element, e);
        });

        element.addEventListener('mouseleave', () => {
            this.resetParallax(element);
        });
    }

    enhanceButton(button) {
        // Add ripple effect on click
        button.addEventListener('click', (e) => {
            this.createRipple(button, e);
        });

        // Add glow effect on hover
        button.addEventListener('mouseenter', () => {
            this.addGlow(button);
        });

        button.addEventListener('mouseleave', () => {
            this.removeGlow(button);
        });
    }

    enhanceInput(input) {
        // Add focus glow effect
        input.addEventListener('focus', () => {
            this.addInputGlow(input);
        });

        input.addEventListener('blur', () => {
            this.removeInputGlow(input);
        });
    }

    applyParallax(element, e) {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const percentX = (x - centerX) / centerX;
        const percentY = (y - centerY) / centerY;
        
        // Apply 3D rotation transform with smooth interpolation
        const rotateX = (-percentY * 3).toFixed(2);
        const rotateY = (percentX * 3).toFixed(2);
        
        element.style.transform = `translateY(-6px) scale(1.01) perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        element.style.transition = 'transform 0.1s ease-out';
        
        // Update light position
        this.updateElementLight(element, x, y);
    }

    resetParallax(element) {
        // Remove inline transform to let CSS take over
        element.style.transform = '';
        element.style.transition = '';
        this.removeElementLight(element);
    }

    updateElementLight(element, x, y) {
        // Create or update light spot
        let light = element.querySelector('.liquid-light');
        if (!light) {
            light = document.createElement('div');
            light.className = 'liquid-light';
            element.appendChild(light);
        }
        
        light.style.left = x + 'px';
        light.style.top = y + 'px';
        light.style.opacity = '1';
    }

    removeElementLight(element) {
        const light = element.querySelector('.liquid-light');
        if (light) {
            light.style.opacity = '0';
        }
    }

    createRipple(button, e) {
        const ripple = document.createElement('span');
        ripple.className = 'liquid-ripple';
        
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    addGlow(button) {
        button.style.filter = 'brightness(1.15) saturate(1.2)';
    }

    removeGlow(button) {
        button.style.filter = '';
    }

    addInputGlow(input) {
        input.style.filter = 'brightness(1.1) drop-shadow(0 0 8px rgba(0, 122, 255, 0.4))';
    }

    removeInputGlow(input) {
        input.style.filter = '';
    }

    updateLighting() {
        // Update global lighting based on mouse position
        const percentX = (this.mouseX / window.innerWidth) * 100;
        const percentY = (this.mouseY / window.innerHeight) * 100;
        
        // Update CSS custom properties for dynamic lighting
        document.documentElement.style.setProperty('--mouse-x', percentX + '%');
        document.documentElement.style.setProperty('--mouse-y', percentY + '%');
    }

    addDynamicHighlights() {
        // Add subtle shimmer effect to glass elements
        const style = document.createElement('style');
        style.textContent = `
            @keyframes liquidShimmer {
                0%, 100% {
                    background-position: -200% center;
                }
                50% {
                    background-position: 200% center;
                }
            }
            
            .liquid-light {
                position: absolute;
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
                pointer-events: none;
                transform: translate(-50%, -50%);
                transition: opacity 0.3s ease;
                opacity: 0;
                filter: blur(30px);
                z-index: 1;
            }
            
            .liquid-ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.5);
                transform: scale(0);
                animation: liquidRipple 0.6s ease-out;
                pointer-events: none;
            }
            
            @keyframes liquidRipple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            
            [data-liquid-glass="true"] {
                position: relative;
                overflow: hidden;
            }
            
            /* Dynamic gradient overlay */
            [data-liquid-glass="true"]::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(
                    circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
                    rgba(255, 255, 255, 0.1) 0%,
                    transparent 50%
                );
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
                z-index: 1;
            }
            
            [data-liquid-glass="true"]:hover::after {
                opacity: 1;
            }
            
            /* Chromatic aberration effect */
            .chromatic-effect {
                position: relative;
            }
            
            .chromatic-effect::before {
                content: attr(data-text);
                position: absolute;
                left: 0;
                text-shadow: -2px 0 #ff00ff, 2px 0 #00ffff;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .chromatic-effect:hover::before {
                opacity: 0.3;
            }
        `;
        document.head.appendChild(style);
    }

    initRefractionEffects() {
        // Create SVG filter for advanced glass effects
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('style', 'position: absolute; width: 0; height: 0;');
        svg.innerHTML = `
            <defs>
                <!-- Liquid Glass Filter -->
                <filter id="liquidGlassFilter" x="-50%" y="-50%" width="200%" height="200%">
                    <!-- Gaussian Blur for frosted effect -->
                    <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
                    
                    <!-- Displacement Map for refraction -->
                    <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="2" result="turbulence"/>
                    <feDisplacementMap in="blur" in2="turbulence" scale="8" xChannelSelector="R" yChannelSelector="G" result="displacement"/>
                    
                    <!-- Color Matrix for tinting -->
                    <feColorMatrix in="displacement" type="matrix" values="
                        1.1 0   0   0 0
                        0   1.1 0   0 0
                        0   0   1.2 0 0
                        0   0   0   1 0
                    " result="tint"/>
                    
                    <!-- Specular Lighting for highlights -->
                    <feSpecularLighting in="tint" surfaceScale="5" specularConstant="1" specularExponent="20" lighting-color="#ffffff" result="specular">
                        <fePointLight x="150" y="60" z="200"/>
                    </feSpecularLighting>
                    
                    <!-- Composite -->
                    <feComposite in="tint" in2="specular" operator="arithmetic" k1="0" k2="1" k3="1" k4="0"/>
                </filter>
                
                <!-- Glass Reflection Filter -->
                <filter id="glassReflection">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur"/>
                    <feOffset in="blur" dx="2" dy="2" result="offsetBlur"/>
                    <feFlood flood-color="#ffffff" flood-opacity="0.3"/>
                    <feComposite in2="offsetBlur" operator="in"/>
                    <feMerge>
                        <feMergeNode/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
                
                <!-- Frost Pattern -->
                <filter id="frostPattern">
                    <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" result="noise"/>
                    <feColorMatrix in="noise" type="saturate" values="0"/>
                    <feComponentTransfer>
                        <feFuncA type="discrete" tableValues="0 0 0 1"/>
                    </feComponentTransfer>
                    <feGaussianBlur stdDeviation="0.5"/>
                </filter>
            </defs>
        `;
        document.body.insertBefore(svg, document.body.firstChild);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.liquidGlass = new LiquidGlass();
    });
} else {
    window.liquidGlass = new LiquidGlass();
}
